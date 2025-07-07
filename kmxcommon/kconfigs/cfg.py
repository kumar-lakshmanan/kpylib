'''
Created on 25-Jun-2022

Base Configuration
- Access it via only - tls.cfg
- All new cfg should be added to base cfg only. and should be overriden.
- Should be accessed via overriden class - cfg_default or cfg_local. Not to be used directly. 
- Can be overridden with custom config. Chk cfg_default or cfg_local. 
- Overriden config module (kmxcommon.kconfigs.cfg -> .cfg_default)
- Make sure to pass while starting your app.
- You can pass explicitly while readying tls tool or pass via env variable - KMXPYCONFIG 
 
Also check xtools getTools function
 
'''

#Config Info
configName = 'kmxbase'
configVersion = 0.1
configLastEditDate = '2022-12-15'
configAuthor = 'kmx'
configDesc = 'This is base config. Should be overriden and used' 

#Common Settings
desktopName = 'KPM_SYSTEM'                                     #HOSTNAME
dateFmt = '%Y%m%d'
timeFmt = '%H%M%S'
configName = 'default'

#Base folders
dataFolder = f'G:/pythonworkspace/kmxdata'           #DATA COLLECTIONS - BASE FOLDER
safeFolder = f'{dataFolder}/safe'
cacheFolder = f'{dataFolder}/cache'                             #CACHE COLLECTIONS - BASE FOLDER
logFolder = f'{dataFolder}/log'                                  #LOG FOLDER - BASE FOLDER

#Logging
dateTimeStampFmt = '%Y%m%d%H%M%S'
logName = 'kmx.pyservice'
logFormat = '[%(asctime)s]%(message)s'
logLevel = 20                                                   # 10 - debug #20 - info #30 - warn #40 - error
logToStream = 1
logToFile = 0
logFile = f'{logFolder}/{dateTimeStampFmt}.log'
showSimpleLog = 0
ignoreSysLogger = 0

#Global Switches
gs_forceReadOnline = 'forceReadOnline'
gs_writeProtectOnline = 'writeProtectOnline'
gs_skipBTCDomCheck = 'skipBTCDomCheck'

#GCP
gcp_project = 'kaymatrix'
gcp_bucket = 'kaymatrixbucket' 
gcp_keyfile = safeFolder + '/gcp.json'

#AWS
aws_region = 'ap-south-1'
aws_access_key_id = ''
aws_secret_access_key = ''

aws_cachePrefixName = 'aws'
aws_cacheBucket = 'kmxcache' 

#CRYPTS
crypts_fetchPerSource = 3
crypts_fetchStartTime = '08:45'
crypts_fetchEndTime = '21:00'
crypts_dailyLoggingStartTime = crypts_fetchStartTime
crypts_dailyLoggingEndTime = crypts_fetchEndTime
crypts_realDayStart = '05:00'
crypts_realDayEnd = '23:55'
crypts_expectHitWithIn = 7   
crypts_defaultExitPercent = 4
crypts_expectedBTCDomAbove = 39.5                #BTCDominance should be above this for fetching symbol
crypts_expectedCalEventConfPercent = 40        #Cal Event Confident Percent - Above 40
crypts_expectedCalEventVotes = 6               #Cal Event Confident Percent - Above 40
crypts_expectedCalEventViewed = 21             #Cal Event Confident Percent - Above 40
crypts_usrReactionExpected = 0
crypts_expectedNewsin2d = 1
crypts_expectedNewsin7d = 1
crypts_topPNLShouldBelow = -10
crypts_sources = []
crypts_sources.append('src_assorted')
crypts_sources.append('src_calevent')
crypts_sources.append('src_newsnet')
crypts_sources.append('src_toppnl')
crypts_ignoreProcessingSymbols = ['BTC','ETH','BUSD','BNB','USDC','ETC','ADA','SOL','MATIC']
crypts_symbols = {}
crypts_symbols['KAVA'] = ['KAVA NETWORK']
crypts_symbols['CRO'] = ['cronos', 'crypto.com']
crypts_symbols['SHIB'] = ['Shiba Inu']
crypts_symbols['BTC'] = ['BITCOIN']
crypts_goodTerms = ['rebound', 'increase', 'gain', 'win', 'good', 'progress', 'profit', 'best', 'super', 'profit', 'large', 'great', 'first', 'top', 'up', 'upgrade', 'update', 'rais', 'high', 'bull']
crypts_badTerms = ['tough', 'problem', 'decrease', 'loss', 'lost', 'sour', 'bad', 'degrade', 'downgrade', 'worst', 'down', 'bottom', 'dropping', 'lower', 'bear']

#APIs
api_twit_apikey = 'nIwelYBfBnyGu28l4zpDT9P3G'
api_twit_apikeysecret = 'spLEwRlZS5YxQMZjcDe5iMMwiMoTCmZjqnJyEP1Y1kBxPOYViL'
api_twit_accesstoken = '1136767650111971329-Elzpa1L5lv5iskLAsbmzqFQoI8d49j'
api_twit_accesstokensecret = 'fx3Gulv7cB48w7npUDPmO3vpco4cm5IYGlxA37jzH5ueh'        
api_clankAppApiKey = '3c13c61d22a41e05a2fcbdbb6378edd5'
api_coinMarketCalAPIKey = 'jSf8OdeFuM1MBUIGKhYHuICOcrcfR2GyYgcvQzj0'
