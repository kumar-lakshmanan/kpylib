
'''
Created on Sep 6, 2014

@author: Mukundan
'''
from importlib import import_module
from datetime import timedelta
#from notify_run import Notify
from decimal import Decimal
from pytz import timezone
import logging as log
import subprocess
import traceback
import datetime
import logging
import getpass
import inspect
import locale
import socket
import pprint
import pickle
import random
import shutil
import atexit
import codecs
import time
import uuid
import math
import sys
import os
import re

#our libs
from kmxcommon.kconfigs import cfg_default

#sys.setrecursionlimit(60)
numbers = re.compile('\d+')
codecs.register_error("strict", codecs.ignore_errors)
# Include below point in your main and errors will be displayed.
#sys.excepthook = kmxTools.errorHandler

def getGlobalTools(handleError=1,runStartUps=1,debug=0,configOverride=None):
    '''
    All module start should use this.
    
    config:
        check base cfg first

    main.py:
    
    from kmxcommon import xtools
    from kmxcommon.kconfigs import cfg_local
    tls = xtools.getGlobalTools(debug=1, configOverride=cfg_local)   

    or 
    
    from kmxcommon import xtools
    os.environ['KMXPYCONFIG'] = "safe.cfg_local"
    os.environ['KMXPYCONFIG'] = "kmxcommon.kconfigs.cfg_local"
    tls = xtools.getGlobalTools(debug=1)   

    or (prod)
    
    from kmxcommon import xtools    
    tls = xtools.getGlobalTools()   
    
    --------------------
    
    others.py:
    
    from kmxcommon import xtools
    tls = xtools.getGlobalTools()
        
    '''
    
    obj = inspect.currentframe()       
    if hasattr(obj, 'f_globals'):
        if 'tls' in obj.f_globals:
            return obj.f_globals['tls']  
        else:
            tls = Tools(None)
            if configOverride:
                tls = Tools(configOverride)
            elif 'KMXPYCONFIG' in os.environ:
                moduleName = os.environ['KMXPYCONFIG']
                configModule = import_module(moduleName)
                tls = Tools(configModule)
            else:
                tls = Tools()
            if handleError: sys.excepthook = errorHandler
            if runStartUps: tls.onStart()
            if debug: tls.setDebugging()
            if tls: tls.info('Global Tools Ready!') 
            globals()['tls'] = tls
            return tls

def errorHandler(etype, value, tb):
    """
    Global function to catch unhandled exceptions.
    @param etype exception type
    @param value exception value
    @param tb traceback object
    """
    errorInfo = []
    try:

        now_utc = datetime.datetime.now(timezone('UTC'))
        now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
        currdatetime = now_asia.strftime('%Y-%m-%d %H:%M:%S')        
        
        mainErrorInfo = traceback.format_exc()
        fullErrorInfos = traceback.format_exception(etype, value, tb)
        errorInfo.append('-------------\n')
        errorInfo.append('Error Occurred!\nTime: ' + currdatetime + '\n')
        errorInfo.append('-------------\n')
        errorInfo.append(str(mainErrorInfo))
        errorInfo.append(f'{etype}, {value}, {tb}\n')
        errorInfo.append('-------------\n')
        for each in fullErrorInfos:
            errorInfo.append(each)
        errorInfo.append('-------------')
        info = ''.join(errorInfo)           
        print(info)
    except:
        print('Traceback formatter failed! Custom formatted exception info')
        print('--------')
        print('')
        info = traceback.format_exception(etype, value, tb)        
        disp = ''
        for eachLine in info:
            disp += eachLine
        print(disp)
        info = disp
        print('--------')
    try:
        f = open('error.log', "w")
        f.write(str(info))
        f.close()
    except IOError:
        pass

def isWindows(): return os.name == 'nt'

def isLinux(): return os.name == 'posix'

def exiting():
    print('-----Script Ends!------')

