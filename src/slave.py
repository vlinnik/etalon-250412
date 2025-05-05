from pyplc.platform import plc
from sys import platform
from collections import namedtuple
from project import name as project_name
from concrete import Container,Dosator,Weight
from concrete.counting import Expense,MoveFlow
from concrete.vibrator import Vibrator,UnloadHelper
from extension import Retarder as Accelerator
from pyplc.pou import POU
from pyplc.utils.trig import TRIG
from pyplc.utils.latch import RS
from concrete.manager import Loaded,Lock


print(f'\tЗапуск проекта {project_name}, управление бункерами инертных')

if platform == 'vscode':
    PLC = namedtuple('PLC', ('FILLER_M_1', 'FILLER_M_2', 'FILLER_M_3', 'FILLER_M_4', 'FILLER_M_5', 'FILLER_M_6', 'DFILLER_CLOSED_1', 'DFILLER_CLOSED_2', 'DFILLER_CLOSED_3', 'DFILLER_CLOSED_4', 'DFILLER_CLOSED_5', 'DFILLER_CLOSED_6', 'FILLER_CLOSED_1', 'FILLER_CLOSED_2', 'FILLER_CLOSED_3', 'FILLER_CLOSED_4', 'FILLER_CLOSED_5', 'FILLER_CLOSED_6', 'FILLER_CLOSED_7', 'FILLER_CLOSED_8', 'FILLER_CLOSED_9', 'FILLER_CLOSED_10', 'FILLER_CLOSED_11', 'FILLER_CLOSED_12', 'DFILLER_OPEN_1',
                     'DFILLER_OPEN_2', 'DFILLER_OPEN_3', 'DFILLER_OPEN_4', 'DFILLER_OPEN_5', 'DFILLER_OPEN_6', 'FILLER_OPEN_1', 'FILLER_OPEN_2', 'FILLER_OPEN_3', 'FILLER_OPEN_4', 'FILLER_OPEN_5', 'FILLER_OPEN_6', 'FILLER_OPEN_7', 'FILLER_OPEN_8', 'FILLER_OPEN_9', 'FILLER_OPEN_10', 'FILLER_OPEN_11', 'FILLER_OPEN_12', 'VIBRATOR_ON_1', 'VIBRATOR_ON_2', 'VIBRATOR_ON_3', 'VIBRATOR_ON_4', 'VIBRATOR_ON_5', 'VIBRATOR_ON_6', 'DF_VIBRATOR_ON_1', 'DF_VIBRATOR_ON_2', 'DF_VIBRATOR_ON_3','HEARTBEAT_1'))
    plc = PLC()
    
class Slave(POU):
    manual = POU.input(True)
    emergency= POU.input(False)
    
    qreset = POU.var(False)
    mc_opened_1 = POU.input(False)    #промежуточный бункер открыт
    tconveyor_ison=POU.input(False)   #транспортный конвейер включен 
    unloaded = POU.var(False)
    
    go = POU.var(False)
    count= POU.var(int(1))
    busy = POU.var(False)
    unload = POU.var(False)
    unloading = POU.var(False)
    
    load = POU.output(float(0.0))
    heartbeat = POU.output(False)
    
    expense_14 = POU.var(0.0)
    expense_15 = POU.var(0.0)
    expense_16 = POU.var(0.0)
    expense_17 = POU.var(0.0)
    expense_18 = POU.var(0.0)
    expense_19 = POU.var(0.0)
    
    weight = POU.output( 0.0 ) #сколько сейчас в mcontainer
    
    def __init__(self,containers: tuple[Container], id = None, parent = None):
        super().__init__(id, parent)
        self.t_manual = TRIG(clk=lambda: self.manual)
        self.t_emergency=TRIG(clk=lambda: self.emergency)
        self.containers = containers
        self.dosators = ( )
        self.mcontainer = tuple( MoveFlow( flow_in = c.q, out = lambda: self.mc_opened_1 ) for c in containers ) #в промежуточный
        self.expenses = tuple( Expense( f.q, lambda: self.qreset ) for f in self.mcontainer )   #в смесителе
        self.bind(Slave.load, self._load_changed)
        self.bind(Slave.heartbeat, plc.HEARTBEAT_1) 
    def _load_changed(self,load: float):
        Weight.g_Load = load
    
    def set_dosators(self,*args):
        self.dosators = tuple(args)
        self.f_unloaded = Loaded( self.dosators )
        self.t_unloading = RS(reset=self.f_unloaded, set=lambda: self.unload )

    def __call__( self ):
        with self:
            if self.t_manual():
                for d in self.dosators: d.switch_mode(self.manual)
            if self.t_emergency():
                for d in self.dosators: d.emergency(self.emergency)
                self.t_unloading.unset( )
                self.f_unloaded.clear( )
            
            self.busy = all( (not d.ready for d in self.dosators) )
            self.unloading = self.t_unloading( )
            for d in self.dosators:
                d.count = self.count
                d.unload = self.unload
                d.go = self.go
                        
            index = 14
            weight = 0.0
            for e in self.mcontainer:   #учет в промежуточный контейнер
                weight += e( )
            self.weight = weight
            for e in self.expenses:     #учет в смеситель
                setattr(self,f'expense_{index}',e())
                index += 1
                
