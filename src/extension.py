from pyplc.sfc import SFC,POU
from concrete.container import Container
from concrete.dosator import Dosator
from concrete.manager import Readiness,Loaded
from pyplc.utils.latch import RS

class Accelerator(SFC):
    dm = POU.var(1.5,persistent=True) #сколько дозировать в точном режиме
    def __init__(self, outs: tuple[callable], sts: tuple[callable] = (),turbo = True, best:int = None , id: str=None, parent: POU = None):
        """Создать ускоритель набора из группы затворов.
        
        Ускоритель позволяет одновременно открывать несколько затворов во время набора в грубом режиме, а в точном режиме - поочередно.

        Args:
            outs (list[callable]): Управляющие сигналы затворами (etc FILLER_OPEN_1)
            sts (list[callable], optional): Обратная связь по затворам (etc FILLER_CLOSED_1). Defaults to [].
            turbo (bool, optional): Режим быстрого набора - из всех затворов сразу.False - best не использовать, True - best использовать. Defaults to True.
            best (int, optional): Номер затвора, которым надо добирать. Defaults to None.
        """        
        super().__init__(id=id,parent=parent)
        self.cnt = len(outs)        #сколько доступно затворов
        self.outs = outs            #все затворы в помощь  
        self.sts = sts              #обратная связь по затворам
        self.turbo = turbo          #режим быстрого набора
        self.best = best            #номер затвора, которым надо добирать
        self._closed = True         #текущее состояние затворов
        self._out = False
        self._container:Container = None      #информация о контейнере, который получает ускорение при наборе
        self._available = tuple(range(self.cnt))    #номера всех затворов с 0 , для оптимизации

        for i in self._available:
            self.export(f'disable_{i+1}',False)
            
        self.subtasks += (self.__update_closed, )
    
    def out(self,out: bool):
        self._out = out
            
    def closed(self):
        return self._closed
    
    @property
    def container(self) -> Container:
        """Контейнер, который получает ускорение при наборе"""
        return self._container
    
    @container.setter
    def container(self, container: Container):
        self._container = container
        
    @property
    def m(self) -> float:
        """Вес дозатора, куда насыпаем"""
        if self.container:
            return self.container.m
        return 0.0
    
    def __update_closed(self):
        closed = True
        for i in self._available:
            closed = closed and self.sts[i]()
        self._closed = closed
        
    def _fast(self,en: bool):
        for i in self._available:
            self.outs[i]( (en if i!=self.best else self.turbo) and self._out )

    def _slow(self,en: bool):
        if self.best is not None:
            self.outs[self.best]( en and self._out )
        else:
            self._fast(en)
            
    def main(self):
        if self.container:
            yield from self.until(lambda: self.container.busy,step='ожидание') 
            till = self.m + self.container.sp - self.dm - self.container.take
            yield from self.till(lambda: self.m<till and self.container.busy,n=(self._fast,),step='быстрый режим' )
            yield from self.till(lambda: self.container.busy, n=(self._slow,),step='медленный режим' )
            yield from self.until(lambda: self._closed,step='ждем закрытия')
        else:
            self.outs[0](self._out)

class Retarder(Accelerator):
    maxT = POU.var(int(3000),persistent=True)
    
    def __init__(self, outs, sts = (), turbo=True, best = None, id = None, parent = None):
        super().__init__(outs, sts, turbo, best, id, parent)
        self._current = best if best is not None else 0
        self.dm = 100
        
    def main(self):
        if self.container:
            yield from self.until(lambda: self.container.busy,step='ready')
            self._current=self.best if self.best is not None else self._current
            while self._out:
                till = self.m + self.dm
                yield from self.till( lambda: self.m<till and self._out,max=self.maxT,n=[self.outs[self._current]])
                self._current=(self._current+1) % len(self.outs)
                yield
            yield from self.until(lambda: self._closed,step='wait.closed')
        else:
            self.outs[0](self._out)
        

class GroupDosator(SFC):
    forced = POU.var(int(-1))   #этот дозатор обрабатывается безусловно
    def __init__(self, dosators:tuple[Dosator] = (), id = None, parent = None):
        super().__init__(id, parent)
        self.count = 1
        self.go = False
        self.ready = False
        self.loaded = False
        self.unload = False
        self._unload= False
        self.unloaded= False
        self.dosators = dosators
        self._used = ( )
        self._loaded:Readiness = None
        self._unloaded:Loaded = None
        self.s_unload = RS(set=lambda: self.unload)
        self.subtasks = (self._always,self.s_unload )
        
    def switch_mode(self,manual: bool):
        pass
            
    def emergency(self,emergency: bool):
        if emergency:
            self._loaded = None
            self._unloaded = None
            self._used = ( )
            
        self.unload = False
        self.s_unload.unset( )                

        for d in self.dosators:
            d.emergency(emergency)
            d()
        self.sfc_reset = emergency
    
    def _always(self):
        all_ready = True
        all_nready = False
        for d in self._used:
            d.go = self.go
            d.unload = self.s_unload.q
            d( )
            all_ready = all_ready and d.ready
            all_nready = all_nready or d.ready
            for c in d.containers:
                c( )
        if self.forced>=0 and self.forced<len(self.dosators):
            self.dosators[self.forced]( )
        
        if self.go:
            self.ready = all_nready 
        else:
            self.ready = all_ready 
                
        if self._loaded is not None:
            self.loaded = self._loaded( )
        else:
            self.loaded = self.go
        if self._unloaded:
            self.unloaded = self._unloaded( )
        else:
            self.unloaded = self.unload and not self._unload
            self._unload = self.unload

    def cycle(self,batch:int ):
        self.log(f'запускаем необходимые дозаторы')
        yield from self.until( lambda: self.loaded ,step='wait.loaded')
        self.log(f'необходимые дозаторы загружены')
        yield from self.until(lambda: self.s_unload.q, step = 'wait.unload')
        self.s_unload.unset()
        self._unload = False
        self.unload = False
        self.log(f'выгрузка группового дозатора')
        yield from self.until( lambda: self.unloaded, step='wait.unloaded')
        self.log(f'завершение выгрузки группового дозатора')
        yield from self.till( lambda: self.unloaded,step = 'wait.clear.unloaded' )
        self.log(f'замес выгружен в смеситель')
            
    def main(self):
        self.log('готов')
        
        self.ready = True
        yield from self.until(lambda: self.go,step='ready')
        self._used = tuple(d for d in filter(lambda d: sum( (c.sp for c in d.containers) )>0 , self.dosators )) 
        if len(self._used)>0:
            self._loaded = Readiness( self._used )
            self._unloaded = Loaded( self._used )
        self._unload = False
        # self.ready = False
        yield from self.till(lambda: self.go, step='steady')
        batch = 0        
        count = self.count
        self.log(f'запуск, {count} циклов')
        while batch<count:   
            yield from self.cycle(batch)

            batch = batch+1 
            count = self.count 
        
        self._loaded = None
        self._unloaded = None
        self._used = ( )