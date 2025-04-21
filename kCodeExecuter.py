'''
Created on 21-Mar-2025

@author: kayma
'''
import os, sys, time, json, importlib, code, inspect
import kTools


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
        Only Code Execution
    """
    
    def __init__(self, parent=None):        
        self.tls = parent if parent else kTools.GetKTools()
        #self.console = code.InteractiveConsole(locals())
        self.console = CapturingConsole(locals())
        
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
            except SyntaxError:
                self.tls.getLastErrorInfo()
            except SystemExit:
                self.tls.getLastErrorInfo()
            except:
                self.tls.getLastErrorInfo()
            return self.console.last_result
    
    def runCode(self, codeStr='', fileName="<input>"):
        self.tls.debug('Executing code string...')
        codeStr = codeStr.strip()
        if(codeStr):
            try:
                self.updateLocals('__name__', '__main__')
                self.console.runsource(codeStr, fileName, 'exec')
                time.sleep(.01)            
            except SyntaxError:
                print(sys.exc_info())
            except SystemExit:
                print(sys.exc_info())
            except:
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
            #importlib.reload(mod)
            return mod
        else:
            if type(modName) == type(""):
                mod = sys.modules[modName]
                #importlib.reload(modName)
                return mod
            elif inspect.ismodule(modName):
                #importlib.reload(modName)
                return modName
    
    def scanModuleFiles(self, moduleRootPath, ignoreFileNameHasText = ["__init__"], advConfig={}):
        checkIsPresent = lambda wordList, inpText: any(word in inpText for word in wordList)
        
        modCollection = {}
        modFiles = self.tls.getFileList(moduleRootPath,".py")        
        for file in modFiles:
            fileName = os.path.basename(file).replace(".py","")
            if checkIsPresent(ignoreFileNameHasText,fileName):
                if not ('silentIgnoredFileInfo' in advConfig and advConfig['silentIgnoredFileInfo']): 
                    self.tls.debug(f"{file} not a valid node.")
            elif fileName in list(modCollection.keys()): 
                self.tls.debug(f"{file} can't be loaded, Might be duplicate.") 
            else:
                modImported = self.loadModule(fileName, file)
                modCollection[fileName] = (modImported, file)                         
        return modCollection
    
if __name__ == "__main__":
    t = KCodeExecuter()
    