import sys

for m in ('master','slave'):
    if m in sys.modules:
        del(sys.modules[m])

try:
  from machine import RTC
  from ds1390 import datetime
  rtc = RTC()
  rtc.init( datetime() )
except:
  pass

try:
    from machine import Pin
    import sys
    usr = Pin(36,Pin.IN)
    rtc_cs = Pin(2,Pin.OUT,1)
    eer_cs = Pin(2,Pin.OUT,1)
    if not usr.value():
        print('\tПереключатель USR включен.')
        import slave
    else:
        print('\tПереключатель USR выключен.')
        import master
except Exception as e:
    print(f'krax.py предназначен только для ESP32 ({e})')