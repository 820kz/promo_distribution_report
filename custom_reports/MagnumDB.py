# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 14:30:46 2022

@author: Babenko
"""

import string
import psycopg2, pandas
import psycopg2.extras as extras
import ast


    #common db settings
def getConnectionString(target:str, db_login:str, db_pass:str, db_ip:str, db_port:str, db_service:str) -> str:
    if target=='':
        #we are to use specific DB adress
        res = """
            host='%s'
            port=%s
            sslmode=prefer 
            dbname=%s
            user=%s
            password=%s
            target_session_attrs=read-write
        """ %(db_ip, db_port, db_service, db_login, db_pass)
    elif target == 'DWH':
        res = """
            host='172.16.10.22'
            port=5432
            sslmode=prefer 
            dbname=adb
            user=%s
            password=%s
            target_session_attrs=read-write
        """ %(db_login, db_pass)
    elif target == 'PROMO_TABEL':
        res = """
            host='172.16.11.178'
            port=5432
            sslmode=prefer 
            dbname=portalDB
            user=%s
            password=%s
            target_session_attrs=read-write
        """ %(db_login, db_pass)
    else:
        raise RuntimeError('Unknown DB referensed: %s' %(target))
    return res
class DBConnection:
    
    def __init__(self, db_login:str, db_pass:str, target:str='',db_ip:str='', db_port:str='', db_service:str=''):
        self.db = ''
        self.cr = ''
        self.isConnected = False
        self.dberror=''
        self.connection_string = getConnectionString(target,db_login,db_pass,db_ip, db_port, db_service)
        
        self.connect()
        
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        
    def close(self):
        self.cr.close()
        self.db.close() 
        
    def connect(self):
        try:    
            self.db = psycopg2.connect(self.connection_string)
            self.db.set_session(autocommit=True)
            self.cr = self.db.cursor()
            self.isConnected = True
            return True
        except psycopg2.DatabaseError as pg:
            print(pg)
            return False
        
    def select(self,sql):
        self.cr.execute(sql)
        res = pandas.DataFrame(self.cr.fetchall(), columns = [x[0] for x in self.cr.description])
        #res.columns = [x[0] for x in self.cr.description]
        return res
    
    def execute(self,sql):
        self.cr.execute(sql)
        return True
    
    def insertManyOld(self, table_name: str, data: pandas.DataFrame):
        #self.cr.executemany(sql,data.values.tolist())
        self.cr.executemany('insert into '+table_name+' values (%s,%s,%s,%s,%s,%s)',data.values.tolist())
        return True
    
    def insertMany(self, table_name: str, data: pandas.DataFrame):
        extras.execute_values(self.cr, 'insert into '+table_name+' values %s', data.values.tolist(),page_size=1000)
        return True

    def test(self):
        try:
            self.cr.execute("select 2+2")
            if self.cr.fetchall()[0][0] == 4:
                return True
            else: 
                return False
        except psycopg2.DatabaseError as pg:
            self.dberror=pg
            return False
