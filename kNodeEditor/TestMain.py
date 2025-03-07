'''
Created on 23-Jan-2025

@author: kayma
'''
import sys
from PyQt5 import QtCore, QtGui, Qsci, QtWidgets

import kTools
from kNodeEditor.kneLib import KNELib 
from kQt.kQtTools import KQTTools
from kQt.kTestWin import TestWindowRunner

from NodeGraphQt import NodeGraph
from SampleNodes import ndInputs
from SampleNodes import ndOutputs
from SampleNodes import ndWebCall 

class TestRunner():
    
    def __init__(self):
        self.win = TestWindowRunner.WindowRunner()
        self.tls = self.win.tls
        self.qtls = self.win.qtls
        self.nelib = KNELib()        

        #--------------

        nodeCollection = []
        nodeCollection.append(ndInputs.NDInputs)
        nodeCollection.append(ndOutputs.NDOutputs)
        nodeCollection.append(ndWebCall.NDWebCall)
        
        self.grp = NodeGraph()        
        self.grp.register_nodes(nodeCollection)        
        self.qtls.swapWidget(self.win.gridLayout, self.win.widget, self.grp.widget)
                
        self.nIp1 = self.grp.create_node('nodes.NDInputs')
        self.nIp2 = self.grp.create_node('nodes.NDInputs')
        self.nOp = self.grp.create_node('nodes.NDOutputs')
        self.nWc = self.grp.create_node('nodes.NDWebCall')
        
        self.grp.auto_layout_nodes()

        #--------------
        
        self.win.pushButton.clicked.connect(self.doB1Clicked)
        self.win.pushButton_2.clicked.connect(self.doB2Clicked)
        self.win.pushButton_3.clicked.connect(self.doB3Clicked)
        self.win.pushButton_4.clicked.connect(self.doB4Clicked)
        
    def doB1Clicked(self):
        n = self.nWc
        print("db1")        
        # self.nelib.nodeChangeLabelFontSize(n, 25)
        # #Node Locked not movable
        # #self.nWc.view.text_item.setEnabled(0)
        # n.view.text_item.set_editable(0)
        # n.view.text_item.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        # n.update()
        
    def doB2Clicked(self):
        print("db2")
        self.nIp2.add_output('out Bzxx', multi_output=True)
        
        #Node Locked not movable
        
    def doB3Clicked(self):
        print("db3")
        #Node Locked not movable
        
    def doB4Clicked(self):
        print("db4")
        #Node Locked not movable

if __name__ == "__main__":
    tls = kTools.GetKTools("TestMain")
    app = QtWidgets.QApplication(sys.argv)
    tr = TestRunner()
    tr.win.show()
    sys.exit(app.exec_())    