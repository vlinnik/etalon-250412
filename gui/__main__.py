import sys
from pysca import app
from pysca.device import PYPLC
from concrete6 import concrete6
import pygui.multihead as navbar
from AnyQt.QtCore import QThread,QCoreApplication

def whats_inside(*args):
    try:
        n = 0
        msg = '<table><tr><th align="left">КОМПОНЕНТ</th><th align="right">M</th></tr>'
        for arg in args:
            if arg>0:
                if n>=4 and n<=13:
                    msg += f'<tr><td>{concrete6.containers[n].component}</td><td align="right">{arg:.3f}</td></tr>\n'
                else:
                    msg += f'<tr><td>{concrete6.containers[n].component}</td><td align="right">{arg:.0f}</td></tr>\n'
            n+=1
        msg+='</table>'
        return msg
    except:
        pass
    
    return "Here should be an tooltip"


def main():
    import argparse
    args = argparse.ArgumentParser(sys.argv)
    args.add_argument('--device', action='store', type=str, default='192.168.2.10', help='IP address of the device')
    args.add_argument('--slave', action='store', type=str, default='192.168.2.11', help='IP address of the slave device')
    args.add_argument('--simulator', action='store_true', default=False, help='Same as --device 127.0.0.1')
    ns = args.parse_known_args()[0]
    if ns.simulator:
        ns.device = '127.0.0.1'
        ns.slave = '127.0.0.1'
        import subprocess
        logic = subprocess.Popen(["python3", "src/master.py"])
        slave = subprocess.Popen(["python3", "src/slave.py","--conf=slave_conf","--port=9005","--cli=2456"])
    
    dev = PYPLC(ns.device)
    sec = PYPLC(ns.slave,port=9005)
    app.devices['PLC'] = dev
    app.devices['SLAVE'] = sec
    
    Home = app.window('ui/Home.ui',ctx={"whats_inside":whats_inside})
    Additions = app.window('ui/Additions.ui')
    app.object(concrete6.instance)
    # с использованием navbar
    navbar.append(Additions)
    navbar.append(Home)
    navbar.tools(app.window('ui/Extensions.ui'))
    concrete6.setContainerPanels((Home.cpanel_1, Home.cpanel_2, Home.cpanel_3, Home.cpanel_4, Additions.cpanel_1, Additions.cpanel_2, Additions.cpanel_3, Additions.cpanel_4, Additions.cpanel_5,
                                 Additions.cpanel_6, Additions.cpanel_7, Additions.cpanel_8, Additions.cpanel_9, Additions.cpanel_10, Home.cpanel_5, Home.cpanel_6, Home.cpanel_7, Home.cpanel_8, Home.cpanel_9, Home.cpanel_10))
    concrete6.setMainWindow(navbar.instance)
    concrete6.reload( )
    navbar.instance.setWindowTitle('АСУ БСУ ЭТАЛОН-250412 (с) 2025, ЭТАЛОН-ПРО')
    navbar.instance.show( )
    # или 
    # Home.show()               
    
    dev.start(100)
    sec.start(100)
    io = QThread()
    dev._timer.moveToThread(io)
    sec._timer.moveToThread(io)
    io.finished.connect( dev._timer.stop )
    io.finished.connect( sec._timer.stop )
    io.start( )
    app.start( ctx = globals() )
    io.quit( )
    # dev.stop( )
    # sec.stop( )
    io.wait()
    
    concrete6.save( )

    if ns.simulator:
        logic.terminate( )
        slave.terminate( )
        pass
    
if __name__=='__main__':
    main( )
    