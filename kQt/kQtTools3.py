'''
Created on 17-Jan-2025

@author: kayma
'''
from PyQt5 import QtCore, QtGui, Qsci, QtWidgets
from PyQt5.Qsci import (QsciScintilla, QsciLexerPython)
from PyQt5.Qt import QLineEdit
from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QSettings, QSignalMapper, QSize, QTextStream, Qt,)
from PyQt5.QtGui import (QIcon, QKeySequence, QFont, QColor)
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow, QMdiArea, QMessageBox, QTextEdit, QWidget, QSpinBox)
import fatcow_rc
import kTools
import functools
from PyQt5.Qt import QPlainTextEdit
class KQTTools():
    def __init__(self, parentWindow=None, iconPath='D:/Akelpads/AkelFiles/Icons/'):
        self.tls = kTools.GetKTools()

        self.CallingUI = parentWindow
        self.IconPath = iconPath
        self.defaultIcon = "document_empty.png"
        
    def swapWidget(self, holderObj, oldObj, newObj):
        '''
        Remove old widget from holder widget and new widget to the holder widget
        Holder widget should be layout. For different types need to extend.  
        '''
        holderObj.removeWidget(oldObj)
        oldObj.deleteLater()
        #holderObj.insertWidget(0,newObj)
        holderObj.addWidget(newObj, 0, 0)       
        
    
    def createSimpleLabelEditor(self, parent, labelStr, valueStr, dataStr="", objName="obj"):
        holderWidget = QtWidgets.QWidget(parent)
        holderWidget.setObjectName("ui"+objName)
        hLayout = QtWidgets.QHBoxLayout(holderWidget)
        lbl  = QtWidgets.QLabel(labelStr, holderWidget)
        edtr  = QtWidgets.QLineEdit(holderWidget)
        edtr.setText(valueStr)        
        hLayout.addWidget(lbl)
        hLayout.addWidget(edtr)
        hLayout.setContentsMargins(0, 0, 0, 0)
        hLayout.setSpacing(6)
        holderWidget.setFixedHeight(35)
        holderWidget.setLayout(hLayout)
        return holderWidget
    
    def createPropForm(self, parent, dictObj, applyFn):
        def _tempApplyFn(): applyFn(allWidgets)
        allWidgets = {}
        
        self.clearLayout(parent)
        
        vLayout = QtWidgets.QVBoxLayout(parent)
        vLayout.setContentsMargins(0, 0, 0, 0)  # ✅ Remove unnecessary margins
        vLayout.setSpacing(6)  # ✅ Set uniform spacing        
        for each in dictObj:
            name = each
            value = dictObj[name]            
            wdgt = self.createSimpleLabelEditor(parent, name, value, name)
            allWidgets[name] = wdgt
            wdgt.show()
            print(f'Creating {wdgt}')
            vLayout.addWidget(wdgt)
        vLayout.addStretch(1)

        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.addStretch()
        aplyBtn = QtWidgets.QPushButton("Apply")
        aplyBtn.setFixedWidth(150)
        aplyBtn.clicked.connect(_tempApplyFn)
        print(f'Applying btn {aplyBtn}')
        btnLayout.addWidget(aplyBtn)
        vLayout.addLayout(btnLayout)        
      
        self.tls.qapp.processEvents()  # Ensure UI refresh
        QApplication.processEvents()        
        
        parent.setLayout(vLayout)
        parent.update()
        parent.repaint()
        self.tls.qapp.processEvents()  # Ensure UI refresh
        QApplication.processEvents()             
        parent.setLayout(parent.layout())  # ✅ Re-assigns layout to trigger recalculation
        parent.layout().invalidate()  # ✅ Invalidates layout, forcing a relayout
        parent.layout().update()  # ✅ Requests layout update
        parent.layout().activate()  # ✅ Ensures layout updates immediately
        self.tls.qapp.processEvents()  # Ensure UI refresh
        QApplication.processEvents()     
        print(f'Vlayouting activated {vLayout}')
        QtCore.QTimer.singleShot(0, parent.update)  # ✅ Ensures update happens in the next event loop
        QtCore.QTimer.singleShot(0, parent.repaint)  # ✅ Forces repaint in next frame        
        
        vLayout.activate()
        parent.repaint()
        self.tls.qapp.processEvents()  # Ensure UI refresh
        QApplication.processEvents()        
        for _ in range(3):  # ✅ Calls it multiple times to ensure proper refresh
            QtWidgets.QApplication.processEvents()
    
        return allWidgets
            
    def clearLayout(self, parent):
        """Remove all widgets and layout from the parent before adding a new form."""
        if isinstance(parent, QtWidgets.QWidget):  # ✅ Ensure it's a QWidget before setting layout
            old_layout = parent.layout()
        elif isinstance(parent, QtWidgets.QLayout):  # ✅ Directly clear layout if parent is a layout
            old_layout = parent
        else:
            return  # Not a valid layout holder
    
        if old_layout:
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()  # ✅ Remove widget
                elif item.layout():
                    self.clearLayout(item.layout())  # ✅ Recursively clear sub-layouts
                parent.update()
                self.tls.qapp.processEvents()  # Ensure UI refresh
                QApplication.processEvents()         
                                
            old_layout.deleteLater()  # ✅ Delete the layout
            self.tls.qapp.processEvents()  # Ensure UI refresh
            QApplication.processEvents()               
            parent.update()
            
            if isinstance(parent, QtWidgets.QWidget):  # ✅ Only set layout if parent is a QWidget
                parent.setLayout(QtWidgets.QVBoxLayout())  # ✅ Set an empty layout to refresh UI
                parent.update()                
                            
            self.tls.qapp.processEvents()  # Ensure UI refresh
            QApplication.processEvents()  
            parent.update()

    def createVerticalWindow(self, parent, name='SystemDialog', buttons=['Button1','Button2','|','Button3']):
        mainWin = QtWidgets.QDialog(parent)        
        layout = QtWidgets.QVBoxLayout(mainWin)        
        btnList = []
        if(buttons and len(buttons)>0):            
            for eachButton in buttons:
                if(eachButton=='|'):
                    layout.addStretch()
                else:
                    btn = QtWidgets.QPushButton(mainWin)
                    btn.setText(eachButton)
                    layout.addWidget(btn)                
                    btnList.append(btn)                
        mainWin.setLayout(layout)    
        mainWin.setWindowTitle(name)     
        return (mainWin,layout,btnList) 
    
    # def createPropWindow(self, parent, name, dictObj):
    #     mainWin = QtWidgets.QDialog(parent)              
    #     widgets = {}
    #     form = QtWidgets.QFormLayout(mainWin)
    #     for key in dictObj.keys():
    #         value = dictObj[key]            
    #         widgets[key] = editor = QLineEdit()
    #         editor.setText(str(value))
    #         #editor.setFrameStyle(3)
    #         #editor.setFrameStyle(QtWidgets.QFrame.WinPanel | QtWidgets.QFrame.Sunken )
    #         editor.setFixedHeight(25)
    #         editor.setStyleSheet("""
    #             QLineEdit {
    #                 border: 2px solid gray;
    #                 border-style: inset;
    #                 background: white;
    #                 padding: 3px;
    #                 border-radius: 2px;
    #             }
    #         """)            
    #
    #         form.addRow(key, editor)
    #     mainWin.setLayout(form)    
    #     mainWin.setWindowTitle(name)
    #     mainWin.resize(220, 100)
    #     #{'item1': {'editor': <PyQt5.QtWidgets.QPlainTextEdit object at 0x0000016D255039A0>}, 'item2': {'editor': <PyQt5.QtWidgets.QPlainTextEdit object at 0x0000016D25503640>}}       
    #     print(widgets)     
    #     return (mainWin,widgets)    

    # def createPropForm(self, parent, dictObj, applyFn): 
    #     self.old_layout = parent.layout()
    #     if self.old_layout:
    #         self.createPropFormCore(parent, dictObj, applyFn)
    #         QApplication.processEvents()
    #         self.tls.qapp.processEvents() 
    #     self.createPropFormCore(parent, dictObj, applyFn)    
        
    def createPropFormx(self, parent, dictObj, applyFn):  
        def _tempApplyFn(): applyFn(widgets)
        
        def cleanOldItems(parent):        
            old_layout = parent.layout()
            if old_layout:
                while old_layout.count():
                    item = old_layout.takeAt(0)
                    if item.widget():
                        item.widget().setParent(None)
                        if item and item.widget(): item.widget().deleteLater()
                    elif item.layout():
                        old_layout.removeItem(item)
                    old_layout.removeRow(0)
                    QApplication.processEvents()
                    self.tls.qapp.processEvents()
    
                old_layout.deleteLater()
                del old_layout
                QApplication.processEvents()
                self.tls.qapp.processEvents()  # 🔥 Ensure UI update before setting a new layout   
    
            for each in parent.findChildren(QtWidgets.QWidget):  
                each.setParent(None)  # ⬅️ REMOVE from parent  
                each.deleteLater()     # ⬅️ DELETE safely  
                QApplication.processEvents()
    
            # for each in parent.children():
            #     each.deleteLater()
            #     del each 
            #     self.tls.qapp.processEvents()  # 🔥 Ensure UI update before setting a new layout
            #     QApplication.processEvents() 
                        
        def createNewItems(parent):
            widgets = {}
            cform = QtWidgets.QFormLayout(parent)
            QApplication.processEvents()        
            self.tls.qapp.processEvents() 
            for key in dictObj.keys():
                value = dictObj[key]            
                widgets[key] = editor = QLineEdit(parent)
                editor.setText(str(value))
                editor.setFixedHeight(25)
                editor.setStyleSheet("""
                    QLineEdit {
                        border: 2px solid gray;
                        border-style: inset;
                        background: white;
                        padding: 3px;
                        border-radius: 2px;
                    }
                """)                            
                cform.addRow(key, editor)
                editor.show()  
                QApplication.processEvents()        
                self.tls.qapp.processEvents()                       
            widgets['gen'] = btn = QtWidgets.QPushButton("Apply")
            btn.setFixedWidth(150)
            btn.clicked.connect(_tempApplyFn)
            cform.addWidget(btn)
            parent.setLayout(cform)
            return widgets
                
        cleanOldItems(parent)

        self.tls.qapp.processEvents()  # Ensure UI refresh
        QApplication.processEvents() 
        
        createNewItems(parent)
        
        self.tls.qapp.processEvents()  # Ensure UI refresh
        QApplication.processEvents() 
        
        if len(parent.children()) <= 1:
            createNewItems(parent)  
                  
        self.tls.qapp.processEvents()  # Ensure UI refresh
        QApplication.processEvents() 
  
    def getIconString(self, iconName='document_empty.ico', alternateIcon='document_empty.ico'):
        """
        Returns the path of ICONNAME found on 'iconPath'. Else
        """
        
        if(iconName):
            return self.IconPath + iconName
        else:
            return self.IconPath + alternateIcon
        
    def getIcon(self, iconName, alternate=''):

            iconPath = self.getIconString(iconName, alternate)
            if not self.tls.isFileExists(iconPath):  
                iconPath = iconPath.replace('.png','.ico')
            if not self.tls.isFileExists(iconPath):
                self.tls.warn(f"Icon not found {iconPath}")
                
            icon = QtGui.QIcon(iconPath)
                 
            return icon

    def setIconForItem(self, item, iconName, isWindow=0, Col=0, comboBoxIndex=0, OptionalIcon='', thisImage='', clear=0):
        itemType = type(item)
        # print itemType
        icon = QtGui.QIcon()
        pxmap = None

        if thisImage:
                if os.path.exists(thisImage):
                    icon.addPixmap(QtGui.QPixmap(thisImage), QtGui.QIcon.Normal, QtGui.QIcon.On)
                    pxmap = QtGui.QPixmap(thisImage)
        else:
            icon = self.getIcon(iconName, OptionalIcon)

        if clear:
                icon = QtGui.QIcon()
                pxmap = QtGui.QPixmap()

        if isWindow:
            item.setWindowIcon(icon)

        if itemType == type(QtWidgets.QPushButton()):
            item.setIcon(icon)

        if itemType == type(QtWidgets.QToolButton()):
            item.setIcon(icon)

        if itemType == type(QtWidgets.QWidget()):
            tabWidget = item.parentWidget().parentWidget()
            if type(tabWidget) == type(QtWidgets.QTabWidget()):
                index = tabWidget.indexOf(item)
                tabWidget.setTabIcon(index, icon)

        if itemType == type(QtWidgets.QTreeWidgetItem()):
            item.setIcon(Col, icon)

        if itemType == type(QtWidgets.QTableWidgetItem()):
            item.setIcon(icon)

        if itemType == type(QtWidgets.QListWidgetItem()):
            item.setIcon(icon)

        if itemType == type(QtWidgets.QAction(None)):
            item.setIcon(icon)

        if itemType == type(QtWidgets.QLabel()):
            if (pxmap is not None):
                item.setPixmap(pxmap)

        if itemType == type(QtWidgets.QComboBox()):
            item.setItemIcon (comboBoxIndex, icon)    


    def connectToRightClick(self, Widget, FunctionToInvoke):
        self.enableRightClick(Widget)
        Widget.customContextMenuRequested.connect(FunctionToInvoke)

    def enableRightClick(self, Widget):
        Widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

    def createAction(self, name, parent, description=None, icon=None, checkable=False, checked=False, fn=None):
        if(icon):
            itm = QAction(self.getIcon(icon), name, parent)
        else:
            itm = QAction(name, parent)
             
        itm.setStatusTip(description)
        itm.triggered.connect(fn)
        itm.setCheckable(checkable)
        itm.setChecked(checked)
        return itm  


    def popUpMenu(self, menuRequestingtObject, PopupPoint, menuListString, funcToInvoke, additionalArguments='', iconList = []):

        """
        self.CallingUI - where the menuRequestingtObject is placed, usaully self
        menuRequestingtObject - Into which menu will be generated
        PopupPoint - QPoint where menu should popout
        menuListString - Array of menu items
        funcToInvoke - Function to be invoked on menu item clicked
        additionalArguments - argument to that function

            Inside funcToInvoke() you will receive a tuple with three items
            1 - Menu Label
            2 - Menu Label Index
            3 - added_arg

            eg:
            myutils().popUpMenu(self,self.textEdit,PopupPoint,["KUMAR","TEST"],self.funs,["myarg1","myarg2"])

            def funs(self,t)
                    print "Label Clicked is: " + str(t[0])
                    print "Label Index is: " + str(t[1])
                    print "Added Argument: " + str(t[2])

        """
        if menuListString == []:
            return 0;
        Rmnu = QtWidgets.QMenu(self.CallingUI)
        lst = []
        for i, itm in enumerate(menuListString):
            newmenuitem = QtWidgets.QAction(itm, self.CallingUI)
            lst.append(newmenuitem)
            if len(itm)>1 and itm[0]=='|':
                itm = itm[1:len(itm)]
                newmenuitem.setEnabled(False)
                newmenuitem.setText(itm)
            if itm != '':
                if len(iconList)>1 and len(iconList)>i:
                    if iconList[i]!=None:
                        icon = QtGui.QIcon()
                        icon.addPixmap(QtGui.QPixmap(iconList[i]), QtGui.QIcon.Normal, QtGui.QIcon.On)
                        newmenuitem.setIcon(icon)

            arg = [itm,i,newmenuitem,additionalArguments]
            newmenuitem.triggered.connect(functools.partial(funcToInvoke, arg))
            newmenuitem.setData(PopupPoint)
            if itm=='':
                Rmnu.addSeparator()
            else:
                Rmnu.addAction(newmenuitem)

        PopupPoint.setY(PopupPoint.y())
        PopupPoint.setX(PopupPoint.x())
        Rmnu.exec_(menuRequestingtObject.mapToGlobal(PopupPoint))
        del(Rmnu)
        
    
    def popUpMenuAdv(self, MenuList, MenuRequestingObject, MenuStartPoint, FunctionToBeInvoked, AdditionalArgument=[], popupOffset=QtCore.QPoint(0,0)):

        """

        popup a menu for a given object and point

        menu = [{'m1':'iconPath'},{'m2':''},[{'m3':''},{'m31':''},[{'m32':''},{'m321':''},{'m322':''}],{'m33':''}],{'m4':''},{'m5':''},[{'m6':''},{'m61':''},{'m62':''}],'m7']
        or
        menu = ['m1','m2',['m3','m31',['m32','m321','m322'],'m33'],'m4','m5',['m6','m61','m62'],'m7']

        m1
        m2
        m3-->m31
        m4   m32-->m321
        m5   m33   m322
        m6
        m7

        eg:

        self.uic = QtUiSupport.uiComman(self)
        self.uif = QtUiSupport.visualFormat('/splIcons')

        ic1 = self.uif.getIconForLabel('photo-album.png')
        ic2 = self.uif.getIconForLabel('shortcut.png')

        menu = [{'m1':ic1},{'m2':ic2},[{'m3':ic3},{'m31':ic4},[{'m32':ic5},{'m321':ic6},{'m322':ic7}],{'m33':ic8}],{'m4':ic9},{'m5':ic0},[{'m6':ic11},{'m61':ic12},{'m62':ic13}],{'m7':ic14}]

        self.uic.popUpMenuAdv(menu,self.pushButton,qpoint,self.myOptFun,'addedArgument')

        Your Function will be invoked and following values will be passed through the single argument.

            RETURN VALUE (Single Tuple):
            ('MENULABEL', 1, 2, 0, 'addedArgument', <PyQt4.QtGui.QAction object at 0x045B9030>)

            MENULABEL = Menu Label
            1 = Menu Level No (0 - Main Menu, 1 - First Level Submenu, 2 - Second Level Submenu....)
            2 = Parent ID - Index of the parent item, In parent's level
            0 = ItemIndex - Index of item, In its level
            addedArgument = Addition Arguments which was added on menu creation.
            QACTION - Action is the item sending the signal.

        See UISUPPORT.menuCreator function for additional info!

        """

        if type(MenuStartPoint)==type(QtCore.QPoint()):
            PopupPoint = MenuStartPoint
        else:
            PopupPoint = QtCore.QPoint(-3,-5)

        Rmnu = self.menuCreator(MenuList, self.CallingUI, AdditionalArgument, FunctionToBeInvoked)
        PopupPoint.setY(PopupPoint.y() + popupOffset.y())
        PopupPoint.setX(PopupPoint.x() + popupOffset.x())
        Rmnu.exec_(MenuRequestingObject.mapToGlobal(PopupPoint))
        del(Rmnu)

    def menuCreator(self, listOfItem, CallingUI, AdditionalArgument, FunctionToInvoke, ParentID=0, Level=0):

        '''
        Do you want menu?
        Give me listOfMenuItem and function to be invoked, and additional args that are to be passed to that functoin... .

        Results a menu which can be used
            * for popup as context menu
            * ui main menu
            * toolbutton popup menu

        Your Function will be invoked and following values will be passed through the single argument.

            RETURN VALUE (Single Tuple):
            ('MENULABEL', 1, 2, 0, 'addedArgument', <PyQt4.QtGui.QAction object at 0x045B9030>)

            MENULABEL = Menu Label
            1 = Menu Level No (0 - Main Menu, 1 - First Level Submenu, 2 - Second Level Submenu....)
            2 = Parent ID - Index of the parent item, In parent's level
            0 = ItemIndex - Index of item, In its level
            addedArgument = Addition Arguments which was added on menu creation.
            QACTION - Action is the item sending the signal.


        Eg:

        ic1 = 'D:\DD\DD\DOWNICON.png'
        ic2 = 'D:\DD\DD\DOWNICON.png'
        .
        .
        .

        menu = [{'mx1':ic1},{'mxx2':ic2},{'kzzzz':ic4},[{'mcccccc3z':ic3},{'mzxczxczcx31':ic4},[{'xzczcm32':ic5},{'sdfsdfm321':ic6},{'m3ffffs22':ic7}],{'msdfsdf33':ic8}],{'mxcvxcv4':ic9},{'ewrwerwerm5':ic0},[{'mrrrwe6':ic11},{'m61':ic12},{'m62':ic13}],{'m7':ic14}]
        mnu = UISUPPORT.menuCreator(menu, self, 'ADDEDARG', self.mySplMenuFunction)

        self.toolButton.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
        self.toolButton.setMenu(mnu)



        See UISUPPORT.popUpMenuAdv function for additional info!

        '''

        Rmnu =  QtWidgets.QMenu(self.CallingUI)

        Rmnu.setTearOffEnabled(False)

        for cnt, eachItem in enumerate(listOfItem):
            if type(eachItem)==type([]):
                Menu = self.menuCreator(eachItem[1:], self.CallingUI, AdditionalArgument, FunctionToInvoke, cnt, Level+1)
                if type(eachItem[0])==type({}):
                    Menu.setTitle(eachItem[0].keys()[0])
                else:
                    Menu.setTitle(str(eachItem[0]))
                Rmnu.addMenu(Menu)
            else:
                itemDict = eachItem

                if type(itemDict)==type({}):
                    Label = itemDict.keys()[0]
                    IconPath = itemDict.values()[0]
                else:
                    Label = str(itemDict)
                    IconPath = ''

                newmenuitem = QtWidgets.QAction(Label, self.CallingUI)
                if len(eachItem)>1 and Label[0]=='|':
                    Label = Label[1:len(Label)]
                    newmenuitem.setEnabled(False)
                    newmenuitem.setText(Label)

                if IconPath:
                    icon = QtGui.QIcon()
                    icon.addPixmap(QtGui.QPixmap(IconPath), QtGui.QIcon.Normal, QtGui.QIcon.On)
                    newmenuitem.setIcon(icon)

                newmenuitem.triggered.connect(lambda passarg=(Label,Level,ParentID,cnt,AdditionalArgument,newmenuitem): FunctionToInvoke(passarg))

                if Label=='':
                    Rmnu.addSeparator()

                else:
                    Rmnu.addAction(newmenuitem)
        return Rmnu    

if __name__ == '__main__':
    tls = kTools.GetKTools(appName="kqttools")
    tls.info("Starting..")