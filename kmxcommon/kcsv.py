'''
Created on 28-Nov-2022

@author: kayma
'''
import csv23
import os
class MyCSV(object):
    '''
    classdocs
    '''


    def __init__(self, csvFile=None):
        '''
        Constructor
        '''
        self.setFile(csvFile)
    
    def setFile(self, csvFile=None):
        self.csvFile=csvFile
        if not os.path.exists(self.csvFile):
            f = open(self.csvFile,'w')
            f.close()
    
    def readRows(self):
        self._tmp = csv23.open_csv(self.csvFile, 'r')
        lst = []
        with csv23.open_csv(self.csvFile, 'r') as r:
            lst = list(r)
        return lst
    
    def updateRow(self, row=[]):
        lst = self.readRows()
        lst.append(row)
        self.writeRows(lst)
    
    def writeRows(self, rows=[]):
        if len(rows):
            with csv23.open_csv(self.csvFile, 'w') as w:
                w.writerows(rows)

if __name__ == '__main__':
    t = MyCSV('myfile.txt')
    #data = t.readRows()
    r = ['test6','test3','test4']
    t.updateRow(r)
    r = ['test4','test8','test4']
    t.updateRow(r)
    data = t.readRows()    
    print(data)
            