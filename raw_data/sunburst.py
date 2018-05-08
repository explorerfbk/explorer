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
import json
import sqlite3
RICERCA="RICERCA"
SUPPORTO_RICERCA="SUPPORTO RICERCA"
AMMINISTRAZIONE="AMMINISTRAZIONE"
aree=[RICERCA,SUPPORTO_RICERCA,AMMINISTRAZIONE]
COCO= 'Co.co. (jobs act)'
DETERMINATO = 'Dipendente T. Determ.'
INDETERMINATO = 'Dipendente T. Indeterm.'
BORSAPHD = 'Dottorando Borsa'
contratti = [DETERMINATO,INDETERMINATO,BORSAPHD,COCO]
UMANISTICO = 'PSUS - POLO UMANISTICO'
SCIENTIFICO = 'PST - POLO SCIENTIFICO'
CASSR = 'CASSR'
PROGSPECIALI = 'PROGETTI SPECIALI-ESPLORATIVI'
ND = 'N/D'
SERVIZIOAMMINISTRAZIONE="SERVIZIO AMMINISTRAZIONE"
poli = [SCIENTIFICO,UMANISTICO,CASSR,PROGSPECIALI,ND,SERVIZIOAMMINISTRAZIONE]
LUMANISTICO = 'polo umanistico'
LSCIENTIFICO = 'polo scientifico'
LCASSR='amministrazione e supporto alla ricerca'
LPROGSPECIALI = 'progetti esplorativi'
LND='extra'
LCOCO='collaborazione coordinata (jobs act)'
LDETERMINATO='tempo determinato'
LBORSAPHD = 'borsa di dottorato'
LINDETERMINATO = 'tempo indeterminato'
LSUPPORTO_RICERCA='supporto alla ricerca'
LRICERCA='ricerca'
LAMMINISTRAZIONE='amministrazione'
LSERVIZIOAMMINISTRAZIONE="servizio amministrazione"
M="Maschio"
F="Femmina"
LM = "uomini"
LF = "donne"
genere=[M,F]
def changeLabel(s):
    r = s
    labels = {}
    labels[UMANISTICO]= LUMANISTICO
    labels[SCIENTIFICO]=  LSCIENTIFICO
    labels[CASSR] = LCASSR
    labels[PROGSPECIALI] = LPROGSPECIALI
    labels[ND] = LND
    labels[COCO] = LCOCO
    labels[DETERMINATO] = LDETERMINATO
    labels[BORSAPHD] = LBORSAPHD
    labels[INDETERMINATO] = LINDETERMINATO
    labels[SUPPORTO_RICERCA]=LSUPPORTO_RICERCA
    labels[RICERCA]=LRICERCA
    labels[AMMINISTRAZIONE]=LAMMINISTRAZIONE
    labels[SERVIZIOAMMINISTRAZIONE]=LSERVIZIOAMMINISTRAZIONE
    labels[M]=LM
    labels[F]=LF
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


conn = sqlite3.connect('people_fbk.sqlite')
conn.row_factory = dict_factory
datasql = conn.cursor()


