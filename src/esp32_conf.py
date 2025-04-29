from machine import Pin
import sys
usr = Pin(36,Pin.IN)

if not usr.value():
    conf_dir = 'slave_conf'
    port = 9005
    nocli= False    
else:
    conf_dir = '.'
    port = 9004
    nocli= False    
    
__all__ = ['port', 'nocli', 'conf_dir']