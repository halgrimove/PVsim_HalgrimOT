"""
Created on Thu Feb  2 13:24:34 2023

@author: halgr
"""

import numpy as np
import pandas as pd


#-------------------------------------------------------------------------------------------
   
'''
DENNE FILEN MODELLERER ENERGIFLYT MELLOM ALLE KOMPONENTENE I ANLEGGET OG INSTALLASJONEN (FORBRUK).
DETTE GJØRES FOR HVERT TIDSSTEG OG LAGRES I "E"
'''
   
#-------------------------------------------------------------------------------------------

def offgrid_model(demand, pv, param, return_series=False):
    
    
    #-------------------------------------------------------------------------------------------


    n = len(pv)
    
    
    #FJERNE "FLUER" FRA INPUT DATAENE
    '''
    for i in range(n):
        
        if (pv[i] < 0):
            pv[i] = 0
        
        if (demand[i] < 0.1):
            demand[i] = 0
    '''
    
    #DEFINERE VARIABLER
    bat_size_e_adj = param['BatteryCapacity']
    bat_size_p_adj = param['MaxPower'] #Max effekt batteriet kan lades/utlades med
    n_bat = param['BatteryEfficiency']
    n_inv = param['InverterEfficiency']
    timestep = param['timestep']
    BatteryDischargeLimit = param['BatteryDischargeLimit']
    
    
    pv2inv = np.minimum(pv, demand/n_inv)
    res_pv = np.maximum(pv - demand/n_inv, 0) #Lasten som momentant er større en forbruket for det gitte tidssteget
    inv2load = pv2inv * n_inv
    res_load = (demand - pv2inv * n_inv) #lasten som ikke dekkes av momentan PV
    pv2inv = pv2inv.values
    
    
    #DEKLARERE VEKTORVARIABLENE SOM INNGÅR I BATTERI-LØKKEN
    pv2store = np.zeros(n)
    store2inv = np.zeros(n)
        
    #BATTERISTATUS    
    LevelOfCharge = np.zeros(n)
    LevelOfCharge[0] = bat_size_e_adj*0.8
    
    #-------------------------------------------------------------------------------------------
    
    #LØKKE SOM TAR FOR SEG SITUASJONENE DER DEN MOMENTANE PRODUSKJONEN ER STØRRE ENN DET MOMENTANE FORBRUKET
    #-> OPPLADING AV BATTERI
    for i in range(1,n):
        
        #BATTERIET ER FULT
        if LevelOfCharge[i-1] >= bat_size_e_adj:  
                pv2store[i] = 0 
        
        else: #BATTERIET ER IKKE FULT, MEN VIL OVERSTIGE MAX KAPASITET VED OPPLADING I GITT TIDSSTEG
            if (LevelOfCharge[i-1] + (res_pv[i] * timestep)) > bat_size_e_adj:
                
                #KAN MAX LADE OPP DET SMO ER IGJEN FØR BATTERIET NÅR MAX KAPASITET
                pv2store[i] = min((bat_size_e_adj - LevelOfCharge[i-1]) / timestep, bat_size_p_adj)
                #OPPLADINGEN BEGRENSES AV MAX OPP/UTLADNINGS EFFEKT. "BAT_SIZE_P_ADJ"
                
                
            else: #BATTERIET ER IKKE FULT OG VIL IKKE OVERTIGE MAX KAPASITET VED OPPLADNING I GITT TIDSSTEG
                pv2store[i] = min(res_pv[i], bat_size_p_adj)
         
              
            
        #ENERGIEN SOM FLYTER FRA BATTERI TIL INVERTER MÅ VÆRE TILGJENGELIG ENERGI LAGRET PÅ BATTERIET I FORRIGE TIDSSTEG
        #BATTERIET KAN IKKE LADES UT UNDER "BATTERYDISCHARGELIMIT"
        #DET SOM SOLCELLENE IKKE KLARER Å DEKKE I TIDSSTEGET ("RES_LOAD"), MÅ FOSYNES FRA BATTERIET
        store2inv[i] = min((LevelOfCharge[i-1]/timestep-BatteryDischargeLimit/timestep), res_load[i]/n_inv, bat_size_p_adj)  
        
        #NY BATTERISTATUS
        LevelOfCharge[i] = min(LevelOfCharge[i-1] - (store2inv[i] - pv2store[i]*n_bat) * timestep,  # DC
                               bat_size_e_adj)
    
    
    #-------------------------------------------------------------------------------------------
    
    
    #EFFEKT FRA INVERTER TIL INSTALLSJON. KOMMER !ENTEN! FRA PV ELLER FRA BATTERI. DETTE SKJER IKKE SAMTIDIG
    #FØRSTEPRIORITET ER Å SENDE ENERGI PV->INVERTER, ANDREPRIORITET ER BATTERI->INVERTER
    inv2load = inv2load + store2inv*n_inv
    
    #EFFEKTEN FRA PV SOM BLIR IGJEN ETTER Å HA FORSYNT FORBRUK DIREKTE ("RES_PV") OG LADET OPP BATTERI TIL MAX ("PV2STORE") 
    lost_production = res_pv - pv2store 
    #surplus energy
    
    #EFFEKTEN SOM ANLEGGET (PV OG BATTERI) IKKE KLARER Å DEKKE
    lost_load = demand - inv2load  
    
    #ENERGIFLYT INN/UT AV BATTERI
    battery_charging = pv2store
    battery_discharging = store2inv
        
    #-------------------------------------------------------------------------------------------
    
    #SAMLE RESULTATENE I EN DICTIONARY
    E = {'pv2inv': pv2inv,
                'res_pv': res_pv,
                'pv2store': pv2store,
                'inv2load': inv2load,
                'lost_load': lost_load,
                'store2inv': store2inv,
                'LevelOfCharge': LevelOfCharge,
                'lost_production': lost_production,
                'battery_charging': battery_charging,
                'battery_discharging': battery_discharging
                
                }
    
    #-------------------------------------------------------------------------------------------
    
    #GI ALLE ELEMENTENE I "E" SAMME INDEX SOM "PV" OG "DEMAND". NØDVENDIG FOR PLOTTING.
    if not return_series:
        E_pd = {}
        for k, v in E.items():  # Create dictionary of pandas series with same index as the input pv
            E_pd[k] = pd.Series(v, index=pv.index)
        E = E_pd


    return(E)



