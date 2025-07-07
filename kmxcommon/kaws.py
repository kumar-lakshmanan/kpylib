'''
Created on 13-Dec-2022

All AWS Call

@author: kayma
'''
import boto3  # pip install boto3
import pickle

from kmxcommon import xtools
from awsbuild.kmxcommon.kaws import bucketFileName
tls = xtools.getGlobalTools()

class KMXAWS(object):
    '''
    classdocs
    '''

    def __init__(self, region = None, access_key_id = None, secret_access_key = None):
        '''
        Constructor        
        '''
        self.tls = tls
        self.region = region if region else self.tls.cfg.aws_region
        self.access_key_id = access_key_id if access_key_id else self.tls.cfg.aws_access_key_id
        self.secret_access_key = secret_access_key if secret_access_key else self.tls.cfg.aws_secret_access_key
        
        self.s3 = self._getS3()
        self.buckets = {}
        self.bucketFiles = {}
        
        self.bucketName = None
        self._cachePrefixName = 'aws'
        self.tls.debug(f'Initialized')
            
    def _getS3(self):
        self.s3 = boto3.resource(
            service_name='s3',
            region_name=self.region,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key
        )
        return self.s3

    def getBuckets(self):
        self.buckets = {}
        if self.s3:
            for bucket in self.s3.buckets.all():
                #print(bucket.name)
                self.buckets[bucket.name] = bucket
        else:
            self.tls.error('S3 Not initalized')
        return self.buckets
    
    def getBucketFiles(self, bucket=None):
        lst = {}
        if not bucket:
            self.tls.error('Invalid Bucket ' + str(bucket))
        
        for each in bucket.objects.all():
            lst[each.key] = each
            
        self.bucketFiles[bucket.name] = lst
        return lst
    
    def isBucketExist(self, bucketName=None):
        if not self.buckets: self.getBuckets()    
        bucket = self.tls.getDictDefault(self.buckets, bucketName, None)
        return True if bucket else False

    def isBucketFileExist(self, bucketFileName=None,  bucketName=None):
        ret = False
        if not self.buckets: self.getBuckets()    
        bucket = self.tls.getDictDefault(self.buckets, bucketName, None)
        if bucket:
            files = self.getBucketFiles(bucket)
            found = False
            for eachFile in files:
                if eachFile == bucketFileName:
                    found = True
                    break
            ret = found
        else:
            ret = False
        return ret

    def readBucketFile(self, bucketFile=None, type_ = 'b'):
        if not bucketFile:
            self.tls.error('Invalid Bucket ' + str(bucketFile))
        data = bucketFile.get()['Body'].read()
        if type_ == 'b': data = pickle.loads(data) 
        return data

    def createNewBucketFile(self, bucketFileName=None, content='', type_ = 'b'):
        ret = False
        content = str(content)
        content = content.encode('utf-8')
        if not bucketFileName:
            self.tls.error('Invalid BucketFileName ' + str(bucketFileName))
        if type_ == 'b': content = pickle.dumps(content) #pickled binary content
        self.tls.fullInfo('Creating new file... ' + bucketFileName)
        self.s3.Bucket(self.bucketName).put_object(Key=bucketFileName, Body=content)
        ret = True
        return ret
        
    def updateBucketFile(self, bucketFile=None, content='', type_ = 'b'):
        ret = False
        content = str(content)
        content = content.encode('utf-8')
        if not bucketFile:
            self.tls.error('Invalid BucketFile ' + str(bucketFile))
        if type_ == 'b': content = pickle.dumps(content) #pickled binary content
        self.tls.fullInfo('Updating file... ' + bucketFileName)
        bucketFile.put(Body=content)
        ret = True
        return ret
    
    def isFileExist(self,fileName=None, bucketName=None):
        return self.isBucketFileExist(fileName, bucketName)
    
    def getFileContent(self, fileName=None, bucketName=None):
        data = ''
        try:
            if not bucketName: bucketName = self.bucketName
            forceReadOnline = tls.getGlobalSwitch(self.tls.cfg.gs_forceReadOnline, 0)
            cacheName = self._cacheNamingConvention(fileName)
            
            #1. Read from Cache Memory
            if tls.isGlobalVarExist(cacheName) and not forceReadOnline:
                data = tls.getGlobalVar(cacheName)
                tls.info(f'Read {cacheName} from cache memory.')    
        
            #2. Read from Cache File
            elif tls.isLocalDev() and tls.isCacheAvailable(cacheName, dated=1) and not forceReadOnline: 
                data = tls.getCache(cacheName, None, dated=1)
                tls.info(f'Read {cacheName} from cache file.')
                
            #3. Read from online
            else:
                if not self.buckets: self.getBuckets()    
                bucket = self.tls.getDictDefault(self.buckets, bucketName, None)
                if bucket:
                    files = self.getBucketFiles(bucket)
                    found = 0
                    for eachFile in files:
                        if eachFile == fileName:
                            bucketFile = files[eachFile]
                            data = self.readBucketFile(bucketFile)
                            found = 1
                            tls.info(f'Read {cacheName} from online.')
                            if tls.isLocalDev(): tls.setCache(cacheName, data, dated=1)
                            tls.setGlobalVar(cacheName, data)                                                        
                    if not found:
                        tls.error(f'Bucket {bucketName} missing the given file {fileName}!')
                else:
                    tls.error(f'Bucket {bucketName} not found!')
            
        except Exception as e:
            tls.error(f'Error: Reading {fileName} - {e}')
            return data
                    
        return data
    
    def setFileContent(self, data='', fileName=None, bucketName=None):
        ret = True
        if tls.getGlobalSwitch(self.tls.cfg.gs_writeProtectOnline, 1):
            tls.info(f'Online Write Protected. Skipping Write on {fileName}') 
            return True
        
        if not bucketName: bucketName = self.bucketName
        
        cacheName = self._cacheNamingConvention(fileName)
        try:
            #Write to memory cache
            tls.setGlobalVar(cacheName, data)
            
            #Write to file cache
            if tls.isLocalDev(): tls.setCache(cacheName, data, dated=1)
            
            #Write to online
            if not self.buckets: self.getBuckets()
            bucket = self.tls.getDictDefault(self.buckets, bucketName, None)
            if bucket:
                
                if self.isBucketFileExist(fileName):
                    files = self.getBucketFiles(bucket)
                    found = 0
                    for eachFile in files:
                        if eachFile == fileName:
                            bucketFile = files[eachFile]
                            self.updateBucketFile(bucketFile, content)
                            found = 1
                            tls.info(f'File updated: {fileName}')
                    if not found:
                        tls.error(f'Bucket {bucketName} missing the given file {fileName}!')
                else:
                    self.createNewBucketFile(fileName, content)
                    
            else:
                tls.error(f'Bucket {bucketName} not found!')
        except Exception as e:
            tls.error(f'Error: writing the bucket/cache: {bucketName} or {fileName} - {e}')
            ret = False

        return ret            
 
    def _cacheNamingConvention(self, cacheName):
        if cacheName.startswith(self.tls.cfg.aws_cachePrefixName):
            finName = cacheName
        else:
            finName = f'{self._cachePrefixName}_{str(cacheName)}'
        return finName
        
    
if __name__ == '__main__':
    tls.setDebugging()
    obj = KMXAWS()
    bucketName = 'kmxbucket'
    bucketFileName = 'requirements.txt'
    
    # bkts = obj.getBuckets()
    # bkt = bkts['kmxbucket']
    # bktFiles = obj.getBucketFiles(bkt)
    # bktFileData = obj.readBucketFile(bktFiles['requirements.txt'])
    
    bktFileData = obj.getFileContent(bucketName, bucketFileName)
    print(str(bktFileData))
    
    content = 'kumaresn first \n\n more new fline'
    obj.setFileContent(bucketName, bucketFileName, content)
    
    