class Tools(object):
    '''
    classdocs
    '''

    def __init__(self, configModule=cfg_default):
        '''
        Constructor
        '''
        if not configModule: return None
                
        #Config can be from default config module or overriden config
        self.cfg = configModule.cfg

        self.dateTimeStampFmt = self.cfg.dateTimeStampFmt
        self.logName = self.cfg.logName
        self.logFormat = self.cfg.logFormat
        self.logLevel = self.cfg.logLevel
        self.logToStream = self.cfg.logToStream
        self.logToFile = self.cfg.logToFile
        self.logFile = self.cfg.logFile
        self.showSimpleLog = self.cfg.showSimpleLog
        self.ignoreSysLogger = self.cfg.ignoreSysLogger
        
        self.dateFmt = self.cfg.dateFmt
        self.timeFmt = self.cfg.timeFmt
        
        self.tags = []
        self.globalVar = {}
        self.globalSwitch = {}
        
        self.localCachePath = self.cfg.cacheFolder        
                
        self.randomSeed = 50
        self.rand = random.Random(self.randomSeed)
        
        atexit._clear()
        atexit.register(self.onExit)

        self.envOverride()
        self.setupLogger()
        self.readyCachePath()

    def envOverride(self):
        pass

    def onStart(self):
        print('---Program Starts---')
                
    def onExit(self):
        print('---Program Quits---')

    def isEnvExist(self, var):
        return var in os.environ
    
    def getEnv(self, var, default):
        if self.isEnvExist(var):
            return str(os.environ[var])
        else:
            return str(default)
    
    def setEnv(self, var, value):
        os.environ[var] = str(value)
        
    def unicodeCompats(self, input):
        supportFmt = locale.getdefaultlocale()[1]
        enc = str(input).encode(supportFmt, errors='ignore')
        return str(enc, supportFmt)
    
    def unicodeCleaner(self, input):
        if type(input) == type(''):
            return self.unicodeCompats(input)
        if type(input) == type([]):
            newlst = []
            for each in input:
                newlst.append(self.unicodeCleaner(each))
            return newlst
        if type(input) == type({}):
            newDict = {}
            for eachKey in input.keys():
                newDict[eachKey] = self.unicodeCleaner(input[eachKey])
            return newDict
        return input

    def print_table_list(self, table):
        '''
        ip table should be list of list
        '''
        longest_cols = [
            (max([len(str(row[i])) for row in table]) + 3)
            for i in range(len(table[0]))
        ]
        row_format = "".join(["{:>" + str(longest_col) + "}" for longest_col in longest_cols])
        for row in table:
            print(row_format.format(*row))   
    
    
    def print_table_dict(self, table):
        '''
        ip table should be simple dict    
        '''
        
        lst = []
        for each in table:
            lst.append([each, table[each]])
        
        self.print_table_list(lst)


    def showAsTable(self, dataDict, simple=0, write2File='', forexcel=0):
        '''
        [
            {'date': '20220706', 'time': '0023', 'status': 'failed', 'symbol': 'BUSD', 'entrySince': 45, 'rank': 6, 'informedOn': '20220705', 'eventOn': '20220707', 'title2': 'Koinbazar Listing', 'category': 'Exchange', 'netNewsCnt': 0, 'netNewsSrcCnt': 0, 'netGoodCnt': 0, 'netBadCnt': 0, 'netNormalCnt': 0, 'news7d': 20, 'news2d': 4, 'diff24h': 0.1101211332465702, 'diff7d': 0.14019627478469424, 'tradeVolPercent': 9.21, 'fullDilutedMarketCapPercent': -0.2},
            {'date': '20220706', 'time': '0023', 'status': 'failed', 'symbol': 'BUSD', 'entrySince': 45, 'rank': 6, 'informedOn': '20220705', 'eventOn': '20220707', 'title2': 'Koinbazar Listing', 'category': 'Exchange', 'netNewsCnt': 0, 'netNewsSrcCnt': 0, 'netGoodCnt': 0, 'netBadCnt': 0, 'netNormalCnt': 0, 'news7d': 20, 'news2d': 4, 'diff24h': 0.1101211332465702, 'diff7d': 0.14019627478469424, 'tradeVolPercent': 9.21, 'fullDilutedMarketCapPercent': -0.2}
        ]
        '''
        if self.isLocalDev(): import tabulate
        if len(dataDict)>0:
            headerRow = dataDict[0].keys()
            rows =  [x.values() for x in dataDict]
                        
            if simple:
                for each in dataDict:
                    print (each)
            else:
                if write2File:
                    data = tabulate.tabulate(rows, headerRow, showindex="always", tablefmt="github", numalign="right", floatfmt=".2f")
                    self.writeFileContent(write2File, data)                        
                else:
                    print(tabulate.tabulate(rows, headerRow, showindex="always", tablefmt="github", numalign="right", floatfmt=".2f"))  
                    
            if forexcel:
                print('-----')
                print(tabulate.tabulate(rows, headerRow, tablefmt='tsv'))                       
    
    def lowHighPercentage(self, lowVal, highVal):
        if lowVal == 0 or highVal == 0:
            return 0
        else:
            return ((highVal - lowVal)/abs(lowVal)) * 100

    def sortListOfDict(self, inpListOfDict, keyToSort, reverse=False): 
        outListOfDict = sorted(inpListOfDict, key=lambda d: d[keyToSort], reverse=reverse)
        return outListOfDict

    def getCalenderMonthDates(self, year, month):
        wdays = ('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')    
        ymonths = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')        
        lst = []
        cnow = datetime.date(int(year), int(month), 1)
        while True:
            tmp = (cnow.day, cnow.weekday(), wdays[cnow.weekday()] , cnow.month, ymonths[cnow.month], cnow.year)
            lst.append(tmp)
            cnow += datetime.timedelta(days=1)
            if cnow.month != month:
                break      
        return lst

    def getDateSplitNo(self, input):
        '''
        For the input date of format '%Y%m%d'
        Will give
        YEAR , MONTH , DAY
        '''
        year = input[0:4]
        month = input[4:6]
        day = input[6:8]
        
        return (int(year),int(month),int(day))
        
    def getCalenderDatesBetween(self, startDate_, endDate_=None):
        '''
        foramt 20221217
        '''
        endDate_ = endDate_ if endDate_ else self.getDateTime('%Y%m%d')
        wdays = ('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')    
        ymonths = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
        
        startYear,startMonth,startDate = self.getDateSplitNo(startDate_)
        endYear,endMonth,endDate = self.getDateSplitNo(endDate_)
             
        lst = []
        strt = datetime.date(int(startYear), int(startMonth), int(startDate))
        end  = datetime.date(int(endYear), int(endMonth), int(endDate))
        cnow = strt
        while True:
            tmp = (cnow.day, cnow.weekday(), wdays[cnow.weekday()] , cnow.month, ymonths[cnow.month], cnow.year)
            lst.append(tmp)
            cnow += datetime.timedelta(days=1)
            if cnow.year == end.year and cnow.month == end.month and cnow.day == end.day:
                break      
        return lst    
        
    def getGlobalVar(self, varName):
        if self.isGlobalVarExist(varName):
            return self.globalVar[varName]
    
    def setGlobalVar(self, varName, value):
        self.globalVar[varName]= value
    
    def isGlobalVarExist(self, varName):
        return varName in self.globalVar
    
    def getGlobalSwitch(self, varName, default=0):
        if self.isGlobalVarSwitch(varName):
            return self.globalSwitch[varName]
        else:
            return default
    
    def setGlobalSwitch(self, varName, value):
        self.info(f'Global switch {varName} triggered to {value}')
        self.globalSwitch[varName]= value
    
    def isGlobalVarSwitch(self, varName):
        return varName in self.globalSwitch    

    def helloWorld(self):
        self.info('Hello World', skipLevel=4)
        
    def setDebugging(self):
        self.logToStream = 1
        self.logLevel = 10
        self.setupLogger(update=1)
    
    def isLocalDev(self):
        if isWindows():
            if 'COMPUTERNAME' in os.environ:
                if os.environ['COMPUTERNAME'].upper() == self.cfg.desktopName.upper():
                    return 1
        return 0    
    
    def isItMorning(self):
        return self.getDateTime('%p').lower() == 'am'

    def readyCachePath(self):
        if self.isLocalDev(): self.pathReady(self.localCachePath)

    def pathClean(self, inputFile):
        inputFile = os.path.normpath(inputFile)
        inputFile = os.path.abspath(inputFile)
        return inputFile

    def pathParts(self, inputFile):
        inputFile = self.pathClean(inputFile)
        fileNameWithExt = os.path.basename(inputFile)
        fileName, Ext = os.path.splitext(fileNameWithExt)
        filePath = os.path.dirname(inputFile)
        Ext = Ext[1:] if Ext.startswith('.') else Ext
        return filePath, fileName, Ext

    def isCacheAvailable(self, fileName, dated=0):
        if dated: fileName = self._cacheName(fileName)
        fileName = self._applyLocalCachePath(fileName)
        return os.path.exists(fileName)

    def getCache(self, fileName, defaultData=None, dated=0):
        if dated: fileName = self._cacheName(fileName)
        fileName = self._applyLocalCachePath(fileName)
        if self.isCacheAvailable(fileName):
            #self.debug(f'Reading cache {fileName}')
            f = open(fileName, 'rb')
            data = pickle.load(f)
            f.close()
        else:
            self.debug(f'Cache not found: {fileName}')
            self.setCache(fileName, defaultData)
            data = defaultData
        return data
    
    def setCache(self, fileName, data, dated=0):
        if dated: fileName = self._cacheName(fileName)
        fileName = self._applyLocalCachePath(fileName)
        self.debug(f'Writing cache {fileName}')
        picData = pickle.dumps(data)
        f = open(fileName, 'wb')
        f.write(picData)
        f.close()
    
    def _applyLocalCachePath(self, fileName):
        return self.pathJoin(self.localCachePath, fileName)

    def _cacheName(self, fileName):
        nw = self.getDateTime('%Y%m%d')
        cacheName = f'{nw}_{fileName}'
        return cacheName

    def storeData(self, fileName, data):
        picData = pickle.dumps(data)
        f = open(fileName, 'wb')
        f.write(picData)
        f.close()

    def readData(self, fileName, defaultData=None):
        if os.path.exists(fileName):
            f = open(fileName, 'rb')
            data = pickle.load(f)
            f.close()
        else:
            data = defaultData
        return data

    def pathReady(self, inputPath):
        inputPath = self.pathClean(inputPath)
        if os.path.exists(inputPath):
            return inputPath
        if os.path.isfile(inputPath):
            inputPath, fileName, Ext = self.pathParts(inputPath)
        os.makedirs(inputPath)
        if os.path.exists(inputPath):
            return inputPath
        return inputPath

    def pathJoin(self, basePath, *joins):
        finPath = basePath
        for each in joins:
            finPath = os.path.join(finPath, each)
        return self.pathClean(finPath)

    def doBackup(self, srcFile, bckUpToPath=1, bckUpPath='G:/pythonworkspace/myscripts/dataBackup', bckUpFmt='[FILENAME]_BKUP[TIMESTAMP].[EXT]'):
        self.debug('Backup Src: ' + srcFile)
        if not os.path.exists(srcFile):
            self.raiseError(
                'Unable to do old as src file not found ' + srcFile)
            return 0
        timeStamp = self.getDateTime('%Y%m%d%H%M%S')
        filePath, fileName, Ext = self.pathParts(srcFile)
        dstPath = self.pathReady(
            bckUpPath) if bckUpToPath else self.pathClean('.')
        dstFileName = bckUpFmt
        dstFileName = dstFileName.replace('[FILENAME]', fileName)
        dstFileName = dstFileName.replace('[TIMESTAMP]', timeStamp)
        dstFileName = dstFileName.replace('[EXT]', Ext)
        dstFile = self.pathJoin(dstPath, dstFileName)
        self.debug('Backup Dst: ' + dstFile)
        self.copyFile(srcFile, dstFile)
        self.debug('Backup Done!')
        return 1

    def getUnixTimeStampCore(self, dtobj):
        #date_time = datetime.datetime(2021, 7, 26, 21, 20)
        return time.mktime(dtobj.timetuple())

    def getUnixTimeStamp(self, days=0, seconds=0):
        if not days and not seconds:
            res = datetime.datetime.now() + timedelta(days=0)
        if days and not seconds:
            res = datetime.datetime.now() + timedelta(days=0)
        if not days and seconds:
            res = datetime.datetime.now() + timedelta(seconds=seconds)
        return self.getUnixTimeStampCore(res)

    def getArgs(self):
        if len(sys.argv) > 1:
            return sys.argv[1:]
        return []

    def isArgPresent(self, checkFor):
        for each in self.getArgs():
            if each.lower().startswith(checkFor.lower()):
                return True
        return False

    def getArgValue(self, argName):
        #['arg="Sdf sd"','fe=xcvx', 'dv=er' ]
        # getArgVALUE('fe') -> xcvx
        if self.isArgPresent(argName):
            for each in self.getArgs():
                if each.lower().startswith(argName.lower()):
                    data = each.split('=')
                    if len(data) == 2:
                        return data[1]
        return ''

    def setupLogger(self, update=0):
        self.loggerName = 'kmx.pyservice'

        if 'mylogger' in globals() and not update:
            self.logSys = globals()['mylogger']
        else:
            for eachHandler in logging.root.handlers:
                logging.root.removeHandler(eachHandler)
            self.logSys = logging.getLogger(self.loggerName)
            self.logSys.setLevel(self.logLevel)
            globals()['mylogger'] = self.logSys
            logFormatter = logging.Formatter(
                fmt=self.logFormat, datefmt=self.dateTimeStampFmt)

            logHands = []
            for each in self.logSys.handlers:
                if update:
                    each.flush()
                    each.close()
                    self.logSys.handlers.remove(each)
                else:
                    logHands.append(each.name)

            if self.logToStream:
                if not 'StreamHandler' in logHands or update:
                    logStrHdl = logging.StreamHandler()
                    logStrHdl.set_name('StreamHandler')
                    logStrHdl.setFormatter(logFormatter)
                    logStrHdl.setLevel(self.logLevel)
                    self.logSys.addHandler(logStrHdl)

            if self.logToFile:
                if not 'FileHandler' in logHands or update:
                    logFileHdl = logging.FileHandler(self.logFile)
                    logFileHdl.set_name('FileHandler')
                    logFileHdl.setFormatter(logFormatter)
                    logFileHdl.setLevel(self.logLevel)
                    self.logSys.addHandler(logFileHdl)

        self.logSys

    def notifyBrowserAlert(self, message='no message', link='https://notify.run/Stq4iPeFaU4ePGS6pqPp'):
        notify = Notify(endpoint='https://notify.run/Stq4iPeFaU4ePGS6pqPp')
        notify.send(str(message), link)
        self.info(f'Alert Notified: {message}')
    
    def notifyMailAlert(self, subject='Auto', message='no message'):
        '''
        GMAIL STOPPED THIS FUNCTION
        '''
        # response = SendEmail(
        #     sender="KMXAuto",
        #     recipient='kaymatrix@gmail.com',
        #     subject=str(subject),
        #     body=str(message),
        #     gmail_user='kaymatrix@gmail.com',
        #     gmail_pass=''
        # ).send_email()
        # if not response.ok:
        #     self.error(response.json())       
        pass 
        
    def notify(self, smallmsg, bigmsg='', subject='kmxauto'):
        if bigmsg == '':
            bigmsg = smallmsg
            
        self.notifyMailAlert(subject, bigmsg)
        self.notifyBrowserAlert(smallmsg)
        
        
        # # mail
        # if 1:
        #     response = SendEmail(
        #         sender="KMXAuto",
        #         recipient='kaymatrix@gmail.com',
        #         subject=subject,
        #         body=str(bigmsg)
        #         #gmail_user='',
        #         #gmail_pass=''
        #     ).send_email()
        #     if not response.ok:
        #         self.error(response.json())
        #     # notify
        # notify = Notify(endpoint='https://notify.run/Stq4iPeFaU4ePGS6pqPp')
        # #notify.send(str(smallmsg))
        # notify.send(str(bigmsg), 'https://notify.run/Stq4iPeFaU4ePGS6pqPp')
        
        

        self.info('Notified: ' + smallmsg)

    def getFloat(self, input):
        return float(Decimal(input))
    
    def getPercentIncrease(self, inputRate, percent):
        return float(inputRate + (Decimal((percent / 100)) * inputRate))

    def getPercentOf(self, inputRate, percent):
        return float((Decimal((percent / 100)) * inputRate))

    def prittyPrint(self, data=''):

        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(data)

    def isWindows(self):
        return isWindows()

    def isLinux(self):
        return isLinux()

    def rowPrint(self, *arg):
        spacer = 25
        info = ''
        for each in arg:
            info = info + str(each).ljust(spacer, '_')
        print(info)

    def precision(self, value, digits=6):
        value = Decimal(value)
        return math.floor(value * 10 ** digits) / 10 ** digits

    def priceFormat(self, price):
        return "{:.2f}".format(float(price))
    
    def logTile(self, title):
        self.info('-------------' + title + '----------')

    def fullInfo(self, msg):
        self.info(msg, fullInfo=1)
        
    def info(self, *msg, skipLevel=2, fullInfo=0):
        if self.isLocalDev() or fullInfo:
            if type(msg) == type(()):
                lst = []
                for each in msg:
                    lst.append(str(each))
                msg = ','.join(lst)
            else:
                msg = msg[0]
            if not self.showSimpleLog:
                msg = self.logMessageFormat(msg, skipLevel)
            if self.ignoreSysLogger:
                print(msg)
            else:
                if hasattr(self, 'logSys'):
                    self.logSys.info(msg)
                else:
                    print(msg)

    def setPlainLog(self):
        self.ignoreSysLogger = 1
        self.showSimpleLog = 1

    def checkPointInfo(self, msg):
        self.info('----------------------------------', skipLevel=3)
        self.info(msg, skipLevel=3)
        self.info('----------------------------------', skipLevel=3)

    def checkPointDebug(self, msg):
        self.debug('----------------------------------')
        self.debug(msg)
        self.debug('----------------------------------')
    
    def isAllConditionPass(self, lstOfCondition):
        for each in lstOfCondition:
            if not each or each == 0 or each == None or each == '':
                return 0
        return 1

    def isAnyConditionPass(self, lstOfCondition):
        for each in lstOfCondition:
            if each or each == 1 or each == True or each != '':
                return 0
        return 1        

    def debug(self, *msg, skipLevel=2):
        if type(msg) == type(()):
            lst = []
            for each in msg:
                lst.append(str(each))

            msg = ','.join(lst)
        else:
            msg = msg[0]
        if not self.showSimpleLog:
            msg = self.logMessageFormat(msg, skipLevel)
            msg = '[D]'+str(msg)
        if self.ignoreSysLogger and self.logSys.level <= 10:
            print(msg)
        else:
            self.logSys.debug(msg)

    def warn(self, msg='', skipLevel=2):
        if not self.showSimpleLog:
            msg = self.logMessageFormat(msg, skipLevel)
        if self.ignoreSysLogger:
            print(msg)
        else:
            self.logSys.warn(msg)

    def error(self, msg='', skipLevel=2):
        if not self.showSimpleLog:
            msg = self.logMessageFormat(msg, skipLevel)
        if self.ignoreSysLogger:
            print(msg)
        else:
            self.logSys.error(msg)

    def logMessageFormat(self, msg='', skipLevel=2):
        fn, cls, mod, modf = self.getCallerInfo(skipLevel)
        if self.getGlobalSwitch('LOGDETAILED'):
            fmsg = '[{0}.{1}.{2}]: {3}'.format(mod, cls, fn, msg)
        else:
            fmsg = '[{1}.{2}]: {3}'.format(mod, cls, fn, msg)
        return fmsg

    def getCallerInfo(self, skipLevel=1):
        fn, cls, mod, modf = '', '', '', ''
        try:
            stack = inspect.stack()
            stack = stack[skipLevel+1:]
            if len(stack) > 0:
                entry = stack[0]
                if len(entry) > 3:
                    fcode = entry[0]
                    fn = str(entry[3])
                    cls = ''
                    mod = ''
                    modf = str(entry[1])
                    if hasattr(fcode, 'f_locals'):
                        locals = fcode.f_locals
                        if 'self' in locals:
                            selfobj = locals['self']
                            if selfobj:
                                cls = str(selfobj.__class__.__name__)
                                mod = str(selfobj.__module__)
                        else:
                            mod = os.path.basename(modf)
                            mod = os.path.splitext(mod)[0]
                    else:
                        mod = os.path.basename(modf)
                        mod = os.path.splitext(mod)[0]
        except:
            pass
        return fn, cls, mod, modf

    def shellExecute(self, command):
        # This will chock and execute
        subprocess.call(command)

    def raiseError(self, msg='CustomError'):
        raise Exception(msg)

    def encrypt(self, text, cryptoKey=4132):
        cipher = ''
        for each in text:
            c = (ord(each)+int(cryptoKey)) % 126
            if c < 32:
                c += 31
            cipher += chr(c)
        return cipher

    def decrypt(self, text, cryptoKey=4132):
        plaintext = ''
        for each in text:
            p = (ord(each)-int(cryptoKey)) % 126
            if p < 32:
                p += 95
            plaintext += chr(p)
        return plaintext

    def getUUID(self):
        return str(uuid.getnode())

    def errorInfoOld(self):
        TrackStack = sys.exc_info()[2]
        ErrorReport = []
        while TrackStack:
            FileName = TrackStack.tb_frame.f_code.co_filename
            FunctionName = TrackStack.tb_frame.f_code.co_name
            ErrorLine = TrackStack.tb_lineno
            TrackStack = TrackStack.tb_next
            ErrorReport.append([FileName, FunctionName, ErrorLine])
        ErrorReport.append([sys.exc_info()[0], sys.exc_info()[1], 0])
        ErrorInfo = ''
        for eachErrorLevel in ErrorReport:
            ErrorInfo += '\nFile: "' + str(eachErrorLevel[0]) + '", line ' + str(
                eachErrorLevel[2]) + ', in ' + str(eachErrorLevel[1])
        self.error(ErrorInfo)
        return None

    def errorInfo(self):
        info = traceback.format_exc()
        self.error(info)

    def printObjInfos(self, obj):
        lst = self.getObjInfos(obj)
        for each in lst:
            print('{0} - {1}'.format(each[0], each[1]))

    def getObjInfos(self, obj):
        infos = []
        members = inspect.getmembers(obj)
        for eachMember in members:
            obj = eachMember[1]
            mem = eachMember[0]
            tp = 'Obj'
            if inspect.isfunction(obj) or inspect.ismethod(obj):
                tp = 'Fn'
            elif inspect.isbuiltin(obj):
                tp = 'Fn-BuiltIn'
            elif inspect.isclass(obj):
                tp = 'Class'
            elif inspect.ismodule(obj):
                tp = 'Module'
            elif inspect.iscode(obj):
                tp = 'Code'
            elif (type(obj) is type(1) or
                  type(obj) is type('') or
                  type(obj) is type([]) or
                  type(obj) is type(()) or
                  type(obj) is type({})
                  ):
                tp = 'Variable'
            elif type(obj) is type(None):
                tp = 'Obj'
            else:
                tp = 'Obj'

            infos.append([mem, tp, eachMember[1]])
        return infos

    def getRandom(self, stop, start=0):
        return self.rand.randrange(start, stop)

    def getSystemName(self):
        return str(socket.gethostname())

    def getCurrentPath(self):
        return os.path.abspath(os.curdir)

    def getCurrentUser(self):
        return getpass.getuser()

    def getRelativeFolder(self, folderName):
        return os.path.join(self.getCurrentPath(), folderName)

    def getDateCalc(self, addRemoveDays=0, format='%Y-%m-%d', fromDate=None):
        fromDate = fromDate if fromDate else datetime.datetime.today() 
        res = fromDate + timedelta(days=addRemoveDays)
        return res.strftime(format)

    def getDateCalcObj(self, addRemoveDays=0, fromDate=None):
        fromDate = fromDate if fromDate else datetime.datetime.today() 
        res = fromDate + timedelta(days=addRemoveDays)
        return res

    def getDateTimeObjFor(self, input, format='%Y-%m-%d'):
        return datetime.datetime.strptime(input, format)

    def getDateTimeForObj(self, dateTimeObj, format='%Y%m%d %H%M%S'):
        return dateTimeObj.strftime(format)

    def getDateBetweenTwoDate(self, startDate, endDate, format='%Y%m%d'):
        sdate = self.getDateTimeObjFor(startDate, format)   # start date
        edate =self.getDateTimeObjFor(endDate, format)   # end date
        lst = [sdate+timedelta(days=x) for x in range((edate-sdate).days)]
        nlst = []
        for each in lst: nlst.append(self.getDateTimeForObj(each, format))
        return nlst

    def getMissingDatesInList(self, startDate, endDate, crossCheckList):
        notToday = True
        cdateStr = startDate
        cdateObj = self.getDateTimeObjFor(startDate, '%Y%m%d')
        missingDateFor = []
        while(notToday):
            if cdateStr == endDate:
                notToday = False
            else:
                cdateObj = self.getDateCalcObj(1, cdateObj)
                cdateStr = self.getDateTimeForObj(cdateObj, '%Y%m%d')
                if not cdateStr in crossCheckList:
                    missingDateFor.append(cdateStr)
        return missingDateFor
    
    def getDictDefault(self, inputDict, keyName, defaultValue):
        if keyName in inputDict:
            return inputDict[keyName]
        else:
            return defaultValue
    
    def getDictSpecifics(self, inputDict, *keys):
        newDict = {}
        for eachKey in keys:
            newDict[eachKey] = self.getDictDefault(inputDict, eachKey, None) 
        return newDict
        
    def getDateDiff(self, date1, date2, format='%Y-%m-%d'):
        '''
        ret 1 means date1 is 1 day old than date 2
        ret 0 measn both are same
        ret -1 means date1 is 1 day after date2
        '''
        d1 = self.getDateTimeObjFor(date1, format)
        d2 = self.getDateTimeObjFor(date2, format)
        res = d2 - d1
        return res.days

    def getDateTimeStamp(self, format="%Y%m%d%H%M%S"):
        return self.getDateTime(format)

    def getDateTime(self, format='%Y%m%d'):
        """
        "%Y-%m-%d %H:%M:%S"
        Directive Meaning Notes
        %a Locale's abbreviated weekday name.
        %A Locale's full weekday name.
        %b Locale's abbreviated month name.
        %B Locale's full month name.
        %c Locale's appropriate date and time representation.
        %d Day of the month as a decimal number [01,31].
        %H Hour (24-hour clock) as a decimal number [00,23].
        %I Hour (12-hour clock) as a decimal number [01,12].
        %j Day of the year as a decimal number [001,366].
        %m Month as a decimal number [01,12].
        %M Minute as a decimal number [00,59].
        %p Locale's equivalent of either AM or PM. (1)
        %S Second as a decimal number [00,61]. (2)
        %U Week number of the year (Sunday as the first day of the week) as a decimal number [00,53]. All days in a new year preceding the first Sunday are considered to be in week 0. (3)
        %w Weekday as a decimal number [0(Sunday),6].
        %W Week number of the year (Monday as the first day of the week) as a decimal number [00,53]. All days in a new year preceding the first Monday are considered to be in week 0. (3)
        %x Locale's appropriate date representation.
        %X Locale's appropriate time representation.
        %y Year without century as a decimal number [00,99].
        %Y Year with century as a decimal number.
        %Z Time zone name (no characters if no time zone exists).
        %% A literal "%" character.
        """
        now_utc = datetime.datetime.now(timezone('UTC'))
        now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
        return now_asia.strftime(format)

    def fileContent(self, fileName):
        f = open(fileName, "r")
        content = str(f.read())
        f.close()
        return content

    def writeFileContent(self, fileName, data):
        f = open(fileName, 'w')
        f.write(str(data))
        f.close()

    def copyFile(self, src, dst):
        shutil.copy(src, dst)

    def copyFolder(self, source_folder, destination_folder, latest_overwrite=1, forced_overwrite=0, verbose=1):
        for root, dirs, files in os.walk(source_folder):
            for item in files:
                src_path = os.path.join(root, item)
                dst_path = os.path.join(
                    destination_folder, src_path.replace(source_folder, ""))
                if os.path.exists(dst_path):
                    if (not forced_overwrite and not latest_overwrite):
                        if(verbose):
                            print("Already exist, Skipping...\n" +
                                  src_path + " to " + dst_path)
                    if (not forced_overwrite and latest_overwrite):
                        if os.stat(src_path).st_mtime > os.stat(dst_path).st_mtime:
                            if(verbose):
                                print("Overwriting latest...\n" +
                                      src_path + " to " + dst_path)
                            shutil.copy2(src_path, dst_path)
                    if (forced_overwrite):
                        if(verbose):
                            print("Overwriting...\n" +
                                  src_path + " to " + dst_path)
                        shutil.copy2(src_path, dst_path)
                else:
                    if(verbose):
                        print("Copying...\n" + src_path + " to " + dst_path)
                    shutil.copy2(src_path, dst_path)
            for item in dirs:
                src_path = os.path.join(root, item)
                dst_path = os.path.join(
                    destination_folder, src_path.replace(source_folder, ""))
                if not os.path.exists(dst_path):
                    if(verbose):
                        print("Creating folder...\n" + dst_path)
                    os.mkdir(dst_path)
        if(verbose):
            print("Copy process completed!")

    def _buildCallerPath(self, parentOnly=0):
        stack = inspect.stack()
        path = ""
        for eachStack in stack:
            if("self" in eachStack[0].f_locals.keys()):
                the_class = eachStack[0].f_locals["self"].__class__.__name__
                the_method = eachStack[0].f_code.co_name
                if(the_class != "basic"):
                    if(parentOnly):
                        path = "{}.{}()->".format(the_class, the_method)
                    else:
                        path += "{}.{}()->".format(the_class, the_method)
        return path

    def makeEmptyFile(self, fileName):
        self.makePathForFile(fileName)
        self.writeFileContent(fileName, '')

    def makePathForFile(self, file):
        base = os.path.dirname(file)
        self.makePath(base)

    def makePath(self, path):
        print(path)
        if(not os.path.exists(path) and path != ''):
            os.makedirs(path)
        else:
            log.error("Unable to read (OR) Path exists " + path)

    def isPathOK(self, path):
        return os.path.exists(path) and path != '' and path is not None

    def isPathFile(self, path):
        return os.path.isfile(path) and path != '' and path is not None

    def pickleSaveObject(self, obj, file=""):
        if(obj is None):
            log.error("Pass me valid object to save" + obj)
        className = obj.__class__.__name__
        if(file is None or file == ""):
            file = className + ".txt"
        base = os.path.dirname(file)
        if(not os.path.exists(base) and base != ''):
            os.makedirs(base)
        f = open(file, "wb")
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
        f.close()
        print("Saved!" + className + "-" + file)

    def pickleLoadObject(self, file):
        x = None
        if(file is None or file == ""):
            log.error("Pass me file name to read and pass the object")
        if(os.path.exists(file)):
            try:
                f = open(file, "rb")
                x = pickle.load(f)
                f.close()
                log.info("File read and obj returned " +
                         file + " obj: " + x.__class__.__name__)
            except:
                log.error("Error loading the pickle. Passing default!")
        else:
            log.error("Error! File doesn't exist " + file)
        return x

    def smart_bool(self, s):
        if s is True or s is False:
            return s
        s = str(s).strip().lower()
        return not s in ['false', 'f', 'n', '0', '']
    
#------------------------

    
    def _updateDict(self, dstDict, srcDict):
        for eachKey in srcDict.keys():
            if not eachKey in dstDict:
                dstDict[eachKey] = srcDict[eachKey]
        return dstDict
        
    
if __name__ == '__main__':
    obj = Tools()
    obj.notifyBrowserAlert("TETS22")