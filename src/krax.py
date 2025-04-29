import sys

for m in ('master','slave'):
    if m in sys.modules:
        del(sys.modules[m])

try:
    from machine import Pin
    import sys
    usr = Pin(36,Pin.IN)
    if not usr.value():
        print('\tПереключатель USR включен.')
        import slave
    else:
        print('\tПереключатель USR выключен.')
        import master
except Exception as e:
    print(f'krax.py предназначен только для ESP32 ({e})')