# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 17:07:42 2023

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

param[10] = {'BatteryCapacity': 30,
                'BatteryEfficiency': .9,
                'BatteryDischargeLimit': 1,
                'BatterySellingLimit': 3,
                'InverterEfficiency': .85,
                'timestep': .25,
                'MaxPower': 10,
                'MaxPowerInverter': 3
               }

param[11] = {'BatteryCapacity': 30,
                'BatteryEfficiency': .9,
                'BatteryDischargeLimit': 1,
                'BatterySellingLimit': 3,
                'InverterEfficiency': .85,
                'timestep': .25,
                'MaxPower': 10,
                'MaxPowerInverter': 3
               }

param[12] = {'BatteryCapacity': 30,
                'BatteryEfficiency': .9,
                'BatteryDischargeLimit': 1,
                'BatterySellingLimit': 3,
                'InverterEfficiency': .85,
                'timestep': .25,
                'MaxPower': 10,
                'MaxPowerInverter': 3
               }

param[13] = {'BatteryCapacity': 20,
                'BatteryEfficiency': .9,
                'BatteryDischargeLimit': 1,
                'BatterySellingLimit': 3,
                'InverterEfficiency': .85,
                'timestep': .25,
                'MaxPower': 10,
                'MaxPowerInverter': 3
               }

param[14] = {'BatteryCapacity': 20,
                'BatteryEfficiency': .9,
                'BatteryDischargeLimit': 1,
                'BatterySellingLimit': 3,
                'InverterEfficiency': .85,
                'timestep': .25,
                'MaxPower': 10,
                'MaxPowerInverter': 3
               }

param[15] = {'BatteryCapacity': 20,
                'BatteryEfficiency': .9,
                'BatteryDischargeLimit': 1,
                'BatterySellingLimit': 3,
                'InverterEfficiency': .85,
                'timestep': .25,
                'MaxPower': 10,
                'MaxPowerInverter': 3
               }

param[16] = {'BatteryCapacity': 20,
                'BatteryEfficiency': .9,
                'BatteryDischargeLimit': 1,
                'BatterySellingLimit': 3,
                'InverterEfficiency': .85,
                'timestep': .25,
                'MaxPower': 10,
                'MaxPowerInverter': 3
               }

param[17] = {'BatteryCapacity': 20,
                'BatteryEfficiency': .9,
                'BatteryDischargeLimit': 1,
                'BatterySellingLimit': 3,
                'InverterEfficiency': .85,
                'timestep': .25,
                'MaxPower': 10,
                'MaxPowerInverter': 3
               }

param[18] = {'BatteryCapacity': 20,
                'BatteryEfficiency': .9,
                'BatteryDischargeLimit': 1,
                'BatterySellingLimit': 3,
                'InverterEfficiency': .85,
                'timestep': .25,
                'MaxPower': 10,
                'MaxPowerInverter': 3
               }

param[19] = {'BatteryCapacity': 20,
                'BatteryEfficiency': .9,
                'BatteryDischargeLimit': 1,
                'BatterySellingLimit': 3,
                'InverterEfficiency': .85,
                'timestep': .25,
                'MaxPower': 10,
                'MaxPowerInverter': 3
               }

#-----------------------------------------------------------------------------------------

deltakere = [1, 2, 1, 4, 2, 1, 2, 3, 4, 1, 1, 2, 1, 4, 2, 1, 2, 3, 4, 1] #Kategorihytte på deltakerene 
bruksmønster = [1, 0, 1, 0, 0, 0, 1, 0, 0, 2, 1, 0, 1, 0, 0, 0, 1, 0, 0, 2] #Bruksmønster på deltakerene
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




sf_rate_pre = sf.sf_rate(K, demand)

print()
for i in range(len(deltakere)):
    
    print('Self sufficient rate for hytte {:.1g}: {:.4g} %'.format(i+1, sf_rate_pre[i]))


x = (sum(K[0]['lost_load'])+sum(K[1]['lost_load'])+sum(K[2]['lost_load'])+sum(K[3]['lost_load'])+sum(K[4]['lost_load'])+sum(K[5]['lost_load'])+sum(K[6]['lost_load'])+sum(K[7]['lost_load'])+sum(K[8]['lost_load'])+sum(K[9]['lost_load']))*0.25
a = (sum(K[0]['lost_production'])+sum(K[1]['lost_production'])+sum(K[2]['lost_production'])+sum(K[3]['lost_production'])+sum(K[4]['lost_production'])+sum(K[5]['lost_production'])+sum(K[6]['lost_production'])+sum(K[7]['lost_production'])+sum(K[8]['lost_production'])+sum(K[9]['lost_production']))*0.25

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
                    

print()
print('ETTER ENERGIDELING')
print('---------------------------------------------------------------------------------------')


sf_rate_post = sf_sharing.sf_rate_sharing(sum_lost_load, demand)

print()
for i in range(len(deltakere)):
    
    print('Self sufficient rate for hytte {:.1g}: {:.4g} %'.format(i+1, sf_rate_post[i]))



b = (sum_lost_production[0]+sum_lost_production[1]+sum_lost_production[2]+sum_lost_production[3]+sum_lost_production[4]+sum_lost_production[5]+sum_lost_production[6]+sum_lost_production[7]+sum_lost_production[8]+sum_lost_production[9])*0.25
y = (sum_lost_load[0]+sum_lost_load[1]+sum_lost_load[2]+sum_lost_load[3]+sum_lost_load[4]+sum_lost_load[5]+sum_lost_load[6]+sum_lost_load[7]+sum_lost_load[8]+sum_lost_load[9])*0.25

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
'''
for week in range(30,31):
    
    ofg_plot.LEC_offgrid_plot(dict_list, demand[0], pv[0], week, 0)
    ofg_plot.LEC_offgrid_plot(dict_list, demand[1], pv[1], week, 1)
    ofg_plot.LEC_offgrid_plot(dict_list, demand[2], pv[2], week, 2)
    ofg_plot.LEC_offgrid_plot(dict_list, demand[3], pv[3], week, 3)
    ofg_plot.LEC_offgrid_plot(dict_list, demand[4], pv[4], week, 4)
    ofg_plot.LEC_offgrid_plot(dict_list, demand[5], pv[5], week, 5)
    ofg_plot.LEC_offgrid_plot(dict_list, demand[6], pv[6], week, 6)
    ofg_plot.LEC_offgrid_plot(dict_list, demand[7], pv[7], week, 7)
    ofg_plot.LEC_offgrid_plot(dict_list, demand[8], pv[8], week, 8)
    ofg_plot.LEC_offgrid_plot(dict_list, demand[9], pv[9], week, 9)
    
#ofg_plot.LEC_offgrid_plot(dict_list, demand[1], pv[1], 10, 1)
'''
'''
SE PÅ CASEN MED TO HYTTER, SE NÅR DET OVERFØRES FRA BATTERIET OSV
'''