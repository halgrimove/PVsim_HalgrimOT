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
import LEC_input_files as lecif
import model_builder_per_timestep2 as ofmb
import offgrid_model_builder as ofmb_pre
import LEC_offgrid_plot as ofg_plot
import sf_rate as sf
import sf_rate_sharing as sf_sharing

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



#-----------------------------------------------------------------------------------------

deltakere = [2, 1, 1] #Kategorihytte på deltakerene 
bruksmønster = [0, 1, 0] #Bruksmønster på deltakerene
#0: bor på hytta, 1: feriebruk, 2: annenhver helg, 3: hver helg

#RAMP-PROFILENE ER RANDOMISERTE! DERFOR FÅR VI IKKE FORDELAKTIG VED SIMULERING AV LIKE HYTTER

demand, pv = lecif.LEC_input_files(deltakere, bruksmønster)


#------------------------------------------------------------------------------------------

K = {}

#Før energideling   
for i in range(len(deltakere)):
             
    K[i] = ofmb_pre.offgrid_model(demand[i], pv[i], param[i], return_series=False)



print('FØR ENERGIDELING')
print('---------------------------------------------------------------------------------------')

print('Bortkastet solenergi for hytte 1: {:.5g} kWh'.format(sum(K[0]['lost_production'])*0.25))
print('Bortkastet solenergi for hytte 2: {:.5g} kWh'.format(sum(K[1]['lost_production'])*0.25))
print('Bortkastet solenergi for hytte 3: {:.5g} kWh'.format(sum(K[2]['lost_production'])*0.25))

sf_rate_pre = sf.sf_rate(K, demand)

print()
print('Self sufficient rate for hytte 1: {:.4g} %'.format(sf_rate_pre[0]))
print('Self sufficient rate for hytte 2: {:.4g} %'.format(sf_rate_pre[1]))
print('Self sufficient rate for hytte 3: {:.4g} %'.format(sf_rate_pre[2]))


print()
print('Estimert forbruk som ikke blir dekt for hytte 1: {:.5g} kWh'.format(sum(K[0]['lost_load'])*0.25))
print('Estimert forbruk som ikke blir dekt for hytte 2: {:.5g} kWh'.format(sum(K[1]['lost_load'])*0.25))
print('Estimert forbruk som ikke blir dekt for hytte 3: {:.5g} kWh'.format(sum(K[2]['lost_load'])*0.25))
print()

x = (sum(K[0]['lost_load'])+sum(K[1]['lost_load'])+sum(K[2]['lost_load']))*0.25
a = (sum(K[0]['lost_production'])+sum(K[1]['lost_production'])+sum(K[2]['lost_production']))*0.25

#Etter energideling
dict_list = []
sum_lost_load = np.zeros(len(deltakere))
sum_lost_production = np.zeros(len(deltakere))



for time in range(0,35037):
    
    
    E = ofmb.E_per_timestep(dict_list, param, time, demand, pv)

    dict_list.append(E)
  


for i in range(0,35037):
    
    for j in range(len(deltakere)):
        
        sum_lost_load[j] += dict_list[i][j]['lost_load'] 
        sum_lost_production[j] += dict_list[i][j]['lost_production']
                    


print('ETTER ENERGIDELING')
print('---------------------------------------------------------------------------------------')

print('Bortkastet solenergi for hytte 1: {:.5g} kWh'.format(sum_lost_production[0]*0.25))
print('Bortkastet solenergi for hytte 2: {:.5g} kWh'.format(sum_lost_production[1]*0.25))
print('Bortkastet solenergi for hytte 3: {:.5g} kWh'.format(sum_lost_production[2]*0.25))
print()

print('Estimert forbruk som ikke blir dekt for hytte 1: {:.5g} kWh'.format(sum_lost_load[0]*0.25))
print('Estimert forbruk som ikke blir dekt for hytte 2: {:.5g} kWh'.format(sum_lost_load[1]*0.25))
print('Estimert forbruk som ikke blir dekt for hytte 3: {:.5g} kWh'.format(sum_lost_load[2]*0.25))

sf_rate_post = sf_sharing.sf_rate_sharing(sum_lost_load, demand)

print()
print('Self sufficient rate for hytte 1: {:.4g} %'.format(sf_rate_post[0]))
print('Self sufficient rate for hytte 2: {:.4g} %'.format(sf_rate_post[1]))
print('Self sufficient rate for hytte 3: {:.4g} %'.format(sf_rate_post[2]))

b = (sum_lost_production[0]+sum_lost_production[1]+sum_lost_production[2])*0.25
y = (sum_lost_load[0]+sum_lost_load[1]+sum_lost_load[2])*0.25

print()
print('RESULTAT')
print('Total reduksjon i estimert forbruk som ikke blir dekt : {:.5g}kWh'.format(x-y))
print('Relativ total reduskjon i estimert forbruk som ikke blir dekt : {:.3g}%'.format(((x-y)*100)/x))
print('----------------------------------------------------------------')
print('Total reduksjon i bortkastet solenergi: {:.5g}kWh'.format(a-b))
print('Relativ total reduksjon av bortasktet solenergi: {:.3g}%'.format((a-b)*100/a))

#------------------------------------------------------------------------------------------



'''
for i in range(len(param)):

    ofg_plot.LEC_offgrid_plot(dict_list, demand[i], pv[i], week, i)


'''

for week in range(30,31):
    
    ofg_plot.LEC_offgrid_plot(dict_list, demand[0], pv[0], week, 0)
    ofg_plot.LEC_offgrid_plot(dict_list, demand[1], pv[1], week, 1)
    ofg_plot.LEC_offgrid_plot(dict_list, demand[2], pv[2], week, 2)
    
#ofg_plot.LEC_offgrid_plot(dict_list, demand[1], pv[1], 10, 1)

'''
SE PÅ CASEN MED TO HYTTER, SE NÅR DET OVERFØRES FRA BATTERIET OSV
'''

