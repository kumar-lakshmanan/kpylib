'''
Created on 01-Jun-2022
ALL RELATED TO GCP
@author: kayma
'''

import os
import pickle

from kmxcommon import xtools
tls = xtools.getGlobalTools()

from google.cloud import storage
    
class GCPSupport():
    
    def __init__(self):    
        self.tls = tls
        self.gcpproject = self.tls.cfg.gcp_project                
        self.gcpbucket = self.tls.cfg.gcp_bucket    
        self.gcpkeyfile = self.tls.cfg.gcp_keyfile
        if tls.isLocalDev(): os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.gcpkeyfile
        self.forceGCP = 0        
        self.sc = storage.Client()
    
    def cacheRead(self, cacheName, gcpbucket=None):
        forceGCP = tls.getGlobalSwitch('gcpForceRead', 0)
        cacheName = self._gcpCacheNamingConvention(cacheName)
        gcpbucket = gcpbucket if gcpbucket else self.gcpbucket
        data = []
        try:
            tls.debug(f'GCP: Reading GCP Cache: {cacheName}...')
            #Is Cache Present InMemory:
            if tls.isGlobalVarExist(cacheName) and not forceGCP:
                data = tls.getGlobalVar(cacheName)
                tls.debug(f'GCP: Read {cacheName} from in memory.')
            #Is Cache Present In Local File:
            elif tls.isLocalDev() and tls.isCacheAvailable(cacheName, dated=1) and not forceGCP: 
                data = tls.getCache(cacheName, None, dated=1)
                tls.debug(f'GCP: Read {cacheName} from local file.')
            #Fetch Cache Present In GCP:
            else:
                bucket = self.sc.bucket(gcpbucket)
                blob = bucket.blob(cacheName)
                picks = blob.download_as_string()
                data = pickle.loads(picks)                
                tls.info(f'GCP: Read {cacheName} from GCP')
                if tls.isLocalDev(): tls.setCache(cacheName, data, dated=1)
                tls.setGlobalVar(cacheName, data)
        except Exception as e:
            tls.error(f'GCP Error reading the bucket/cache: {gcpbucket} or {cacheName} - {e}')
        return data

    def cacheWrite(self, data, cacheName, gcpbucket=None):
        if tls.getGlobalSwitch('gcpWriteProtect', 0):
            tls.info(f'GCP: Write Protected. Skipping GCP Write!') 
            return True
        cacheName = self._gcpCacheNamingConvention(cacheName)
        gcpbucket = gcpbucket if gcpbucket else self.gcpbucket
        try:
            tls.debug(f'GCP: Storing GCP Cache: {cacheName}...')
            tls.setGlobalVar(cacheName, data)
            if tls.isLocalDev(): tls.setCache(cacheName, data, dated=1)
            bucket = self.sc.bucket(gcpbucket)
            blob = bucket.blob(cacheName)
            picks = pickle.dumps(data)
            blob.upload_from_string(picks)
            tls.info(f'GCP: Storing {cacheName} in GCP')
        except Exception as e:
            tls.error(f'GCP Error: writing the bucket/cache: {gcpbucket} or {cacheName} - {e}')
            return False
        return True
    
    def cacheIsExist(self, cacheName, gcpbucket=None):
        forceGCP = tls.getGlobalSwitch('gcpForceRead', 0)
        cacheName = self._gcpCacheNamingConvention(cacheName)
        gcpbucket = gcpbucket if gcpbucket else self.gcpbucket
        try:
            if tls.isGlobalVarExist(cacheName) and not forceGCP:
                return True
            elif tls.isLocalDev():
                if tls.isCacheAvailable(cacheName, dated=1) and not forceGCP: 
                    return True
            bucket = self.sc.bucket(gcpbucket)
            blob = bucket.blob(cacheName)
            return blob and blob.exists()
        except:
            tls.error(f'GCP Error reading the bucket/cache: {gcpbucket} or {cacheName}')
        return 0
    
    def _gcpCacheNamingConvention(self, cacheName):
        prefix = 'gcp'
        if cacheName.startswith('gcp_'):
            finName = cacheName
        else:
            finName = f'{prefix}_{str(cacheName)}'
        return finName
        
if __name__ == '__main__':
    tls.setDebugging()
    
    g = GCPSupport()
    data = {'sample':'datx'} 
    cacheName = 'testing'
    #g.cacheWrite(data, cacheName)
    # data = g.cacheIsExist(cacheName)
    data = g.cacheRead(cacheName)
    tls.info(data) 
    
    tls.info('End')                