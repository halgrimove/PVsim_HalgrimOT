"""
Created on Mon Feb  6 13:22:08 2023

@author: halgr
"""

#-------------------------------------------------------------------------------------------


import offgrid_model_builder as ofgm
import offgrid_plot as ofgp
import offgrid_analysis as ofga
import offgrid_input_files as ofgi
import season_generator as sg


#-------------------------------------------------------------------------------------------

'''
Denne filen simulerer offgrid-anlegget. Den tar inn input filene og parameterene og bruker enksterne funksjoner
til å modellere energiflyt i anlegget, plotting og tall-analyser

DERSOM DET GJØRES ENDRINGER PÅ PV-ANLEGG (OFFGRID_PVLIB.PV_PRODUCTION), INNSTRÅLINGSDATA (PVGIS)
ELLER FORBRUKSDATA (RAMP), MÅ DE ENKELTE FILENE KJØRES PÅ NY FOR Å OPPDATERE INPUT FILENE TIL 
OFFGRID_SIMULATION. OM IKKE KODENE KJØRS OG INPUT FILENE OPPDATERES, VIL IKKE SIMULERINGSFILEN
REGISTRERE ENDRINGENE.

AC; NEDSTRØMS FOR INVERTER
DC; OPPSTRØMS FOR INVERTER
FORSKJELLEN LIGGER I OM TAPET GJENNOM INVERTER ER INKLUDERT ELLER IKKE
'''

#-------------------------------------------------------------------------------------------


#INPUT TIL SIMULERING
input_file = 4 #1, 2, 3 eller 4 kan velges. Svarer til de ulike kategorihyttene.
week = 31


bruksmønster = 1
#0: bor på hytta 
#1: feriebruk 
#2: annenhver helg 
#3: hver helg


#SEASON_GENERATOR
#Vinterferie; uke 8
#Sommerferie; uke 24 og 29
#Høstferie; uke 40
#Juleferie; uke 51-52


demand, pv = ofgi.offgrid_input(input_file, bruksmønster)


#GJØRE OM INPUTDATAENE TIL KILOWATT 
demand = demand/1000 #AC 
pv = pv/1000 #DC 


#PARAMETERE GJELDENE ANLEGG, kW/kWh
param = {'BatteryCapacity': 20,
                'BatteryEfficiency': .9,
                'BatteryDischargeLimit': 2,
                'InverterEfficiency': .85,
                'timestep': .25,
                'MaxPower': 10,
                'MaxPowerInverter': 3
               }


if (param['MaxPower'] > param['MaxPowerInverter']):

    #Den minste verdien setter begrensningen
    param['MaxPower'] = param['MaxPowerInverter']
    

'''
TIMESTEP; Tidsforskjellen mellom datapunktene i input-filene "demand" og "pv". Dette har stor betydning i energibetrakningene.
Inputfilene (solproduksjon og forbruk) er gitt i Watt og Watt * tidsenehet = Energi. Timestep lik 0.25 viser
til at det er 15 minutter mellom datapunktene i inputfilen. PS! Dette er det interpolert for i filen 
"offgrid_input_files.py". Innstrålingsdataene i PVGIS er opprinnelig timesdata og mens forbruksdataene fra RAMP
er opprinnelig minutt data. 
'''


#-------------------------------------------------------------------------------------------


#SIMULERE ENERGIFLYT, RETURNERER EN DICTIONARY
E = ofgm.offgrid_model(demand, pv, param, return_series=False) 

#PLOTTE RESULTATER FOR EN BESTEMT UKE I SIMULERINGEN
ofgp.offgrid_plot(E, demand, pv, week)

#PRINTE TALL-ANALYSER FRA SIMULERINGEN AV ENERGIFLYT I ANLEGGET
ofga.print_analysis(E, demand, pv, param)


#-------------------------------------------------------------------------------------------




