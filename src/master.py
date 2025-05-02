# АСУ БСУ ETALON-250412 - Алексеевск Дор Строй
from pyplc.platform import plc
from sys import platform
from concrete import Weight,Container,Dosator,FlowMeter,Factory,Mixer,Manager,Readiness,Loaded,Transport,Lock
from concrete.motor import MotorST as Motor
from concrete.msgate import MPGate as Gate
from concrete.dosator import ManualDosator
from extension import Accelerator as Adapter
from collections import namedtuple
from project import name as project_name
from pyplc.utils.subscriber import Subscriber
from pyplc.utils.latch import RS
from pyplc.utils.trig import FTRIG
from pyplc.utils.misc import BLINK
from concrete.vibrator import UnloadHelper

print(f'\tЗапуск проекта {project_name}, управление цементом/водой/ХД/смесителем')

if platform == 'vscode': #never true, but helps vscode autocomplete IO variables 
    PLC = namedtuple('PLC', ('CEMENT_M_1', 'CEMENT_M_2', 'CEMENT_M_3', 
                            'WATER_M_1', 
                            'ADDITION_M_1', 'ADDITION_M_2', 'ADDITION_M_3', 'ADDITION_M_4', 'ADDITION_M_5', 'ADDITION_M_6', 'ADDITION_M_7', 
                            'MIXER_I_1', 
                            'DCEMENT_CLOSED_1', 'DCEMENT_CLOSED_2', 'DCEMENT_CLOSED_3', 
                            'DWATER_CLOSED_1', 
                            'DADDITION_CLOSED_1', 'DADDITION_CLOSED_2', 'DADDITION_CLOSED_3', 'DADDITION_CLOSED_4', 'DADDITION_CLOSED_5', 'DADDITION_CLOSED_6', 'DADDITION_CLOSED_7', 'DADDITION_CLOSED_8', 'DADDITION_CLOSED_9', 'DADDITION_CLOSED_10', 
                            'AUGER_ISON_1', 'AUGER_ISON_2', 'AUGER_ISON_3', 
                            'WPUMP_ISON_1', 'WPUMP_ISON_2', 
                            'APUMP_ISON_1', 'APUMP_ISON_2', 'APUMP_ISON_3', 'APUMP_ISON_4', 'APUMP_ISON_5', 'APUMP_ISON_6', 'APUMP_ISON_7', 'APUMP_ISON_8', 'APUMP_ISON_9', 'APUMP_ISON_10', 
                            'CONVEYOR_ISON_1', 'TCONVEYOR_ISON_1', 'MC_CLOSED_1', 'MC_OPENED_1', 'MIXER_ISON_1', 'MIXER_CLOSED_1', 'MIXER_MIDDLE_1', 'MIXER_OPENED_1', 
                            'LLEVEL_1', 'LLEVEL_2', 'LLEVEL_3', 'HLEVEL_1', 'HLEVEL_2', 'HLEVEL_3', 
                            'ROPE_1', 'ROPE_2', 'ADDITION_Q_1', 'ADDITION_Q_2','ADDITION_Q_3', 
                            'DADDITION_ISEMPTY_8', 'DADDITION_ISEMPTY_9', 'DADDITION_ISEMPTY_10', 
                            'DCEMENT_OPEN_1', 'DCEMENT_OPEN_2', 'DCEMENT_OPEN_3', 
                            'DWATER_OPEN_1', 'DADDITION_OPEN_1', 'DADDITION_OPEN_2', 'DADDITION_OPEN_3', 'DADDITION_OPEN_4', 'DADDITION_OPEN_5', 'DADDITION_OPEN_6', 'DADDITION_OPEN_7', 'DADDITION_OPEN_8', 'DADDITION_OPEN_9', 'DADDITION_OPEN_10', 
                            'ADDITION_OPEN_1', 'ADDITION_OPEN_2', 'ADDITION_OPEN_3', 'ADDITION_OPEN_4', 'ADDITION_OPEN_5', 'ADDITION_OPEN_6', 'ADDITION_OPEN_7',
                            'MC_OPEN_1', 'MIXER_OPEN_1', 'MIXER_CLOSE_1', 
                            'OIL_ON_1', 'AERATOR_ON_1', 'AERATOR_ON_2', 'AERATOR_ON_3', 'DC_VIBRATOR_ON_1', 'DC_VIBRATOR_ON_2', 'DC_VIBRATOR_ON_3', 'FILTER_CLEAR_1', 
                            'AUGER_ON_1', 'AUGER_ON_2', 'AUGER_ON_3', 'WPUMP_ON_1', 'WPUMP_ON_2', 'APUMP_ON_1', 'APUMP_ON_2', 'APUMP_ON_3', 'APUMP_ON_4', 'APUMP_ON_5', 'APUMP_ON_6', 'APUMP_ON_7', 'APUMP_ON_8', 'APUMP_ON_9', 'APUMP_ON_10', 
                            'CONVEYOR_ON_1', 'TCONVEYOR_ON_1', 'MIXER_STAR_1', 'MIXER_TRIA_1', 'OIL_PUMP_ON_1', 'S_VIBRATOR_ON_1', 'S_VIBRATOR_ON_2', 'S_VIBRATOR_ON_3', 'MC_FILTER_ON_1', 'MC_VIBRATOR_ON_1'))
    plc = PLC()

