# kTools – Generic Tool Collection

> The `kTools` library is a **singleton** utility collection that powers many of the scripts in this project. It is designed to be lightweight, easy to drop into any Python application, and comes with a full set of helpers for configuration, logging, file handling, system integration, and simple encryption.

---
## PreSetup
!! IMPORTANT !!

This lib should be available in pythonpath. Use any trick. But add this to the pythonpath.
Below are sample options.

1. Create a .pth file 
```
    Find your interpreter's site-packages folder:
    
    Python
    import site
    print(site.getsitepackages())
```
then, create file - mypaths.pth with below content
```
G:\pyworkspace\kpylib
G:\pyworkspace\somemore_lib_proj
```

2. sitecustomize.py (i use this)
```
Just like in Option.1, instead of creating .pth path create sitecustomize.py file with below content

import sys

sys.path.insert(0, r"G:\pyworkspace\kpylib")
sys.path.insert(0, r"G:\pyworkspace\somemore_lib_proj")
```

3. System Env Variable (Least Prefered)
    Add sys env variable K_PYLIB and set its value G:\pyworkspace\kpylib
    else in your first executing code. you can have below snippet

```
import os,sys
K_PYLIB = '../kpylib'
K_CONFIG = os.path.abspath('config.json')
_kpylib = os.environ.get("K_PYLIB", K_PYLIB)
_kconfig = os.environ.get("K_CONFIG", K_CONFIG)
if not os.path.exists(_kpylib): sys.exit("K_PYLIB not found!")
if not os.path.exists(_kconfig): sys.exit("K_CONFIG not found!")
sys.path.extend(x.strip() for x in _kpylib.split(os.pathsep))

#----------------------------------------------
import kTools
tls = kTools.KTools()   
```

Additional to above any one option. along with it, do this too if you are using pycharm or any idea. So that IDE will populate autocomplete.
```
PyCharm Settings -> Python -> Interpreter -> Python Interpreter Drop Drown -> Show All... -> Interpreter Paths -> Add Custom Path
```

---
## Quick Start

```bash
# Install the project (or just copy `commonlib/kTools.py` into your own package)
python -m pip install -e .
```

```python
# Simple example
import kTools

tls = kTools.KTools("MyApp", defaults=None, CONFIG_JSON="config.json")

tls.helloworld()
print(tls.getRandom(10))
```

---

## Features

| Category | Feature | Description |
|----------|---------|-------------|
| **Application bootstrap** | `KTools(appName, customLookUp, customJsonConfig)` | Creates the singleton instance, loads a lookup module (default or custom) and a JSON config file.  |
| **Logging** | `info`, `debug`, `warn`, `error`, `errorAndExit` | Configurable via the `logging` section of `config.json`. Supports console & file output, custom formatting, and runtime log‑level changes. |
| **Configuration** | `getSafeConfig`, `getValue`, `getConfigFile` | Hierarchical lookup from args → env → config → lookup → defaults.  |
| **System path utilities** | `sysPathUpdater`, `sysPathAdder`, `sysPathDuplicatesRemover` | Keeps `sys.path` clean and up‑to‑date with environment variables and user/site packages. |
| **File & folder helpers** | `getFileContent`, `writeFileContent`, `cleanFolder`, `copyFile`, `copyFolder`, `makePath`, `makeEmptyFile` | CRUD for files/folders, including recursive XML content, zip creation, backup and cache. |
| **Random / Date helpers** | `getRandom`, `getDateTime`, `getDateTimeStamp`, `getDateBetweenTwoDate`, `getDateDelta` | Random numbers (seedable), date & time formatting, timestamp generation, and date arithmetic. |
| **Executable shell commands** | `shellExecuteWait`, `shellExecuteNoBlock`, `shellExecuteWithIO` | Run os commands synchronously, asynchronously or with custom IO streams. |
| **Encryption** | `encrypt`, `decrypt` | Very lightweight Caesar‑style cipher using a configurable key. |
| **Short‑hand number conversion** | `shortHandNumberConverter` | Converts `1K`, `2.5M`, `3T`, `1P` to integers. |
| **Cache** | `setCache`, `getCache`, `setCacheFile`, `getCacheFile` | Simple binary cache backed by `pickle` or `json`. Can be timestamped. |
| **UUID helpers** | `getUUID`, `getUUID4` | Generates node / v4 UUIDs. |
| **Signal helpers** | `addOnlyUniqueToDict`, `addObjectToList`, `isNotPresentInDict` |
| **Boolean helpers** | `smartBool` | Normalizes truthy/falsey values and strings. |
| **Environment helpers** | `getSafeEnv`, `getSafeDictValue` |
| **Language helpers** | `convertStrToLiteralObject`, `convertDictStrToDict` |
| **Tool integration** | `getToolsFn` | Exposes registered tool functions for Ollama, e.g. file operations or web actions. |
|
---

