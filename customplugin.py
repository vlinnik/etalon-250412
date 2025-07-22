#!/usr/bin/python3
from AnyQt.QtGui import QIcon
from AnyQt.QtWidgets import QWidget
from AnyQt.QtDesigner import QPyDesignerCustomWidgetPlugin
from AnyQt.QtCore import pyqtProperty
from pysca.helpers import custom_widget_plugin,custom_widget

class FillerDosatorAddons(custom_widget(ui_file="ui/FillerDosatorAddons.ui")):
    def __init__(self, parent: QWidget = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
    def get_dm(self):
        return self._dm.value()
    
    def set_dm(self,value: int):
        self._dm.setValue(value)
        
    def get_pulse(self):
        return self._pt.value()
    
    def set_pulse(self,value: int):
        self._pt.setValue(value)
        
    def get_maxT(self):
        return self._tmax.value() 

    def set_maxT(self,value: int):
        self._tmax.setValue(value)
        
    pulse = pyqtProperty(int, fget=get_pulse, fset=set_pulse)
    dm = pyqtProperty(int, fget=get_dm, fset=set_dm)
    maxT = pyqtProperty(int, fget=get_maxT,fset=set_maxT)

__FillerDosatorAddonsPlugin = custom_widget_plugin(
    widget = FillerDosatorAddons,
    name="FillerDosatorAddons",
    include="customplugin",
    toolTip="Дополнительные настройки для дозаторов наполнителя",
    whatsThis="Настройки импульсной выгрузки, параметров Accelerator и т.д.",
    group="PYSCA",
    is_container=False
)