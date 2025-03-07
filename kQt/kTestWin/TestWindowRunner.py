'''
Created on 23-Jan-2025

@author: kayma
'''
import os
import sys

from PyQt5 import QtCore, QtGui, Qsci, QtWidgets
from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QSettings, QSignalMapper, QSize, QTextStream, Qt,)
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow, QMdiArea, QMessageBox, QTextEdit, QWidget,)
from PyQt5.QtGui import (QIcon, QKeySequence, QFont, QColor)
from PyQt5.Qsci import (QsciScintilla, QsciLexerPython)
from PyQt5.Qt import QLineEdit
from PyQt5.uic import loadUi

import kTools
from kQt import kQtTools 

class WindowRunner(QtWidgets.QMainWindow):

    def __init__(self, parent = None):
        super().__init__()
        self.tls = kTools.GetKTools()
        self.qtls = kQtTools.KQTTools()
        
        self.tls.info('Preparing GUI...')
        QtWidgets.QMainWindow.__init__(self)        
        self.uiFile = sys.modules[__name__].__file__
        self.uiFile = self.uiFile.replace(".py", ".ui")
        self.uiFile = self.uiFile.replace("Runner", "")
        loadUi(self.uiFile, self)
        
        self.pushButton.clicked.connect(self.doB1Clicked)
        self.pushButton_2.clicked.connect(self.doB2Clicked)
        self.pushButton_3.clicked.connect(self.doB3Clicked)
        self.pushButton_4.clicked.connect(self.doB4Clicked)
        
    def doB1Clicked(self):
        print("b1")

    def doB2Clicked(self):
        print("b2")
        
    def doB3Clicked(self):
        print("b3")
        
    def doB4Clicked(self):
        print("b4")
        

if __name__ == "__main__":
    tls = kTools.GetKTools()
    app = QtWidgets.QApplication(sys.argv)
    appwin = WindowRunner()
    appwin.show()
    sys.exit(app.exec_())
