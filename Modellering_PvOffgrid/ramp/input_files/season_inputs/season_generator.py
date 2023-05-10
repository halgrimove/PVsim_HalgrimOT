# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 15:09:46 2023

@author: halgr
"""
import pandas as pd

'''
Denne filen modifiserer input-filene fra ramp til et tilpasset bruksmønster.
Eksempelvis feriebruk, helgebruk, kombinasjon osv..
'''

bruk = 1 
#1; feriebruk
#2; helgebruk

hyttekategori = 1

demand = pd.read_csv('C:/Users\halgr/OneDrive - NTNU/Masteroppgave/Python/Modellering_PvOffgrid/offgrid_PVsyst/input_files/demand_{}.csv'.format(hyttekategori), index_col=0, squeeze=True)


def season_generator(h)


#DATOER FRA 2022
if bruk == 1:
    
    
    #HYTTA ER I BRUK I VINTER, SOMMER, HØST OG JULE-FERIE
    '''
    Vinterferie; 20-26 februar -> Noe som vil si fra minutt (50dagerx24timerx60minutter) 72000 til
    minutt (57x24x60) 8280.
    
    Sommerferie; Minutt 233280 -> 243360 (12-18 juni) og 283680 -> 293760 (17-23 juli)
    
    Høstferie; Minutt 396000 -> 406080 (3-9 oktober)
    
    Juleferie; Minutt 515520 -> 525600 (25-31 desember)
    
    ANTALL MINUTTER TILSVARER ANTALL RADER I DEMAND FILEN
    '''
    
    demand[0:7200] = 0
    demand[8280:233280] = 0
    demand[243360:283680] = 0
    demand[293760:396000] = 0
    demand[406080:515520] = 0
    
    

    
    
    
    
    
    
    