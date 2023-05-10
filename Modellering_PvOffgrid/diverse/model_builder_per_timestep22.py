# -*- coding: utf-8 -*-
"""
Created on Mon May  1 08:43:31 2023

@author: halgr
"""

import numpy as np
import pandas as pd
import LEC_input_files as lecif
import trade_pv2pv as trade_pv2pv
import trade_flex2pv as trade_flex2pv
import trade_batt2pv as trade_batt2pv
import trade_pv2batt as trade_pv2batt

flex_limit = 0.5

def E_per_timestep(dict_list, param, time, demand, pv):

    
    E = {}
    bidding_battery = {}
    bidding_pv = {}
    
    return_series = True
    deltakere_n = len(param)
    
    max_transfer = 3

    

    for x in range(len(param)):
        
        discharge_limit = param[x]['BatteryDischargeLimit']
        #LAVESTE MULIGE BATTERISTATUS
        
        
        if time == 0:
            
            LevelOfCharge_previous = 0.8*param[x]['BatteryCapacity']
            #BATTERINIVÅ VED FØRSTE TIDSSTEG
        
        else:
        
            LevelOfCharge_previous = dict_list[time-1][x]['LevelOfCharge']
            
            
        if LevelOfCharge_previous < discharge_limit:
            
            LevelOfCharge_previous = discharge_limit    
    
        
        #FJERNE "FLUER" FRA INPUT DATAENE
        if (pv[x][time] < 0):
                pv[x][time] = 0
            
        if (demand[x][time] < 0.1):
                demand[x][time] = 0
        
        
        #DEFINERE VARIABLER
        battery_capacity = param[x]['BatteryCapacity']
        max_power = param[x]['MaxPower'] #Max effekt batteriet kan lades/utlades med
        n_bat = param[x]['BatteryEfficiency']
        n_inv = param[x]['InverterEfficiency']
        timestep = param[x]['timestep']
        
        
        #ENERGIFLYTVARAIBLER
        pv2inv = np.minimum(pv[x][time], demand[x][time]/n_inv)
        res_pv = np.maximum(pv[x][time] - demand[x][time]/n_inv, 0) #Lasten som momentant er større en forbruket for det gitte tidssteget
        inv2load = pv2inv * n_inv
        res_load = (demand[x][time] - pv2inv * n_inv) #lasten som ikke dekkes av momentan PV
        #pv2inv = pv2inv.values
        
    
        
        #-------------------------------------------------------------------------------------------
            
        #HYTTA FORSYNER FØRST SEG SELV. 
        if LevelOfCharge_previous >= battery_capacity:  
                    pv2store = 0 
            
        else: #BATTERIET ER IKKE FULT, MEN VIL OVERSTIGE MAX KAPASITET VED OPPLADING I GITT TIDSSTEG
                if (LevelOfCharge_previous + (res_pv * timestep)) > battery_capacity:
                    
                    #MAX_POWER BEGRENSER HURTIGHETEN BATTERIET LADES OPP MED
                    pv2store = min((battery_capacity - LevelOfCharge_previous) / timestep, max_power)
                    
                    
                    
                else: #BATTERIET ER IKKE FULT OG VIL IKKE OVERTIGE MAX KAPASITET VED OPPLADNING I GITT TIDSSTEG
                    
                    #OPPLADNINGEN BEGRENSES AV MAX_POWER
                    pv2store = min(res_pv, max_power)
             
                  
        #ENERGI SOM FLYTER FRA BATTERI TIL INVERTER I GITT TIDSSTEG
        #BEGRENSES AV MAX_POWER        
        store2inv = min((LevelOfCharge_previous/timestep-discharge_limit/timestep), res_load/n_inv, max_power)  
            
        
        #LADE OPP EGET BATTERI MED DEN ENEGIEN SOM GÅR TIL BATTERIET SOM IKKE GÅR VIDERE TIL INVERTEREN
        LevelOfCharge = min(LevelOfCharge_previous - (store2inv - pv2store*n_bat) * timestep,  # DC
                                   battery_capacity, max_power*timestep)
        
        
        
        #-------------------------------------------------------------------------------------------
        
        
        inv2load = inv2load + store2inv*n_inv
        lost_production = res_pv - pv2store #som kan selges
        #print(lost_production)
        lost_load = demand[x][time] - inv2load  
        
        
        #DEKLARERE VARIABLER FOR PLOTTING 
        battery_self_charging = pv2store
        battery_self_discharging = store2inv
        
        battery_transfer_charging = 0
        battery_transfer_discharging = 0
        pv_self_charging = pv2store
        pv_transfer_charging = 0
        pv_transfer_pv = 0
    
        pv_self_charging = 0
        pv_transfer_batterycharging = 0
        pv_transfer_pv = 0
        pv_self_pv = pv2inv
        
        #--------------------------------------------------------------------------------------------
        
        #FJERNE FLUER
        if lost_load < 0.001:
            
            lost_load == 0
            
        if lost_production < 0.001:
            
            lost_production == 0
        
        #-------------------------------------------------------------------------------------------
        
        #SAMLE RESULTATENE I EN DICTIONARY SOM ANGIR STATUS PÅ HYTTE ETTER Å HA FORSYNT SEG SELV OG 
        #KAN EVENTUELT DELE/KJØPE ENERGI
        
        
        E[x] = {'pv2inv': pv2inv,
                    'res_pv': res_pv,
                    'pv2store': pv2store,
                    'inv2load': inv2load,
                    'lost_load': lost_load,
                    'store2inv': store2inv,
                    'LevelOfCharge': LevelOfCharge,
                    'lost_production': lost_production,
                    'battery_self_charging': battery_self_charging,
                    'battery_self_discharging': battery_self_discharging,
                    'battery_sell_battery': battery_transfer_charging,
                    'battery_sell_pv': pv_transfer_batterycharging,
                    'battery_buy_battery': battery_transfer_discharging,
                    'pv_buy_battery': pv_transfer_batterycharging,
                    'pv_sell_battery': pv_transfer_batterycharging,
                    'pv_sell_pv': pv_transfer_pv, 
                    'battery_buy_pv': pv_transfer_batterycharging,
                    'pv_buy_pv': pv_transfer_pv, 
                    }
        
        
        
        #BUDENE HYTTE X LEGGER UT
        
        if lost_production < 0.01:
            lost_production = 0
            
        if lost_load < 0.01:
            lost_load = 0
        
       
        if ((LevelOfCharge < battery_capacity) & (LevelOfCharge > discharge_limit)) :      
        
                      bidding_battery[x] = 3 #KAN KJØPE OG SELGE, MELLOMTING!
        
        else:
            if LevelOfCharge == discharge_limit: 
          
          
                bidding_battery[x] = 1 #BUY
          
            else:
                if LevelOfCharge == battery_capacity:
                                  
                    bidding_battery[x] = 2 #SELL
             
        if (lost_production > 0): #SELL -> Det er noe til overs etter å ha forsynt eget anlegg og batteri
              
               bidding_pv[x] = 2 #sell
                   
        else: 
            if (lost_load > 0): 
                    
                  
                       
                   bidding_pv[x] = 1 #buy
  
            else:
                
                bidding_pv[x] = 0 #Ingen handel
        #-------------------------------------------------------------------------------------------
        
        #GI ALLE ELEMENTENE I "E" SAMME INDEX SOM "PV" OG "DEMAND". NØDVENDIG FOR PLOTTING.
        if not return_series:
            E_pd = {}
            for k, v in E.items():  # Create dictionary of pandas series with same index as the input pv
                E_pd[k] = pd.Series(v, index=pv.index)
            E = E_pd
    

    #ALLE HYTTENE HAR NÅ FORSYNT SEG SELV I TIDSSTEGET, OG KAN POTENISELT SAMHANDEL MED ANDRE
    
    
    
    #FÅ OVERSIKT OVER HVILKE HYTTER (INDEKSER I VEKTOREN) SOM LEGGER UT HVILKET BUD
    
    count_sellers_pv = 0
    count_buyers_pv = 0
    count_sellers_battery = 0
    count_buyers_battery = 0
    count_buyers_battery_flex = 0
    count_sellers_battery_flex = 0
    count_flex_battery = 0
    
    energy_profit_pv = np.zeros(deltakere_n)
    energy_demand_pv = np.zeros(deltakere_n)
    energy_profit_battery = np.zeros(deltakere_n)
    energy_demand_battery = np.zeros(deltakere_n)
    
    index_seller_pv = []
    index_buyer_pv = []
    index_seller_battery = []
    index_buyer_battery = [] #default like mange som antall deltakere
    index_flex_buy_battery = []
    index_flex_sell_battery = []
    index_flex_battery = []
    
    flex_lower_limit = 0
    felx_upper_limit = 0
    
    for j in range(len(param)):  
        
        
        lost_production = E[j]['lost_production'] #BORTKASTET SOLENERGI
        res_load = E[j]['lost_load'] #LAST SOM IKKE BLIR DEKKET
        LevelOfCharge = E[j]['LevelOfCharge'] #BATTERISTATUS ETTER Å HA EVENTUELT LADET SEG SELV
        discharge_limit = param[j]['BatteryDischargeLimit'] #MINUM BATTERNIVÅ
        battery_capacity = param[j]['BatteryCapacity'] #MAX OPP/UTLADNINGSEFFEKT AV BATTERI
        max_power = param[0]['MaxPower']
        
        '''
        #FJERNE FLUER
        if res_load < 0.01:
            res_load = 0
            
        if lost_production < 0.01:
            lost_production = 0
        '''
    
        if bidding_pv[j] == 2: #SELGE
        
            
            count_sellers_pv += 1
            energy_profit_pv[j] = lost_production
                     
            index_seller_pv.append(j)
                
            
        else:
            if (bidding_pv[j] == 1): #KJØPE
            
                
                count_buyers_pv += 1
                energy_demand_pv[j] = res_load
                
                
                index_buyer_pv.append(j)
                
                
                #BIDDINGSTATUS == 0 -> HAR IKKE BEHOV FOR Å KJØPE ELLER SELGE
                
               
        if bidding_battery[j] == 2: #SELGE VED FULLADA BATTERI
         
             count_sellers_battery += 1
             index_seller_battery.append(j)
    
             
        else:
             if (bidding_battery[j] == 1): #KJØPE
             
                 count_buyers_battery += 1 
                 index_buyer_battery.append(j)
                 
                 
            #batteriet lades opp/ut ettersom hva som blir igjen
            
             else:
                if (bidding_battery[j] == 3):
                    
             
                    count_flex_battery += 1 
                    index_flex_battery.append(j)
          
                             
    #HAR NÅ OVERSIKT OVER STATUS PÅ ANLEGG ETTER Å HA FORYNT SEG SELV OG HVILKE BUD SOM HAR BLITT
    #LAGT UT AV HVEM I MARKEDET
    
    sum_energy_profit_pv = sum(energy_profit_pv)
    sum_energy_demand_pv = sum(energy_demand_pv)
    
    '''
    if time == 27507:
        
        print('Time {:.5g}'.format(time))
        print('----------------------')
        print('Batteri:')
        print('Selger:', index_seller_battery)
        print('Kjøper:', index_buyer_battery)
        print('----------------------')
        print('Anlegg:')
        print('Selger:', index_seller_pv)
        print('Kjøper:', index_buyer_pv)
        print('----------------------')
        print('Flex-Batteri')
        print(index_flex_battery)
        print()
    '''    
        
    '''
    if (count_buyers_pv > 1) & (count_flex_battery > 1):
            
            print(time)
    '''
    
    #if ((sum_energy_demand_pv < sum_energy_profit_pv) & (sum_energy_demand_pv*sum_energy_profit_pv != 0)):
    
    '''    
    #UTVEKSLING AV PV-ENERGI SOM FØRSTE PROIRITET
    print(count_buyers_pv)
    print(count_sellers_pv)
    print(E[0]['lost_load'])
    print()
    '''
    
   
    '''
    SIDEN ANLEGGET FØRST FORSYNER SEG SELV GÅR PV TIL Å LADE OPP BATTERIET, DERFOR ER DET SJELDENT OVERSKUDDS-PV IGJEN
    NÅR MARKEDET KLARERERS. DET ER OBSERVERT AT NÅR FLEX_LIMIT ER UNDER 1, VIL ALDRI BATTERI STÅ  FULLE, NOE SOM
    VIL SI AT EGEN OVERSKUDDS-PV BRUKES TIL Å LADE EGET BATTERI, FOR SÅ AT BATTERIET SELGER SIN ENERGI TIL FLEX_LIMIT NÅS.
    VED Å SETTE FLEX_LIMIT LIK 100% FÅR VI PV-UTVEKSLING MELLOM ANLEGGSDELENE
    '''
    

    
    if (count_buyers_pv != 0) & (sum_energy_demand_pv != 0):
  
        
        seller_transfer, buyer_transfer, rest_profit, rest_demand = trade_pv2pv.trade_pv2pv(sum_energy_profit_pv, sum_energy_demand_pv, index_buyer_pv, index_seller_pv, count_buyers_pv, count_sellers_pv, len(param), E)
        
        for j in index_seller_pv:
            
            for i in index_buyer_pv:
                
                #print('pv2pv')
                '''
                transfer = min(E[j]['lost_production']/count_buyers_pv, E[i]['lost_load'], max_transfer)
                transfer = max(transfer,0)
                '''
                
                E[j]['lost_production'] -= seller_transfer[j]
                E[j]['pv_sell_pv'] += seller_transfer[j]
                #SIDEN FØRSTE PRIORITET LIGGER I EGET ANLEGG, VIL OVERSKUDDSPV BRUKES TIL Å LADE OPP EGET BATTERI
                #OG DENNE VIL VÆRE TILNÆRMET NULL
                
                E[i]['lost_load'] -= buyer_transfer[i]
                E[i]['pv_buy_pv'] += buyer_transfer[i]
                
                
                sum_energy_demand_pv = rest_demand
                sum_energy_profit_pv = rest_profit
               
                '''
                E[j]['lost_production'] -= transfer
                E[j]['pv_sell_pv'] += transfer
                #SIDEN FØRSTE PRIORITET LIGGER I EGET ANLEGG, VIL OVERSKUDDSPV BRUKES TIL Å LADE OPP EGET BATTERI
                #OG DENNE VIL VÆRE TILNÆRMET NULL
                
                E[i]['lost_load'] -= transfer
                E[i]['pv_buy_pv'] += transfer
                '''
                             
               
                if E[i]['lost_load'] < 0:
                    
                    E[i]['lost_load'] = 0     
        
                if E[j]['lost_production'] <= 0:
                    
                    index_seller_pv.remove(j)
                    break
                    
                if E[i]['lost_load'] <= 0:
                    
                    index_buyer_pv.remove(i)
                    
        
        seller_trade, buyer_trade, rest_profit, rest_demand  = trade_batt2pv.trade_batt2pv(sum_energy_profit_pv, sum_energy_demand_pv, index_buyer_pv, index_seller_battery, count_buyers_pv, count_sellers_battery, len(param), E, param)
        #seller_trade in energy
        #buyer_trade in power        
       
        for j in index_seller_battery:
            
            for i in index_buyer_pv:
                
                #print('batt2pv')
                '''
                transfer = min((E[j]['LevelOfCharge']-discharge_limit)/(count_buyers_pv), E[i]['lost_load']*0.25, max_transfer*0.25)
                transfer = max(transfer,0)
               '''
                
               
                '''
                E[j]['LevelOfCharge'] -= transfer
                E[j]['battery_sell_pv'] += transfer

                E[i]['lost_load'] -= transfer/0.25
                E[i]['pv_buy_battery'] += transfer/0.25        
                '''
                
                E[j]['LevelOfCharge'] -= seller_trade[j]
                E[j]['battery_sell_pv'] += seller_trade[j] #energy
                
                E[i]['lost_load'] -= buyer_trade[i]
                E[i]['pv_buy_battery'] += buyer_trade[i] #power       
                
                sum_energy_demand_pv = rest_demand
                sum_energy_demand_pv = rest_profit
                
                if E[j]['LevelOfCharge'] <= discharge_limit:
                    
                    index_seller_battery.remove(j)
                    break
                    
                if E[i]['lost_load'] <= 0:
                    
                    index_buyer_pv.remove(i)
                
      
        
        seller_trade, buyer_trade, rest_profit, rest_demand  = trade_flex2pv.trade_flex2pv(time, sum_energy_profit_pv, sum_energy_demand_pv, index_buyer_pv, index_flex_battery, count_buyers_pv, count_flex_battery, len(param), E, param)
        #seller_trade in energy
        #buyer_trade in power
        
       
        
        for j in index_flex_battery:
            #print('flex2pv')
            
                if (E[j]['LevelOfCharge'] > flex_limit*battery_capacity):
                
                    for i in index_buyer_pv:
                        
                        #print('flex2pv')    
                        '''
                        transfer = min((E[j]['LevelOfCharge']-discharge_limit)/(count_buyers_pv), E[i]['lost_load']*0.25, max_transfer*0.25)
                        transfer = max(transfer,0)
                        print(transfer)
                        '''
                        
                    
                         
                        E[j]['LevelOfCharge'] -= seller_trade[j]/count_buyers_pv
                        E[j]['battery_sell_pv'] += seller_trade[j]/count_buyers_pv
                        
                        E[i]['lost_load'] -= seller_trade[j]/count_buyers_pv/0.25
                        E[i]['pv_buy_battery'] += seller_trade[j]/count_buyers_pv/0.25        
                        
                        
                        sum_energy_demand_pv = rest_demand
                        sum_energy_demand_pv = rest_profit
                        
                        '''
                        E[j]['LevelOfCharge'] -= transfer
                        E[j]['battery_sell_pv'] += transfer
                        
                        E[i]['lost_load'] -= transfer
                        E[i]['pv_buy_battery'] += transfer    
                        '''
                        
                        
                        if E[j]['LevelOfCharge'] <= discharge_limit:
                            
                            index_flex_battery.remove(j)
                            break
                    
                        
                        
                        if E[i]['lost_load'] <= 0:
                            
                            E[i]['lost_load'] = 0
                            index_buyer_pv.remove(i)     
                        
                        '''            
                        if time == 27507:
                                        
                                        print()
                                        print('ETTER ENERGIDELING')
                                        print('------------------------------------------------------------')
                                        print('Batteristatus for hytte 2: {:.5g} kWh'.format(E[2]['LevelOfCharge']))
                                        print('Batteristatus for hytte 3: {:.5g} kWh'.format(E[3]['LevelOfCharge']))
                                        print('Batteristatus for hytte 4: {:.5g} kWh'.format(E[4]['LevelOfCharge']))
                                        print('Estimert forburk som ikke blir dekt for hytte 0: {:.5g} kW'.format(E[0]['lost_load']))
                                        print('Estimert forburk som ikke blir dekt for hytte 1: {:.5g} kW'.format(E[1]['lost_load']))
                        '''                
                                  
                
    if  count_buyers_battery != 0:

        #ANLEGG MED OVERSKUDD SOM FØRSTEPRIORITET?
        seller_trade, buyer_trade, rest_profit, rest_demand = trade_pv2batt.trade_pv2bat(sum_energy_profit_pv, sum_energy_demand_pv, index_buyer_pv, index_flex_battery, count_buyers_pv, count_flex_battery, len(param), E, param)        

        for j in index_seller_pv:
            
            for i in index_buyer_battery:
                
                #print('pv2bat')
                '''
                transfer = min(E[j]['lost_production']/count_buyers_battery, E[i]['LevelOfCharge']*0.25, max_transfer)
                transfer = max(transfer,0)
                '''
                
                E[j]['lost_production'] -= seller_trade[j]
                E[j]['pv_sell_battery'] += seller_trade[j]
                
            
                E[i]['LevelOfCharge'] += buyer_trade[i]
                E[i]['battery_buy_pv'] += buyer_trade[i]
               
               
                if E[i]['lost_load'] < 0:
                    
                    E[i]['lost_load'] = 0     
        
                if E[j]['lost_production'] == 0:
                    
                    index_seller_pv.remove(j)
                    break
                    
                if E[i]['LevelOfCharge'] <= discharge_limit:
                    
                    index_buyer_battery.remove(i)
                    
                    
    

        for j in index_seller_pv:
            
            for i in index_flex_battery:
                
                if (count_flex_battery != 0) & (E[i]['lost_load'] != 0):
                
                
                    #print('pv2flex')
                    transfer = min(E[j]['lost_production']/count_flex_battery, E[i]['LevelOfCharge']*0.25, max_transfer)
                    transfer = max(transfer,0)
                    E[j]['lost_production'] -= transfer
                    E[j]['pv_sell_battery'] += transfer
                    
                    
                    
                    E[i]['LevelOfCharge'] += transfer/0.25
                    E[i]['battery_buy_pv'] += transfer/0.25
                   
                   
                    if E[i]['lost_load'] < 0:
                        
                        E[i]['lost_load'] = 0     
            
                    if E[j]['lost_production'] <= 0:
                        
                        index_seller_pv.remove(j)
                        break
                        
                    if E[i]['LevelOfCharge'] > 0.8*battery_capacity:
                        
                        index_flex_battery.remove(i)
                        break
                                


    if count_buyers_battery != 0:

        for j in index_seller_battery:
            
            for i in index_buyer_battery:
                
                #print('bat2bat')
                transfer = min((E[j]['LevelOfCharge']-discharge_limit)/(count_buyers_battery), (battery_capacity - E[i]['LevelOfCharge'] - discharge_limit), max_transfer*0.25)
                transfer = max(transfer,0)
                E[j]['LevelOfCharge'] -= transfer
                E[j]['battery_sell_battery'] += transfer
                
                E[i]['LevelOfCharge'] += transfer
                E[i]['battery_buy_battery'] += transfer       
                
                if E[j]['LevelOfCharge'] <= discharge_limit:
                    
                    index_seller_battery.remove(j)
                    break
                    
                if E[i]['LevelOfCharge'] >= battery_capacity:
                    
                    index_buyer_battery.remove(i)
        
                
        #FLEX BATTERI SOM SELGER           
        for j in index_flex_battery:
            
            #GRENSE FOR NÅR ET FLEXBATTERI KAN SELGE
            if (E[j]['LevelOfCharge'] > flex_limit*battery_capacity) & (E[j]['lost_load'] != 0):
            
                for i in index_buyer_battery:
                    
                    #print('flex2bat')
                    transfer = min((E[j]['LevelOfCharge']-discharge_limit)/(count_buyers_battery), (battery_capacity - E[i]['LevelOfCharge'] - discharge_limit), max_transfer*0.25)
                    transfer = max(transfer,0)
                    E[j]['LevelOfCharge'] -= transfer
                    E[j]['battery_sell_battery'] += transfer
                    
                    E[i]['LevelOfCharge'] += transfer
                    E[i]['battery_buy_battery'] += transfer       
                    
                    if E[j]['LevelOfCharge'] <= 0.3*battery_capacity:
                        
                        index_flex_battery.remove(j)
                        break
                        
                    if E[i]['LevelOfCharge'] > battery_capacity:
                        
                        index_buyer_battery.remove(i)
                        
           
     
        
    if count_flex_battery != 0:
        
        for j in index_seller_battery:
            
            #FLEX BATTERI SOM KJØPER
            for i in index_flex_battery:
                
                if (count_flex_battery != 0) & (E[i]['lost_load'] != 0):
                #FLEX-BATTERIET MÅ HA UNDER 50% KAPASITET FOR Å KJØPE
                
                        
                    #print('bat2flex')
                    transfer = min((E[j]['LevelOfCharge']-discharge_limit)/(count_flex_battery), (battery_capacity - E[i]['LevelOfCharge'] - discharge_limit), max_transfer*0.25)
                    transfer = max(transfer,0)
                    E[j]['LevelOfCharge'] -= transfer
                    E[j]['battery_sell_battery'] += transfer
                    
                    E[i]['LevelOfCharge'] += transfer
                    E[i]['battery_buy_battery'] += transfer       
                    
                    if E[j]['LevelOfCharge'] <= discharge_limit:
                        
                        index_seller_battery.remove(j)
                        break
                        
                    if E[i]['LevelOfCharge'] >= battery_capacity:
                        
                        index_flex_battery.remove(i)
    
    
                #FELXBATTERI SOM SELGER TIL FLEXBATTERI  
        
       
        for j in index_flex_battery:
                
                
                count_flex_buy = 0
            
                for i in index_flex_battery:
                    
                    
                    #print('flex2flex')
                    if E[j]['LevelOfCharge'] == E[i]['LevelOfCharge']:
                        break
                    
                    else:
                        
                        if (E[j]['LevelOfCharge'] > E[i]['LevelOfCharge'])  & (E[j]['LevelOfCharge'] > flex_limit*battery_capacity) & (E[i]['lost_load'] != 0):
                           #anlegg i kjøper fra j 
                            
                            #for k in index_flex_battery:
                                
                                #if (E[k]['LevelOfCharge'] < E[j]['LevelOfCharge']) & (E[k]['LevelOfCharge'] < 0.5*battery_capacity) & (E[j]['LevelOfCharge'] > 0.5*battery_capacity) & (E[k]['lost_load'] != 0):
                                #Hvor mange som vil kjøpe fra anlegg j
                                    count_flex_buy += 1  
                                
                                    
                                    '''
                                    LAGT INN AT KUN FLEX BATTERI MED STATUS UNDER 50% KAN KJØPE, og at batteri med status over 50% kan selge
                                    '''
                                    
                                    transfer = min((E[j]['LevelOfCharge']-discharge_limit)/(count_flex_buy), (battery_capacity - E[i]['LevelOfCharge'] - discharge_limit), max_transfer*0.25)
                                    transfer = max(transfer,0)
                                    
                                    E[j]['LevelOfCharge'] -= transfer
                                    E[j]['battery_sell_battery'] += transfer
                                    
                                    
                                    E[i]['LevelOfCharge'] += transfer
                                    E[i]['battery_buy_battery'] += transfer       
                                    
                                    if E[j]['LevelOfCharge'] <= discharge_limit:
                                        
                                        index_flex_battery.remove(j)
                                        break
                                        
                                    if E[i]['LevelOfCharge'] >= battery_capacity:
                                        
                                        index_flex_battery.remove(i)
             
                        else:
                        
                            if (E[j]['LevelOfCharge'] < E[i]['LevelOfCharge']) & (E[i]['LevelOfCharge'] > flex_limit*battery_capacity) & (E[j]['lost_load'] != 0):
                            
                                #for k in index_flex_battery:
                                    
                                    #if (E[k]['LevelOfCharge'] < E[i]['LevelOfCharge']) & (E[k]['LevelOfCharge'] < 0.5*battery_capacity) & (E[j]['LevelOfCharge'] > 0.5*battery_capacity) & (E[k]['lost_load'] != 0):
                                    
                                        count_flex_buy += 1  
                                        
                            
                                        transfer = min((E[j]['LevelOfCharge']-discharge_limit)/(count_flex_buy), (battery_capacity - E[j]['LevelOfCharge'] - discharge_limit), max_transfer*0.25)
                                        transfer = max(transfer,0)
                                        E[i]['LevelOfCharge'] -= transfer
                                        E[i]['battery_sell_battery'] += transfer
                                        
                                        E[j]['LevelOfCharge'] += transfer
                                        E[j]['battery_buy_battery'] += transfer       
                                        
                                        if E[i]['LevelOfCharge'] <= discharge_limit:
                                            
                                            index_flex_battery.remove(i)
                                            
                                            
                                        if E[j]['LevelOfCharge'] >= battery_capacity:
                                            
                                    
                                         index_flex_battery.remove(j)
                                         break
        
    
    
    
    return(E)