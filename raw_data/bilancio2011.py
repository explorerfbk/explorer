# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pyexcel as pe
import json
import os
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column , Integer, String, Float

from sqlalchemy.orm import sessionmaker

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

dbfile = "bilancio_fbk.db"
if os.path.exists(dbfile):
    os.remove(dbfile)
xlsxfile = "bilancio_consuntivo_2011.xlsx"

engine = create_engine("sqlite:///" + dbfile)
Base = declarative_base()
Session = sessionmaker(bind=engine)
class Budget(Base):
    __tablename__='bilancio'
    id=Column(Integer, primary_key=True)
    anno=Column(Integer)
    cdc=Column(String)
    class_conti=Column(String)
    conti=Column(String)
    consuntivo=Column(Float)

Base.metadata.create_all(engine) 
session = Session()
pe.save_as(file_name=xlsxfile, name_columns_by_row=0, dest_session=session, dest_table=Budget)

conn = sqlite3.connect(dbfile)
conn.row_factory = dict_factory
datasql = conn.cursor()

years_sql="select distinct(anno) from bilancio;"
years = []
data=datasql.execute(years_sql).fetchall()
for y in data:
    years.append(y['anno'])
year=years[0]
cdcs_sql='select distinct(cdc) from bilancio where anno=%s' % (str(year))
print cdcs_sql
data=datasql.execute(cdcs_sql).fetchall()
cdcs= []
for c in data:
    cdcs.append(c['cdc'])

jyears = {}
centri = []
for year in years:
    nomecentro = {}
    for cdc in cdcs:
        data = {}
        sql_incoming="select conti,consuntivo from bilancio where anno=%s and class_conti='Ricavi' and cdc='%s'" % (str(year),cdc)
        sql_incoming_adp="select conti,consuntivo from bilancio where anno=%s and class_conti='ADP' and cdc='%s'" % (str(year),cdc)
        sql_expenses="select conti,consuntivo from bilancio where anno=%s and class_conti='Costi' and cdc='%s'" % (str(year),cdc)
        incoming=datasql.execute(sql_incoming).fetchall()
        incoming_adp = datasql.execute(sql_incoming_adp).fetchall()
        expenses= datasql.execute(sql_expenses).fetchall()
        jexpenses = {}
        for i in incoming:
            v = abs((i['consuntivo']))*1000
            jexpenses[i['conti'].replace('ADP','accordo_di_programma').lower().replace(' ','_')]= v
        for i in incoming_adp:
            v = abs(i['consuntivo'])*1000
            jexpenses[i['conti'].replace('ADP','accordo_di_programma').lower().replace(' ','_')]= v 
        jincoming = {}
        for i in expenses:
            v = abs(i['consuntivo'])*1000
            jincoming[i['conti'].replace('ADP','accordo_di_programma').lower().replace(' ','_')]=v
        data['polo']='FBK'
        data['expenses']=jincoming
        data['incoming']=jexpenses
        nomecentro[cdc]=data
        #centri.append(nomecentro)
    jyears[str(year)] = nomecentro
json_data = json.dumps(jyears)
fname = "balance.json"
file = open(fname,"w") 
file.write(json_data) 
file.close() 
datasql.close()   
conn.close()  