factory_1 = Factory()
motor_1 = Motor(ison=plc.MIXER_ISON_1,star = plc.MIXER_STAR_1,tria = plc.MIXER_TRIA_1)
gate_1 = Gate( closed = plc.MIXER_CLOSED_1, opened = plc.MIXER_OPENED_1, open = plc.MIXER_OPEN_1, close = plc.MIXER_CLOSE_1 )

# все весы
cement_m_1 = Weight(raw = plc.CEMENT_M_1,mmax=1500)
cement_m_2 = Weight(raw = plc.CEMENT_M_2,mmax=1500)
cement_m_3 = Weight(raw = plc.CEMENT_M_3,mmax=1500)
water_m_1 = Weight(raw = plc.WATER_M_1,mmax=1500)
addition_m_1 = Weight(raw = plc.ADDITION_M_1,mmax=10)
addition_m_2 = Weight(raw = plc.ADDITION_M_2,mmax=10)
addition_m_3 = Weight(raw = plc.ADDITION_M_3,mmax=10)
addition_m_4 = Weight(raw = plc.ADDITION_M_4,mmax=10)
addition_m_5 = Weight(raw = plc.ADDITION_M_5,mmax=10)
addition_m_6 = Weight(raw = plc.ADDITION_M_6,mmax=10)
addition_m_7 = Weight(raw = plc.ADDITION_M_7,mmax=10)

# дозатор цемента #1. набор шнеком
auger_1 = Container(m = lambda: cement_m_1.m, out=plc.AUGER_ON_1, max_sp=1000,lock=Lock(key=~plc.DCEMENT_CLOSED_1))
dcement_1 = Dosator(m = lambda: cement_m_1.m, out=plc.DCEMENT_OPEN_1, closed=plc.DCEMENT_CLOSED_1, containers=( auger_1,),lock=Lock(key=lambda: plc.AUGER_ON_1 or not plc.MIXER_ISON_1) )
# дозатор цемента #2. набор шнеком
auger_2 = Container(m = lambda: cement_m_2.m, out=plc.AUGER_ON_2, max_sp=1000,lock=Lock(key=~plc.DCEMENT_CLOSED_2))
dcement_2 = Dosator(m = lambda: cement_m_2.m, out=plc.DCEMENT_OPEN_2, closed=plc.DCEMENT_CLOSED_2, containers=( auger_2,),lock=Lock(key=lambda: plc.AUGER_ON_2 or not plc.MIXER_ISON_1)  )
# дозатор цемента #3. набор шнеком
auger_3 = Container(m = lambda: cement_m_3.m, out=plc.AUGER_ON_3, max_sp=1000,lock=Lock(key=~plc.DCEMENT_CLOSED_3))
dcement_3 = Dosator(m = lambda: cement_m_3.m, out=plc.DCEMENT_OPEN_3, closed=plc.DCEMENT_CLOSED_3, containers=( auger_3,),lock=Lock(key=lambda: plc.AUGER_ON_3 or not plc.MIXER_ISON_1)  )

aerator_1 = BLINK(enable=plc.AUGER_ON_1,q=plc.AERATOR_ON_1)
aerator_2 = BLINK(enable=plc.AUGER_ON_2,q=plc.AERATOR_ON_2)
aerator_3 = BLINK(enable=plc.AUGER_ON_3,q=plc.AERATOR_ON_3)
dc_vibrator_1 = UnloadHelper(dosator=dcement_1,weight=cement_m_1,q=plc.DC_VIBRATOR_ON_1)
dc_vibrator_2 = UnloadHelper(dosator=dcement_2,weight=cement_m_2,q=plc.DC_VIBRATOR_ON_2)
dc_vibrator_3 = UnloadHelper(dosator=dcement_3,weight=cement_m_3,q=plc.DC_VIBRATOR_ON_3)

