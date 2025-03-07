'''
Created on 17-Jan-2025

@author: kayma
'''
import kTools

class KQTTools():
    def __init__(self):
        self.tls = kTools.GetKTools()
        
    def swapWidget(self, holderObj, oldObj, newObj):
        '''
        Remove old widget from holder widget and new widget to the holder widget
        Holder widget should be layout. For different types need to extend.  
        '''
        holderObj.removeWidget(oldObj)
        oldObj.deleteLater()
        #holderObj.insertWidget(0,newObj)
        holderObj.addWidget(newObj, 0, 0)        
    

if __name__ == '__main__':
    tls = kTools.GetKTools(appName="kqttools")
    tls.info("Starting..")