# -*- coding: utf-8 -*-
"""
xls del personale di FBK a json
convert from xls to json
"""

import pyexcel as pe
import json
import os
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column , Integer, String
from sqlalchemy.orm import sessionmaker
dbfile = "people_fbk.db"
if os.path.exists(dbfile):
    os.remove(dbfile)
xlsxfile = "statistica_personale_2017.xlsx"
#records = pe.get_records(file_name=xlsxfile)
#my_array = pe.get_array(file_name=xlsxfile)
#my_dict = pe.get_dict(file_name=xlsxfile, name_columns_by_row=0)

engine = create_engine("sqlite:///" + dbfile)
Base = declarative_base()
Session = sessionmaker(bind=engine)

#VERIFICARE I NOMI DEI CAMPI NEL FILE XLSX e RINOMINARLI
class Employers(Base):
    __tablename__='statistica_personale'
    id=Column(Integer, primary_key=True)
    year=Column(Integer)
    cdc=Column(String)
    contract=Column(String)
    gender=Column(String)
    provenance=Column(String)
    protected=Column(Integer)
    number=Column(Integer)
    age=Column(Integer)
    area=Column(String)
    polo=Column(String)

Base.metadata.create_all(engine)
session = Session()
pe.save_as(file_name=xlsxfile, name_columns_by_row=0, dest_session=session, dest_table=Employers)

#VERIFICARE I DISTINCT DELLE POSSIBILI ETICHETTE
RICERCA="RICERCA"
SUPPORTO_RICERCA="SUPPORTO RICERCA"
AMMINISTRAZIONE="AMMINISTRAZIONE"
aree=[RICERCA,SUPPORTO_RICERCA,AMMINISTRAZIONE]
COCO= 'Co.co. (jobs act)'
DETERMINATO = 'Dipendente Tempo Determinato'
INDETERMINATO = 'Dipendente Tempo Indeterminato'
BORSAPHD = 'Dottorando Borsa'
contratti = [DETERMINATO,INDETERMINATO,BORSAPHD,COCO]

UMANISTICO = 'PSUS - POLO UMANISTICO'
SCIENTIFICO = 'PST - POLO SCIENTIFICO'
CASSR = 'CASSR'
PROGSPECIALI = 'PROGETTI SPECIALI-ESPLORATIVI'
SERVIZIOAMMINISTRAZIONE="SUPPORTO ALLA RICERCA"

poli = [SCIENTIFICO,UMANISTICO,CASSR,PROGSPECIALI,SERVIZIOAMMINISTRAZIONE]

LUMANISTICO = 'polo umanistico'
LSCIENTIFICO = 'polo scientifico'
LCASSR='servizi a supporto alla ricerca'
LPROGSPECIALI = 'progetti speciali'
LCOCO='collaborazione coordinata (jobs act)'
LDETERMINATO='tempo determinato'
LBORSAPHD = 'borsa di dottorato'
LINDETERMINATO = 'tempo indeterminato'
LSUPPORTO_RICERCA='supporto alla ricerca'
LRICERCA='ricerca'
LAMMINISTRAZIONE='amministrazione'
LSERVIZIOAMMINISTRAZIONE="comparto amministrazione"
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


conn = sqlite3.connect(dbfile)
conn.row_factory = dict_factory
datasql = conn.cursor()


