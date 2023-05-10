# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 12:27:01 2023

@author: halgr
"""

#----------------------------------------------------------------------------------------------------------


import pandas as pd

'''
HENTER INN TIMESDATA FRA SARAH2 I PVGIS. INKLUDERER DE RADENE SOM DET SKAL SIMULERES FOR. INKLUDERER OGSÅ DE 
KOLONNENE SOM ER NØDVENDIGE FOR SIMULERINGEN I PVLIB.MODELCHAIN.RUN_MODEL(INPUT-FIL). FINN IGJEN NAVNET PÅ DISSE
KOLONNENE VED Å BRUKE CTR + i.
'''

#----------------------------------------------------------------------------------------------------------


pvgis_oslo = pd.read_csv("C:/Users\halgr/OneDrive - NTNU/Masteroppgave/Python/modellering_solcelleanlegg/offgrid_Pvgis/input_files/pvgis_oslo.csv", 
                         skiprows=16, nrows = 8760, usecols=["time(UTC)","T2m", "G(h)","Gb(n)","Gd(h)", "WS10m"], index_col=0)



#GI INDEXEN I PVGIS FILEN RETT FORMAT -> SAMME FORMAT KREVES I PVLIB.MODELCHAIN
pvgis_oslo.index = pd.to_datetime(pvgis_oslo.index, format="%Y%m%d:%H%M")


#DATE RANGE MÅ STEMME OVERENS MED ANTALL RADER I INUPT-FILEN. 8760 RADER -> 8760 TIMER -> ETT ÅR MED TIMESDATA
pvgis_oslo.index = pd.date_range(start='2021-01-01 00:00', end='2021-12-31 23:59', freq="h")


#GI KOLONNEN SAMME NAVN SOM PVLIB.MODELCHAIN.RUN_MODEL ETTERSPØR. SE "HELP" FOR MERE DETALJER
pvgis_oslo.columns = ["temp_air", "ghi", "dni", "dhi", "wind_speed"]


#----------------------------------------------------------------------------------------------------------


#LAGRE DEN PREPARERTE FILEN PÅ EN LUR PLASS. KLAR TIL BRUK I PVLIB.MODELCHAIN.RUN_MODEL(INPUT-FIL)
pvgis_oslo.to_csv("C:/Users\halgr/OneDrive - NTNU/Masteroppgave/Python/Modellering_PvOffgrid/offgrid_Pvlib/input_files/irradiance_oslo.csv")

