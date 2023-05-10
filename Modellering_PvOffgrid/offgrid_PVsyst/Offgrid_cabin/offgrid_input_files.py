"""
Created on Tue Jan 31 16:30:31 2023

@author: halgr
"""

import pandas as pd
import warnings as wp
import season_generator as sg

#FJERNE IRRITERENDE MELDING I KONTROLLVINDUET
wp.filterwarnings(action='ignore', category=FutureWarning)


#-------------------------------------------------------------------------------------------

'''
DENNE FILEN HENTER FORBRUKSDATA FRA RAMP OG PRODUKSJONSDATA FRA PVLIB. DEN PREPARER FILENE VED Å 
INTERPOLERE DEM TIL Å HA LIK LENGDE. SAMT GI DEM LIK INDEX
'''


def offgrid_input(input_file, bruksmønster=0):
    #0 er deafult, ingen aktivering av bruksmønster
    
    
    #-------------------------------------------------------------------------------------------
    
    
    #ANTALL DAGER DET SIMULERES FOR. DETTE MÅ ANGIS FOR KUNNE TA MED ET TILSTREKKELIG ANTALL RADER I RAMP-FILEN
    antall_dager = 365

  
    #HENTE UT FORBURKET FRA RAMP. MED KORREKT ANTALL RADER SOM STEMMER OVERENS MED INPUT-FILEN FRA PVLIB
    demand_ramp = pd.read_csv('C:/Users\halgr/OneDrive - NTNU/Masteroppgave/Python/Modellering_PvOffgrid/offgrid_PVsyst/input_files/demand_{}.csv'.format(input_file), index_col=0, nrows=(60*24*antall_dager-59), squeeze=True)
    

    #HENTE UT PRODUKSJONSDATA FRA PVLIB. ANTALL RADER MÅ STEMME OVERENS MED HVA SOM ER ANTGITT I RAMP-FILEN
    pv_pvlib = pd.read_csv('C:/Users\halgr/OneDrive - NTNU/Masteroppgave/Python/Modellering_PvOffgrid/offgrid_PVsyst/input_files/pv_oslo.csv',
                         index_col=0, usecols=[0, 1], header=None, parse_dates=True, squeeze=True, nrows=(antall_dager*24+1), skiprows=1)
    

    
    
    #ANGI KORREKT INDEX I RAMP-FILEN (SOM STEMMER OVERENS MED INDEXEN I PVLIB-FILEN)
    #ANTALL MINUTTER MELLEOM "START" OG "END" MÅ TILSVARE ANTALL RADER SOM "DEMAND_RAMP" INNEHOLDER 
    demand_ramp.index = pd.date_range(start='2021-01-01 00:00',end='2021-12-31 23:00', freq='min')
    
    #-----------------------------------------------------------------
    
    if bruksmønster != 0:
        
        demand_ramp = sg.season_generator(demand_ramp, bruksmønster)
        #TAR HENSYN TIL BRUKSMØNSTER
    
    #-----------------------------------------------------------------
    
    #INTERPOLERE MINUTTDATAENE TIL "15MINUTTS" DATA. KORTER I PRAKSIS NED PÅ ANTALL RADER.
    demand_ramp = demand_ramp.resample('15min').interpolate(method='linear')
    
      
    #INTERPOLERE TIMESDATAENE I PVLIB-FILEN TIL 15MINUTTS DATA. ØKER I PRAKSIS ANTALLET RADER.
    pv_pvlib = pv_pvlib.resample('15min').interpolate(method='linear')
    
    
    #-------------------------------------------------------------------------------------------
    
  
    #RETURNERE DE FERDIG PREPARERTE FORBRUKS OG PRODUSKJONS FILENE
    #FILENE HAR LIKE MANGE RADER OG KOLONNER, SAMT LIK INDEX.
    return demand_ramp, pv_pvlib
    