# дозатор воды. набор 2мя насосами, грубо обоими, точно поочереди
wpumps_1 = Adapter(outs=(plc.WPUMP_ON_1,plc.WPUMP_ON_2), sts=(~plc.WPUMP_ISON_1,~plc.WPUMP_ISON_2), turbo=True, best=1)
water_1 = Container(m = lambda: water_m_1.m,out=wpumps_1.out,closed=wpumps_1.closed,max_sp=1000,lock=Lock(key=~plc.DWATER_CLOSED_1) )
wpumps_1.container = water_1
dwater_1 = Dosator(m = lambda: water_m_1.m, out=plc.DWATER_OPEN_1, closed=plc.DWATER_CLOSED_1, containers=( water_1,),lock=Lock(key=lambda: plc.WPUMP_ON_1 or plc.WPUMP_ON_2) )

"""
# дозаторы ХД №1-7. набор насосом через переливную емкость и затвором из переливной в точном режиме
"""
# ХД #1. набор насосом через переливную емкость и затвором из переливной в точном режиме
apumpvalve_1 = Adapter(outs=(plc.APUMP_ON_1,plc.ADDITION_OPEN_1),sts=(~plc.APUMP_ISON_1,~plc.ADDITION_OPEN_1), turbo=False, best=1)
addition_1 = Container(m = addition_m_1.get_m, out=apumpvalve_1.out,closed=apumpvalve_1.closed, max_sp=10,lock=Lock(key=~plc.DADDITION_CLOSED_1))
daddition_1 = Dosator(m = addition_m_1.get_m, out=plc.DADDITION_OPEN_1, closed=plc.DADDITION_CLOSED_1, containers=( addition_1,),lock=Lock(key=lambda: plc.APUMP_ON_1 or plc.ADDITION_OPEN_1 or not plc.MIXER_ISON_1) )
apumpvalve_1.container = addition_1
# ХД #2. набор насосом через переливную емкость и затвором из переливной в точном режиме
apumpvalve_2 = Adapter(outs=(plc.APUMP_ON_2,plc.ADDITION_OPEN_2),sts=(~plc.APUMP_ISON_2,~plc.ADDITION_OPEN_2), turbo=False, best=1)
addition_2 = Container(m = addition_m_2.get_m, out=apumpvalve_2.out,closed=apumpvalve_2.closed, max_sp=10,lock=Lock(key=~plc.DADDITION_CLOSED_2))
daddition_2 = Dosator(m = addition_m_2.get_m, out=plc.DADDITION_OPEN_2, closed=plc.DADDITION_CLOSED_2, containers=( addition_2,),lock=Lock(key=lambda: plc.APUMP_ON_2 or plc.ADDITION_OPEN_2 or not plc.MIXER_ISON_1)  )
apumpvalve_2.container = addition_2
# ХД #3. набор насосом через переливную емкость и затвором из переливной в точном режиме
apumpvalve_3 = Adapter(outs=(plc.APUMP_ON_3,plc.ADDITION_OPEN_3),sts=(~plc.APUMP_ISON_3,~plc.ADDITION_OPEN_3), turbo=False, best=1)
addition_3 = Container(m = addition_m_3.get_m, out=apumpvalve_3.out,closed=apumpvalve_3.closed, max_sp=10,lock=Lock(key=~plc.DADDITION_CLOSED_3))
apumpvalve_3.container = addition_3
daddition_3 = Dosator(m = addition_m_3.get_m, out=plc.DADDITION_OPEN_3, closed=plc.DADDITION_CLOSED_3, containers=( addition_3,),lock=Lock(key=lambda: plc.APUMP_ON_3 or plc.ADDITION_OPEN_3 or not plc.MIXER_ISON_1)  )
# ХД #4. набор насосом через переливную емкость и затвором из переливной в точном режиме
apumpvalve_4 = Adapter(outs=(plc.APUMP_ON_4,plc.ADDITION_OPEN_4),sts=(~plc.APUMP_ISON_4,~plc.ADDITION_OPEN_4), turbo=False, best=1)
addition_4 = Container(m = addition_m_4.get_m, out=apumpvalve_4.out, closed=apumpvalve_4.closed, max_sp=10,lock=Lock(key=~plc.DADDITION_CLOSED_4))
daddition_4 = Dosator(m = addition_m_4.get_m, out=plc.DADDITION_OPEN_4, closed=plc.DADDITION_CLOSED_4, containers=( addition_4,),lock=Lock(key=lambda: plc.APUMP_ON_4 or plc.ADDITION_OPEN_4 or not plc.MIXER_ISON_1)  )
apumpvalve_4.container = addition_4
# ХД #5. набор насосом через переливную емкость и затвором из переливной в точном режиме
apumpvalve_5 = Adapter(outs=(plc.APUMP_ON_5,plc.ADDITION_OPEN_5),sts=(~plc.APUMP_ISON_5,~plc.ADDITION_OPEN_5), turbo=False, best=1)
addition_5 = Container(m = addition_m_5.get_m, out=apumpvalve_5.out,closed=apumpvalve_5.closed, max_sp=10,lock=Lock(key=~plc.DADDITION_CLOSED_5))
daddition_5 = Dosator(m = addition_m_5.get_m, out=plc.DADDITION_OPEN_5, closed=plc.DADDITION_CLOSED_5, containers=( addition_5,),lock=Lock(key=lambda: plc.APUMP_ON_5 or plc.ADDITION_OPEN_5 or not plc.MIXER_ISON_1)  )
apumpvalve_5.container = addition_5
# ХД #6. набор насосом через переливную емкость и затвором из переливной в точном режиме
apumpvalve_6 = Adapter(outs=(plc.APUMP_ON_6,plc.ADDITION_OPEN_6),sts=(~plc.APUMP_ISON_6,~plc.ADDITION_OPEN_6), turbo=False, best=1)
addition_6 = Container(m = addition_m_6.get_m, out=apumpvalve_6.out,closed=apumpvalve_6.closed, max_sp=10,lock=Lock(key=~plc.DADDITION_CLOSED_6))
daddition_6 = Dosator(m = addition_m_6.get_m, out=plc.DADDITION_OPEN_6, closed=plc.DADDITION_CLOSED_6, containers=( addition_6,),lock=Lock(key=lambda: plc.APUMP_ON_6 or plc.ADDITION_OPEN_6 or not plc.MIXER_ISON_1)  )
apumpvalve_6.container = addition_6
# ХД #7. набор насосом через переливную емкость и затвором из переливной в точном режиме
apumpvalve_7 = Adapter(outs=(plc.APUMP_ON_7,plc.ADDITION_OPEN_7),sts=(~plc.APUMP_ISON_7,~plc.ADDITION_OPEN_7), turbo=False, best=1)
addition_7 = Container(m = addition_m_7.get_m, out=apumpvalve_7.out,closed=apumpvalve_7.closed, max_sp=10,lock=Lock(key=~plc.DADDITION_CLOSED_7))
daddition_7 = Dosator(m = addition_m_7.get_m, out=plc.DADDITION_OPEN_7, closed=plc.DADDITION_CLOSED_7, containers=( addition_7,),lock=Lock(key=lambda: plc.APUMP_ON_7 or plc.ADDITION_OPEN_7 or not plc.MIXER_ISON_1)  )
apumpvalve_7.container = addition_7
"""
# дозаторы ХД №8-10. набор по расходомеру, выгрузка по датчику уровня
"""
# ХД #8. набор по расходомеру, выгрузка по датчику уровня 
addition_8 = FlowMeter( cnt = plc.ADDITION_Q_8,out=plc.APUMP_ON_8, closed = ~plc.APUMP_ON_8, max_sp=5)
daddition_8 = ManualDosator( level = plc.DADDITION_ISEMPTY_8, out=plc.DADDITION_OPEN_8, closed=plc.DADDITION_CLOSED_8,containers=(addition_8,),lock=Lock(key=lambda: plc.APUMP_ON_8 or not plc.MIXER_ISON_1))
daddition_8.join('loaded',lambda: addition_8.loaded)
# ХД #9. набор по расходомеру, выгрузка по датчику уровня
addition_9 = FlowMeter( cnt = plc.ADDITION_Q_9,out=plc.APUMP_ON_9, max_sp=5 )
daddition_9 = ManualDosator( level = plc.DADDITION_ISEMPTY_9, out=plc.DADDITION_OPEN_9, closed=plc.DADDITION_CLOSED_9,containers=(addition_9,),lock=Lock(key=lambda: plc.APUMP_ON_9 or not plc.MIXER_ISON_1) )
daddition_9.join('loaded',lambda: addition_9.loaded)
# ХД #10. набор по расходомеру, выгрузка по датчику уровня
addition_10 = FlowMeter( cnt = plc.ADDITION_Q_10,out=plc.APUMP_ON_10, max_sp=5 )
daddition_10 = ManualDosator( level = plc.DADDITION_ISEMPTY_10, out=plc.DADDITION_OPEN_10, closed=plc.DADDITION_CLOSED_10,containers=(addition_10,),lock=Lock(key=lambda: plc.APUMP_ON_10 or not plc.MIXER_ISON_1) )
daddition_10.join('loaded',lambda: addition_10.loaded)

