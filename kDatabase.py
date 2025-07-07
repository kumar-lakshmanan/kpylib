'''
@name: Simple KDATAbase
@author:  kayma
@createdon: 11-May-2025
@description:




'''
__created__ = "11-May-2025"
__updated__ = "2025-07-07"
__author__ = "kayma"

from typing import List, Tuple, Optional
from urllib.parse import quote, urljoin
import mysql.connector
import couchdb
import sqlite3
import requests
import json
import ast

import kTools

class SimpleCouchDB():

    def __init__(self, database="mydata", host="localhost", port="5984", dbuser="root", dbpass=None):
        self.tls = kTools.KTools()
        self.host = host
        self.port = port
        self.database = database
        self.dbuser = dbuser
        self.dbpass = dbpass if dbpass else self.tls.getSafeEnv("DB_PASS")
        if not self.dbpass: self.tls.errorAndExit("!!!CouchDB password error!!!")
        self.couchdb_url = f'http://{self.host}:{self.port}'

    def _coreGetService(self, uri):
        targetUrl = f"{self.couchdb_url}/{self.database}/{uri}"
        self.tls.debug(f"Calling... {targetUrl}")
        response = requests.get(
            targetUrl,
            headers={"Content-Type": "application/json","Referer": "http://localhost:5984"},
            auth=(self.dbuser, self.dbpass)
        )
        return response

    def _corePostService(self, uri, data):
        targetUrl = f"{self.couchdb_url}/{self.database}/{uri}"
        self.tls.debug(f"Calling... {targetUrl}")
        response = requests.post(
            targetUrl,
            headers={"Content-Type": "application/json","Referer": "http://localhost:5984"},
            auth=(self.dbuser, self.dbpass),
            data=json.dumps(data)
        )
        return response

    def _corePutService(self, uri, data):
        targetUrl = f"{self.couchdb_url}/{self.database}/{uri}"
        self.tls.debug(f"Calling... {targetUrl}")
        self.tls.debug(f"Updating... {data}")
        response = requests.put(
            targetUrl,
            headers={"Content-Type": "application/json","Referer": "http://localhost:5984"},
            auth=(self.dbuser, self.dbpass),
            data=json.dumps(data)
        )
        return response

    def _coreDeleteService(self, uri):
        targetUrl = f"{self.couchdb_url}/{self.database}/{uri}"
        self.tls.debug(f"Calling... {targetUrl}")
        response = requests.delete(
            targetUrl,
            headers={"Content-Type": "application/json","Referer": "http://localhost:5984"},
            auth=(self.dbuser, self.dbpass)
        )
        return response

    def createDocument(self, docDict):
        resp = self._corePostService('', docDict)
        if not resp.status_code == 201:
            self.tls.error(f"Unable to create new document : {resp} : {docDict}, Status: {resp.status_code} and {resp.text}")
        return resp

    def updateDocument(self, docid, updateDict):
        resp = self._corePutService(docid, updateDict)
        if not resp.status_code == 201:
            self.tls.error(f"Unable to update {docid}, Status: {resp.status_code} and {resp.text}")
            return False
        return True

    def deleteDocument(self, docid, revid):
        resp = self._coreDeleteService(f"{docid}?rev={revid}")
        if not resp.status_code == 200:
            self.tls.error(f"Unable to update {docid}, Status: {resp.status_code} and {resp.text}")
            return False
        return True

    def deleteDocuments(self, docAndRevIds=[]):
        bulkDocToDelete = []
        for each in docAndRevIds:
            bulkDocToDelete.append({'_id': each[0], '_rev': each[1], '_deleted': True})
        self.tls.debug("Bulk delete")
        return self.bulkProcess(bulkDocToDelete)

    def getDocumentById(self, docid):
        doc = {}
        resp = self._coreGetService(docid)
        if not resp.status_code == 200:
            self.tls.error(f"Unable to get doc : {docid}, Status: {resp.status_code} and {resp.text}")
        else:
            doc = resp.json()
        return doc

    def getAllDocuments(self):
        docs = []
        resp = self._coreGetService('_all_docs?include_docs=true')
        if not resp.status_code == 200:
            self.tls.error(f"Unable to get docs : {resp}, Status: {resp.status_code} and {resp.text}")
        else:
            docs = [row['doc'] for row in resp.json()['rows'] if 'doc' in row]
        return docs

    def qryToDocs(self, qry):
        response = self._corePostService("_find", qry)
        docs = []
        if response.status_code == 200:
            docs = response.json()["docs"]
        else:
            print("Query failed:", response.status_code, response.text)
        self.tls.debug(f"Fetched {len(docs)} document(s).")
        return docs

    def docsToPrint(self, docs):
        ids = []
        for eachDoc in docs:
            print(eachDoc)
        return ids

    def docsToIds(self, docs):
        ids = []
        for eachDoc in docs:
            ids.append((eachDoc['_id'], eachDoc['_rev']))
        return ids

    def docsToFile(self, docs, fileName, includeIdRev = 0):
        data = []
        for eachDoc in docs:
            if not includeIdRev:
                eachDoc.pop('_id')
                eachDoc.pop('_rev')
                data.append(str(eachDoc))
            else:
                data.append(str(eachDoc))
        dataStr = '\n'.join(data)
        self.tls.writeFileContent(fileName, dataStr)
        self.tls.debug(f"Docs stored in file {fileName}")

    def bulkProcess(self, updatedListOfDocsWithId=[]):
        updates = {"docs" : updatedListOfDocsWithId}
        resp = self._corePostService("_bulk_docs", updates)
        if not resp.status_code == 201:
            self.tls.error(f"Unable to bulk update, Status: {resp.status_code} and {resp.text}")
            return False
        self.tls.debug("Bulk update compeletd!")
        return True

    def fileToBulkUpdate(self, fileName):
        data = self.tls.getFileContent(fileName)
        rows = data.split("\n")
        docs = []
        for each in rows:
            print(each)
            docs.append(ast.literal_eval(each))
        self.bulkProcess(docs)

