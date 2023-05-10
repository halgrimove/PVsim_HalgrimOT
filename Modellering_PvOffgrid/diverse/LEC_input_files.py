# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 12:31:02 2023

@author: halgr
"""

import pandas as pd
import season_generator as sg
#import matplotlib.pyplot as plt

'''
Returnerer en dictionary med Demand- og PV- profiler basert på deltakerene i LEC.
Det legges også inn deltakerenes bruksmønster.
'''


def LEC_input_files(deltakere_lec, bruksmønster):
    
    #DELTAKEGERE I LEC. 1, 2, 3 eller 4 avhenging av hvilken hyttekategori delakeren faller under
    #To deltakere, en hyttekategori1 og en hyttekategori 2
    #Begge deltakerene med bruksmønster 1
    #0: bor på hytta, 1: feriebruk, 2: annenhver helg, 3: hver helg
    
    deltakere = len(deltakere_lec)
    antall_dager = 365
    
    #DICTIONARY med serier av lastprofiler og PV produksjon
    demand_ramp = {}
    pv_pvlib = {}
    
    
    for i in range(deltakere):
        
    
        #HENTE UT FORBURKET FRA RAMP. MED KORREKT ANTALL RADER SOM STEMMER OVERENS MED INPUT-FILEN FRA PVLIB
        demand_ramp[i] = pd.read_csv('C:/Users\halgr/OneDrive - NTNU/Masteroppgave/Python/Modellering_PvOffgrid/offgrid_PVsyst/input_files/demand_{}.csv'.format(deltakere_lec[i]), index_col=0, nrows=(60*24*antall_dager-59), squeeze=True)
        
    
    
        #HENTE UT PRODUKSJONSDATA FRA PVLIB. ANTALL RADER MÅ STEMME OVERENS MED HVA SOM ER ANTGITT I RAMP-FILEN
        pv_pvlib[i] = pd.read_csv('C:/Users\halgr/OneDrive - NTNU/Masteroppgave/Python/Modellering_PvOffgrid/offgrid_PVsyst/input_files/pv_oslo.csv',
                             index_col=0, usecols=[0, 1], header=None, parse_dates=True, squeeze=True, nrows=(antall_dager*24+1), skiprows=1)
        
    
        
        
        #ANGI KORREKT INDEX I RAMP-FILEN (SOM STEMMER OVERENS MED INDEXEN I PVLIB-FILEN)
        #ANTALL MINUTTER MELLEOM "START" OG "END" MÅ TILSVARE ANTALL RADER SOM "DEMAND_RAMP" INNEHOLDER 
        demand_ramp[i].index = pd.date_range(start='2021-01-01 00:00',end='2021-12-31 23:00', freq='min')
        
        #-----------------------------------------------------------------
        
        if bruksmønster[i] != 0:
            
            demand_ramp[i] = sg.season_generator(demand_ramp[i], bruksmønster[i])
            #TAR HENSYN TIL BRUKSMØNSTER
        
        #-----------------------------------------------------------------
        
        #INTERPOLERE MINUTTDATAENE TIL "15MINUTTS" DATA. KORTER I PRAKSIS NED PÅ ANTALL RADER.
        demand_ramp[i] = demand_ramp[i].resample('15min').interpolate(method='linear')
        
          
        #INTERPOLERE TIMESDATAENE I PVLIB-FILEN TIL 15MINUTTS DATA. ØKER I PRAKSIS ANTALLET RADER.
        pv_pvlib[i] = pv_pvlib[i].resample('15min').interpolate(method='linear')
    
    
    for i in range(len(demand_ramp[0])):
       
       if demand_ramp[0][i] < 0.1:
           
           demand_ramp[0][i] = 0
           
           
       if demand_ramp[1][i] < 0.1:
           
           demand_ramp[1][i] = 0   
    
    for i in range(len(pv_pvlib[0])):
       
       if pv_pvlib[0][i] < 0.1:
           
           pv_pvlib[0][i] = 0
           
           
       if pv_pvlib[1][i] < 0.1:
           
           pv_pvlib[1][i] = 0   
    
    for i in range(deltakere):
    
        demand_ramp[i] = demand_ramp[i]/1000 #AC 
        pv_pvlib[i] = pv_pvlib[i]/1000 #DC 
    
  
    return demand_ramp, pv_pvlib





