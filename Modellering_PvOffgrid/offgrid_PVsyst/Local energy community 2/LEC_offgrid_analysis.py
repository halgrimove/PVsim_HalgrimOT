# -*- coding: utf-8 -*-
"""
Created on Fri Mar  3 10:03:48 2023

@author: halgr
"""

import numpy as np

import pv_manipulate as pv_man

import LEC_input_files as lecif
#Fil som inneholder funksjonene som bearbeider input-filene (forburk og produksjon)

import model_builder_per_timestep as ofmb
#Inneholder funksjonen som beregner energiflytsverdier før og etter handel i et tidssteg

import LEC_offgrid_plot as ofg_plot
#Inneholder funksjonene som plotter energiflytsverdier for ønsket antall deltakere og over ønsket tidsrom

import offgrid_plot as offgrid_plot

import offgrid_model_builder as ofmb_pre
#Inneholder funksjoner som beregner energiflytsverdier uten energihandel (basecase)

import sf_rate as sf
#Inneholder funksoner som beregner SF-rate

import matplotlib.pyplot as plt

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
Tapsfaktor i handel er ikke lagt inn i koden. Det ligger inne tapsfaktor på energiflyt i egen 
installasjon før handel. 
'''

#NESTED DICTIONARY AV ANNLEGGSPARAMETERE TIL DELTAKERENE
param = {}


#AKTIVRE ESTIMERING AV TAP I ENERGIHANDELEN (SUMMERES PÅ LOST_LOAD I RESULTATENE)
energihandel_tap_activate = 1

#AKTIVERE ENERGIHANDEL (MÅ AKTIVERES OGSÅ I MODEL_BUILDER_PER_TIMESTEP)
energihandel_activate = 1

param_ex1 = {'BatteryCapacity': 18.45,
                'BatteryEfficiency': 0.95,
                'BatteryDischargeLimit': 2,
                'BatterySellingLimit': 3,
                'InverterEfficiency': 0.95,
                'timestep': .25,
                'MaxPower': 3.36,
                'MaxPowerInverter': 4
               }


n_bat = param_ex1['BatteryEfficiency']
n_inv = param_ex1['InverterEfficiency']


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


#KATEGORIHYTTEFORDELINGEN SOM DET ER SIMULERT FOR I MASTEROPPGAVEN
scenario_d = [1, 2, 3, 4, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 4, 4]

#DE TRE BRUKSMØNSTER-FORDELINGENE SOM DET ER SIMULERT FOR I MASTEROPPGAVEN
scenario_b1 = [1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 2, 2, 3, 1, 1, 1, 1, 1]
scenario_b2 = [1, 1, 1, 1, 3, 3, 1, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 2, 1, 2]
scenario_b3 = [1, 1, 1, 1, 3, 3, 0, 0, 1, 3, 3, 3, 3, 2, 2, 1, 2, 2, 2, 2]

#Hente input-filene med kvartersverdier gjennom et helt år
demand, pv = lecif.LEC_input_files(scenario_d, scenario_b3)

steps = 7
#FUNKSJON SOM FORSYVER ALLE DATAPUNKTENE I LISTEN "STEPS" KVARTER. DET VIRKER SOM AT 
#DET BLIR BRUKT FEILTIDSSONE I DE ORGINALE DATAENE (2 TIMER BAK)
pv = pv_man.pv_forskyvning(pv, steps)

#antall datapunkter
n = len(demand)

#Produsere tekniske parametere for alle deltakerene (alle får like når det gjøres på denne måten)
for i in range(n):

    #Gjør alle hyttene lik eksempelhytta    
    param[i] = param_ex1


#RESULTATER UTEN ENERGIDELING (BASE CASE)
#------------------------------------------------------------------------------------------

K = {}

#Energiflytsverdier uten energideling  
for i in range(n):
             
    K[i] = ofmb_pre.offgrid_model(demand[i], pv[i], param[i], return_series=False)


print()
print('Uten energideling (ÅRLIG RESULTAT):')
print('------------------------------------------')


print()
for i in range(n):
    
    z = sum(K[i]['lost_production'])*0.25 
    
    if z < 0.1:
        
        z = 0
    
    print('Overskuddsenergi {:.2g}: {:.5g} kWh (B:{:.1g}, K:{:.1g})'.format(i+1,z,scenario_b1[i],scenario_d[i]))



sf_rate_pre = sf.sf_rate(K, demand)

print()
print('SF-rate uten energideling (årlig resultat):')
print('------------------------------------------')
for i in range(n):
    
    print('SF-rate for hytte {:.2g}: {:.3g}% (B:{:.1g}, K:{:.1g})'.format(i+1, sf_rate_pre[i], scenario_b1[i], scenario_d[i]))


print()
print('Lost_load uten energideling (årlig resultat):')
print('--------------------------------------------')
for i in range(n):
    
    z = sum(K[i]['lost_load'])*0.25 
    
    if z < 0.1:
        
        z = 0
    
    print('Lost load for hytte {:.2g}: {:.4g} kWh (B:{:.1g}, K:{:.1g})'.format(i+1, z, scenario_b1[i], scenario_d[i]))



x = 0
a = 0
b = 0
sf_rate_pre1 = 0

#Totale verdier gjennom et helt år
for i in range(n):
    
    x += sum(K[i]['lost_load'])*0.25
    a += sum(K[i]['lost_production'])*0.25
    b += sum(demand[i])*0.25

sf_rate_pre1 = ((b-x)/b)*100   

print()
print('Årlig resultat uten energideling:')
print('--------------------------------------------')
print('Totalt estimert forbruk: {:.5g} kWh'.format(b))
print('Estimert forbruk som ikke blir dekt : {:.5g} kWh'.format(x))
print('SF-rate til hele hyttefeltet: {:.3g} %'.format(sf_rate_pre1))
print('Bortkastet solenergi: {:.5g} kWh'.format(a))
print()
print()
print()
print()
print()
print()
print()
print()



#Uke og deltaker som det ønskes plottes for (uten energideling)
week = 40
deltaker = 3

offgrid_plot.offgrid_plot(K[deltaker], demand[deltaker], pv[deltaker], week)


#------------------------------------------------------------------------------------


#ETTER ENERGIDELING
#------------------------------------------------------------------------------------

dict_list = []
sum_lost_load = np.zeros(n)
sum_lost_production = np.zeros(n)
totalt_tap_vec = np.zeros(n)


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

#AKTIVERE ENERGIDELING
if energihandel_activate == 1:

    #BRUKE FUNKSJONEN MODEL_BUILDER_PER_TIMESTEP() TIL Å BEREGNE ENERGIFLYTSVERDIER (E) FOR ALLE DELTAKERNE
    #DETTE SKJER ITERATIVT, DER DET ITERERES KRONOLOGISK GJENNOM ALLE KVARTER GJENNOM ET ÅR
    for time in range(0,35037):
        
        E, dict_count = ofmb.E_per_timestep(dict_list, dict_count, param, time, demand, pv)
    
        dict_list.append(E)
        
    #DERSOM DET ØNSKES Å BEREGNE TAP SOM FØLGE AV ENERGIDELING. DETTE GJØRES ETTER AT DET ER SIMULERT FOR
    #HYTTENE. EN FORENKLING. SE MATEROPPGAVEN FOR MER DETALJER.    
    if energihandel_tap_activate == 1:
    
        #Tap i følge overføring av energi fra/til batteri i handelen
        for j in range(n):
            
                sum_bat_sell = 0
                sum_bat_buy = 0
                sum_pv_buy = 0
                
                for i in range(0,35037):
                
                    #n_inv inkluderes her siden denne energien trekker direkte fra lost load 
                    sum_pv_buy += dict_list[i][j]['pv_buy_pv'] + dict_list[i][j]['pv_buy_battery']
                    
                    sum_bat_buy += dict_list[i][j]['battery_buy_pv'] + dict_list[i][j]['battery_buy_battery']
                    sum_bat_sell += dict_list[i][j]['battery_sell_pv'] + dict_list[i][j]['battery_sell_battery'] 
        
                tap_bat_buy = (1-n_bat)*sum_bat_buy
                tap_bat_sell = (1-n_bat)*sum_bat_sell
                tap_pv_buy = (1-n_inv)*sum_pv_buy*0.25 #converting energy yo power
        
                #Enhet ENERGI
                totalt_tap_vec[j] = tap_bat_buy + tap_bat_sell + tap_pv_buy
                
    
    #BEREGNE TOTALE VERDIER GJENNOM HELE SIMULERINGEN (ET ÅR)
    for i in range(0,35037):
        
        for j in range(n):
            
            sum_lost_load[j] += dict_list[i][j]['lost_load']
            sum_lost_production[j] += dict_list[i][j]['lost_production']
            
    #LEGGE TIL DE ESTIMERTE TAPENE     
    for j in range(n):
        
         sum_lost_load[j] += totalt_tap_vec[j]/0.25
    
    
    for j in range(n):
    
         if (sum_lost_load[j]*0.25 < 0.1):
             
             sum_lost_load[j] = 0
         
         if (sum_lost_production[j]*0.25 < 0.1):
             
             sum_lost_production[j] = 0
    
    
    #SKRIVE UT RESULTATENE I KONTROLLVINDUET. TAP ER TATT MED DERSOM DET ER "AKTIVERT".
    print('ETTER ENERGIDELING (ÅRLIG RESULTAT)')
    print('---------------------------------------------------------------------------------------')
    
    print()
    for i in range(n):
        
        print('Bortkastet solenergi for hytte {:.1g}: {:.5g} kWh (B:{:.1g}, K:{:.1g})'.format(i+1, sum_lost_production[i]*0.25,scenario_b1[i],scenario_d[i]))
    
    
    sf_rate_post = sf.sf_rate_sharing(sum_lost_load, demand)
    
    print()
    for i in range(n):
        
        print('Self sufficient rate for hytte {:.1g}: {:.4g}% (B:{:.1g}, K:{:.1g})'.format(i+1, sf_rate_post[i],scenario_b1[i],scenario_d[i]))
        
        
    print()
    for i in range(n):
        
        print('Estimert forbruk som ikke blir dekt for hytte {:.1g}: {:.5g} kWh (B:{:.1g}, K:{:.1g})'.format(i+1, sum_lost_load[i]*0.25,scenario_b1[i],scenario_d[i]))
    
    
    b = 0
    y = 0
    
    for i in range(n):
        
        b += sum_lost_production[i]*0.25
        y += sum_lost_load[i]*0.25
        
    lost_load_tot = x-y
    lost_production_tot = a-b
    
    #Fjerne (uforklarlige) småfeil som oppstår i koden underveis
    if ((lost_load_tot/lost_production_tot) > 0.995) & ((lost_load_tot/lost_production_tot) < 1.005):
        
        lost_load_tot = lost_production_tot
    
    
    for i in range(n):
        
        z += sum(demand[i])*0.25
    
    sf_rate_post1 = ((z-y)/z)*100
    delta_sf = sf_rate_post1 - sf_rate_pre1
    
    tap_e = sum(totalt_tap_vec)+(lost_production_tot-lost_load_tot-sum(totalt_tap_vec))
    
    print()
    print('Årlig resultat etter energideling:')
    print('----------------------------------------------------------------')
    print('Total reduksjon i estimert forbruk som ikke blir dekt : {:.5g} kWh'.format(lost_load_tot))
    print('Relativ total reduskjon i estimert forbruk som ikke blir dekt : - {:.3g} %'.format(((lost_load_tot)*100)/x))
    print('Endring i SF-rate for hele hyttefeltet: + {:.3g} %'.format(delta_sf))
    print('Tap som følge av økt energiflyt i tilknytning energihandel: {:.5g} kWh'.format(tap_e))
    print()
    print('Total reduksjon i bortkastet solenergi: {:.5g} kWh'.format((lost_production_tot)))
    print('Relativ total reduksjon av bortkastet solenergi: - {:.3g}%'.format((lost_production_tot)*100/a))
    print()
    print()
    print()
    print()
    print()
    print()
    print()
    print()
 
    

    
    print('SF-rate etter energideling (årlig resultat):')
    print('------------------------------------------')
    
    for i in range(n):
        
        
        print('Endring i SF-rate for hytte {:.2g}: {:.2g}% (B:{:.1g}, K:{:.1g})'.format(i+1, (sf_rate_post[i]-sf_rate_pre[i]),scenario_b1[i],scenario_d[i]))
    
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
    
'''
Det er lagt inn et estimat på tapet som oppstår i energihandelen. Dette er gjort ved å se på den totale energien som går ut 
ut av et batteri (bat2pv, bat2bat, bat2flex) og inn (pv2bat, bat2bat, flex2bat). Denne multiplisert med (1-n_bat)