def getJsonData(anno):

    sql_eta_totale="""
    select sum(`number`) as totale, round(avg(`age`)) as etamedia
    from statistica_personale WHERE  year=%s;
    """ % (anno)

    sql_eta_totale_donne="""
    select sum(`number`)  as totale, round(avg(`age`)) as etamedia
    from statistica_personale WHERE `gender`= 'Femmina' and  year=%s;
    """  % (anno)

    sql_eta_totale_uomini="""
    select sum(`number`)  as totale, round(avg(`age`)) as etamedia
    from statistica_personale WHERE `gender`= 'Maschio' and  year=%s;
    """  % (anno)


    sql_eta_totale_stranieri="""
    select sum(`number`) as totale, round(avg(`age`)) as etamedia
    from statistica_personale WHERE year=%s and provenance='Estero';
    """ % (anno)

    sql_eta_totale_donne_stranieri="""
    select sum(`number`)  as totale, round(avg(`age`)) as etamedia
    from statistica_personale WHERE `gender`= 'Femmina' and year=%s and provenance='Estero';
    """  % (anno)

    sql_eta_totale_uomini_stranieri="""
    select sum(`number`)  as totale, round(avg(`age`)) as etamedia
    from statistica_personale WHERE `gender`= 'Maschio' and year=%s and provenance='Estero';
    """  % (anno)

    sql_eta_totale_categoria_protetta="""
    select sum(`number`) as totale, round(avg(`age`)) as etamedia
    from statistica_personale WHERE year=%s and protected=1;
    """ % (anno)

    sql_eta_totale_donne_categoria_protetta="""
    select sum(`number`)  as totale, round(avg(`age`)) as etamedia
    from statistica_personale WHERE `gender`= 'Femmina' and year=%s and protected=1;
    """  % (anno)

    sql_eta_totale_uomini_categoria_protetta="""
    select sum(`number`)  as totale, round(avg(`age`)) as etamedia
    from statistica_personale WHERE `gender`= 'Maschio' and year=%s and protected=1;
    """  % (anno)

    sql_area_eta_totale="""
    select sum(`number`) as totale,  round(avg(`age`)) as etamedia
    from statistica_personale where  year=%s and Area='NOMEAREA'
    """ % (anno)

    sql_area_eta_totale_donne="""
    select sum(`number`) as totale, round(avg(`age`)) as etamedia
    from statistica_personale where  year=%s and Area='NOMEAREA' and gender='Femmina'
    """ % (anno)

    sql_area_eta_totale_uomini="""
    select sum(`number`) as totale, round(avg(`age`)) as etamedia
    from statistica_personale where  year=%s and Area='NOMEAREA' and gender='Maschio'
    """ % (anno)

    sql_area_eta_totale_stranieri="""
    select sum(`number`) as totale,  round(avg(`age`)) as etamedia
    from statistica_personale where  year=%s and Area='NOMEAREA' and provenance='Estero';
    """ % (anno)

    sql_area_eta_totale_donne_stranieri="""
    select sum(`number`) as totale, round(avg(`age`)) as etamedia
    from statistica_personale where  year=%s and Area='NOMEAREA' and gender='Femmina' and provenance='Estero';
    """ % (anno)

    sql_area_eta_totale_uomini_stranieri="""
    select sum(`number`) as totale, round(avg(`age`)) as etamedia
    from statistica_personale where  year=%s and Area='NOMEAREA' and gender='Maschio' and provenance='Estero';
    """ % (anno)

    sql_area_eta_totale_categoria_protetta="""
    select sum(`number`) as totale,  round(avg(`age`)) as etamedia
    from statistica_personale where  year=%s and Area='NOMEAREA' and protected=1;
    """ % (anno)

    sql_area_eta_totale_donne_categoria_protetta="""
    select sum(`number`) as totale, round(avg(`age`)) as etamedia
    from statistica_personale where  year=%s and Area='NOMEAREA' and gender='Femmina' and protected=1;
    """ % (anno)

    sql_area_eta_totale_uomini_categoria_protetta="""
    select sum(`number`) as totale, round(avg(`age`)) as etamedia
    from statistica_personale where  year=%s and Area='NOMEAREA' and gender='Maschio' and protected=1;
    """ % (anno)


    sql_contratto_eta_totale="""
    select sum(`number`) as totale,  round(avg(`age`)) as etamedia
    from statistica_personale where  year=%s and `contract`='NOMECONTRATTO'
    """ % (anno)

    sql_contratto_eta_totale_donne="""
    select sum(`number`) as totale, round(avg(`age`)) as etamedia
    from statistica_personale where  year=%s and `contract`='NOMECONTRATTO' and gender='Femmina'
    """ % (anno)

    sql_contratto_eta_totale_uomini="""
    select sum(`number`) as totale, round(avg(`age`)) as etamedia
    from statistica_personale where  year=%s and `contract`='NOMECONTRATTO' and gender='Maschio'
    """ % (anno)

    sql_contratto_eta_totale_stranieri="""
    select sum(`number`) as totale,  round(avg(`age`)) as etamedia
    from statistica_personale where  year=%s and `contract`='NOMECONTRATTO' and provenance='Estero'
    """ % (anno)

    sql_contratto_eta_totale_donne_stranieri="""
    select sum(`number`) as totale, round(avg(`age`)) as etamedia
    from statistica_personale where  year=%s and `contract`='NOMECONTRATTO' and gender='Femmina' and provenance='Estero'
    """ % (anno)

    sql_contratto_eta_totale_uomini_stranieri="""
    select sum(`number`) as totale, round(avg(`age`)) as etamedia
    from statistica_personale where  year=%s and `contract`='NOMECONTRATTO' and gender='Maschio' and provenance='Estero'
    """ % (anno)

    sql_contratto_eta_totale_categoria_protetta="""
    select sum(`number`) as totale,  round(avg(`age`)) as etamedia
    from statistica_personale where  year=%s and `contract`='NOMECONTRATTO' and protected=1
    """ % (anno)

    sql_contratto_eta_totale_donne_categoria_protetta="""
    select sum(`number`) as totale, round(avg(`age`)) as etamedia
    from statistica_personale where  year=%s and `contract`='NOMECONTRATTO' and gender='Femmina' and protected=1
    """ % (anno)

    sql_contratto_eta_totale_uomini_categoria_protetta="""
    select sum(`number`) as totale, round(avg(`age`)) as etamedia
    from statistica_personale where  year=%s and `contract`='NOMECONTRATTO' and gender='Maschio' and protected=1
    """ % (anno)



    sql_lista_poli="""
    select distinct(Polo) as polo from statistica_personale where year = %s order by polo desc;
    """ % (anno)

    sql_polo_totale_eta = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO'
    """ % (anno)

    sql_polo_totale_eta_uomini = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO' and gender='Maschio'
    """ % (anno)

    sql_polo_totale_eta_donne = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO' and gender='Femmina'
    """ % (anno)

    sql_polo_totale_eta_stranieri = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO'
  and provenance='Estero';
    """ % (anno)

    sql_polo_totale_eta_uomini_stranieri = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO' and gender='Maschio'
  and provenance='Estero';
    """ % (anno)

    sql_polo_totale_eta_donne_stranieri = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO' and gender='Femmina'
  and provenance='Estero';
    """ % (anno)


    sql_polo_totale_eta_categoria_protetta = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO'
   and protected=1;
    """ % (anno)

    sql_polo_totale_eta_uomini_categoria_protetta = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO' and gender='Maschio'
  and protected=1;
    """ % (anno)

    sql_polo_totale_eta_donne_categoria_protetta = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO' and gender='Femmina'
  and protected=1;
    """ % (anno)


    sql_polo_area_eta_totale = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO'
  and `Area`='NOMEAREA'
    """ % (anno)

    sql_polo_area_eta_totale_donne = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO' and gender='Femmina'
   and `Area`='NOMEAREA' """ % (anno)

    sql_polo_area_eta_totale_uomini = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO' and gender='Maschio'
   and `Area`='NOMEAREA' """ % (anno)

    sql_polo_area_eta_totale_stranieri = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO'
  and `Area`='NOMEAREA' and provenance='Estero';
    """ % (anno)

    sql_polo_area_eta_totale_donne_stranieri = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO' and gender='Femmina'
   and `Area`='NOMEAREA' and provenance='Estero'; """ % (anno)

    sql_polo_area_eta_totale_uomini_stranieri = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO' and gender='Maschio'
   and `Area`='NOMEAREA' and provenance='Estero';""" % (anno)

    sql_polo_area_eta_totale_categoria_protetta = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO'
  and `Area`='NOMEAREA' and protected=1;
    """ % (anno)

    sql_polo_area_eta_totale_donne_categoria_protetta = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO' and gender='Femmina'
   and `Area`='NOMEAREA' and protected=1 """ % (anno)

    sql_polo_area_eta_totale_uomini_categoria_protetta = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO' and gender='Maschio'
   and `Area`='NOMEAREA' and protected=1""" % (anno)

    sql_polo_contratto_eta_totale = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO'
   and `contract`='NOMECONTRATTO' """ % (anno)

    sql_polo_contratto_eta_totale_uomini = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO' and gender='Maschio'
   and `contract`='NOMECONTRATTO' """ % (anno)

    sql_polo_contratto_eta_totale_donne = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO' and gender='Femmina'
   and `contract`='NOMECONTRATTO' """ % (anno)

    sql_polo_contratto_eta_totale_stranieri = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO'
   and `contract`='NOMECONTRATTO' and provenance='Estero'""" % (anno)

    sql_polo_contratto_eta_totale_uomini_stranieri = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO' and gender='Maschio'
   and `contract`='NOMECONTRATTO' and provenance='Estero'""" % (anno)

    sql_polo_contratto_eta_totale_donne_stranieri = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO' and gender='Femmina'
   and `contract`='NOMECONTRATTO' and provenance='Estero'""" % (anno)

    sql_polo_contratto_eta_totale_categoria_protetta = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO'
   and `contract`='NOMECONTRATTO' and protected=1 """ % (anno)

    sql_polo_contratto_eta_totale_uomini_categoria_protetta = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO' and gender='Maschio'
   and `contract`='NOMECONTRATTO' and protected=1""" % (anno)

    sql_polo_contratto_eta_totale_donne_categoria_protetta = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and Polo='NOMEPOLO' and gender='Femmina'
   and `contract`='NOMECONTRATTO' and protected=1""" % (anno)


    sql_lista_centri_polo="""
    select distinct cdc as centro from statistica_personale where year = %s and Polo='NOMEPOLO' order by centro asc;
    """ % (anno)

    sql_centro_totale_eta="""
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO' and Polo='NOMEPOLO'
    """ % (anno)

    sql_centro_totale_eta_uomini = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and Polo='NOMEPOLO' and gender='Maschio'
    """ % (anno)

    sql_centro_totale_eta_donne = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and Polo='NOMEPOLO' and gender='Femmina'
    """ % (anno)

    sql_centro_totale_eta_stranieri="""
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO' and Polo='NOMEPOLO'
   and provenance='Estero'
    """ % (anno)

    sql_centro_totale_eta_uomini_stranieri = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and Polo='NOMEPOLO' and gender='Maschio'
   and provenance='Estero'
    """ % (anno)

    sql_centro_totale_eta_donne_stranieri = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and Polo='NOMEPOLO' and gender='Femmina'
   and provenance='Estero'
    """ % (anno)

    sql_centro_totale_eta_categoria_protetta="""
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO' and Polo='NOMEPOLO'
  and protected=1""" % (anno)

    sql_centro_totale_eta_uomini_categoria_protetta = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and Polo='NOMEPOLO' and gender='Maschio'
  and protected=1""" % (anno)

    sql_centro_totale_eta_donne_categoria_protetta = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and Polo='NOMEPOLO' and gender='Femmina'
  and protected=1""" % (anno)

    sql_centro_area_eta_totale = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and Polo='NOMEPOLO'
  and `Area`='NOMEAREA'
    """ % (anno)

    sql_centro_area_eta_totale_donne = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO' and Polo='NOMEPOLO' and gender='Femmina'
   and `Area`='NOMEAREA' """ % (anno)

    sql_centro_area_eta_totale_uomini = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO' and Polo='NOMEPOLO' and gender='Maschio'
 and `Area`='NOMEAREA' """ % (anno)

    sql_centro_area_eta_totale_stranieri = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and Polo='NOMEPOLO'
  and `Area`='NOMEAREA' and provenance='Estero'
    """ % (anno)

    sql_centro_area_eta_totale_donne_stranieri = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO' and Polo='NOMEPOLO' and gender='Femmina'
   and `Area`='NOMEAREA' and provenance='Estero' """ % (anno)

    sql_centro_area_eta_totale_uomini_stranieri = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO' and Polo='NOMEPOLO' and gender='Maschio'
 and `Area`='NOMEAREA' and provenance='Estero'""" % (anno)

    sql_centro_area_eta_totale_categoria_protetta = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and Polo='NOMEPOLO'
  and `Area`='NOMEAREA'  and protected=1
    """ % (anno)

    sql_centro_area_eta_totale_donne_categoria_protetta = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO' and Polo='NOMEPOLO' and gender='Femmina'
   and `Area`='NOMEAREA'  and protected=1""" % (anno)

    sql_centro_area_eta_totale_uomini_categoria_protetta = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO' and Polo='NOMEPOLO' and gender='Maschio'
 and `Area`='NOMEAREA'  and protected=1""" % (anno)

    sql_centro_contratto_eta_totale = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and Polo='NOMEPOLO'
   and `contract`='NOMECONTRATTO' """ % (anno)

    sql_centro_area_eta_totale_stranieri = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and Polo='NOMEPOLO'
  and `Area`='NOMEAREA' and provenance='Estero'
    """ % (anno)

    sql_centro_area_eta_totale_donne_stranieri = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO' and Polo='NOMEPOLO' and gender='Femmina'
   and `Area`='NOMEAREA' and provenance='Estero'""" % (anno)

    sql_centro_contratto_eta_totale = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and Polo='NOMEPOLO'
   and `contract`='NOMECONTRATTO' """ % (anno)

    sql_centro_contratto_eta_totale_uomini = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and gender='Maschio'  and Polo='NOMEPOLO'
   and `contract`='NOMECONTRATTO' """ % (anno)

    sql_centro_contratto_eta_totale_donne = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and gender='Femmina'  and Polo='NOMEPOLO'
   and `contract`='NOMECONTRATTO' """ % (anno)

    sql_centro_contratto_eta_totale_stranieri = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and Polo='NOMEPOLO'
   and `contract`='NOMECONTRATTO'  and provenance='Estero'""" % (anno)

    sql_centro_contratto_eta_totale_uomini_stranieri = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and gender='Maschio'  and Polo='NOMEPOLO'
   and `contract`='NOMECONTRATTO'  and provenance='Estero'""" % (anno)

    sql_centro_contratto_eta_totale_donne_stranieri = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and gender='Femmina'  and Polo='NOMEPOLO'
   and `contract`='NOMECONTRATTO'  and provenance='Estero'""" % (anno)

    sql_centro_contratto_eta_totale_categoria_protetta = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and Polo='NOMEPOLO'
   and `contract`='NOMECONTRATTO' and protected=1""" % (anno)

    sql_centro_contratto_eta_totale_uomini_categoria_protetta = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and gender='Maschio'  and Polo='NOMEPOLO'
   and `contract`='NOMECONTRATTO' and protected=1""" % (anno)

    sql_centro_contratto_eta_totale_donne_categoria_protetta = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and gender='Femmina'  and Polo='NOMEPOLO'
   and `contract`='NOMECONTRATTO' and protected=1""" % (anno)


    sql_centro_contratto_area_eta_totale = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and Polo='NOMEPOLO'
   and `contract`='NOMECONTRATTO' and `Area`='NOMEAREA'""" % (anno)

    sql_centro_contratto_area_eta_totale_uomini = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and gender='Maschio'  and Polo='NOMEPOLO'
   and `contract`='NOMECONTRATTO'  and `Area`='NOMEAREA'""" % (anno)

    sql_centro_contratto_area_eta_totale_donne = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and gender='Femmina'  and Polo='NOMEPOLO'
   and `contract`='NOMECONTRATTO'  and `Area`='NOMEAREA'""" % (anno)

    sql_centro_contratto_area_eta_totale_stranieri = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and Polo='NOMEPOLO'
   and `contract`='NOMECONTRATTO' and `Area`='NOMEAREA' and provenance='Estero'""" % (anno)

    sql_centro_contratto_area_eta_totale_uomini_stranieri = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and gender='Maschio'  and Polo='NOMEPOLO'
   and `contract`='NOMECONTRATTO'  and `Area`='NOMEAREA' and provenance='Estero'""" % (anno)

    sql_centro_contratto_area_eta_totale_donne_stranieri = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and gender='Femmina'  and Polo='NOMEPOLO'
   and `contract`='NOMECONTRATTO'  and `Area`='NOMEAREA' and provenance='Estero'""" % (anno)

    sql_centro_contratto_area_eta_totale_categoria_protetta= """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and Polo='NOMEPOLO'
   and `contract`='NOMECONTRATTO' and `Area`='NOMEAREA' and protected=1""" % (anno)

    sql_centro_contratto_area_eta_totale_uomini_categoria_protetta = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and gender='Maschio'  and Polo='NOMEPOLO'
   and `contract`='NOMECONTRATTO'  and `Area`='NOMEAREA' and protected=1""" % (anno)

    sql_centro_contratto_area_eta_totale_donne_categoria_protetta = """
    select sum(`number`) as totale, round(avg(`age`)) as etamedia from statistica_personale where year = %s and cdc='NOMECENTRO'  and gender='Femmina'  and Polo='NOMEPOLO'
   and `contract`='NOMECONTRATTO' and `Area`='NOMEAREA' and protected=1""" % (anno)

    def getCensus(datatotale,datadonne,datauomini):

        default={}
        if datatotale['totale'] is None:
            datatotale['totale'] = 0
        if datatotale['etamedia'] is None:
            datatotale['etamedia'] = 0
        if datadonne['totale'] is None:
            datadonne['totale'] = 0
        if datadonne['etamedia'] is None:
            datadonne['etamedia'] = 0
        if datauomini['totale'] is None:
            datauomini['totale'] = 0
        if datauomini['etamedia'] is None:
            datauomini['etamedia'] = 0
        default['totale']= datatotale['totale']
        default["totale_donne"]=datadonne['totale']
        default["totale_uomini"]=datauomini['totale']
        default["etamedia"]=int(datatotale['etamedia'])
        default['etamedia_donne']=int(datadonne['etamedia'])
        default['etamedia_uomini']=int(datauomini['etamedia'])
        return default

    header={}
    header["name"] = "FBK"
    header["anno"] = str(anno)

    datatotale = datasql.execute(sql_eta_totale).fetchall()[0]
    datadonne = datasql.execute(sql_eta_totale_donne).fetchall()[0]
    datauomini = datasql.execute(sql_eta_totale_uomini).fetchall()[0]
    header['default']=getCensus(datatotale,datadonne,datauomini)

    datatotale =  datasql.execute(sql_eta_totale_stranieri).fetchall()[0]
    datadonne =  datasql.execute(sql_eta_totale_donne_stranieri).fetchall()[0]
    datauomini =  datasql.execute(sql_eta_totale_uomini_stranieri).fetchall()[0]
    header['stranieri']=getCensus(datatotale,datadonne,datauomini)

    datatotale = datasql.execute(sql_eta_totale_categoria_protetta).fetchall()[0]
    datadonne = datasql.execute(sql_eta_totale_donne_categoria_protetta).fetchall()[0]
    datauomini = datasql.execute(sql_eta_totale_uomini_categoria_protetta).fetchall()[0]
    header['categoria_protetta']=getCensus(datatotale,datadonne,datauomini)

    bodyarea={}
    for area in aree:
        labelarea = changeLabel(area).replace(" ","_").replace(")","").replace("(","")
        values = {}
        datatotale = datasql.execute(sql_area_eta_totale.replace('NOMEAREA',area)).fetchall()[0]
        datadonne = datasql.execute(sql_area_eta_totale_donne.replace('NOMEAREA',area)).fetchall()[0]
        datauomini = datasql.execute(sql_area_eta_totale_uomini.replace('NOMEAREA',area)).fetchall()[0]
        values['default']=getCensus(datatotale,datadonne,datauomini)

        datatotale = datasql.execute(sql_area_eta_totale_stranieri.replace('NOMEAREA',area)).fetchall()[0]
        datadonne = datasql.execute(sql_area_eta_totale_donne_stranieri.replace('NOMEAREA',area)).fetchall()[0]
        datauomini = datasql.execute(sql_area_eta_totale_uomini_stranieri.replace('NOMEAREA',area)).fetchall()[0]
        values['stranieri']=getCensus(datatotale,datadonne,datauomini)

        datatotale = datasql.execute(sql_area_eta_totale_categoria_protetta.replace('NOMEAREA',area)).fetchall()[0]
        datadonne = datasql.execute(sql_area_eta_totale_donne_categoria_protetta.replace('NOMEAREA',area)).fetchall()[0]
        datauomini = datasql.execute(sql_area_eta_totale_uomini_categoria_protetta.replace('NOMEAREA',area)).fetchall()[0]
        values['categoria_protetta']=getCensus(datatotale,datadonne,datauomini)
        bodyarea[labelarea]=values

    header['aree']=bodyarea

    bodycontratti = {}
    for contratto in contratti:
        label_area_contratto = changeLabel(contratto).replace(" ","_").replace(")","").replace("(","")
        values = {}
        datatotale = datasql.execute(sql_contratto_eta_totale.replace('NOMECONTRATTO',contratto)).fetchall()[0]
        datadonne = datasql.execute(sql_contratto_eta_totale_donne.replace('NOMECONTRATTO',contratto)).fetchall()[0]
        datauomini = datasql.execute(sql_contratto_eta_totale_uomini.replace('NOMECONTRATTO',contratto)).fetchall()[0]
        values['default']=getCensus(datatotale,datadonne,datauomini)

        datatotale = datasql.execute(sql_contratto_eta_totale_stranieri.replace('NOMECONTRATTO',contratto)).fetchall()[0]
        datadonne = datasql.execute(sql_contratto_eta_totale_donne_stranieri.replace('NOMECONTRATTO',contratto)).fetchall()[0]
        datauomini = datasql.execute(sql_contratto_eta_totale_uomini_stranieri.replace('NOMECONTRATTO',contratto)).fetchall()[0]
        values['stranieri']=getCensus(datatotale,datadonne,datauomini)

        datatotale = datasql.execute(sql_contratto_eta_totale_categoria_protetta.replace('NOMECONTRATTO',contratto)).fetchall()[0]
        datadonne = datasql.execute(sql_contratto_eta_totale_donne_categoria_protetta.replace('NOMECONTRATTO',contratto)).fetchall()[0]
        datauomini = datasql.execute(sql_contratto_eta_totale_uomini_categoria_protetta.replace('NOMECONTRATTO',contratto)).fetchall()[0]
        values['categoria_protetta']=getCensus(datatotale,datadonne,datauomini)
        bodycontratti[label_area_contratto]=values


    header['contratti']=bodycontratti

    listapoli = datasql.execute(sql_lista_poli).fetchall()
    bodypoli = []

    #POLO
    for polo in listapoli:
        nomepolo = polo['polo']
        bodypolo = {}
#        label_polo = changeLabel(nomepolo).replace(" ","_").replace(")","").replace("(","")

        bodypolo['name']=changeLabel(nomepolo)

        datatotale = datasql.execute(sql_polo_totale_eta.replace('NOMEPOLO',nomepolo)).fetchall()[0]
        datadonne = datasql.execute(sql_polo_totale_eta_donne.replace('NOMEPOLO',nomepolo)).fetchall()[0]
        datauomini = datasql.execute(sql_polo_totale_eta_uomini.replace('NOMEPOLO',nomepolo)).fetchall()[0]
        bodypolo['default']=getCensus(datatotale,datadonne,datauomini)


        datatotale = datasql.execute(sql_polo_totale_eta_stranieri.replace('NOMEPOLO',nomepolo)).fetchall()[0]
        datadonne = datasql.execute(sql_polo_totale_eta_donne_stranieri.replace('NOMEPOLO',nomepolo)).fetchall()[0]
        datauomini = datasql.execute(sql_polo_totale_eta_uomini_stranieri.replace('NOMEPOLO',nomepolo)).fetchall()[0]
        bodypolo['stranieri'] = getCensus(datatotale,datadonne,datauomini)

        datatotale = datasql.execute(sql_polo_totale_eta_categoria_protetta.replace('NOMEPOLO',nomepolo)).fetchall()[0]
        datadonne = datasql.execute(sql_polo_totale_eta_donne_categoria_protetta.replace('NOMEPOLO',nomepolo)).fetchall()[0]
        datauomini = datasql.execute(sql_polo_totale_eta_uomini_categoria_protetta.replace('NOMEPOLO',nomepolo)).fetchall()[0]
        bodypolo['categoria_protetta'] = getCensus(datatotale,datadonne,datauomini)

        bodyarea={}
        #polo -> aree
        for area in aree:
            values = {}
            label_area_polo = changeLabel(area).replace(" ","_").replace(")","").replace("(","")
            datatotale = datasql.execute(sql_polo_area_eta_totale.replace('NOMEPOLO',nomepolo).replace('NOMEAREA',area)).fetchall()[0]
            datadonne = datasql.execute(sql_polo_area_eta_totale_donne.replace('NOMEAREA',area).replace('NOMEPOLO',nomepolo)).fetchall()[0]
            datauomini = datasql.execute(sql_polo_area_eta_totale_uomini.replace('NOMEAREA',area).replace('NOMEPOLO',nomepolo)).fetchall()[0]
            values['default']=getCensus(datatotale,datadonne,datauomini)


            datatotale = datasql.execute(sql_polo_area_eta_totale_stranieri.replace('NOMEPOLO',nomepolo).replace('NOMEAREA',area)).fetchall()[0]
            datadonne = datasql.execute(sql_polo_area_eta_totale_donne_stranieri.replace('NOMEAREA',area).replace('NOMEPOLO',nomepolo)).fetchall()[0]
            datauomini = datasql.execute(sql_polo_area_eta_totale_uomini_stranieri.replace('NOMEAREA',area).replace('NOMEPOLO',nomepolo)).fetchall()[0]
            values['stranieri']=getCensus(datatotale,datadonne,datauomini)


            datatotale = datasql.execute(sql_polo_area_eta_totale_categoria_protetta.replace('NOMEPOLO',nomepolo).replace('NOMEAREA',area)).fetchall()[0]
            datadonne = datasql.execute(sql_polo_area_eta_totale_donne_categoria_protetta.replace('NOMEAREA',area).replace('NOMEPOLO',nomepolo)).fetchall()[0]
            datauomini = datasql.execute(sql_polo_area_eta_totale_uomini_categoria_protetta.replace('NOMEAREA',area).replace('NOMEPOLO',nomepolo)).fetchall()[0]
            values['categoria_protetta']=getCensus(datatotale,datadonne,datauomini)

            bodyarea[label_area_polo] = values;
        bodypolo['aree'] = bodyarea
        bodycontratti = {}

        #polo -> contratti
        for contratto in contratti:
            values = {}
            label_contratto_polo = changeLabel(contratto).replace(" ","_").replace(")","").replace("(","")
            datatotale = datasql.execute(sql_polo_contratto_eta_totale.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo)).fetchall()[0]
            datadonne = datasql.execute(sql_polo_contratto_eta_totale_donne.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo)).fetchall()[0]
            datauomini = datasql.execute(sql_polo_contratto_eta_totale_uomini.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo)).fetchall()[0]
            values['default']=getCensus(datatotale,datadonne,datauomini)

            datatotale = datasql.execute(sql_polo_contratto_eta_totale_stranieri.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo)).fetchall()[0]
            datadonne = datasql.execute(sql_polo_contratto_eta_totale_donne_stranieri.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo)).fetchall()[0]
            datauomini = datasql.execute(sql_polo_contratto_eta_totale_uomini_stranieri.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo)).fetchall()[0]
            values['stranieri']=getCensus(datatotale,datadonne,datauomini)

            datatotale = datasql.execute(sql_polo_contratto_eta_totale_categoria_protetta.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo)).fetchall()[0]
            datadonne = datasql.execute(sql_polo_contratto_eta_totale_donne_categoria_protetta.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo)).fetchall()[0]
            datauomini = datasql.execute(sql_polo_contratto_eta_totale_uomini_categoria_protetta.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo)).fetchall()[0]
            values['categoria_protetta']=getCensus(datatotale,datadonne,datauomini)

            bodycontratti[label_contratto_polo] = values

        bodypolo['contratti'] = bodycontratti

        centri = datasql.execute(sql_lista_centri_polo.replace("NOMEPOLO",nomepolo)).fetchall()
        #polo -> centri
        bodycentri = []
        for centro in centri:
            nomecentro = centro['centro']
            bodycentro = {}
            bodycentro['name']=changeLabel(nomecentro)
            datatotale = datasql.execute(sql_centro_totale_eta.replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
            datadonne = datasql.execute(sql_centro_totale_eta_donne.replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
            datauomini = datasql.execute(sql_centro_totale_eta_uomini.replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
            bodycentro['default']=getCensus(datatotale,datadonne,datauomini)

            datatotale = datasql.execute(sql_centro_totale_eta_stranieri.replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
            datadonne = datasql.execute(sql_centro_totale_eta_donne_stranieri.replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
            datauomini = datasql.execute(sql_centro_totale_eta_uomini_stranieri.replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
            bodycentro['stranieri']=getCensus(datatotale,datadonne,datauomini)

            datatotale = datasql.execute(sql_centro_totale_eta_categoria_protetta.replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
            datadonne = datasql.execute(sql_centro_totale_eta_donne_categoria_protetta.replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
            datauomini = datasql.execute(sql_centro_totale_eta_uomini_categoria_protetta.replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
            bodycentro['categoria_protetta']=getCensus(datatotale,datadonne,datauomini)

            bodyareecentro={}
            #polo -> centri -> aree
            for area in aree:
                values = {}
                label_centro_area = changeLabel(area).replace(" ","_").replace(")","").replace("(","")
                datatotale = datasql.execute(sql_centro_area_eta_totale.replace('NOMEPOLO',nomepolo).replace('NOMEAREA',area).replace('NOMECENTRO',nomecentro)).fetchall()[0]
                datadonne = datasql.execute(sql_centro_area_eta_totale_donne.replace('NOMEAREA',area).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
                datauomini = datasql.execute(sql_centro_area_eta_totale_uomini.replace('NOMEAREA',area).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
                values['default']=getCensus(datatotale,datadonne,datauomini)

                datatotale = datasql.execute(sql_centro_area_eta_totale_stranieri.replace('NOMEPOLO',nomepolo).replace('NOMEAREA',area).replace('NOMECENTRO',nomecentro)).fetchall()[0]
                datadonne = datasql.execute(sql_centro_area_eta_totale_donne_stranieri.replace('NOMEAREA',area).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
                datauomini = datasql.execute(sql_centro_area_eta_totale_uomini_stranieri.replace('NOMEAREA',area).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
                values['stranieri']=getCensus(datatotale,datadonne,datauomini)


                datatotale = datasql.execute(sql_centro_area_eta_totale_categoria_protetta.replace('NOMEPOLO',nomepolo).replace('NOMEAREA',area).replace('NOMECENTRO',nomecentro)).fetchall()[0]
                datadonne = datasql.execute(sql_centro_area_eta_totale_donne_categoria_protetta.replace('NOMEAREA',area).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
                datauomini = datasql.execute(sql_centro_area_eta_totale_uomini_categoria_protetta.replace('NOMEAREA',area).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
                values['categoria_protetta']=getCensus(datatotale,datadonne,datauomini)

                for contratto in contratti:
                    values_contratti = {}
                    label_centro_area_contratto = changeLabel(contratto).replace(" ","_").replace(")","").replace("(","")
                    datatotale = datasql.execute(sql_centro_contratto_area_eta_totale.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro).replace('NOMEAREA',area)).fetchall()[0]
                    datadonne = datasql.execute(sql_centro_contratto_area_eta_totale_donne.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro).replace('NOMEAREA',area)).fetchall()[0]
                    datauomini = datasql.execute(sql_centro_contratto_area_eta_totale_uomini.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro).replace('NOMEAREA',area)).fetchall()[0]
                    values_contratti['default']=getCensus(datatotale,datadonne,datauomini)

                    datatotale = datasql.execute(sql_centro_contratto_area_eta_totale_stranieri.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro).replace('NOMEAREA',area)).fetchall()[0]
                    datadonne = datasql.execute(sql_centro_contratto_area_eta_totale_donne_stranieri.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro).replace('NOMEAREA',area)).fetchall()[0]
                    datauomini = datasql.execute(sql_centro_contratto_area_eta_totale_uomini_stranieri.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro).replace('NOMEAREA',area)).fetchall()[0]
                    values_contratti['stranieri']=getCensus(datatotale,datadonne,datauomini)

                    datatotale = datasql.execute(sql_centro_contratto_area_eta_totale_categoria_protetta.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro).replace('NOMEAREA',area)).fetchall()[0]
                    datadonne = datasql.execute(sql_centro_contratto_area_eta_totale_donne_categoria_protetta.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro).replace('NOMEAREA',area)).fetchall()[0]
                    datauomini = datasql.execute(sql_centro_contratto_area_eta_totale_uomini_categoria_protetta.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro).replace('NOMEAREA',area)).fetchall()[0]
                    values_contratti['categoria_protetta']=getCensus(datatotale,datadonne,datauomini)
                    values[label_centro_area_contratto] = values_contratti


                bodyareecentro[label_centro_area] = values;

            bodycentro['aree'] = bodyareecentro

            bodycontratticentro = {}
            for contratto in contratti:
                values = {}
                labelcontratto = changeLabel(contratto).replace(" ","_").replace(")","").replace("(","")
                datatotale = datasql.execute(sql_centro_contratto_eta_totale.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
                datadonne = datasql.execute(sql_centro_contratto_eta_totale_donne.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
                datauomini = datasql.execute(sql_centro_contratto_eta_totale_uomini.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
                values['default']=getCensus(datatotale,datadonne,datauomini)

                datatotale = datasql.execute(sql_centro_contratto_eta_totale_stranieri.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
                datadonne = datasql.execute(sql_centro_contratto_eta_totale_donne_stranieri.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
                datauomini = datasql.execute(sql_centro_contratto_eta_totale_uomini_stranieri.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
                values['stranieri']=getCensus(datatotale,datadonne,datauomini)

                datatotale = datasql.execute(sql_centro_contratto_eta_totale_categoria_protetta.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
                datadonne = datasql.execute(sql_centro_contratto_eta_totale_donne_categoria_protetta.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
                datauomini = datasql.execute(sql_centro_contratto_eta_totale_uomini_categoria_protetta.replace('NOMECONTRATTO',contratto).replace('NOMEPOLO',nomepolo).replace('NOMECENTRO',nomecentro)).fetchall()[0]
                values['categoria_protetta']=getCensus(datatotale,datadonne,datauomini)

                bodycontratticentro[labelcontratto]=values
                #bodyareecentro[labelcontratto]=bodycontratticentro

            bodycentro['contratti'] =  bodycontratticentro #bodyareecentro
#            bodycentro['aree'] = bodyareecentro
            bodycentri.append(bodycentro)
            bodypolo['centri']=bodycentri

        bodypoli.append(bodypolo)
    header['poli'] = bodypoli
    #json_data = json.dumps(header)
    return header

years_sql="select distinct(year) from statistica_personale;"
anni = []
data=datasql.execute(years_sql).fetchall()
for y in data:
    anni.append(y['year'])

datajson = {}
for anno in anni:
    datajson[str(anno)]= getJsonData(anno)
json_data = json.dumps(datajson)
fname = "employees.json"
file = open(fname,"w")
file.write(json_data)
file.close()
datasql.close()
conn.close()
