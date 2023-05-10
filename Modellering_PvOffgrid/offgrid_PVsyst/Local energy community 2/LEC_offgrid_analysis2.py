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




#-----------------------------------------------------------------------------------------

deltakere = [4, 1] #Kategorihytte på deltakerene 
bruksmønster = [0, 1] #Bruksmønster på deltakerene
#0: bor på hytta, 1: feriebruk, 2: annenhver helg, 3: hver helg

#RAMP-PROFILENE ER RANDOMISERTE! DERFOR FÅR VI IKKE FORDELAKTIG VED SIMULERING AV LIKE HYTTER

demand, pv = lecif.LEC_input_files(deltakere, bruksmønster)


#------------------------------------------------------------------------------------------


K = {}


#Før energideling   
for i in range(len(deltakere)):
             
    K[i] = ofmb_pre.offgrid_model(demand[i], pv[i], param[i], return_series=False)

sf_rate_pre = sf.sf_rate(K, demand)

print('FØR ENERGIDELING')
print('---------------------------------------------------------------------------------------')

print('Bortkastet solenergi for hytte 1: {:.5g} kWh'.format(sum(K[0]['lost_production'])*0.25))
print('Bortkastet solenergi for hytte 2: {:.5g} kWh'.format(sum(K[1]['lost_production'])*0.25))

print()
print('Estimert forbruk som ikke blir dekt for hytte 1: {:.5g} kWh'.format(sum(K[0]['lost_load'])*0.25))
print('Estimert forbruk som ikke blir dekt for hytte 2: {:.5g} kWh'.format(sum(K[1]['lost_load'])*0.25))
print()
print('Self sufficient rate for hytte 1: {:.4g} %'.format(sf_rate_pre[0]))
print('Self sufficient rate for hytte 2: {:.4g} %'.format(sf_rate_pre[1]))

print()

x = (sum(K[0]['lost_load'])+sum(K[1]['lost_load']))*0.25
a = (sum(K[0]['lost_production'])+sum(K[1]['lost_production']))*0.25


#Etter energideling

sum_lost_load = np.zeros(len(deltakere))
sum_lost_production = np.zeros(len(deltakere))