filler_m_1 = Weight(raw = plc.FILLER_M_1, mmax=4000)
filler_m_2 = Weight(raw = plc.FILLER_M_2, mmax=4000)
filler_m_3 = Weight(raw = plc.FILLER_M_3, mmax=4000)
filler_m_4 = Weight(raw = plc.FILLER_M_4, mmax=4000)
filler_m_5 = Weight(raw = plc.FILLER_M_5, mmax=4000)
filler_m_6 = Weight(raw = plc.FILLER_M_6, mmax=4000)

twogate_1 = Accelerator(outs=(plc.FILLER_OPEN_1,plc.FILLER_OPEN_2),sts=(plc.FILLER_CLOSED_1,plc.FILLER_CLOSED_2))
twogate_2 = Accelerator(outs=(plc.FILLER_OPEN_3,plc.FILLER_OPEN_4),sts=(plc.FILLER_CLOSED_3,plc.FILLER_CLOSED_4))
twogate_3 = Accelerator(outs=(plc.FILLER_OPEN_5,plc.FILLER_OPEN_6),sts=(plc.FILLER_CLOSED_5,plc.FILLER_CLOSED_6))
twogate_4 = Accelerator(outs=(plc.FILLER_OPEN_7,plc.FILLER_OPEN_8),sts=(plc.FILLER_CLOSED_7,plc.FILLER_CLOSED_8))
twogate_5 = Accelerator(outs=(plc.FILLER_OPEN_9,plc.FILLER_OPEN_10),sts=(plc.FILLER_CLOSED_9,plc.FILLER_CLOSED_10))
twogate_6 = Accelerator(outs=(plc.FILLER_OPEN_11,plc.FILLER_OPEN_12),sts=(plc.FILLER_CLOSED_11,plc.FILLER_CLOSED_12))

filler_1 = Container(m = filler_m_1.get_m,out=twogate_1.out,closed=twogate_1.closed,max_sp=4000)
filler_2 = Container(m = filler_m_2.get_m,out=twogate_2.out,closed=twogate_2.closed,max_sp=4000)
filler_3 = Container(m = filler_m_3.get_m,out=twogate_3.out,closed=twogate_3.closed,max_sp=4000)
filler_4 = Container(m = filler_m_4.get_m,out=twogate_4.out,closed=twogate_4.closed,max_sp=4000)
filler_5 = Container(m = filler_m_5.get_m,out=twogate_5.out,closed=twogate_5.closed,max_sp=4000)
filler_6 = Container(m = filler_m_6.get_m,out=twogate_6.out,closed=twogate_6.closed,max_sp=4000)

twogate_1.container = filler_1
twogate_2.container = filler_2
twogate_3.container = filler_3
twogate_4.container = filler_4
twogate_5.container = filler_5
twogate_6.container = filler_6

slave = Slave( containers=(filler_1,filler_2,filler_3,filler_4,filler_5,filler_6) )