Tilsvarende for total energi som går til å minske lost load (pv2pv, bat2pv, flex2pv), denne multiplisert med(1-n_inv).
DETTE ER GJORT I ETTERKANT AV SIMULERINGEN, SÅ RESULTAT MED TAP VISES I KONTROLLVINDUET, MEN IKKE I PLOTTET
'''


#PLOTTE FOR EN DELTAKER OVER BESTEMTE UKER
for week in range(38,42):
    
    
    #for i in range(n):
    
        ofg_plot.LEC_offgrid_plot(dict_list, demand[10], pv[10], week, 10)

    

#PLOTTE EN UKE FOR EN BESTEMT DELTAKER
#ofg_plot.LEC_offgrid_plot(dict_list, demand[deltaker], pv[deltaker], week, deltaker)

delta_sf = sf_rate_post-sf_rate_pre


#SØYLEDIAGRAM, VISE RESULTATENE I SØYLEDIAGRAM

hytter = np.zeros(20)

for i in range(n):
    
    hytter[i] = i+1


hytter11 = ['F1', 'F2', 'F3', 'F4', 'F1', 'HH1', 'F2', 
          'F2', 'F2', 'F2', 'F2', 'F2', 'AH2', 'AH2', 'HH2',
          'F3', 'F3', 'F3', 'F4', 'F4']


scenario_d = [1, 2, 3, 4, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 4, 4]


hytter22 = ['F1', 'F2', 'F3', 'F4', 'HH1', 'HH1', 'F2', 'HH2', 'HH2', 'HH2', 'AH2', 'AH2', 
            'AH2', 'AH2', 'AH2', 'F3', 'F3', 'AH3', 'F4', 'AH4']

hytter33 = ['F1', 'F2', 'F3', 'F4',  'HH1', 'HH1', 'P2', 'P2', 'F2', 'HH2', 'HH2', 'HH2', 
            'HH2', 'AH2', 'AH2', 'F3', 'AH3', 'AH3', 'AH4', 'AH4']

fig = plt.figure(figsize = (10, 5))
 
# creating the bar plot
#plt.bar(hytter, delta_sf, color ='dodgerblue',
#        width = 0.5)



# Plotting the bars
plt.bar(hytter, sf_rate_pre, label='SF-rate', color='dodgerblue', width=0.4)

# Adding labels, title, and legend
plt.ylabel("SF-rate [%]")
plt.xlabel("Hytter")
plt.title('Bar Chart')
plt.xticks(hytter, hytter11)

plt.title("SF-rate")

plt.legend()

# Display the plot
#plt.show()





