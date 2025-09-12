'''
Created on 17-Jan-2025

@author: kayma
'''
__updated__ = "2025-09-08"

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QAction, QVBoxLayout)
from PyQt5.uic import loadUi
import kTools
import functools

import os, pickle

class KQTTools():
    
    def __init__(self, parentWindow=None, iconPath='G:/resources/Icons/'):
        self.tls = kTools.KTools()
        self.CallingUI = parentWindow
        self.IconPath = iconPath
        self.defaultIcon = "document_empty.png"
        
    def getFormInput(self, inputDictForm, parent=None, title="KQt"):
        '''
        Give kvpair of items. and it will be placed in editable list as a form and will be provided for user input. 
        On close, you will get updated output
        inputDIctForm = {}
        '''        
        if not parent and self.CallingUI: parent = self.CallingUI
        if not parent:
            self.tls.error("No parent window to attach form window!") 
            return None
        outputDict = {}
        def dataFetcher(tbl, winObj):
            nonlocal outputDict        
            for row in range(tbl.rowCount()):
                key = tbl.item(row, 0).text()  # Property name (column 1)
                value = tbl.item(row, 1).text()  # User-edited value (column 2)
                outputDict[key] = value  
            winObj.close()
        winObj = QtWidgets.QDialog(parent)
        winObj.setWindowTitle(title)
        layout = QVBoxLayout()
        winObj.setLayout(layout)
        self.createPropEditor(winObj, inputDictForm, dataFetcher, winObj) 
        winObj.exec_()
        return outputDict
    
    def createUiDialog(self, uiFileName, parent=None, title="KQt", isModel=True):
        '''
            Creates a UI Dialog window with given UI file. and returns the dialogWin and uiObjCollection.
            Use "showUiDialog" fn for displaying the dialog window . After you do all your UI modificaitons.
        '''
        winObj = None
        uiObject = None
        if uiFileName and self.tls.isFileExists(uiFileName):
            if not parent: parent = self.CallingUI
            winObj = QtWidgets.QDialog(parent)
            uiObject = loadUi(uiFileName, winObj)
            uiObject.setModal(isModel)
            winObj.setWindowTitle(title)            
        else:
            self.tls.error(f"UI file [{uiFileName}] doesn't exist.")
        return winObj, uiObject
    
    def showUiDialog(self, winObj, isModel=True):
        '''
            Show the ui winobj. Mostly used with "createUiDialog" fn
        '''
        try:
            if isModel:            
                winObj.exec_()
            else:
                winObj.show()
        except Exception as e:
            print(self.tls.getLastErrorInfo())
            
    def createPropEditor(self, parent: QtWidgets.QFrame, data: dict, apply_callback, metaData=None):
        """
        Creates a QTableWidget inside the given parent frame with editable key-value pairs.
        
        - `parent`: QFrame where the table will be placed.
        - `data`: Dictionary containing key-value pairs.
        - `apply_callback`: Function that will be called when Apply button is clicked, with the table as an argument.
        """
        if parent.layout():
            while parent.layout().count():
                item = parent.layout().takeAt(0)            
                parent.layout().removeWidget(item.widget())
                del(item)
            
        # Create Table
        table = QtWidgets.QTableWidget(parent)
        table.setColumnCount(2)
        table.setRowCount(len(data))
        table.setHorizontalHeaderLabels(["Property", "Value"])
        
        # Set table properties
        table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        table.setSelectionMode(QtWidgets.QTableWidget.SingleSelection)
        table.verticalHeader().setVisible(False)
        #table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Interactive)  # Key column
        table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)  # Value column            
        
        # Populate Table
        for row, (key, value) in enumerate(data.items()):
            # Key Column (Non-editable)
            key_item = QtWidgets.QTableWidgetItem(str(key))
            key_item.setFlags(QtCore.Qt.ItemIsEnabled)  # Disable editing
            key_item.setBackground(QtGui.QColor("#F4F4F4"))  # Light Gray
            table.setItem(row, 0, key_item)
            
            # Value Column (Editable)
            value_item = QtWidgets.QTableWidgetItem(str(value))
            table.setItem(row, 1, value_item)
        
        # Create Apply Button
        apply_button = QtWidgets.QPushButton("Apply")
        apply_button.setFixedWidth(150)
        apply_button.clicked.connect(lambda: apply_callback(table, metaData))  # Pass table to callback

        parent.layout().addWidget(table)
        parent.layout().addWidget(apply_button)
        return table  # Return the table widget (if needed)          

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

    def showInputBox(self, Title='Information', Message='Information', DefaultValue=''):
        comments, ok = QtWidgets.QInputDialog.getText(self.CallingUI, str(Title), str(Message), QtWidgets.QLineEdit.Normal, DefaultValue)
        if ok:
            return comments
        else:
            return ''

    def showInformation(self, Title='Information', Message='Information'):
        ret = QtWidgets.QMessageBox.information(self.CallingUI, Title, Message, QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
        return ret
                    
    def showYesNoBox(self, Title='Information', Message='Information'):
        ret = QtWidgets.QMessageBox.question(self.CallingUI, Title, Message, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        return ret == QtWidgets.QMessageBox.Yes

    def getFile(self, Title='Select a file to open...', FileName='Select File', FileType='All Files (*);;Excel Files (*.xls);;Text Files (*.txt)'):
        fileName = QtWidgets.QFileDialog.getOpenFileName(self.CallingUI, str(Title), FileName, str(FileType))
        if(fileName[0] == ""): return ""
        return fileName[0]

    def getFileToSave(self, Title='Select a file to save...', FileName='Select File', FileType='All Files (*);;Excel Files (*.xls);;Text Files (*.txt)'):
        fileName = QtWidgets.QFileDialog.getSaveFileName(self.CallingUI, str(Title), FileName, str(FileType))
        if(fileName[0] == ""): return ""
        return fileName[0]
    
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


    def uiLayoutSave(self, layoutFile='layout.lyt', additionalObjToSaveStates=None, saveThisList=[]):
        dirname = os.path.dirname(layoutFile)
        if dirname!='' and not os.path.exists(dirname):
            os.makedirs(dirname)

        win={}
        win['state']=self.CallingUI.saveState()
        win['size']=self.CallingUI.size()
        win['pos']=self.CallingUI.pos()
        
        additionalObjs=[]
        if additionalObjToSaveStates:
            for each in additionalObjToSaveStates:
                splt={}
                splt['state']=each.saveState()
                additionalObjs.append(splt)

        data={}
        data['win']=win
        data['added']=additionalObjs
        data['mylist']=saveThisList
        data['ismax']=self.CallingUI.isMaximized()
        
        with open(layoutFile, 'wb') as handle:
            pickle.dump(data, handle)

    def uiLayoutRestore(self,layoutFile='layout.lyt',additionalObjToRestoreStates=None):
        if os.path.exists(layoutFile):
            with open(layoutFile, 'rb') as handle:
                data=pickle.load(handle)            
                
            win=data['win']               
            self.CallingUI.restoreState(win['state'])
            self.CallingUI.resize(win['size'])
            self.CallingUI.move(win['pos'])
            
            ismaxed = data['ismax'] if 'ismax' in data else 0
            if ismaxed:
                self.CallingUI.showMaximized()
            
            dcksObj = []
            sptsObj = []
            for each in self.CallingUI.children():
                if isinstance(each,QtWidgets.QDockWidget):
                    dcksObj.append(each)
                elif isinstance(each,QtWidgets.QSplitter):
                    sptsObj.append(each)
            
#             dcks=data['dcks']
#             for cnt, each in enumerate(range(len(dcksObj),0,-1)):
#                 dcksObj[cnt].resize(dcks[cnt]['size'])
#                 dcksObj[cnt].move(dcks[cnt]['pos'])

            added=data['added']
            if additionalObjToRestoreStates:
                for cnt, each in enumerate(range(0,len(additionalObjToRestoreStates))):
                    additionalObjToRestoreStates[cnt].restoreState(added[cnt]['state'])
        
            return data['mylist']
        return None

    def swapWidget(self, holderObj, oldObj, newObj, delete=1):
        '''
        Remove old widget from holder widget and new widget to the holder widget
        Holder widget should be layout. For different types need to extend.  
        '''
        holderObj.removeWidget(oldObj)
        if delete: oldObj.deleteLater()
        holderObj.addWidget(newObj, 0, 0)     

    def uiRefresh(self):
        for _ in range(3):  # ✅ Calls it multiple times to ensure proper refresh
            self.tls.qapp.processEvents()
            QtWidgets.QApplication.processEvents()    
                
    def clearLayout(self, parent):
        """Remove all widgets and layout from the parent before adding a new form."""
        
        for each in parent.children():
            each.deleteLater()
        
        if isinstance(parent, QtWidgets.QWidget):  # ✅ Ensure it's a QWidget before setting layout
            old_layout = parent.layout()
        elif isinstance(parent, QtWidgets.QLayout):  # ✅ Directly clear layout if parent is a layout
            old_layout = parent
        else:
            return  # Not a valid layout holder
    
        if old_layout:
            parent.setLayout(QtWidgets.QVBoxLayout())
            self.cleanChildren(parent)
            self.cleanChildren(old_layout)
            self.uiRefresh()
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item and (item.widget() or item.layout()):
                    if item.widget(): old_layout.removeWidget(item.widget())
                    if item.layout(): old_layout.removeItem(item.layout())
                    if item.widget(): item.widget().deleteLater()  # ✅ Remove widget
                    if item.layout(): item.layout().deleteLater()  # ✅ Remove widget
                
                parent.update()
                self.uiRefresh()                 
                QtCore.QTimer.singleShot(1, parent.update)
                QtCore.QTimer.singleShot(1, parent.repaint)                
                self.uiRefresh()         
            
            if old_layout:
                old_layout.invalidate()
                old_layout.disconnectNotify() 
                old_layout.deleteLater()  # ✅ Delete the layout
            
            self.cleanChildren(parent)
            self.cleanChildren(old_layout.parent())
            parent.setLayout(QtWidgets.QVBoxLayout())
                                            
            parent.update()
            self.uiRefresh()         
            
            if isinstance(parent, QtWidgets.QWidget):  # ✅ Only set layout if parent is a QWidget
                parent.setLayout(QtWidgets.QVBoxLayout())  # ✅ Set an empty layout to refresh UI
                parent.update()                
                            
            self.uiRefresh() 

    def cleanChildren(self, parent):
        if len(parent.children()):
            for each in parent.children():
                each.deleteLater()
                self.uiRefresh()    
                
    def listAdder(self, listWidgetObj, text):
        itm = QtWidgets.QListWidgetItem(text.strip())
        listWidgetObj.addItem(itm)         
                
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