dfiller_1 = Dosator( m = lambda: filler_m_1.m, out=plc.DFILLER_OPEN_1,closed=plc.DFILLER_CLOSED_1,containers=(filler_1,),lock=Lock(key=lambda: not slave.tconveyor_ison))
dfiller_2 = Dosator( m = lambda: filler_m_2.m, out=plc.DFILLER_OPEN_2,closed=plc.DFILLER_CLOSED_2,containers=(filler_2,),lock=Lock(key=lambda: not slave.tconveyor_ison))
dfiller_3 = Dosator( m = lambda: filler_m_3.m, out=plc.DFILLER_OPEN_3,closed=plc.DFILLER_CLOSED_3,containers=(filler_3,),lock=Lock(key=lambda: not slave.tconveyor_ison))
dfiller_4 = Dosator( m = lambda: filler_m_4.m, out=plc.DFILLER_OPEN_4,closed=plc.DFILLER_CLOSED_4,containers=(filler_4,),lock=Lock(key=lambda: not slave.tconveyor_ison))
dfiller_5 = Dosator( m = lambda: filler_m_5.m, out=plc.DFILLER_OPEN_5,closed=plc.DFILLER_CLOSED_5,containers=(filler_5,),lock=Lock(key=lambda: not slave.tconveyor_ison))
dfiller_6 = Dosator( m = lambda: filler_m_6.m, out=plc.DFILLER_OPEN_6,closed=plc.DFILLER_CLOSED_6,containers=(filler_6,),lock=Lock(key=lambda: not slave.tconveyor_ison))

vibrator_1 = Vibrator( q = plc.VIBRATOR_ON_1, containers = (plc.FILLER_OPEN_1,plc.FILLER_OPEN_2),weight=filler_m_1)
vibrator_2 = Vibrator( q = plc.VIBRATOR_ON_2, containers = (plc.FILLER_OPEN_3,plc.FILLER_OPEN_4),weight=filler_m_2)
vibrator_3 = Vibrator( q = plc.VIBRATOR_ON_3, containers = (plc.FILLER_OPEN_5,plc.FILLER_OPEN_6),weight=filler_m_3)
vibrator_4 = Vibrator( q = plc.VIBRATOR_ON_4, containers = (plc.FILLER_OPEN_7,plc.FILLER_OPEN_8),weight=filler_m_4)
vibrator_5 = Vibrator( q = plc.VIBRATOR_ON_5, containers = (plc.FILLER_OPEN_9,plc.FILLER_OPEN_10),weight=filler_m_5)
vibrator_6 = Vibrator( q = plc.VIBRATOR_ON_6, containers = (plc.FILLER_OPEN_11,plc.FILLER_OPEN_12),weight=filler_m_6)

df_vibrator_1 = UnloadHelper( q=plc.DF_VIBRATOR_ON_1, dosator=dfiller_1, weight=filler_m_1 )
df_vibrator_2 = UnloadHelper( q=plc.DF_VIBRATOR_ON_2, dosator=dfiller_2, weight=filler_m_2 )
df_vibrator_3 = UnloadHelper( q=plc.DF_VIBRATOR_ON_3, dosator=dfiller_1, weight=filler_m_3 )

slave.set_dosators( dfiller_1,dfiller_2,dfiller_3,dfiller_4,dfiller_5,dfiller_6 )

instances = (
            slave,
            filler_m_1,filler_m_2,filler_m_3,filler_m_4,filler_m_5,filler_m_6,
            dfiller_1,dfiller_2,dfiller_3,dfiller_4,dfiller_5,dfiller_6,
            twogate_1,twogate_2,twogate_3,twogate_4,twogate_5,twogate_6,
            filler_1,filler_2,filler_3,filler_4,filler_5,filler_6,
            vibrator_1,vibrator_2,vibrator_3,vibrator_4,vibrator_5,vibrator_6,
            df_vibrator_1,df_vibrator_2,df_vibrator_3
            )

