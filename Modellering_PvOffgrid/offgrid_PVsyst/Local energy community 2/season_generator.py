# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 15:09:46 2023

@author: halgr
"""
import pandas as pd

import matplotlib.pyplot as plt

'''
Denne filen modifiserer input-filene fra ramp til et tilpasset bruksmønster.
Eksempelvis feriebruk, helgebruk, kombinasjon osv..
'''


#DET ER 4 KVARTER I HVER TIME -> 4X24; 96 KVARTER PER DØGN

def season_generator(demand, bruksmønster):


    #DATOER FRA 2021. Året starter på en fredag. Første mandag er 4 januar.
    if bruksmønster == 1:
        
        
        #HYTTA ER I BRUK I VINTER, SOMMER, HØST OG JULE-FERIE
        #DEMAND-INPUT FILEN ER DEN FERDIG PREPARERTE INPUTFILEN
        '''
        Vinterferie; 20-26 februar -> Noe som vil si fra minutt (50dagerx24timerx60minutter) 72000 til
        minutt (57x24x60) 8280.
        
        Sommerferie; Minutt 233280 -> 243360 (12-18 juni) og 283680 -> 293760 (17-23 juli)
        
        Høstferie; Minutt 396000 -> 406080 (3-9 oktober)
        
        Juleferie; Minutt 515520 -> 525600 (25-31 desember)
        
        ANTALL MINUTTER TILSVARER ANTALL RADER I DEMAND FILEN
        '''
        
        demand[0:74880] = 0 
        #VINTERFERIE
        demand[85680:236160] = 0 
        #SOMMERFERIE UKE 1
        demand[246240:286560] = 0
        #SOMMERFERIE UKE 2
        demand[296640:397440] = 0
        #HØSTFERIE
        demand[407520:515520] = 0
        #JULEFERIE
        
        
     
    else:
            if bruksmønster == 2:
                    
                   #HYTTA ER I BRUK ANNENHVER HELG I TILLEGG TIL FERIENE
                    
                   n = 14*60*24 #Antall minutter mellom annenhver helg
                   
                    
                  
                   hytte_ankomst = 8*60*24 #første fredag folk drar på hytta
                
                   hytte_avreise = 10*60*24 #første søndag folk drar på hytta
                    
                   demand[0:hytte_ankomst] = 0 #forbruket før første helg på hytta
                    
                   demand[hytte_avreise:(n+hytte_ankomst)] = 0 #Forbruket mellom første og andre helg på hytta
                    
                   
                   
                   for i in range(1,25):
                    
                        
                            demand[(hytte_avreise+n*i):(hytte_ankomst+n*(i+1))] = 0
                    
                
        
     
            if bruksmønster == 3:
                 
                 n = 7*60*24 #Antall minutter mellom hver helg
                 
                  
                
                 hytte_ankomst = 8*60*24 #første fredag folk drar på hytta
              
                 hytte_avreise = 10*60*24 #første søndag folk drar på hytta
                  
                 demand[0:hytte_ankomst] = 0 #forbruket før første helg på hytta
                  
                 demand[hytte_avreise:(n+hytte_ankomst)] = 0 #Forbruket mellom første og andre helg på hytta
                  
                 
                 
                 for i in range(1,51):
                                           
                         
                          demand[(hytte_avreise+n*i):(hytte_ankomst+n*(i+1))] = 0
                  
    
    return demand
    

'''
bruk = 3 
#1; feriebruk
#2; helgebruk

hyttekategori = 4

demand = pd.read_csv('C:/Users\halgr/OneDrive - NTNU/Masteroppgave/Python/Modellering_PvOffgrid/offgrid_PVsyst/input_files/demand_{}.csv'.format(hyttekategori), index_col=0, squeeze=True)

    
x = season_generator(demand, bruk)

    
plt.plot(x.index, x)    

'''




