# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 11:49:00 2023

@author: halgr
"""

import numpy as np
import LEC_input_files as lif
import matplotlib.pyplot as plt
import pandas as pd
#import LEC_model_builder_pre as lecmbp
import offgrid_model_builder as ofmb
import offgrid_plot as ofp
import LEC_bidding_status as lecbs
import LEC_sharing_analysis as lecsa
import LEC_sharing as lecs
import LEC_offgrid_plot as lecop


import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

#-----------------------------------------------------------------------------------------

#NESTED DICTIONARY AV ANNLEGGSPARAMETERE TIL DELTAKERENE
param = {}



param[0] = {'BatteryCapacity': 30,
                'BatteryEfficiency': .9,
                'BatteryDischargeLimit': 1,
                'BatterySellingLimit': 3,
                'InverterEfficiency': .85,
                'timestep': .25,
                'MaxPower': 10,
                'MaxPowerInverter': 3
               }

param[1] = {'BatteryCapacity': 30,
                'BatteryEfficiency': .9,
                'BatteryDischargeLimit': 1,
                'BatterySellingLimit': 3,
                'InverterEfficiency': .85,
                'timestep': .25,
                'MaxPower': 10,
                'MaxPowerInverter': 3
               }


param[2] = {'BatteryCapacity': 30,
                'BatteryEfficiency': .9,
                'BatteryDischargeLimit': 1,
                'BatterySellingLimit': 3,
                'InverterEfficiency': .85,
                'timestep': .25,
                'MaxPower': 10,
                'MaxPowerInverter': 3
               }

param[3] = {'BatteryCapacity': 30,
                'BatteryEfficiency': .9,
                'BatteryDischargeLimit': 1,
                'BatterySellingLimit': 3,
                'InverterEfficiency': .85,
                'timestep': .25,
                'MaxPower': 10,
                'MaxPowerInverter': 3
               }


#-----------------------------------------------------------------------------------------

timestep = 1000 #itereres gjennom et år

#TIMESTEP 15000 (35000), OUNDERSKUDD PÅ DEMAND [4,4,3], [0,0,0]
#TIMESTEP 33540, Underskudd på forbruk [1,2,3], [0,0,0] 
#TIMESTEP 5000, [4 4 3], [1 0 0]
#TIMESTEP 20200, OVERSKUDD PÅ PRODUSKJON [4 4 3] [1 0 0]

'''
1500, 4.2.3, 0.0.0; To batteri flex, en kjøper
'''


deltakere = [3, 3, 3, 1] #Kategorihytte på deltakerene 
bruksmønster = [0, 1, 0, 1] #Bruksmønster på deltakerene
#0: bor på hytta, 1: feriebruk, 2: annenhver helg, 3: hver helg

demand, pv = lif.LEC_input_files(deltakere, bruksmønster) #kW

return_series=False
G = {}
E = {}
K = {}

'''
Kan overskudd fra PV gå rett til inverter hos nabo, eller må det overføres via nabos batteri?

Manipulere energiflyt verdiene i hvert tidssteg avhengig av hvilke bud som legges inn fra PV og batteri på
de ulike anleggene.
'''

#------------------------------------------------------------------------------------------

week = 39
start = 1
end = 35037

deltakere = len(param)

    
for i in range (deltakere):
             
    K[i] = ofmb.offgrid_model(demand[i], pv[i], param[i], return_series=False)
    #ofp.offgrid_plot(E[i], demand[i], pv[i], week)
   
#for i in range (deltakere):

ofp.offgrid_plot(K[3], demand[3], pv[3], week)

biddingstatus_pv, biddingstatus_battery = lecbs.bidding_status_per_timestep(K, param, 0)
#intitierer bud i første tidssteg

for timestep in range(start,end):
   
   #print(timestep, end, sep='/') 
   
            #Gir bidding status i hver tidssteg gjennom et helt år basert påå de momentane verdiene for innstråling og
            #forbruk som ikke kan spås
   
            
   E = lecs.energysharing_per_timestep(K, param, biddingstatus_pv, biddingstatus_battery, timestep)
   
   biddingstatus_pv, biddingstatus_battery = lecbs.bidding_status_per_timestep(E, param, timestep)
   

for i in range(deltakere):
    
    for timestep in range(start,end):

        if E[i]['LevelOfCharge'][timestep] < param[i]['BatteryDischargeLimit']:
            
               E[i]['LevelOfCharge'][timestep] = param[i]['BatteryDischargeLimit']
               
        else:
            if E[i]['LevelOfCharge'][timestep] > param[i]['BatteryCapacity']:
                
                E[i]['LevelOfCharge'][timestep] = param[i]['BatteryCapacity']


#for i in range (deltakere):


lecop.LEC_offgrid_plot(E[0], demand[0], pv[0], week)
lecop.LEC_offgrid_plot(E[1], demand[1], pv[1], week)
lecop.LEC_offgrid_plot(E[2], demand[2], pv[2], week)
lecop.LEC_offgrid_plot(E[3], demand[3], pv[3], week)

#OBS, den hytta som det ikke bor folk på står alltid på minimal verdi. Fordi battereit 
#hele tiden lades ut. Lag en variabel som viser denne flyten av energi

'''
Til neste gang:
    
    Får negative batteriverdier. Jobbe med å få plottene til å vise riktig.
    Sjekk variablene i E, og påse at de er realistiske
'''

#------------------------------------------------------------------------------------------
 