if platform=='linux' or True:
    from concrete.imitation import iVALVE,iWEIGHT
    idfiller_1 = iVALVE(open=plc.DFILLER_OPEN_1,closed=plc.DFILLER_CLOSED_1)
    idfiller_2 = iVALVE(open=plc.DFILLER_OPEN_2,closed=plc.DFILLER_CLOSED_2)
    idfiller_3 = iVALVE(open=plc.DFILLER_OPEN_3,closed=plc.DFILLER_CLOSED_3)
    idfiller_4 = iVALVE(open=plc.DFILLER_OPEN_4,closed=plc.DFILLER_CLOSED_4)
    idfiller_5 = iVALVE(open=plc.DFILLER_OPEN_5,closed=plc.DFILLER_CLOSED_5)
    idfiller_6 = iVALVE(open=plc.DFILLER_OPEN_6,closed=plc.DFILLER_CLOSED_6)
    ifiller_1 = iVALVE(open=plc.FILLER_OPEN_1,closed=plc.FILLER_CLOSED_1)
    ifiller_2 = iVALVE(open=plc.FILLER_OPEN_2,closed=plc.FILLER_CLOSED_2)
    ifiller_3 = iVALVE(open=plc.FILLER_OPEN_3,closed=plc.FILLER_CLOSED_3)
    ifiller_4 = iVALVE(open=plc.FILLER_OPEN_4,closed=plc.FILLER_CLOSED_4)
    ifiller_5 = iVALVE(open=plc.FILLER_OPEN_5,closed=plc.FILLER_CLOSED_5)
    ifiller_6 = iVALVE(open=plc.FILLER_OPEN_6,closed=plc.FILLER_CLOSED_6)
    ifiller_7 = iVALVE(open=plc.FILLER_OPEN_7,closed=plc.FILLER_CLOSED_7)
    ifiller_8 = iVALVE(open=plc.FILLER_OPEN_8,closed=plc.FILLER_CLOSED_8)
    ifiller_9 = iVALVE(open=plc.FILLER_OPEN_9,closed=plc.FILLER_CLOSED_9)
    ifiller_10 = iVALVE(open=plc.FILLER_OPEN_10,closed=plc.FILLER_CLOSED_10)
    ifiller_11 = iVALVE(open=plc.FILLER_OPEN_11,closed=plc.FILLER_CLOSED_11)
    ifiller_12 = iVALVE(open=plc.FILLER_OPEN_12,closed=plc.FILLER_CLOSED_12)
    ifiller_m_1 = iWEIGHT(speed=100,loading=lambda:plc.FILLER_OPEN_1 or plc.FILLER_OPEN_2,unloading=plc.DFILLER_OPEN_1,q = plc.FILLER_M_1)
    ifiller_m_2 = iWEIGHT(speed=100,loading=lambda:plc.FILLER_OPEN_3 or plc.FILLER_OPEN_4,unloading=plc.DFILLER_OPEN_2,q = plc.FILLER_M_2)
    ifiller_m_3 = iWEIGHT(speed=100,loading=lambda:plc.FILLER_OPEN_5 or plc.FILLER_OPEN_6,unloading=plc.DFILLER_OPEN_3,q = plc.FILLER_M_3)
    ifiller_m_4 = iWEIGHT(speed=100,loading=lambda:plc.FILLER_OPEN_7 or plc.FILLER_OPEN_8,unloading=plc.DFILLER_OPEN_4,q = plc.FILLER_M_4)
    ifiller_m_5 = iWEIGHT(speed=100,loading=lambda:plc.FILLER_OPEN_9 or plc.FILLER_OPEN_10,unloading=plc.DFILLER_OPEN_5,q = plc.FILLER_M_5)
    ifiller_m_6 = iWEIGHT(speed=100,loading=lambda:plc.FILLER_OPEN_11 or plc.FILLER_OPEN_12,unloading=plc.DFILLER_OPEN_6,q = plc.FILLER_M_6)
    instances+=(idfiller_1,idfiller_2,idfiller_3,idfiller_4,idfiller_5,idfiller_6,
                ifiller_1,ifiller_2,ifiller_3,ifiller_4,ifiller_5,ifiller_6,ifiller_7,ifiller_8,ifiller_9,ifiller_10,ifiller_11,ifiller_12,
                ifiller_m_1,ifiller_m_2,ifiller_m_3,ifiller_m_4,ifiller_m_5,ifiller_m_6)
    
plc.run( instances=instances,ctx=globals() )