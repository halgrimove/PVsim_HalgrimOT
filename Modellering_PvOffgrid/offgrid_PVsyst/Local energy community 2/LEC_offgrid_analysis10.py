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


param[3] = {'BatteryCapacity': 20,
                'BatteryEfficiency': .9,
                'BatteryDischargeLimit': 1,
                'BatterySellingLimit': 3,
                'InverterEfficiency': .85,
                'timestep': .25,
                'MaxPower': 10,
                'MaxPowerInverter': 3
               }

param[4] = {'BatteryCapacity': 20,
                'BatteryEfficiency': .9,
                'BatteryDischargeLimit': 1,
                'BatterySellingLimit': 3,
                'InverterEfficiency': .85,
                'timestep': .25,
                'MaxPower': 10,
                'MaxPowerInverter': 3
               }

param[5] = {'BatteryCapacity': 20,
                'BatteryEfficiency': .9,
                'BatteryDischargeLimit': 1,
                'BatterySellingLimit': 3,
                'InverterEfficiency': .85,
                'timestep': .25,
                'MaxPower': 10,
                'MaxPowerInverter': 3
               }

param[6] = {'BatteryCapacity': 20,
                'BatteryEfficiency': .9,
                'BatteryDischargeLimit': 1,
                'BatterySellingLimit': 3,
                'InverterEfficiency': .85,
                'timestep': .25,
                'MaxPower': 10,
                'MaxPowerInverter': 3
               }

param[7] = {'BatteryCapacity': 20,
                'BatteryEfficiency': .9,
                'BatteryDischargeLimit': 1,
                'BatterySellingLimit': 3,
                'InverterEfficiency': .85,
                'timestep': .25,
                'MaxPower': 10,
                'MaxPowerInverter': 3
               }

param[8] = {'BatteryCapacity': 20,
                'BatteryEfficiency': .9,
                'BatteryDischargeLimit': 1,
                'BatterySellingLimit': 3,
                'InverterEfficiency': .85,
                'timestep': .25,
                'MaxPower': 10,
                'MaxPowerInverter': 3
               }

param[9] = {'BatteryCapacity': 20,
                'BatteryEfficiency': .9,
                'BatteryDischargeLimit': 1,
                'BatterySellingLimit': 3,
                'InverterEfficiency': .85,
                'timestep': .25,
                'MaxPower': 10,
                'MaxPowerInverter': 3
               }




#-----------------------------------------------------------------------------------------

deltakere = [1, 2, 1, 4, 2, 1, 2, 3, 4, 1] #Kategorihytte på deltakerene 
bruksmønster = [1, 0, 1, 0, 1, 1, 1, 0, 0, 2] #Bruksmønster på deltakerene
#0: bor på hytta, 1: feriebruk, 2: annenhver helg, 3: hver helg

#RAMP-PROFILENE ER RANDOMISERTE! DERFOR FÅR VI IKKE FORDELAKTIG VED SIMULERING AV LIKE HYTTER

demand, pv = lecif.LEC_input_files(deltakere, bruksmønster)


#------------------------------------------------------------------------------------------

K = {}

#Før energideling   
for i in range(len(deltakere)):
             
    K[i] = ofmb_pre.offgrid_model(demand[i], pv[i], param[i], return_series=False)


print()
print('FØR ENERGIDELING')
print('---------------------------------------------------------------------------------------')


print()
for i in range(len(deltakere)):
    
    print('Bortkastet solenergi for hytte {:.1g}: {:.5g} kWh'.format(i+1,sum(K[i]['lost_production'])*0.25))



sf_rate_pre = sf.sf_rate(K, demand)

print()
for i in range(len(deltakere)):
    
    print('Self sufficient rate for hytte {:.1g}: {:.4g} %'.format(i+1, sf_rate_pre[i]))


print()
for i in range(len(deltakere)):
    
    print('Estimert forbruk som ikke blir dekt for hytte {:.1g}: {:.5g} kWh'.format(i+1, sum(K[i]['lost_load'])*0.25))

x = 0
a = 0

for i in range(len(deltakere)):
    
    x += sum(K[i]['lost_load'])*0.25
    a += sum(K[i]['lost_production'])*0.25

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

print()
for i in range(len(deltakere)):
    
    print('Bortkastet solenergi for hytte {:.1g}: {:.5g} kWh'.format(i+1, sum_lost_production[i]*0.25))



sf_rate_post = sf_sharing.sf_rate_sharing(sum_lost_load, demand)

print()
for i in range(len(deltakere)):
    
    print('Self sufficient rate for hytte {:.1g}: {:.4g} %'.format(i+1, sf_rate_post[i]))
    
    
print()
for i in range(len(deltakere)):
    
    print('Estimert forbruk som ikke blir dekt for hytte {:.1g}: {:.5g} kWh'.format(i+1, sum_lost_load[i]*0.25))


b = 0
y = 0

for i in range(len(deltakere)):
    
    b += sum_lost_production[i]*0.25
    y += sum_lost_load[i]*0.25

print()
print('RESULTAT')
print('Total reduksjon i estimert forbruk som ikke blir dekt : {:.5g}kWh'.format(x-y))
print('Relativ total reduskjon i estimert forbruk som ikke blir dekt : {:.3g}%'.format(((x-y)*100)/x))
print('----------------------------------------------------------------')
print('Total reduksjon i bortkastet solenergi: {:.5g}kWh'.format(a-b))
print('Relativ total reduksjon av bortasktet solenergi: {:.3g}%'.format((a-b)*100/a))

#------------------------------------------------------------------------------------------



for week in range(30,31):
    
    for i in range(len(deltakere)):
    
        ofg_plot.LEC_offgrid_plot(dict_list, demand[i], pv[i], week, i)
     


