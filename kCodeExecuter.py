'''
Created on 21-Mar-2025

@author: kayma
'''
__created__ = "24-Apr-2025"
__updated__ = "2025-07-15"
__author__ = "kayma"

import os, sys, time, json, importlib, code, inspect, types, atexit, traceback
from time import strftime
from kTools import KTools

# Single line console command capture response and give back on demand
class CapturingConsole(code.InteractiveConsole):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_result = None

    def push(self, line):
        old_displayhook = sys.displayhook

        def capture_displayhook(value):
            self.last_result = value
            # Prevent printing to stdout
            # If you still want to print: old_displayhook(value)

        sys.displayhook = capture_displayhook
        try:
            return super().push(line)
        finally:
            sys.displayhook = old_displayhook

class KCodeExecuter(object):
    """
        Singleton Code Executor 
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            print("Creating Singleton KCodeExecuter instance...")
            cls._instance = super(KCodeExecuter, cls).__new__(cls)

        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.tls = KTools()
            #self.console = code.InteractiveConsole(locals())
            self.console = CapturingConsole(locals())
            self._initialized = True

    def getLocals(self):
        return self.console.locals

    def updateLocals(self, name, value):
        self.console.locals[name] = value

    # def getUpdatedLocals(self):
    #     try:
    #         raise None
    #     except:
    #         frame = sys.exc_info()[2].tb_frame.f_back
    #     namespace = frame.f_globals.copy()
    #     namespace.update(frame.f_locals)
    #     namespace['__name__'] = '__main__'
    #     return namespace

    def runCommand(self, codeStr):
        self.tls.info(f'>> {codeStr}')
        codeStr = codeStr.strip()
        if(codeStr):
            try:
                self.updateLocals('__name__', '__main__')
                #self.console.runsource(codeStr, "<console>", "single")
                self.console.last_result = None
                self.console.push(codeStr)
                time.sleep(.01)
            except Exception as e:
                self.tls.error(e)
            finally:
                self.console.resetbuffer()
            return self.console.last_result

    def runCode(self, codeStr='', fileName="<input>"):
        self.tls.debug('Executing code string...')
        codeStr = codeStr.strip()
        if(codeStr):
            try:
                self.updateLocals('__name__', '__main__')
                self.console.runsource(codeStr, fileName, 'exec')
                time.sleep(.01)
            except Exception as e:
                self.tls.error(e)                
                print(sys.exc_info())

    def runScript(self, scriptFile=None):
        self.tls.debug('Trying to execute script file... %s' % scriptFile)
        if scriptFile and os.path.exists(scriptFile):
            basePath = os.path.dirname(scriptFile)
            fName = os.path.basename(scriptFile)
            data = self.tls.getFileContent(scriptFile)
            self.addToSysPath(basePath)
            self.runCode(data,fName)
        else:
            self.tls.error('Script file missing...' + str(scriptFile))

    def cleanAndUpdateSysPaths(self, newPaths=[]):
        #Clean Existing Path
        existingPaths = []
        for eachSysPath in sys.path:
            pth = os.path.abspath(eachSysPath)
            if not pth in existingPaths:
                existingPaths.append(pth)
        sys.path = existingPaths
        for each in newPaths:
            self.addToSysPath(each)

    def addToSysPath(self, path):
        path = os.path.abspath(path)
        if('\.' in path): return None
        if path not in sys.path and os.path.exists(path):
            self.tls.info("Adding path to system... " + str(path))
            sys.path.append(path)

    def loadModule(self, modName, modFilePath):
        """Dynamically loads a Python module from an absolute file path.
        Args:
            module_name (str): The name to assign to the module.
            file_path (str): The absolute path of the Python file.
        Returns:
            module: The loaded module.
        if hasattr(loaded_module, "some_function"):
            loaded_module.some_function()
        """
        spec = importlib.util.spec_from_file_location(modName, modFilePath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules[modName] = module
        return module

    def isModuleExist(self, modName):
        return modName in sys.modules.keys()

    def getModule(self, modName):
        if self.isModuleExist(modName):
            mod = sys.modules[modName]
            return mod
        else:
            if isinstance(modName, types.ModuleType) and inspect.ismodule(modName):
                return modName
            else:
                mod = importlib.import_module(modName)
                sys.modules[modName] = mod
                return mod

    def scanModuleFiles(self, moduleRootPath, ignoreFileNameHasText = ["__init__"], advConfig={}):
        checkIsPresent = lambda wordList, inpText: any(word in inpText for word in wordList)
        modCollection = {}
        modFiles = self.tls.getFileList(moduleRootPath,".py")
        for file in modFiles:
            fileName = os.path.basename(file).replace(".py","")
            if checkIsPresent(ignoreFileNameHasText,fileName):
                if not ('silentIgnoredFileInfo' in advConfig and advConfig['silentIgnoredFileInfo']):
                    self.tls.debug(f"{file} not a valid file.")
            elif fileName in list(modCollection.keys()):
                self.tls.debug(f"{file} can't be loaded, Might be duplicate.")
            else:
                try:
                    #self.console.compile
                    modImported = self.loadModule(fileName, file)
                except Exception as e:
                    fullErrorDetail = self.tls.getLastErrorInfo()
                    self.tls.error(f"[Error loading the module: {file}]")
                    if 'showErrors' in advConfig and advConfig['showErrors']:
                        print(fullErrorDetail)
                        print("--")
                        print(e)
                    else:
                        self.tls.error(e)
                modCollection[fileName] = (modImported, file)
        return modCollection

if __name__ == "__main__":
    t = KCodeExecuter()
    res = t.runCommand("10+2")
    print(res)
    res = t.runCommand("10+42")
    print(res)
    res = t.runCommand("10/0")
    print(res)    
    res = t.runCommand("10+1")
    print(res)        