## Configuration files

### `config.json`
```json
{
    "general": {
        "timeStampFormat": "%Y%m%d%H%M%S",
        "dateTimeFormat": "%Y-%m-%d %I:%M:%S %p",
        "hostname": "MUKUND_PC",
        "verbose": 0,
        "repeatCoreCallingCountLimit": 10,
        "simulate": 0,
        "include_reference_files": 1,
        "include_past_conversation": 0,
        "save_conversation": 1,
        "mainModel": "qwen3-coder:480b-cloud",
        "mainModel": "gpt-oss:20b-cloud",
        "ai_definition": "ai_definition_for_coding",
        "ai_definition_sample1": "ai_definition_for_general",
        "ai_definition_sample2": "ai_definition_for_coding",
        "save_prompt": 1,
        "prompt_file": "prompt.txt",
        "conversation_file_path": "./conversation/coding"
    },
    "logging": {
        "logDisable": 0,
        "logLevel": "INFO",
        "logDateTimeFormat2": "%Y-%m-%d %I:%M:%S%p",
        "logDateTimeFormat": "%I:%M:%S%p",
        "logFormat": "[%(asctime)s]%(levelname).1s:%(message)s",
        "logToConsole": 1,
        "logToFile": 1,
        "logFile": "output.log",
        "logModuleName": 0,
        "logProdMode": 0
    },
    "folders": {
        "temp": "C:/TEMP",
        "cache": "C:/TEMP/ktools/cache"
    }
}
```

### `lookup.py`
- Holds the constants such as `K_PYLIB`, `K_CONFIG`, `K_ISPROD`, and defaults for random seed, encryption key, model names, etc.

---

## Environment Variables

| Variable | Purpose | Example |
|-----------|---------|---------|
| `K_PYLIB` | Directory of the `commonlib` package used for path resolution | `C:/projects` |
| `K_CONFIG` | Path to a JSON config file if not passed explicitly | `/etc/app/config.json` |
| `K_ISPROD` | 1 for production mode, 0 or missing for development | `1` |
| `COMPUTERNAME` | Used by `isLocal()` to identify a development machine. | `MUKUND_PC` |
| `OLLM_API_KEY` | API key for Ollama. | `sk-xxxxx` |

---

## How It Works

1. **Singleton** – `KTools()` is implemented as a singleton; the first call creates the instance and subsequent calls return the same instance. This keeps configuration and loggers in sync.
2. **Lookup** – At initialization it loads a lookup module. If none provided it tries `kToolsDefaultLookUps.py`; if that fails a dynamic module is created.
3. **Configuration** – The `config.json` (or file specified on init) is parsed and used throughout the library. `getSafeConfig()` allows safely retrieving nested values.
4. **Logging** – `setUpLogger()` creates a `logging` instance following the configuration. The library also supports a custom callback via `addCustomLogPrinter()`.
5. **Tools** – Files, folders, and simple system calls are wrapped in helper functions. The `Tools` class registers them so an AI agent can invoke them via Ollama’s tool‑call feature.
6. **Run** – Example usage in a real project: create `kTools.KTools(...)`, perform any helper call, and use `writeFileContent()` / `getFileContent()` for persistence.

---

## Usage in a Project

```python
# project/main.py
from commonlib import kTools

tls = kTools.KTools("MyApp", customLookUp=None, customJsonConfigFile="/path/to/config.json")

# Access logging
tls.info("Application started")

# File operation
content = tls.getFileContent("data.txt")
output = content.upper()
tls.writeFileContent("data.txt", output)

# Random number
rand_num = tls.getRandom(100)

# Date/time
now = tls.getDateTime()

# Shell command
tls.shellExecuteWait("echo Hello World")
```

---

## Extending

- Add new tool functions to `commonlib/kTools.py` or register them in `Tools.addCustomTools()`.
- Create a custom lookup module by copying `kToolsDefaultLookUps.py` and extending it.
- Update `config.json` as needed – the library will automatically pick up changes on restart.

---

## License

This project is licensed under the MIT License – see the root `LICENSE` file.

---

## Author

> **Kumaresan Lakshmanan (kayma)** – <kaymatrix@gmail.com>  
> **Created:** 24‑Apr‑2025
> **Last updated:** 16‑Mar‑2026