#транспорт из под дозаторов инертных до промежуточной емкости, вопрос должен быть включен во время выгрузки или можно на выключенный
tconveyor_1 = Transport( ison=plc.TCONVEYOR_ISON_1, power=plc.TCONVEYOR_ON_1,out=plc.CONVEYOR_ON_1,pt = 20)
conveyor_1 = Transport( ison=plc.CONVEYOR_ISON_1, power=tconveyor_1.set_auto,pt=20)

class Slave(Subscriber):
  FIELDS= ('manual','emergency','go','busy','unload','unloading','tconveyor_ison','mc_opened_1','qreset','load','heartbeat')
  SLAVE = namedtuple('SLAVE',('manual','emergency','go','busy','unload','unloading','tconveyor_ison','mc_opened_1','qreset','load','heartbeat'))
  def __init__(self,host: str,port: int=9005):
      super().__init__( host,port )
      self._go = False
      self._unload = False
      self._unloaded = False
      self.containers = ( )
      self.main:Slave.SLAVE = self.group('slave',Slave.FIELDS)
      with self.main as remote: 
        self.ack_go = RS( set = lambda: self.go, reset = remote.busy, q = remote.go)
        self.ack_unload = RS( set = lambda: self.unload, reset = remote.unloading,q = remote.unload)
        self.ack_unloaded = FTRIG( clk = remote.unloading )

  def __call__(self,**kwds):
    self.ack_go( )
    self.ack_unload( )
    self.ack_unloaded( )
    self.main.tconveyor_ison = plc.CONVEYOR_ISON_1
    self.main.mc_opened_1 = plc.MC_OPENED_1
    conveyor_1.set_auto( self.main.unloading )
    super().__call__(**kwds)
      
  def switch_mode(self,val: bool):
    self.main.manual = val
  
  def emergency(self,val: bool):
    self.main.emergency = val
    self.ack_go.unset( )
    self.ack_unload.unset( )
    
  def set_load(self,load: float):
    self.main.load = load
    
  @property
  def go(self):
    return self._go
  @go.setter
  def go(self,val: bool):
    self._go = val
  
  @property
  def unload(self)->bool:
    return self._unload
  
  @unload.setter
  def unload(self,val: bool):
    self._unload = val
  
  @property
  def unloaded(self):
    return self.ack_unloaded.q
  
  def group(self,id: str,fields: tuple | dict ):
      values = namedtuple( id, fields )( *(self.subscribe(f'{id}.{field}') for field in fields) )
      class remote():
          def __init__(self):
              for key in zip(fields,values):
                  setattr(self.__class__,key[0],key[1])
          def __enter__(self):
              return self.__class__
          def __exit__(self,*args):
              pass
          
      return remote()