'''
Lager først en tom liste "dict_list". Denne fylles med en dictionary (E) med likt antall dictionaries (E[i]) som antall
deltakere i hyttefeltet stegvis for hvert tidssteg (E[i][timestep] -> Hyttekategori i i tidssteg "timestep"). I hvert tidssteg 
legges det på en en ny E[i][timestep] -> E[i][timestep], E[i][timestep+1], E[i][timestep+2]  osv..


SIMULERING I ET TIDSSTEG (ETABLEREING AV E[i][TIMESTEP], E[j][timestep] osv...):
Først gjøres det en simuelering i EGEN installsjon. Til dette benyttes parametere for eget anleag pv[timestep] og demand[i][timetep] 
samt batterikapasiteten fra forrige tidssteg E[i]['LevelOfCharge'][timestep-1]. Første prioritet er derfor å benytte energi i
eget anlegg. Verdiene "lost_load" (estimert forburk som ikke blir dekt) og "lost_production" (estimert solproduksjon som går til spille)
brukes så videre i MARKEDET. 


ETABLERING AV BUD:
Dersom en hytte har "lost_laod" etter å ha "simulert seg selv", vil anlegget legge ut et bud om å kjøpe. Anlegget kan enten kjøpe
fra andre PV anlegg eller andre batterier.

Dersom en hytte har "lost_production" vil anlegget legge ut et bud om å selge. Anlegget kan enten selge til andre anlegg i underskudd 
eller lade opp andre batterier.

Dersom et batteri er tomt, vil det legge ut et bud om å kjøpe.
Dersom et batteri er fult vil det legge ut et bud om å selge.
Dersom et batteri er mellom tomt og fult vil det fungere som "flex". Det vil legge ut bud om å både kjøpe og selge. Et flex batteri
vil alltid kunne selge til et tomt batteri/kjøpe fra et fult batteri. Flex batterier kan også kjøpe seg i mellom basert på en sammenligning
dem imellom.


ETABLERING AV MARKED:
Alle bud i markedet registreres og indekseres slik at korrekt hytte kan bli hentet frem i det det skal forekomme en handel. Bud fra 
eksempelvis flex-batteri registreres i en indekserings vektor som kan se slik ut -> index_flex_battery: [0, 2, 4]; Noe som vil si at
batteriet til hyttedeltaker med indeks 0, 2 og 4 har et batteri som fungerer som flex (kan både kjøpe og selge).

Prioriteringsrekkefølgen i markedet er slik:
-Anlegg med underskudd i forbruk har førsteprioritet på kjøp. Med "selgere" i prioritert rekkefølge:
    Anlegg med overskudd i sløst solproduksjon, fulle batterier, flex batterier
    
-Anlegg med tomme batterier har andre prioritet på kjøp. Med selgere i prioritert rekkefølge:
    Anlegg med overskudd, fulle batterier, flex batterier
    
-Anlegg med flex batteri har tredjeprioritet på kjøp. Med selgere i prioritert rekkefølge:
    Anlegg med overskudd, fulle batterier, flex batterier (dersom de har høyere batterikapasitet enn kjøpende felx batteri)
    

ENDRING AV ENERGIFLYT-VERDIER    
Denne handelen skjer i hvert tidssteg. Ettersom kraft kjøpes og selges endres verdiene på E[i]['lost_load'], E[i]['lost_production'],
E[i]['LevelOfCharge'] i forhold til simulering av hytte ENKELTVIS UTEN HANDEL. 

'''

dict_list = []

for time in range(0,35037):
    
    
    E = ofmb.E_per_timestep(dict_list, param, time, demand, pv)

    dict_list.append(E)

    


for i in range(0,35037):
    
    for j in range(len(deltakere)):
        
        sum_lost_load[j] += dict_list[i][j]['lost_load'] 
        sum_lost_production[j] += dict_list[i][j]['lost_production']
  
                  
sf_rate_post = sf_sharing.sf_rate_sharing(sum_lost_load, demand)
    
    

print('ETTER ENERGIDELING')
print('---------------------------------------------------------------------------------------')

print()
for i in range(len(deltakere)):
    
    print('Self sufficient rate for hytte {:.1g}: {:.4g} %'.format(i+1, sf_rate_post[i]))

'''
print('Bortkastet solenergi for hytte 1: {:.5g} kWh'.format(sum_lost_production[0]*0.25))
print('Bortkastet solenergi for hytte 2: {:.5g} kWh'.format(sum_lost_production[1]*0.25))
'''
print()

print('Estimert forbruk som ikke blir dekt for hytte 1: {:.5g} kWh'.format(sum_lost_load[0]*0.25))
print('Estimert forbruk som ikke blir dekt for hytte 2: {:.5g} kWh'.format(sum_lost_load[1]*0.25))

print()
print('Self sufficient rate for hytte 1: {:.4g} %'.format(sf_rate_post[0]))
print('Self sufficient rate for hytte 2: {:.4g} %'.format(sf_rate_post[1]))


b = (sum_lost_production[0]+sum_lost_production[1])*0.25
y = (sum_lost_load[0]+sum_lost_load[1])*0.25

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

for week in range(31,32):
    
    ofg_plot.LEC_offgrid_plot(dict_list, demand[0], pv[0], week, 0)
    ofg_plot.LEC_offgrid_plot(dict_list, demand[1], pv[1], week, 1)
    
    
#ofg_plot.LEC_offgrid_plot(dict_list, demand[1], pv[1], 10, 1)

'''
SE PÅ CASEN MED TO HYTTER, SE NÅR DET OVERFØRES FRA BATTERIET OSV
'''

