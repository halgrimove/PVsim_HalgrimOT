# -*- coding: utf-8 -*-
"""
Created on Fri Mar  3 10:03:48 2023

@author: halgr
"""

import numpy as np

import LEC_input_files as lecif
#Fil som inneholder funksjonene som bearbeider input-filene (forburk og produksjon)

import model_builder_per_timestep as ofmb
#Inneholder funksjonen som beregner energiflytsverdier før og etter handel i et tidssteg

import LEC_offgrid_plot as ofg_plot
#Inneholder funksjonene som plotter energiflytsverdier for ønsket antall deltakere og over ønsket tidsrom

import offgrid_model_builder as ofmb_pre
#Inneholder funksjoner som beregner energiflytsverdier uten energihandel (basecase)

import sf_rate as sf
#Inneholder funksoner som beregner SF-rate

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
#Forhindre plagsomme warnings i kontrollvinduet

#-----------------------------------------------------------------------------------------

'''
DENNE FILEN KJØRER SIMULERING FOR ØNSKET ANTALL HYTTER MED ØNSKET BRUKSMØNSTER. FILEN
ER FORENKLET BYGD OPP. ALT KJØRES I LØKKER. PÅ DENNE MÅTEN VIL ALLE HYTTENE SOMULERES MED LIKE 
TEKNISKE PARAMETERE. OM DISSE PARAMETERENE VIL SPESIFIESRES ANNERLEDES FOR HVER DELTAKER, KAN DETTE
FJØRES I FILENE  "LEC_offgrid_analysis2/3/4/10/20/50".

'''

'''
Tapsfaktorere i handel er ikke lagt inn i koden. Det ligger inne tapsfaktor på energiflyt i egen 
installasjon før handel. (Noe som fører til at litt produsert energi blir borte )
'''

#NESTED DICTIONARY AV ANNLEGGSPARAMETERE TIL DELTAKERENE
param = {}


#Lite bakgrunnsinfo ligger bak de valgte tekniske parameterene
param_ex1 = {'BatteryCapacity': 30,
                'BatteryEfficiency': .9,
                'BatteryDischargeLimit': 2,
                'BatterySellingLimit': 3,
                'InverterEfficiency': .85,
                'timestep': .25,
                'MaxPower': 1.8,
                'MaxPowerInverter': 4
               }

'''
Max power for batteriet. Hva er typisk utladning/oppladningseffekt for batteri?

Ser et lithium batteri (12V) har max 150A utladningsstrøm og max oppladningsstrøm på 150A 
-> 1800W -> 450Wh per tidssteg max opp/utladning

Finner vekselrettere med max effekt på 4kW på sunwind.no (Kontinuerlig effekt er anbefalt til 2kW)
'''


'''
SAMMENLIGNE MED BOLIGERS FORBRUK. 
'''

#-----------------------------------------------------------------------------------------
#0: bor på hytta, 1: feriebruk, 2: annenhver helg, 3: hver helg
deltakere1 = [1, 4]
bruksmønster1 = [1, 0] #Bruksmønster på deltakerene

deltakere2 = [1, 2, 3]
bruksmønster2 = [1, 0, 0] #Bruksmønster på deltakerene

deltakere3 = [1, 2, 1, 4]
bruksmønster3 = [1, 0, 2, 3] #Bruksmønster på deltakerene

deltakere4 = [1, 4, 1, 2, 1]
bruksmønster4 = [1, 0, 1, 3, 1] #Bruksmønster på deltakerene

deltakere5 = [4, 2, 1, 1, 1] #Kategorihytte på deltakerene 
bruksmønster5 = [0, 0, 0, 1, 2] #Bruksmønster på deltakerene

deltakere10 = [1, 2, 1, 4, 4, 1, 2, 1, 4, 4]
bruksmønster10 = [1, 2, 1, 0, 0, 1, 2, 1, 0, 0]

deltakere20 = [1, 2, 1, 4, 4, 1, 2, 1, 4, 4, 1, 2, 1, 4, 4, 1, 2, 1, 4, 4]
bruksmønster20 = [1, 2, 1, 0, 0, 1, 2, 1, 0, 0, 1, 2, 1, 0, 0, 1, 2, 1, 0, 0]

deltakere50 = [1, 2, 1, 4, 4, 1, 2, 1, 4, 4, 1, 2, 1, 4, 4, 1, 2, 1, 4, 4, 1, 2, 1, 4, 4, 1, 2, 1, 4, 4, 1, 2, 1, 4, 4, 1, 2, 1, 4, 4, 1, 2, 1, 4, 4, 1, 2, 1, 4, 4]
bruksmønster50 = [1, 0, 1, 0, 0, 0, 1, 0, 0, 2, 1, 0, 1, 0, 0, 0, 1, 0, 0, 2, 1, 0, 1, 0, 0, 0, 1, 0, 0, 2, 1, 0, 1, 0, 0, 0, 1, 0, 0, 2, 1, 0, 1, 0, 0, 0, 1, 0, 0, 2]


