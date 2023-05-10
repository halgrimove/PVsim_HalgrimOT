 # -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 11:55:50 2023

@author: halgr
"""


#----------------------------------------------------------------------------------

'''
Benytter seg av et bibilotek i python klat PVLIB. ModelChain, Location, PVSystem og TEMPERATUR_MODEL_PARAMETER
er funksjoner på filplasseringene modelchain, location osv... i pvlib-biblioteket.
'''


import pvlib

from pvlib.modelchain import ModelChain
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS


#----------------------------------------------------------------------------------


import pandas as pd
import matplotlib.pyplot as plt


#----------------------------------------------------------------------------------





#INNSTRÅLINGSDATA FRA PVGIS
pvlib_oslo = pd.read_csv("C:/Users\halgr/OneDrive - NTNU/Masteroppgave/Python/Modellering_PvOffgrid/offgrid_Pvlib/input_files/irradiance_oslo.csv", index_col=0)


#GI INPUT DATAENE RETT INDEX
pvlib_oslo.index = pd.to_datetime((pvlib_oslo.index))



#-------------------------------------------------------------------------

#SOLCELLEANLEGGETS PLASSERING
location = Location(latitude=50.94, longitude=10.956, tz='Europe/Berlin', 
                    altitude=80, name = 'Hytta')

#DATABLADVERDIER FOR !ET PANEL! 
celltype = 'monoSi' #MONO-CRYSTALLINE
pDc0 = 400 #Pm
v_mp = 44.1 #Vmp
i_mp = 9.08 #Imp
v_oc = 53.4 #Voc
i_sc = 9.6 #Isc

#PARAMETERE
inverter_max_effekt = 3000
antall_paneler = 15
surface_tilt = 45
surface_azimuth = 180

#-------------------------------------------------------------------------

#TEMPERATURKOEFFISENT FOR CELLENS KORTSLUTNINGSSTRØM
alpha_sc = 0.0005 * i_sc #Effekt
#HVOR 

#TEMPERATURKOEFFISENT FOR ÅPEN KRETS SPENNING (INGEN LAST)
beta_voc = -0.0029 * v_oc


#TEMPERATURKOEFFISENT FOR MAX EFFEKT
gamma_pdc = -0.0037 #0.37%
#HVORDAN MAX EFFEKT ENDRER SEG MED TEMPERATUR (CELSIUS)

antall_paneler = 15 #5 paneler
cells_in_series = 3*10 #10 celler i serie, 6 grupper i parallell (ett panel)

temp_ref = 25 


#-------------------------------------------------------------------------


start= '2021-01-01 00:00'
end= '2021-12-31 23:59'

pvlib_oslo_data = pvlib_oslo[start:end]

#SOLAR POSITIONS
solarpos = location.get_solarposition(times=pd.date_range(start=start, end=end, freq="h"))

angle_of_incidence = pvlib.irradiance.aoi(surface_tilt, surface_azimuth, solarpos.apparent_zenith, solarpos.azimuth)

incident_of_modifier = pvlib.iam.ashrae(angle_of_incidence)

effective_irradiance = pvlib_oslo_data['dni'] * incident_of_modifier + pvlib_oslo_data['dhi'] 

#TEMPERATUR PÅ CELLEN -> HENTET FRA PVGIS
temp_cell = pvlib.temperature.faiman(pvlib_oslo_data['ghi'], pvlib_oslo_data['temp_air'], pvlib_oslo_data['wind_speed'])

#DC PRODUKSJONEN FRA CELLEN
result_dc = pvlib.pvsystem.pvwatts_dc(effective_irradiance, temp_cell, pDc0, gamma_pdc = gamma_pdc, temp_ref = temp_ref)


#-------------------------------------------------------------------------


#BEGRENSINGER PÅ INVERTER
for i in range(len(result_dc)):
    
    if result_dc[i] > inverter_max_effekt:
        
        result_dc[i] = inverter_max_effekt


#-------------------------------------------------------------------------


#PRODUSERT EFFEKT FRA HELE ANLEGGET
result_dc_anlegg = antall_paneler*result_dc

#LAGRE RESULTATENE KLAR TIL BRUK SOM "PRODUKSJONSDATA"
#DC EFFEKT
result_dc_anlegg.to_csv("C:/Users\halgr/OneDrive - NTNU/Masteroppgave/Python/Modellering_PvOffgrid/offgrid_PVsyst/input_files/pv_oslo.csv")



result_dc_anlegg.plot(figsize=(16,9))