if platform == 'linux':
  slave = Slave('127.0.0.1')
else:
  slave = Slave('192.168.2.11')
  
factory_1.bind(Factory.load,slave.set_load )
factory_1.bind(Factory.heartbeat,slave.main.__class__.heartbeat)

mcontainer_1 = ManualDosator( closed=plc.MC_CLOSED_1, out=plc.MC_OPEN_1,helper=plc.MC_VIBRATOR_ON_1,dosator=slave)

mixer_1 = Mixer(gate=gate_1, motor=motor_1, use_ack=False, flows=tuple(x.q for x in [
                auger_1, auger_2, auger_3, 
                water_1, 
                addition_1, addition_2, addition_3, addition_4, addition_5, addition_6, addition_7,daddition_8.expenses[0],daddition_9.expenses[0],daddition_10.expenses[0]]) )

ready_1 = Readiness(rails=(dcement_1, dcement_2,dcement_3,dwater_1,daddition_1,daddition_2,daddition_3,daddition_4,daddition_5,daddition_6,daddition_7,daddition_8,daddition_9,daddition_10,mcontainer_1) )
loaded_1 = Loaded( rails=(dcement_1, dcement_2,dcement_3,dwater_1,daddition_1,daddition_2,daddition_3,daddition_4,daddition_5,daddition_6,daddition_7,daddition_8,daddition_9,daddition_10,mcontainer_1) )
manager_1 = Manager(collected=ready_1,loaded=loaded_1, mixer=mixer_1, dosators=(dcement_1,dcement_2,dcement_3,dwater_1,daddition_1,daddition_2,daddition_3,daddition_4,daddition_5,daddition_6,daddition_7,daddition_8,daddition_9,daddition_10,mcontainer_1) )