class SimpleMySql:

    def __init__(self,dbuser="root",dbpass="pas"):
        self.conn = None
        self.dbuser = dbuser
        self.dbpass = dbpass

    def connect(self):
        if self.conn is None:
            self.conn = mysql.connector.connect(
                            host="127.0.0.1",
                            port=3306,
                            user=self.dbuser,
                            password=self.dbpass)
        return self.conn

    def execute_query(self, query: str, params: Tuple = ()) -> None:
        """Execute INSERT/UPDATE/DELETE queries."""
        self.conn = self.connect()
        self.cursor = self.conn.cursor()
        self.cursor.execute(query, params)

    def commit_all(self):
        if self.conn: self.conn.commit()

    def fetch_query(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """Execute SELECT query and return results as list of tuples."""
        self.conn = self.connect()
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

class SimpleSQLite:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
        return self.conn

    def execute_query(self, query: str, params: Tuple = ()) -> None:
        """Execute INSERT/UPDATE/DELETE queries."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()

    def fetch_query(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """Execute SELECT query and return results as list of tuples."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def list_tables(self) -> List[str]:
        """Return a list of table names in the database."""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        results = self.fetch_query(query)
        return [row[0] for row in results]

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

if __name__ == '__main__':
    tls = kTools.KTools()
    tls.turnOnDebugLogs(1)

    # dbname = ""
    # db = SimpleSQLite("test.db")
    #
    # # Add or update
    # db.execute_query("INSERT INTO users (name, age) VALUES (?, ?)", ("Alice", 30))
    #
    # # Fetch
    # results = db.fetch_query("SELECT * FROM users WHERE age > ?", (25,))
    # print(results)  # List of tuples
    #
    # # List tables
    # tables = db.list_tables()
    # print(tables)
    #
    # # Close when done
    # db.close()

    cb = SimpleCouchDB()
    #Qry - Fetch - Print - Copy To File - Do Manual Edit - Re Update

    # qry = {
    #         "selector":
    #                 {
    #                     "status": "open"
    #                 }
    #       }
    # docs = cb.qryToDocs(qry)
    # cb.docsToPrint(docs)
    # cb.docsToFile(docs, "data_collect.txt", 1)

    cb.fileToBulkUpdate("data_collect.txt")


# cb.updateDocument('02625d7542b35cd59641ac400f000f1b', {'winDate': '20250624044917', 'winDuration': 0, 'status': 'pass'})

# [04:49:17AM]D:[SimpleCouchDB-_corePutService] Calling... http://localhost:5984/mydata/02625d7542b35cd59641ac400f000f1b
# [04:49:17AM]D:[SimpleCouchDB-_corePutService] Updating... {'winDate': '20250624044917', 'winDuration': 0, 'status': 'pass'}
# [04:49:19AM]E:[SimpleCouchDB-updateDocument] Unable to update 02625d7542b35cd59641ac400f000f1b, Status: 409 and {"error":"conflict","reason":"Document update conflict."}



    #newDoc = {'date': 20250522061648, 'coin': 'KUMAR', 'coinslug': 'ondo-finance', 'price': 0.982861048955422, 'pricechangepercent': 4.41548545, 'binanceTradeVolPercent': 0.0, 'trend7d': -14, 'trendttl': 19, 'rank': 35, 'cmcWatchers': 349000, 'cmcStarRating': 4, 'status': 'pass', 'winDate': 20250522155833, 'winDuration': 0, 'isMostVisited': 1, 'isMostTrending': 1, 'isSentimental': 1, 'bullvotes': 268, 'bearvotes': 57, 'bullpercent': 83, 'bearpercent': 18, 'ttlvotes': 548, 'trendpercent': -6.3, 'sentimenttype': 'bearish'}
    #resp = cb.createDocument(newDoc)
    # resp = cb.getAllDocuments()
    # for each in resp:
    #     print(each)

    # qry = {"selector":{"trendPercent": {"$exists":True}}}
    # qry = {"selector":{"coin": "KUMAR"}}
    # docs = cb.qryToDocs(qry)
    # cb.docsToPrint(docs)
    # cb.docsToFile(docs, "test5.txt", 1)

    # docs = cb.getAllDocuments()
    # ids = cb.docsToIds(docs)
    # cb.deleteDocuments(ids)

    #cb.fileToBulkUpdate("test5.txt")

    print("done")