#Hente input-filene med kvartersverdier gjennom et helt år
demand, pv = lecif.LEC_input_files(deltakere10, bruksmønster10)

#antall datapunkter
n = len(demand)

#Produsere tekniske parametere for alle deltakerene (alle får like når det gjøres på denne måten)
for i in range(n):

    #Gjør alle hyttene lik eksempelhytta    
    param[i] = param_ex1


K = {}

#Energiflytsverdier uten energideling  
for i in range(n):
             
    K[i] = ofmb_pre.offgrid_model(demand[i], pv[i], param[i], return_series=False)


print()
print('FØR ENERGIDELING (ÅRLIG RESULTAT)')
print('---------------------------------------------------------------------------------------')


print()
for i in range(n):
    
    print('Bortkastet solenergi for hytte {:.1g}: {:.5g} kWh'.format(i+1,sum(K[i]['lost_production'])*0.25))



sf_rate_pre = sf.sf_rate(K, demand)

print()
for i in range(n):
    
    print('Self sufficient rate for hytte {:.1g}: {:.4g} %'.format(i+1, sf_rate_pre[i]))


print()
for i in range(n):
    
    print('Estimert forbruk som ikke blir dekt for hytte {:.1g}: {:.5g} kWh'.format(i+1, sum(K[i]['lost_load'])*0.25))



x = 0
a = 0

#Totale verdier gjennom et helt år
for i in range(n):
    
    x += sum(K[i]['lost_load'])*0.25
    a += sum(K[i]['lost_production'])*0.25

#Etter energideling
dict_list = []
sum_lost_load = np.zeros(n)
sum_lost_production = np.zeros(n)

dict_count = {}
dict_count['pv2pv'] = 0
dict_count['pv2bat'] = 0
dict_count['pv2flex'] = 0
dict_count['bat2pv'] = 0
dict_count['flex2pv'] = 0
dict_count['bat2bat'] = 0
dict_count['flex2bat'] = 0
dict_count['bat2flex'] = 0
dict_count['flex2flex'] = 0

#Energiflytsverdier med energideling
for time in range(0,35037):
    
    
    E, dict_count = ofmb.E_per_timestep(dict_list, dict_count, param, time, demand, pv)

    dict_list.append(E)
    
#Totale verdier gjennom et helt år
for i in range(0,35037):
    
    for j in range(n):
        
        sum_lost_load[j] += dict_list[i][j]['lost_load'] 
        sum_lost_production[j] += dict_list[i][j]['lost_production']
                    


print('ETTER ENERGIDELING (ÅRLIG RESULTAT)')
print('---------------------------------------------------------------------------------------')

print()
for i in range(n):
    
    print('Bortkastet solenergi for hytte {:.1g}: {:.5g} kWh'.format(i+1, sum_lost_production[i]*0.25))



sf_rate_post = sf.sf_rate_sharing(sum_lost_load, demand)

print()
for i in range(n):
    
    print('Self sufficient rate for hytte {:.1g}: {:.4g} %'.format(i+1, sf_rate_post[i]))
    
    
print()
for i in range(n):
    
    print('Estimert forbruk som ikke blir dekt for hytte {:.1g}: {:.5g} kWh'.format(i+1, sum_lost_load[i]*0.25))


b = 0
y = 0

for i in range(n):
    
    b += sum_lost_production[i]*0.25
    y += sum_lost_load[i]*0.25

print()
print('RESULTAT')
print('Total reduksjon i estimert forbruk som ikke blir dekt : {:.5g}kWh'.format(x-y))
print('Relativ total reduskjon i estimert forbruk som ikke blir dekt : {:.3g}%'.format(((x-y)*100)/x))
print('----------------------------------------------------------------')
print('Total reduksjon i bortkastet solenergi: {:.5g}kWh'.format(a-b))
print('Relativ total reduksjon av bortasktet solenergi: {:.3g}%'.format((a-b)*100/a))
print()
print('OVERSIKT OVER ANTALL BUD GJENNOM ÅRET [stk]')
print('----------------------------------------------------------------')
print('pv2pv: {:.5g}'.format(dict_count['pv2pv']))
print('bat2pv: {:.5g}'.format(dict_count['bat2pv']))
print('flex2pv: {:.5g}'.format(dict_count['flex2pv']))
print('pv2bat: {:.5g}'.format(dict_count['pv2bat']))
print('pv2flex: {:.5g}'.format(dict_count['pv2flex']))
print('bat2bat: {:.5g}'.format(dict_count['bat2bat']))
print('flex2bat: {:.5g}'.format(dict_count['flex2bat']))
print('bat2flex: {:.5g}'.format(dict_count['bat2flex']))
print('flex2flex: {:.5g}'.format(dict_count['flex2flex']))

#------------------------------------------------------------------------------------------



#Plotting for bestemte uker
for week in range(20,21):
    
    
    for i in range(n):
    
        ofg_plot.LEC_offgrid_plot(dict_list, demand[i], pv[i], week, i)
    
    
 #ofg_plot.LEC_offgrid_plot(dict_list, demand[0], pv[0], week, 0)
