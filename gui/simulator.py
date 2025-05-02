import subprocess
from AnyQt.QtWidgets import QApplication,QSystemTrayIcon
from AnyQt.QtGui import QIcon

logic = subprocess.Popen(["python3", "src/master.py"])
slave = subprocess.Popen(["python3", "src/slave.py","--conf=slave_conf","--port=9005","--cli=2456"])

app = QApplication([])
sti = QSystemTrayIcon( app )
sti.show()
sti.activated.connect(app.quit)
app.exec( )

logic.terminate( )
slave.terminate( )