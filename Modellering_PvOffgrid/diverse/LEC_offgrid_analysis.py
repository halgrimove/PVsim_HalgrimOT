# -*- coding: utf-8 -*-
"""
Created on Fri Mar  3 10:03:48 2023

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


import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

#-----------------------------------------------------------------------------------------

#NESTED DICTIONARY AV ANNLEGGSPARAMETERE TIL DELTAKERENE
param = {}
week = 40



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


deltakere = [1, 1, 3, 4] #Kategorihytte på deltakerene 
bruksmønster = [1, 1, 1, 0] #Bruksmønster på deltakerene
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

start = 1
end = 35037 #Ett år

    
    
for i in range (len(param)):
             
    K[i] = ofmb.offgrid_model(demand[i], pv[i], param[i], return_series=False)
    #ofp.offgrid_plot(E[i], demand[i], pv[i], week)
   
print('FØR ENERGIDELING')
print('---------------------------------------------------------------------------------------')
'''
print('Bortkastet solenergi for hytte 1: {:.5g} kWh'.format(sum(E[0]['lost_production'])*0.25))
print('Bortkastet solenergi  for hytte 2: {:.5g} kWh'.format(sum(E[1]['lost_production'])*0.25))
print('Bortkastet solenergi  for hytte 3: {:.5g} kWh'.format(sum(E[2]['lost_production'])*0.25))
print('Bortkastet solenergi  for hytte 4: {:.5g} kWh'.format(sum(E[3]['lost_production'])*0.25))


'''
print('Estimert forbruk som ikke blir dekt for hytte 1: {:.5g} kWh'.format(sum(K[0]['lost_load'])*0.25))
print('Estimert forbruk som ikke blir dekt for hytte 2: {:.5g} kWh'.format(sum(K[1]['lost_load'])*0.25))
print('Estimert forbruk som ikke blir dekt for hytte 3: {:.5g} kWh'.format(sum(K[2]['lost_load'])*0.25))
print('Estimert forbruk som ikke blir dekt for hytte 4: {:.5g} kWh'.format(sum(K[3]['lost_load'])*0.25))
#print('Estimert forbruk som ikke blir dekt for hytte 4: {:.5g} kWh'.format(sum(E[4]['lost_load'])*0.25))
print()


x = (sum(K[0]['lost_load'])+sum(K[1]['lost_load'])+sum(K[2]['lost_load'])+sum(K[3]['lost_load']))*0.25
a = (sum(K[0]['lost_production'])+sum(K[1]['lost_production'])+sum(K[2]['lost_production'])+sum(K[3]['lost_production']))*0.25

biddingstatus_pv, biddingstatus_battery = lecbs.bidding_status_per_timestep(K, param, 0)

for timestep in range(start,end):
   
   #print(timestep, end, sep='/') 
            
            #Gir bidding status i hver tidssteg gjennom et helt år basert påå de momentane verdiene for innstråling og
            #forbruk som ikke kan spås
            
   E = lecs.energysharing_per_timestep(K, param, biddingstatus_pv, biddingstatus_battery, timestep)
   
   biddingstatus_pv, biddingstatus_battery = lecbs.bidding_status_per_timestep(E, param, timestep)
   
for i in range(len(param)):
    
    for timestep in range(start,end):

        if E[i]['LevelOfCharge'][timestep] < param[i]['BatteryDischargeLimit']:
            
               E[i]['LevelOfCharge'][timestep] = param[i]['BatteryDischargeLimit']
               
        else:
            if E[i]['LevelOfCharge'][timestep] > param[i]['BatteryCapacity']:
                
                E[i]['LevelOfCharge'][timestep] = param[i]['BatteryCapacity']
   

print('ETTER ENERGIDELING')
print('---------------------------------------------------------------------------------------')
'''
print()
print('Bortkastet solenergi for hytte 1: {:.5g} kWh'.format(sum(E[0]['lost_production'])*0.25))
print('Bortkastet solenergi for hytte 2: {:.5g} kWh'.format(sum(E[1]['lost_production'])*0.25))
print('Bortkastet solenergi for hytte 3: {:.5g} kWh'.format(sum(E[2]['lost_production'])*0.25))
print('Bortkastet solenergi for hytte 4: {:.5g} kWh'.format(sum(E[3]['lost_production'])*0.25))

'''

print('Estimert forbruk som ikke blir dekt for hytte 1: {:.5g} kWh'.format(sum(E[0]['lost_load'])*0.25))
print('Estimert forbruk som ikke blir dekt for hytte 2: {:.5g} kWh'.format(sum(E[1]['lost_load'])*0.25))
print('Estimert forbruk som ikke blir dekt for hytte 3: {:.5g} kWh'.format(sum(E[2]['lost_load'])*0.25))
print('Estimert forbruk som ikke blir dekt for hytte 4: {:.5g} kWh'.format(sum(E[3]['lost_load'])*0.25))
#print('Estimert forbruk som ikke blir dekt for hytte 4: {:.5g} kWh'.format(sum(E[4]['lost_load'])*0.25))


y = (sum(E[0]['lost_load'])+sum(E[1]['lost_load'])+sum(E[2]['lost_load'])+sum(E[3]['lost_load']))*0.25
b = (sum(E[0]['lost_production'])+sum(E[1]['lost_production'])+sum(E[2]['lost_production'])+sum(E[3]['lost_production']))*0.25

print()
print('Total reduksjon i estimert forbruk som ikke blir dekt : {:.5g}kWh'.format(x-y))
print('Relativ total reduskjon i estimert forbruk som ikke blir dekt : {:.3g}%'.format(((x-y)*100)/x))
print('----------------------------------------------------------------')
print('Total reduksjon i bortkastet solenergi: {:.5g}kWh'.format(a-b))
print('Relativ total reduksjon av bortasktet solenergi: {:.3g}%'.format((a-b)*100/a))

#------------------------------------------------------------------------------------------
 