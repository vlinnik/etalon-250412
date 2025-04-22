from pyplc.sfc import SFC,POU
from concrete.container import Container

class Accelerator(SFC):
    dm = POU.var(5.0,persistent=True) #сколько дозировать в точном режиме
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

            