def getJsonData(anno):

    sql_eta_totale="""
    select sum(`MeasuresConteggio Risorse`) as totale, round(avg(`Eta_Media_Column`)) as etamedia 
    from statistica_personale WHERE anno=%s;
    """ % (anno)
    
    sql_eta_totale_donne="""
    select sum(`MeasuresConteggio Risorse`)  as totale, round(avg(`Eta_Media_Column`)) as etamedia 
    from statistica_personale WHERE `Genere`= 'Femmina' and anno=%s;
    """  % (anno)
    
    sql_eta_totale_uomini="""
    select sum(`MeasuresConteggio Risorse`)  as totale, round(avg(`Eta_Media_Column`)) as etamedia 
    from statistica_personale WHERE `Genere`= 'Maschio' and anno=%s;
    """  % (anno)
    
    sql_area_eta_totale="""
    select sum(`MeasuresConteggio Risorse`) as totale,  round(avg(`Eta_Media_Column`)) as etamedia  
    from statistica_personale where anno=%s and Area='NOMEAREA'
    """ % (anno)
    
    sql_area_eta_totale_donne="""
    select sum(`MeasuresConteggio Risorse`) as totale, round(avg(`Eta_Media_Column`)) as etamedia
    from statistica_personale where anno=%s and Area='NOMEAREA' and Genere='Femmina'
    """ % (anno)
    
    sql_area_eta_totale_uomini="""
    select sum(`MeasuresConteggio Risorse`) as totale, round(avg(`Eta_Media_Column`)) as etamedia
    from statistica_personale where anno=%s and Area='NOMEAREA' and Genere='Maschio'
    """ % (anno)
    
    sql_contratto_eta_totale="""
    select sum(`MeasuresConteggio Risorse`) as totale,  round(avg(`Eta_Media_Column`)) as etamedia  
    from statistica_personale where anno=%s and `Tipo Rapporto`='NOMECONTRATTO'
    """ % (anno)
    
    sql_contratto_eta_totale_donne="""
    select sum(`MeasuresConteggio Risorse`) as totale, round(avg(`Eta_Media_Column`)) as etamedia
    from statistica_personale where anno=%s and `Tipo Rapporto`='NOMECONTRATTO' and Genere='Femmina'
    """ % (anno)
    
    sql_contratto_eta_totale_uomini="""
    select sum(`MeasuresConteggio Risorse`) as totale, round(avg(`Eta_Media_Column`)) as etamedia
    from statistica_personale where anno=%s and `Tipo Rapporto`='NOMECONTRATTO' and Genere='Maschio'
    """ % (anno)
    
    sql_lista_poli="""
    select distinct(Polo) as polo from statistica_personale where anno = %s
    """ % (anno)
    
    sql_polo_totale_eta = """
    select sum(`MeasuresConteggio Risorse`) as totale, round(avg(`Eta_Media_Column`)) as etamedia from statistica_personale where anno = %s and Polo='NOMEPOLO'
    """ % (anno)
    
    sql_polo_totale_eta_uomini = """
    select sum(`MeasuresConteggio Risorse`) as totale, round(avg(`Eta_Media_Column`)) as etamedia from statistica_personale where anno = %s and Polo='NOMEPOLO' and Genere='Maschio'
    """ % (anno)
    
    sql_polo_totale_eta_donne = """
    select sum(`MeasuresConteggio Risorse`) as totale, round(avg(`Eta_Media_Column`)) as etamedia from statistica_personale where anno = %s and Polo='NOMEPOLO' and Genere='Femmina'
    """ % (anno)
    
    sql_polo_area_eta_totale = """
    select sum(`MeasuresConteggio Risorse`) as totale, round(avg(`Eta_Media_Column`)) as etamedia from statistica_personale where anno = %s and Polo='NOMEPOLO' 
    and `Area`='NOMEAREA'
    """ % (anno)
    
    sql_polo_area_eta_totale_donne = """
    select sum(`MeasuresConteggio Risorse`) as totale, round(avg(`Eta_Media_Column`)) as etamedia from statistica_personale where anno = %s and Polo='NOMEPOLO' and Genere='Femmina'
     and `Area`='NOMEAREA' """ % (anno)
    
    sql_polo_contratto_eta_totale = """
    select sum(`MeasuresConteggio Risorse`) as totale, round(avg(`Eta_Media_Column`)) as etamedia from statistica_personale where anno = %s and Polo='NOMEPOLO'
     and `Tipo Rapporto`='NOMECONTRATTO' """ % (anno)
    
    sql_polo_contratto_eta_totale_uomini = """
    select sum(`MeasuresConteggio Risorse`) as totale, round(avg(`Eta_Media_Column`)) as etamedia from statistica_personale where anno = %s and Polo='NOMEPOLO' and Genere='Maschio'
     and `Tipo Rapporto`='NOMECONTRATTO' """ % (anno)
    
    sql_polo_contratto_eta_totale_donne = """
    select sum(`MeasuresConteggio Risorse`) as totale, round(avg(`Eta_Media_Column`)) as etamedia from statistica_personale where anno = %s and Polo='NOMEPOLO' and Genere='Femmina'
     and `Tipo Rapporto`='NOMECONTRATTO' """ % (anno)
    
    sql_lista_centri_polo="""
    select distinct Centro as centro from statistica_personale where anno = %s and Polo='NOMEPOLO'
    """ % (anno)
    
    sql_centro_totale_eta="""
    select sum(`MeasuresConteggio Risorse`) as totale, round(avg(`Eta_Media_Column`)) as etamedia from statistica_personale where anno = %s and Centro='NOMECENTRO' and Polo='NOMEPOLO'
    """ % (anno)
    
    sql_centro_totale_eta_uomini = """
    select sum(`MeasuresConteggio Risorse`) as totale, round(avg(`Eta_Media_Column`)) as etamedia from statistica_personale where anno = %s and Centro='NOMECENTRO'  and Polo='NOMEPOLO' and Genere='Maschio'
    """ % (anno)
    
    sql_centro_totale_eta_donne = """
    select sum(`MeasuresConteggio Risorse`) as totale, round(avg(`Eta_Media_Column`)) as etamedia from statistica_personale where anno = %s and Centro='NOMECENTRO'  and Polo='NOMEPOLO' and Genere='Femmina'
    """ % (anno)

    sql_centro_area_eta_totale = """
    select sum(`MeasuresConteggio Risorse`) as totale, round(avg(`Eta_Media_Column`)) as etamedia from statistica_personale where anno = %s and Centro='NOMECENTRO'  and Polo='NOMEPOLO'
    and `Area`='NOMEAREA'
    """ % (anno)

    sql_centro_area_eta_totale_donne = """
    select sum(`MeasuresConteggio Risorse`) as totale, round(avg(`Eta_Media_Column`)) as etamedia from statistica_personale where anno = %s and Centro='NOMECENTRO'   and Polo='NOMEPOLO' and Genere='Femmina'
     and `Area`='NOMEAREA' """ % (anno)
    
    sql_centro_contratto_eta_totale = """
    select sum(`MeasuresConteggio Risorse`) as totale, round(avg(`Eta_Media_Column`)) as etamedia from statistica_personale where anno = %s and Centro='NOMECENTRO'  and Polo='NOMEPOLO'
     and `Tipo Rapporto`='NOMECONTRATTO' """ % (anno)
    
    sql_centro_contratto_eta_totale_uomini = """
    select sum(`MeasuresConteggio Risorse`) as totale, round(avg(`Eta_Media_Column`)) as etamedia from statistica_personale where anno = %s and Centro='NOMECENTRO'  and Genere='Maschio'  and Polo='NOMEPOLO'
     and `Tipo Rapporto`='NOMECONTRATTO' """ % (anno)
    
    sql_centro_contratto_eta_totale_donne = """
    select sum(`MeasuresConteggio Risorse`) as totale, round(avg(`Eta_Media_Column`)) as etamedia from statistica_personale where anno = %s and Centro='NOMECENTRO'  and Genere='Femmina'  and Polo='NOMEPOLO'
     and `Tipo Rapporto`='NOMECONTRATTO' """ % (anno)

    sql_centro_contratto_area_eta_totale = """
    select sum(`MeasuresConteggio Risorse`) as totale, round(avg(`Eta_Media_Column`)) as etamedia from statistica_personale where anno = %s and Centro='NOMECENTRO'  and Polo='NOMEPOLO'
     and `Tipo Rapporto`='NOMECONTRATTO' and `Area`='NOMEAREA'""" % (anno)
    
    sql_centro_contratto_area_eta_totale_uomini = """
    select sum(`MeasuresConteggio Risorse`) as totale, round(avg(`Eta_Media_Column`)) as etamedia from statistica_personale where anno = %s and Centro='NOMECENTRO'  and Genere='Maschio'  and Polo='NOMEPOLO'
     and `Tipo Rapporto`='NOMECONTRATTO'  and `Area`='NOMEAREA'""" % (anno)
    
    sql_centro_contratto_area_eta_totale_donne = """
    select sum(`MeasuresConteggio Risorse`) as totale, round(avg(`Eta_Media_Column`)) as etamedia from statistica_personale where anno = %s and Centro='NOMECENTRO'  and Genere='Femmina'  and Polo='NOMEPOLO'
     and `Tipo Rapporto`='NOMECONTRATTO'  and `Area`='NOMEAREA'""" % (anno)

    
    header={}
    header["name"] = "FBK"
    header["anno"] = anno
    datatotale = datasql.execute(sql_eta_totale).fetchall()[0]
    datadonne = datasql.execute(sql_eta_totale_donne).fetchall()[0]
    datauomini = datasql.execute(sql_eta_totale_uomini).fetchall()[0]
    header["totale"]=datatotale['totale']
    header['totaledonne']=datadonne['totale']
    header['totaleuomini']=datauomini['totale']
    header['etamedia_donne']=int(datadonne['etamedia'])
    header['etamedia_uomini']=int(datauomini['etamedia'])
    header["etamedia"]=int(datauomini['etamedia'])
    bodyarea={}  
    for area in aree:
        datatotale = datasql.execute(sql_area_eta_totale.replace('NOMEAREA',area)).fetchall()[0]
        datadonne = datasql.execute(sql_area_eta_totale_donne.replace('NOMEAREA',area)).fetchall()[0]
        datauomini = datasql.execute(sql_area_eta_totale_uomini.replace('NOMEAREA',area)).fetchall()[0]
        label = changeLabel(area).replace(" ","_").replace(")","").replace("(","")
        values = {}
        values['totale'] = datatotale['totale']
        values['totale_donne']=  datadonne['totale']
        values['totale_uomini']=  datauomini['totale']
        values['etamedia_uomini']=  int(datauomini['etamedia'])
        values['etamedia_donne']=  int(datadonne['etamedia'])
        values['etamedia']=  int(datatotale['etamedia'])
        bodyarea[label]=values
    header['aree']=bodyarea
    bodycontratti = {}
    for contratto in contratti:
        datatotale = datasql.execute(sql_contratto_eta_totale.replace('NOMECONTRATTO',contratto)).fetchall()[0]
        datadonne = datasql.execute(sql_contratto_eta_totale_donne.replace('NOMECONTRATTO',contratto)).fetchall()[0]
        datauomini = datasql.execute(sql_contratto_eta_totale_uomini.replace('NOMECONTRATTO',contratto)).fetchall()[0]
        label = changeLabel(contratto).replace(" ","_").replace(")","").replace("(","")
        values = {}
        values['totale'] = datatotale['totale']
        values['totale_donne']=  datadonne['totale']
        values['totale_uomini']=  datauomini['totale']
        values['etamedia_uomini']=  int(datauomini['etamedia'])
        values['etamedia_donne']=  int(datadonne['etamedia'])
        values['etamedia']=  int(datatotale['etamedia'])
        bodycontratti[label]=values
    header['contratti']=bodycontratti
    listapoli = datasql.execute(sql_lista_poli).fetchall()
    bodypoli = []
    
    for polo in listapoli:
        nomepolo = polo['polo']
        bodypolo = {}
        datatotale = datasql.execute(sql_polo_totale_eta.replace('NOMEPOLO',nomepolo)).fetchall()[0]
        datadonne = datasql.execute(sql_polo_totale_eta_donne.replace('NOMEPOLO',nomepolo)).fetchall()[0]
        datauomini = datasql.execute(sql_polo_totale_eta_uomini.replace('NOMEPOLO',nomepolo)).fetchall()[0]
        label = changeLabel(area).replace(" ","_").replace(")","").replace("(","")
        bodypolo['totale_donne']=  datadonne['totale']
        bodypolo['totale_uomini']=  datauomini['totale']
        bodypolo['etamedia_uomini']=  int(datauomini['etamedia'])
        bodypolo['etamedia_donne']=  int(datadonne['etamedia'])
        bodypolo['etamedia']=  int(datatotale['etamedia'])
        bodypolo['name']=changeLabel(nomepolo)
        bodypolo['totale']= datatotale['totale']
        bodyarea={}        
        for area in aree:            
            datatotale = datasql.execute(sql_polo_area_eta_totale.replace('NOMEPOLO',nomepolo).replace('NOMEAREA',area)).fetchall()[0]
            datadonne = datasql.execute(sql_polo_area_eta_totale_donne.replace('NOMEAREA',area).replace('NOMEPOLO',nomepolo)).fetchall()[0]
            datauomini = datasql.execute(sql_polo_area_eta_totale_donne.replace('NOMEAREA',area).replace('NOMEPOLO',nomepolo)).fetchall()[0]
            label = changeLabel(area).replace(" ","_").replace(")","").replace("(","")
            values = {}
            values['totale'] = 0
            values['totale_donne'] = 0
            values['totale_uomini'] = 0
            values['etamedia'] = 0
            values['etamedia_uomini'] = 0
            values['etamedia_donne'] = 0

            if datatotale['totale'] != None:
                values['totale'] = datatotale['totale']
                values['etamedia'] =  int(datatotale['etamedia'])
            if datadonne['totale'] != None:
                values['totale_donne']=  datadonne['totale']
                values['etamedia_donne']=  int(datadonne['etamedia'])
            if datauomini['totale'] != None:
                values['totale_uomini']=  datauomini['totale']
                values['etamedia_uomini']=  int(datauomini['etamedia'])
            bodyarea[label] = values;
        bodypolo['aree'] = bodyarea
        bodycontratti = {}
        for contratto in contratti:
            datatotale = datasql.execute(sql_polo_contratto_eta_totale.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo)).fetchall()[0]
            datadonne = datasql.execute(sql_polo_contratto_eta_totale_donne.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo)).fetchall()[0]
            datauomini = datasql.execute(sql_polo_contratto_eta_totale_uomini.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo)).fetchall()[0]
            label = changeLabel(contratto).replace(" ","_").replace(")","").replace("(","")
            values = {}            
            values['totale'] = 0
            values['totale_donne']=  0
            values['etamedia_donne']=  0
            values['totale_uomini']=  0
            values['etamedia_uomini']=  0
            values['etamedia']=  0
            if datatotale['totale'] != None:
                values['totale'] = datatotale['totale']
                values['etamedia']=  int(datatotale['etamedia'])
            if datadonne['totale'] != None:
                values['totale_donne']=  datadonne['totale']
                values['etamedia_donne']=  int(datadonne['etamedia'])
            if datauomini['totale'] != None:
                values['totale_uomini']=  datauomini['totale']
                values['etamedia_uomini']=  int(datauomini['etamedia'])
            bodycontratti[label] = values
        bodypolo['contratti'] = bodycontratti
        centri = datasql.execute(sql_lista_centri_polo.replace("NOMEPOLO",nomepolo)).fetchall()
        bodycentri = []    
        for centro in centri:
            nomecentro = centro['centro']
            bodycentro = {}
            datatotale = datasql.execute(sql_centro_totale_eta.replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
            datadonne = datasql.execute(sql_centro_totale_eta_donne.replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
            datauomini = datasql.execute(sql_centro_totale_eta_uomini.replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
            bodycentro['totale_donne']=  datadonne['totale']
            bodycentro['totale_uomini']=  datauomini['totale']
            bodycentro['etamedia_uomini']=  0
            bodycentro['etamedia_donne']=  0
            if datadonne['etamedia'] != None:
                bodycentro['etamedia_donne']=  int(datadonne['etamedia'])
            if datauomini['etamedia'] != None:
                bodycentro['etamedia_uomini']=  int(datauomini['etamedia'])
            bodycentro['etamedia']=  int(datatotale['etamedia'])
            bodycentro['name']=changeLabel(nomecentro)
            bodycentro['totale']= datatotale['totale']
            bodyareecentro={} 
            for area in aree:
                datatotale = datasql.execute(sql_centro_area_eta_totale.replace('NOMEPOLO',nomepolo).replace('NOMEAREA',area).replace('NOMECENTRO',nomecentro)).fetchall()[0]
                datadonne = datasql.execute(sql_centro_area_eta_totale_donne.replace('NOMEAREA',area).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
                datauomini = datasql.execute(sql_centro_area_eta_totale_donne.replace('NOMEAREA',area).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
                label = changeLabel(area).replace(" ","_").replace(")","").replace("(","")
                values={}                              
                values['totale'] = 0
                values['totale_donne']=  0
                values['totale_uomini']=  0
                values['etamedia_uomini']= 0
                values['etamedia_donne']=  0
                values['etamedia']=  0
                
                if datatotale['totale'] != None:
                    values['totale'] = datatotale['totale']
                    values['etamedia']=  int(datatotale['etamedia'])
                if datadonne['totale'] != None:
                    values['totale_donne']=  datadonne['totale']
                    values['etamedia_donne']=  int(datadonne['etamedia'])
                if datauomini['totale'] != None:
                    values['totale_uomini']=  datauomini['totale']
                    values['etamedia_uomini']=  int(datauomini['etamedia'])
                
                bodycontratticentroarea = {}               
                for contratto in contratti:
                    datatotale = datasql.execute(sql_centro_contratto_area_eta_totale.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro).replace('NOMEAREA',area)).fetchall()[0]
                    datadonne = datasql.execute(sql_centro_contratto_area_eta_totale_donne.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro).replace('NOMEAREA',area)).fetchall()[0]
                    datauomini = datasql.execute(sql_centro_contratto_area_eta_totale_uomini.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro).replace('NOMEAREA',area)).fetchall()[0]
                    labela = changeLabel(contratto).replace(" ","_").replace(")","").replace("(","")
                    valuesa={}                              
                    valuesa['totale'] = 0
                    valuesa['totale_donne']=  0
                    valuesa['totale_uomini']=  0
                    valuesa['etamedia_uomini']= 0
                    valuesa['etamedia_donne']=  0
                    valuesa['etamedia']=  0
                    if datatotale['totale'] != None:
                        valuesa['totale'] = datatotale['totale']
                        valuesa['etamedia']=  int(datatotale['etamedia'])
                    if datadonne['totale'] != None:
                        valuesa['totale_donne']=  datadonne['totale']
                        valuesa['etamedia_donne']=  int(datadonne['etamedia'])
                    if datauomini['totale'] != None:
                        valuesa['totale_uomini']=  datauomini['totale']
                        valuesa['etamedia_uomini']=  int(datauomini['etamedia'])
                    bodycontratticentroarea[labela] = valuesa; 
                    values[labela]= bodycontratticentroarea[labela] 
                bodyareecentro[label] = values;
                
               
            bodycentro['aree'] = bodyareecentro
            bodycontratticentro = {}               
            for contratto in contratti:
                datatotale = datasql.execute(sql_centro_contratto_eta_totale.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
                datadonne = datasql.execute(sql_centro_contratto_eta_totale_donne.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
                datauomini = datasql.execute(sql_centro_contratto_eta_totale_uomini.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
                label = changeLabel(contratto).replace(" ","_").replace(")","").replace("(","")
                values={}                              
                values['totale'] = 0
                values['totale_donne']=  0
                values['totale_uomini']=  0
                values['etamedia_uomini']= 0
                values['etamedia_donne']=  0
                values['etamedia']=  0
                if datatotale['totale'] != None:
                    values['totale'] = datatotale['totale']
                    values['etamedia']=  int(datatotale['etamedia'])
                if datadonne['totale'] != None:
                    values['totale_donne']=  datadonne['totale']
                    values['etamedia_donne']=  int(datadonne['etamedia'])
                if datauomini['totale'] != None:
                    values['totale_uomini']=  datauomini['totale']
                    values['etamedia_uomini']=  int(datauomini['etamedia'])
                bodycontratticentro[label] = values;
            bodycentro['contratti']=bodycontratticentro
            bodycentri.append(bodycentro)
            bodypolo['centri']=bodycentri
    
    
        bodypoli.append(bodypolo)
    header['poli'] = bodypoli
    json_data = json.dumps(header)
    return json_data

anni = [2013,2014,2015,2016]
for anno in anni:
    fname = str(anno) + ".json"
    file = open(fname,"w") 
    file.write(getJsonData(anno)) 
    file.close() 
        
    
