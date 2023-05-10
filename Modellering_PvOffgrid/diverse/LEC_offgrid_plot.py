# -*- coding: utf-8 -*-
"""
Created on Fri Mar  3 10:06:15 2023

@author: halgr
"""

import matplotlib.pyplot as plt

#-------------------------------------------------------------------------------------------

'''
DENNE FUNKSJONEN PLOTTER RESULTATENE AV ENERGIFLYT-MODELLERINGEN 
'''

#-------------------------------------------------------------------------------------------

def LEC_offgrid_plot(E, demand, pv, week):
    
    
    #-------------------------------------------------------------------------------------------


    fig, axes = plt.subplots(nrows=4, ncols=1, sharex=True, figsize=(17, 6*3), frameon=False,
                             gridspec_kw={'height_ratios': [1.5, 3.5, 2, 0.5], 'hspace': 0.04})
    
    
    '''
    n=len(LevelOfCharge)
    n_vector = np.zeros(n)
    
    
    for i in range (n):
        n_vector[i] = i
    
    axes[0].plot(pv.index, LevelOfCharge, color='black', lw=2)
    axes[1].plot(pv.index, lost_production, color='black', lw=1)
    axes[2].plot(demand.index, lost_load, color='black', lw=1)
    '''
    
    #PLOTTE KUN BESTEMTE UKER -> SLICE LISTEN -> HENTE UT BESTEMTE VERDIER FRA "E"
    sliced_index = (pv.index.isocalendar().week==week)
    #returns true to the week during the year with "week" number.
    
    #Returnerer verdiene i de ukene med TRUE -> ukene med ukenummer "week" 
    pv_sliced = pv[sliced_index]
    demand_sliced = demand[sliced_index]
    
    
    
                
    #VERDIENE I "E" FOR DEN GITTE UKA SOM DET SKAL PLOTTES FOR
    self_consumption_sharing = demand_sliced - E['lost_load'][sliced_index]
    self_consumption = E['inv2load'][sliced_index]
    battery_charging_sliced = E['battery_charging'][sliced_index]
    battery_discharging_sliced = E['battery_discharging'][sliced_index]
    res_pv_sliced = E['res_pv'][sliced_index]
    pv2inv_sliced = E['pv2inv'][sliced_index]
    lost_load_sliced = E['lost_load'][sliced_index]
    store2inv_sliced = E['store2inv'][sliced_index]
    LevelOfCharge = E['LevelOfCharge'][sliced_index]
    inv2grid = E['lost_production'][sliced_index]
    lost_load = E['lost_load'][sliced_index]
    
  
    #EFFEKT PRODUSERT AV SOLCELLEANLEGG   
    axes[0].fill_between(pv_sliced.index, 0, pv_sliced, color='yellow', alpha=.2)
    axes[0].set_ylabel('Power (kW)')
    
    
    #-------------------------------------------------------------------------------------------
    
    
    #ESTIMERT FORBRUK FRA RAMP
    axes[1].plot(demand_sliced.index, demand_sliced, color='black', lw=0.5)  
    
    #EFFEKT FORSYNT FRA ANLEGGET (PV OG BATTERI), EFFEKT UT AV INVERTEREN
    axes[1].fill_between(self_consumption.index, 0, self_consumption, color='blue', alpha=.2) 
    
    axes[1].fill_between(self_consumption_sharing.index, 0, self_consumption_sharing, color='blue', alpha=.1) 
    #Energi fra LEC
    
    #EFFKET SOM IKKE ANLEGGET KLARER Å DEKKE
    axes[1].fill_between(lost_load_sliced.index,0 , -lost_load_sliced, color='red', alpha=.2)
    axes[1].set_ylabel('Power (kW)')
    
    
    #-------------------------------------------------------------------------------------------
    
    
    #BATTERIET LADES OPP
    axes[2].fill_between(battery_charging_sliced.index, 0, battery_charging_sliced, color='green', alpha=.2)
    
    #BATTERIET LADES UT
    axes[2].fill_between(battery_discharging_sliced.index, 0, -battery_discharging_sliced, color='red', alpha=.2)
    axes[2].set_ylabel('Battery charging cycle')
    
    
    #-------------------------------------------------------------------------------------------
  
    
    #BATTERISTATUS
    axes[3].fill_between(LevelOfCharge.index, 0, LevelOfCharge, color='grey', alpha=.2)
    axes[3].set_ylabel('State of Charge (kWh)')
    

    return