factory_1.on_emergency = tuple( x.emergency for x in (dcement_1, dcement_2, dcement_3, dwater_1, daddition_1,daddition_2,daddition_3,daddition_4,daddition_5,daddition_6,daddition_7,daddition_8,daddition_9,daddition_10, mixer_1,manager_1,water_1,mcontainer_1,slave) )
factory_1.on_mode = tuple( x.switch_mode for x in (dcement_1, dcement_2, dcement_3, dwater_1, daddition_1,daddition_2,daddition_3,daddition_4,daddition_5,daddition_6,daddition_7,daddition_8,daddition_9,daddition_10,mcontainer_1,slave) )

def qreset():
  slave.main.qreset = mixer_1.qreset
  
additions = ( addition_m_1,addition_m_2,addition_m_3,addition_m_4,addition_m_5,addition_m_6,addition_m_7,None,None,None,
              daddition_1,daddition_2,daddition_3,daddition_4,daddition_5,daddition_6,daddition_7,daddition_8,daddition_9,daddition_10,
              addition_1, addition_2,addition_3,addition_4,addition_5,addition_6,addition_7,addition_8,addition_9,addition_10,
              apumpvalve_1,apumpvalve_2,apumpvalve_3,apumpvalve_4,apumpvalve_5,apumpvalve_6,apumpvalve_7,None,None,None, 
            )

cements = ( cement_m_1,cement_m_2,cement_m_3, 
            dcement_1,dcement_2,dcement_3,
            auger_1,auger_2,auger_3,
          )

other = ( factory_1,gate_1,motor_1,mixer_1,
          water_m_1,
          dwater_1,
          water_1,
          wpumps_1,
          conveyor_1,tconveyor_1,mcontainer_1,
          ready_1,loaded_1,manager_1,
          slave,qreset,
          aerator_1,aerator_2,aerator_3,dc_vibrator_1,dc_vibrator_2,dc_vibrator_3
        )

stat = (0,0,0)
from time import time_ns
def profiler():
  global stat
  t1 = time_ns()
  index=0
  p0 = t1
  parts = []
  for f in additions:
    if f: f( )
    index+=1
    if index % 10 == 0:
      parts.append( time_ns()-p0 )
      p0=time_ns()
    
  t2 = time_ns()
  for f in cements:
    if f: f( )
  t3 = time_ns()
  for f in other:
    if f: f( )
  t4 = time_ns( )
  stat = ((t2-t1)/(t4-t1)*100,(t3-t2)/(t4-t1)*100,(t4-t3)/(t4-t1)*100)+tuple( x/(t2-t1)*100 for x in parts )
  
def term():
  raise KeyboardInterrupt

instances = (profiler,)

