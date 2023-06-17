# -*- coding: utf-8 -*-
"""
Created on Fri Mar  3 10:06:15 2023

@author: halgr
"""

import matplotlib.pyplot as plt
import pandas as pd

#-------------------------------------------------------------------------------------------

'''
DENNE FUNKSJONEN PLOTTER RESULTATENE AV ENERGIFLYT-MODELLERINGEN 
'''

tap_activate = 1

#-------------------------------------------------------------------------------------------

def LEC_offgrid_plot(dict_list, demand, pv, week, deltaker):
    
    
    #-------------------------------------------------------------------------------------------

    
    E = {}
    E['lost_load'] = []
    E['LevelOfCharge'] = []
    E['inv2load'] = []
    E['battery_self_charging'] = []
    E['battery_self_discharging'] = []
    E['battery_sell_battery'] = []
    E['battery_sell_pv'] = []
    E['battery_buy_battery'] = []
    E['battery_buy_pv'] = []
    E['pv_sell_pv'] = []
    E['pv_buy_battery'] = []
    E['pv_sell_battery'] = []
    E['pv_buy_pv'] = []

  
    
    for i in range(0,35037):
        
        E['lost_load'].append(dict_list[i][deltaker]['lost_load'])
        E['LevelOfCharge'].append(dict_list[i][deltaker]['LevelOfCharge'])
        E['inv2load'].append(dict_list[i][deltaker]['inv2load'])
        E['battery_self_charging'].append(dict_list[i][deltaker]['battery_self_charging'])
        E['battery_self_discharging'].append(dict_list[i][deltaker]['battery_self_discharging'])
        E['battery_sell_battery'].append(dict_list[i][deltaker]['battery_sell_battery'])
        E['battery_sell_pv'].append(dict_list[i][deltaker]['battery_sell_pv'])
        E['battery_buy_battery'].append(dict_list[i][deltaker]['battery_buy_battery'])
        E['battery_buy_pv'].append(dict_list[i][deltaker]['battery_buy_pv'])
        E['pv_sell_pv'].append(dict_list[i][deltaker]['pv_sell_pv'])
        E['pv_buy_pv'].append(dict_list[i][deltaker]['pv_buy_pv'])
        E['pv_buy_battery'].append(dict_list[i][deltaker]['pv_buy_battery'])
        E['pv_sell_battery'].append(dict_list[i][deltaker]['pv_sell_battery'])    
     
        
    datetime = pd.date_range(start='2021-01-01 00:00', end='2021-12-31 23:00', freq="15min")
    
    df1 = pd.DataFrame(E['lost_load'], columns=['lost_load'])
    df1.set_index(datetime, inplace=True)
    
    df2 = pd.DataFrame(E['LevelOfCharge'], columns=['LevelOfCharge'])
    df2.set_index(datetime, inplace=True)
    
    df3 = pd.DataFrame(E['inv2load'], columns=['inv2load'])
    df3.set_index(datetime, inplace=True)
    
    df4 = pd.DataFrame(E['battery_self_charging'], columns=['battery_self_charging'])
    df4.set_index(datetime, inplace=True)
    
    df5 = pd.DataFrame(E['battery_self_discharging'], columns=['battery_self_discharging'])
    df5.set_index(datetime, inplace=True)
    
    df6 = pd.DataFrame(E['battery_sell_battery'], columns=['battery_sell_battery'])
    df6.set_index(datetime, inplace=True)
    

    df7 = pd.DataFrame(E['battery_sell_pv'], columns=['battery_sell_pv'])
    df7.set_index(datetime, inplace=True)
    
    
    df8 = pd.DataFrame(E['pv_sell_pv'], columns=['pv_sell_pv'])
    df8.set_index(datetime, inplace=True)
    
    df9 = pd.DataFrame(E['battery_buy_battery'], columns=['battery_buy_battery'])
    df9.set_index(datetime, inplace=True)
    
    df10 = pd.DataFrame(E['pv_buy_battery'], columns=['pv_buy_battery'])
    df10.set_index(datetime, inplace=True)
 
    df11 = pd.DataFrame(E['pv_sell_battery'], columns=['pv_sell_battery'])
    df11.set_index(datetime, inplace=True)
     
    df12 = pd.DataFrame(E['battery_buy_pv'], columns=['battery_buy_pv'])
    df12.set_index(datetime, inplace=True)
    
    df13 = pd.DataFrame(E['pv_buy_pv'], columns=['pv_buy_pv'])
    df13.set_index(datetime, inplace=True)
 
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
    
    self_consumption_col = df3['inv2load']
    lost_load_col = df1['lost_load']
    LevelOfCharge_col = df2['LevelOfCharge']
    battery_self_charging_col = df4['battery_self_charging']
    battery_self_discharging_col = df5['battery_self_discharging']
    battery_sell_battery_col = df6['battery_sell_battery']
    battery_sell_pv_col = df7['battery_sell_pv']
    pv_sell_pv_col = df8['pv_sell_pv']
    pv_sell_battery_col = df11['pv_sell_battery']
    battery_buy_battery_col = df9['battery_buy_battery']
    battery_buy_pv_col = df12['battery_buy_pv']
    pv_buy_battery_col = df10['pv_buy_battery']
    pv_buy_pv_col = df13['pv_buy_pv']
    
                
    #VERDIENE I "E" FOR DEN GITTE UKA SOM DET SKAL PLOTTES FOR
    self_consumption_sharing = demand_sliced - lost_load_col[sliced_index]
    self_consumption = self_consumption_col[sliced_index]
    lost_load_sliced = lost_load_col[sliced_index]
    LevelOfCharge = LevelOfCharge_col[sliced_index]
    
    battery_self_charging = battery_self_charging_col[sliced_index]
    battery_self_discharging = battery_self_discharging_col[sliced_index]
    battery_sell_pv = battery_sell_pv_col[sliced_index]
    battery_sell_battery = battery_sell_battery_col[sliced_index]
    pv_sell_pv = pv_sell_pv_col[sliced_index]
    pv_buy_pv = pv_buy_pv_col[sliced_index]
    pv_sell_battery = pv_sell_battery_col[sliced_index]
    pv_buy_battery = pv_buy_battery_col[sliced_index]
    battery_buy_battery = battery_buy_battery_col[sliced_index]
    battery_buy_pv = battery_buy_pv_col[sliced_index]
    
    
    
    fig, axes = plt.subplots(nrows=3, ncols=1, sharex=True, figsize=(17, 6*3), frameon=False,
                             gridspec_kw={'height_ratios': [1.5, 3.5, 1.5], 'hspace': 0.1})
    
    plt.xlabel('Time', color='black')
    plt.xticks(color='black')
    
    
  
    #EFFEKT PRODUSERT AV SOLCELLEANLEGG   '
    #axes[0].fill_between(pv_sell_pv.index, 0, pv_sell_pv, color='yellow', alpha=.3)
    axes[0].fill_between(pv_sliced.index, 0, pv_sliced, color='yellow', alpha=.2)
    axes[0].plot(pv_sliced.index, pv_sliced, color='black', lw=0.5)
    
    axes[0].fill_between(pv_buy_battery.index, 0, pv_buy_battery, color='green', alpha=.2)
    axes[0].fill_between(pv_buy_pv.index, 0, pv_buy_pv, color='green', alpha=.3)
    
    axes[0].fill_between(pv_sell_pv.index, 0, -pv_sell_pv, color='red', alpha=.2)
    axes[0].fill_between(pv_sell_battery.index, 0, -pv_sell_battery, color='red', alpha=.2)
    
    axes[0].set_ylabel('Power (kW)',color='black')
    plt.ylabel('Power (kW)',color='black')
    plt.yticks(color='black')
    axes[0].tick_params(axis='both', colors='black')
    axes[0].set_title('Produksjon fra eget solcelleanelgg og kjøp/salg fra/til av momentan PV', color='black')
    #-------------------------------------------------------------------------------------------
    
    
    #ESTIMERT FORBRUK FRA RAMP
    axes[1].plot(demand_sliced.index, demand_sliced, color='black', lw=0.5)  
     
    #HVA SOM BLIR DEKT AV FORBURK ETTER KJØP FRA MARKEDET
    axes[1].fill_between(self_consumption_sharing.index, 0, self_consumption_sharing, color='blue', alpha=.2) 
    plt.yticks(color='black')
  
    #EFFKET SOM IKKE ANLEGGET KLARER Å DEKKE
    #axes[1].plot(lost_load_sliced.index, -(lost_load_sliced), color='black', lw=0.5)
    axes[1].fill_between(lost_load_sliced.index,0 , -(lost_load_sliced), color='red', alpha=.2)
    
    axes[1].set_ylabel('Power (kW)',color='black')
    plt.ylabel('Power (kW)',color='black')
    plt.yticks(color='black')
    axes[1].tick_params(axis='both', colors='black')
    axes[1].set_title('Dekt, ikke-dekt last og estimert forbruk i egen installasjon', color='black')
    
    #BATTERISTATUS
    #axes[2].plot(LevelOfCharge.index, LevelOfCharge, color='black', lw=0.5)
    axes[2].fill_between(LevelOfCharge.index, 0, LevelOfCharge, color='grey', alpha=.2)
    axes[2].set_ylabel('State of Charge (kWh)',color='black')
    plt.ylabel('Energy (kWh)',color='black')
    plt.yticks(color='black')
    axes[2].tick_params(axis='both', colors='black')
    axes[2].set_title('Batteristatus', color='black')
    
    fig, axes = plt.subplots(nrows=3, ncols=1, sharex=True, figsize=(17, 6*3), frameon=False,
                             gridspec_kw={'height_ratios': [1.5, 3.5, 1.5], 'hspace': 0.1})
    
    
    plt.xlabel('Time', color='black')
    plt.xticks(color='black')
    

    #EFFEKT SOM BATTERIET SELLER TIL PV-ANLEGG OG ANDRE BATTERIER I NETTVERKET
    axes[0].fill_between(battery_sell_pv.index, 0, -battery_sell_pv, color='yellow', alpha=.4)
    axes[0].plot(battery_sell_pv.index, -battery_sell_pv, color='black', lw=0.2)
    axes[0].fill_between(battery_sell_battery.index, 0, -battery_sell_battery, color='green', alpha=.4)
    
    axes[0].set_ylabel('Energy (kW)',color='black')
    axes[0].tick_params(axis='both', colors='black')
    axes[0].set_title('Salg fra eget batteri til PV-anlegg/batteri hos andre deltakere', color='black')
  
    
    #EFFEKT SOM BATTERIET KJØPER FRA ANDRE PV-ANLEGG OG ANDRE BATTERIER I NETTVERKET
    axes[1].fill_between(battery_buy_pv.index, 0, battery_buy_pv, color='yellow', alpha=.2)
    axes[1].fill_between(battery_buy_battery.index, 0, battery_buy_battery, color='green', alpha=.3)
    
    axes[1].set_ylabel('Power (kW)',color='black')
    plt.ylabel('Energy (kWh)')
    axes[1].tick_params(axis='both', colors='black')
    axes[1].set_title('Kjøp til eget batteri fra andre deltakeres PV/batteri', color='black')
    
    #axes[2].plot(LevelOfCharge.index, LevelOfCharge, color='black', lw=0.5)
    axes[2].fill_between(LevelOfCharge.index, 0, LevelOfCharge, color='grey', alpha=.2)
    axes[2].set_ylabel('State of Charge (kWh)',color='black')
    plt.ylabel('Energy (kWh)')
    axes[2].tick_params(axis='both', colors='black')
    axes[2].set_title('Batteristatus', color='black')
    
    return



'''
axes[0].plot(battery_self_charging.index, battery_self_charging, color='black', lw=0.5)
axes[0].fill_between(battery_self_charging.index, 0, battery_self_charging, color='green', alpha=.2)
axes[0].plot(battery_self_discharging.index, -battery_self_discharging, color='black', lw=0.5)
axes[0].fill_between(battery_self_discharging.index, 0, -battery_self_discharging, color='red', alpha=.2)
'''



