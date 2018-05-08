# -*- coding: utf-8 -*-
"""
Created on Tue Apr 07 15:11:49 2014
@author: Maurizio Napolitano <napo@fbk.eu>
The MIT License (MIT)
Copyright (c) 2016 Fondazione Bruno Kessler http://fbk.eu
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

"""
{
    "2016": {
        "ICT": {
            "incomes": {
                "Commesse con privati": 22000,
                "Altri ricavi": 3500
            },
            "expenses": {
                "Personale": 17200,
                "Altre spese": 8200
            }
        },
        "CMM": {
            "incomes": {
                "Commesse con privati": 11400,
                "Altri ricavi": 5000
            },
            "expenses": {
                "Personale": 12000,
                "Phd": 3600,
                "Altre spese": 1600
            }
        }
    },
 """

import json
import sqlite3

ANNO="`Anno`"
POLO="`Cdc.Polo`"
CENTRO="`CdC.Centro`"
CDCRLHII="`CdC.RL/HII`"
CONTI="`Tabelle Conti`"
CONSUNTIVO="`Consuntivo`"
UMANISTICO = 'PSUS - POLO UMANISTICO'
SCIENTIFICO = 'PST - POLO SCIENTIFICO'
CASSR = 'CASSR'
PARTECIPATE='PARTECIPATE IN ADP'
FUNZIONAMENTO='FUNZIONAMENTO'
PROGSPECIALI = 'PROGETTI SPECIALI-ESPLORATIVI'
poli = [UMANISTICO,SCIENTIFICO,CASSR, PARTECIPATE,FUNZIONAMENTO,PROGSPECIALI]
LUMANISTICO = 'polo umanistico'
LSCIENTIFICO = 'polo scientifico'
LCASSR='amministrazione e supporto alla ricerca'
LPROGSPECIALI = 'progetti esplorativi'
LPARTECIPATE = 'partecipate in accordo di programma'
LFUNZIONAMENTO = 'funzionamento'

def changeLabel(s):
    r = s
    labels = {}
    labels[UMANISTICO]= LUMANISTICO
    labels[SCIENTIFICO]=  LSCIENTIFICO
    labels[CASSR] = LCASSR
    labels[PROGSPECIALI] = LPROGSPECIALI
    labels[PARTECIPATE] = LPARTECIPATE
    labels[FUNZIONAMENTO] = LFUNZIONAMENTO
    for label in labels.keys():
        if (s == label):
            r = labels[label]
            break
    return r



def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn = sqlite3.connect('dati_bilancio.sqlite')
conn.row_factory = dict_factory
datasql = conn.cursor()
anno = ""

sql_anni = """
select distinct(Anno) as anno from dati_bilancio;
"""
budget={}
years = datasql.execute(sql_anni)
for year in years: 
    anno = year['anno']
    sql_centri = """
        select distinct(replace(lower(`CdC.Centro`),'adp','accordo di programma')) as centro, lower(`Cdc.Polo`) as polo from dati_bilancio where Anno = %s;
    """ % (anno)
    bodycentri = {}   
    centri = datasql.execute(sql_centri).fetchall()
    for center in centri:
        bodycenter = {}
        centro = center['centro']
        sql_budget_centro_uscite = """
        SELECT lower(`Cdc.Polo`) AS 'polo',
               lower(`CdC.Centro`) AS 'centro',
               replace(lower(`Tabelle Conti`),'adp','accordo di programma') AS 'voce',
               dati_bilancio.`Consuntivo` AS 'uscite'
        FROM dati_bilancio
        GROUP BY polo,centro,uscite
        HAVING sum(dati_bilancio.`Consuntivo`)  > 0 and anno = %s and centro = '%s'
    
        """ % (anno, centro)
        uscite_centro = datasql.execute(sql_budget_centro_uscite).fetchall()
        expenses = {}
        for uscite in uscite_centro:
            expenses[uscite['voce'].replace(" ","_")] = int(uscite['uscite'])
        bodycenter['expenses'] = expenses 
        
        sql_budget_centro_entrate = """
        SELECT lower(`Cdc.Polo`) AS 'polo',
               lower(`CdC.Centro`) AS 'centro',
               replace(lower(`Tabelle Conti`),'adp','accordo di programma') AS 'voce',
               abs(dati_bilancio.`Consuntivo`) AS 'entrate'
        FROM dati_bilancio
        GROUP BY polo,centro,entrate
        HAVING sum(dati_bilancio.`Consuntivo`) <= 0 and anno = %s and centro = '%s'
    
        """ % (anno, centro)
        entrate_centro = datasql.execute(sql_budget_centro_entrate).fetchall()
        incoming = {}
        for entrate in entrate_centro:
            incoming[entrate['voce'].replace(" ","_")] = int(entrate['entrate'])
        bodycenter['incoming'] = incoming 
        bodycenter['polo'] = center['polo']
        bodycentri[centro]=bodycenter 
    budget[anno]= bodycentri
json_data = json.dumps(budget)
fname = "budget_consuntivo.json"
file = open(fname,"w") 
file.write(json_data) 
file.close() 