if platform=="linux" or True:
  from concrete.imitation import iGATE,iMOTOR,iVALVE,iWEIGHT,iROTARYFLOW
  from pyplc.utils.latch import RS 
  from pyplc.utils.misc import TON
  icement_m_1 = iWEIGHT( speed=100, loading=plc.AUGER_ON_1, unloading=plc.DCEMENT_OPEN_1, q = plc.CEMENT_M_1 )
  icement_m_2 = iWEIGHT( speed=100, loading=plc.AUGER_ON_2, unloading=plc.DCEMENT_OPEN_2, q = plc.CEMENT_M_2 )
  icement_m_3 = iWEIGHT( speed=100, loading=plc.AUGER_ON_3, unloading=plc.DCEMENT_OPEN_3, q = plc.CEMENT_M_3 )
  iwater_m_1 = iWEIGHT( speed=100, loading=lambda: plc.WPUMP_ON_1 or plc.WPUMP_ON_2, unloading=plc.DWATER_OPEN_1, q = plc.WATER_M_1 )
  iaddition_m_1 = iWEIGHT( speed=100, loading=lambda: plc.APUMP_ON_1 or plc.ADDITION_OPEN_1, unloading=plc.DADDITION_OPEN_1, q = plc.ADDITION_M_1 )
  iaddition_m_2 = iWEIGHT( speed=100, loading=lambda: plc.APUMP_ON_2 or plc.ADDITION_OPEN_2, unloading=plc.DADDITION_OPEN_2, q = plc.ADDITION_M_2 )
  iaddition_m_3 = iWEIGHT( speed=100, loading=lambda: plc.APUMP_ON_3 or plc.ADDITION_OPEN_3, unloading=plc.DADDITION_OPEN_3, q = plc.ADDITION_M_3 )
  iaddition_m_4 = iWEIGHT( speed=100, loading=lambda: plc.APUMP_ON_4 or plc.ADDITION_OPEN_4, unloading=plc.DADDITION_OPEN_4, q = plc.ADDITION_M_4 )
  iaddition_m_5 = iWEIGHT( speed=100, loading=lambda: plc.APUMP_ON_5 or plc.ADDITION_OPEN_5, unloading=plc.DADDITION_OPEN_5, q = plc.ADDITION_M_5 )
  iaddition_m_6 = iWEIGHT( speed=100, loading=lambda: plc.APUMP_ON_6 or plc.ADDITION_OPEN_6, unloading=plc.DADDITION_OPEN_6, q = plc.ADDITION_M_6 )
  iaddition_m_7 = iWEIGHT( speed=100, loading=lambda: plc.APUMP_ON_7 or plc.ADDITION_OPEN_7, unloading=plc.DADDITION_OPEN_7, q = plc.ADDITION_M_7 )
  iaddition_q_8 = iROTARYFLOW( loading=plc.APUMP_ON_8,q = plc.ADDITION_Q_8 )
  iaddition_q_9 = iROTARYFLOW( loading=plc.APUMP_ON_9, q = plc.ADDITION_Q_9 ) 
  iaddition_q_10 = iROTARYFLOW( loading=plc.APUMP_ON_10, q = plc.ADDITION_Q_10 )
  
  imotor_1 = iMOTOR(simple = True,on = plc.MIXER_TRIA_1, ison=plc.MIXER_ISON_1 )
  igate_1 = iGATE(open=plc.MIXER_OPEN_1,close=plc.MIXER_CLOSE_1,opened=plc.MIXER_OPENED_1,closed=plc.MIXER_CLOSED_1)
  
  iauger_1 = iMOTOR(simple=True,on=plc.AUGER_ON_1,ison=plc.AUGER_ISON_1)
  iauger_2 = iMOTOR(simple=True,on=plc.AUGER_ON_2,ison=plc.AUGER_ISON_2)
  iauger_3 = iMOTOR(simple=True,on=plc.AUGER_ON_3,ison=plc.AUGER_ISON_3)
  iwpump_1 = iMOTOR(simple=True,on=plc.WPUMP_ON_1,ison=plc.WPUMP_ISON_1)
  iwpump_2 = iMOTOR(simple=True,on=plc.WPUMP_ON_2,ison=plc.WPUMP_ISON_2)
  iapump_1 = iMOTOR(simple=True,on=plc.APUMP_ON_1,ison=plc.APUMP_ISON_1)
  iapump_2 = iMOTOR(simple=True,on=plc.APUMP_ON_2,ison=plc.APUMP_ISON_2)
  iapump_3 = iMOTOR(simple=True,on=plc.APUMP_ON_3,ison=plc.APUMP_ISON_3)
  iapump_4 = iMOTOR(simple=True,on=plc.APUMP_ON_4,ison=plc.APUMP_ISON_4)
  iapump_5 = iMOTOR(simple=True,on=plc.APUMP_ON_5,ison=plc.APUMP_ISON_5)
  iapump_6 = iMOTOR(simple=True,on=plc.APUMP_ON_6,ison=plc.APUMP_ISON_6)
  iapump_7 = iMOTOR(simple=True,on=plc.APUMP_ON_7,ison=plc.APUMP_ISON_7)
  iapump_8 = iMOTOR(simple=True,on=plc.APUMP_ON_8,ison=plc.APUMP_ISON_8)
  iapump_9 = iMOTOR(simple=True,on=plc.APUMP_ON_9,ison=plc.APUMP_ISON_9)
  iapump_10 = iMOTOR(simple=True,on=plc.APUMP_ON_10,ison=plc.APUMP_ISON_10)
  
  idcement_1 = iVALVE(open=plc.DCEMENT_OPEN_1,closed=plc.DCEMENT_CLOSED_1)
  idcement_2 = iVALVE(open=plc.DCEMENT_OPEN_2,closed=plc.DCEMENT_CLOSED_2)
  idcement_3 = iVALVE(open=plc.DCEMENT_OPEN_3,closed=plc.DCEMENT_CLOSED_3)
  idwater_1 = iVALVE(open=plc.DWATER_OPEN_1,closed=plc.DWATER_CLOSED_1)
  idaddition_1 = iVALVE(open=plc.DADDITION_OPEN_1,closed=plc.DADDITION_CLOSED_1)
  idaddition_2 = iVALVE(open=plc.DADDITION_OPEN_2,closed=plc.DADDITION_CLOSED_2)
  idaddition_3 = iVALVE(open=plc.DADDITION_OPEN_3,closed=plc.DADDITION_CLOSED_3)
  idaddition_4 = iVALVE(open=plc.DADDITION_OPEN_4,closed=plc.DADDITION_CLOSED_4)
  idaddition_5 = iVALVE(open=plc.DADDITION_OPEN_5,closed=plc.DADDITION_CLOSED_5)
  idaddition_6 = iVALVE(open=plc.DADDITION_OPEN_6,closed=plc.DADDITION_CLOSED_6)
  idaddition_7 = iVALVE(open=plc.DADDITION_OPEN_7,closed=plc.DADDITION_CLOSED_7)
  idaddition_8 = iVALVE(open=plc.DADDITION_OPEN_8,closed=plc.DADDITION_CLOSED_8)
  idaddition_9 = iVALVE(open=plc.DADDITION_OPEN_9,closed=plc.DADDITION_CLOSED_9)
  idaddition_10 = iVALVE(open=plc.DADDITION_OPEN_10,closed=plc.DADDITION_CLOSED_10)
  
  iconveyor_1 = iMOTOR(simple=True,on=plc.CONVEYOR_ON_1,ison=plc.CONVEYOR_ISON_1)
  itconveyor_1 = iMOTOR(simple=True,on=plc.TCONVEYOR_ON_1,ison=plc.TCONVEYOR_ISON_1)
  imcontainer_1 = iGATE(simple=True,open=plc.MC_OPEN_1,closed=plc.MC_CLOSED_1,opened=plc.MC_OPENED_1)
  
  daddition_full_8 = RS(reset = TON(clk=plc.DADDITION_OPEN_8),set=plc.APUMP_ON_8,q=plc.DADDITION_ISEMPTY_8.force )
  daddition_full_9 = RS(reset = TON(clk=plc.DADDITION_OPEN_9),set=plc.APUMP_ON_9,q=plc.DADDITION_ISEMPTY_9.force )
  daddition_full_10= RS(reset = TON(clk=plc.DADDITION_OPEN_10),set=plc.APUMP_ON_10,q=plc.DADDITION_ISEMPTY_10.force )
  
  instances+=(icement_m_1,icement_m_2,icement_m_3,
              iwater_m_1, 
              iaddition_m_1,iaddition_m_2,iaddition_m_3,iaddition_m_4,iaddition_m_5,iaddition_m_6,iaddition_m_7,iaddition_q_8,iaddition_q_9,iaddition_q_10,
              imotor_1,igate_1,
              iauger_1,iauger_2,iauger_3,
              iwpump_1,iwpump_2,
              iapump_1,iapump_2,iapump_3,iapump_4,iapump_5,iapump_6,iapump_7,iapump_8,iapump_9,iapump_10,
              idcement_1,idcement_2,idcement_3,
              idwater_1,
              idaddition_1,idaddition_2,idaddition_3,idaddition_4,idaddition_5,idaddition_6,idaddition_7,idaddition_8,idaddition_9,idaddition_10,
              iconveyor_1,itconveyor_1,imcontainer_1,
              daddition_full_8,daddition_full_9,daddition_full_10
              )

print(f'\tИнициализация проекта {project_name} завершена, работаем...')
plc.run(instances=instances, ctx=globals())
