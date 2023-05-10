# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 15:53:18 2023

@author: halgr
"""

import numpy as np
import pandas as pd
import LEC_input_files as lecif

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

E = {}
bidding_battery = {}
bidding_pv = {}

deltakere = [3, 1]  # Kategorihytte på deltakerene
bruksmønster = [0, 1]  # Bruksmønster på deltakerene
# 0: bor på hytta, 1: feriebruk, 2: annenhver helg, 3: hver helg


demand, pv = lecif.LEC_input_files(deltakere, bruksmønster)


time = 0
dict_list = []


def E_per_timestep(dict_list, param, time, demand, pv):
    
    E = {}
    bidding_battery = {}
    bidding_pv = {}
    
    return_series = True
    deltakere_n = len(param)
    
    max_transfer = 3

    for x in range(len(param)):
        
        if time == 0:
            
            LevelOfCharge_previous = 0.8*param[x]['BatteryCapacity']
        
        else:
        
            LevelOfCharge_previous = dict_list[time-1][x]['LevelOfCharge']
    
    
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
        discharge_limit = param[x]['BatteryDischargeLimit']
        
        
        pv2inv = np.minimum(pv[x][time], demand[x][1]/n_inv)
        res_pv = np.maximum(pv[x][time] - demand[x][time]/n_inv, 0) #Lasten som momentant er større en forbruket for det gitte tidssteget
        inv2load = pv2inv * n_inv
        res_load = (demand[x][time] - pv2inv * n_inv) #lasten som ikke dekkes av momentan PV
        #pv2inv = pv2inv.values
        
        
        if time == 0:
        
            LevelOfCharge_previous = battery_capacity*0.8
        
        
        #-------------------------------------------------------------------------------------------
            
        
        #1. prioritet -> Forsyne eget batteri
        
        if LevelOfCharge_previous >= battery_capacity:  
                    pv2store = 0 
            
        else: #BATTERIET ER IKKE FULT, MEN VIL OVERSTIGE MAX KAPASITET VED OPPLADING I GITT TIDSSTEG
                if (LevelOfCharge_previous + (res_pv * timestep)) > battery_capacity:
                    
                    #KAN MAX LADE OPP DET SMO ER IGJEN FØR BATTERIET NÅR MAX KAPASITET
                    pv2store = min((battery_capacity - LevelOfCharge_previous) / timestep, max_power)
                    #OPPLADINGEN BEGRENSES AV MAX OPP/UTLADNINGS EFFEKT. "BAT_SIZE_P_ADJ"
                    
                    
                else: #BATTERIET ER IKKE FULT OG VIL IKKE OVERTIGE MAX KAPASITET VED OPPLADNING I GITT TIDSSTEG
                    pv2store = min(res_pv, max_power)
             
                  
                
        store2inv = min((LevelOfCharge_previous/timestep-discharge_limit/timestep), res_load/n_inv, max_power)  
            
        
        #LDE OPP DET MAN KAN MED EGEN ENERGI
        LevelOfCharge = min(LevelOfCharge_previous - (store2inv - pv2store*n_bat) * timestep,  # DC
                                   battery_capacity)
        
        
        
        #-------------------------------------------------------------------------------------------
        
        
        
        inv2load = inv2load + store2inv*n_inv
        lost_production = res_pv - pv2store 
        lost_load = demand[x][time] - inv2load  
        
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
                    'battery_transfer_charging': battery_transfer_charging,
                    'battery_transfer_discharging': battery_transfer_discharging,
                    'pv_self_batterycharging': pv_self_charging,
                    'pv_self_pv' : pv_self_pv,
                    'pv_seller_battery': pv_transfer_batterycharging,
                    'pv_buyer_battery': pv_transfer_batterycharging,
                    'pv_seller_pv': pv_transfer_pv, 
                    'pv_buyer_pv': pv_transfer_pv, 
                    'battery_seller_pv': pv_transfer_batterycharging,
                    'battery_buyer_pv': pv_transfer_batterycharging,
                    }
        
        
        
        #BUDENE HYTTE X LEGGER UT
        
      
        if ((LevelOfCharge_previous <= battery_capacity*0.95) & (LevelOfCharge_previous >= 0.3*battery_capacity)) :      
        
                      bidding_battery[x] = 5 #KAN KJØPE OG SELGE MELLOMTING!
        
        else:
            if ((LevelOfCharge_previous > discharge_limit) & (LevelOfCharge_previous < 0.3*battery_capacity)): 
                
                    bidding_battery[x] = 3 #flex_buy
                
            else:
                    if ((LevelOfCharge_previous < battery_capacity) & (LevelOfCharge_previous > 0.95*battery_capacity)) : 
                      
                          bidding_battery[x] = 4 #flex_sell
                  
                    
                          
                    else:
                    
                          if LevelOfCharge_previous == discharge_limit: 
                        
                        
                              bidding_battery[x] = 1 #charge (buy)
                        
                          else:
                                                
                              bidding_battery[x] = 2 #discharge (sell)
            
             
        if (lost_production > 0): #sell -> Det er noe til overs etter å ha forsynt eget anlegg og batteri
              
                        bidding_pv[x] = 2 #sell
                   
        else: 
                  if (lost_load > 0): 
                          
                         bidding_pv[x] = 1 #buy
        
                  else:
                          bidding_pv[x] = 9
        
        #-------------------------------------------------------------------------------------------
        print(bidding_pv)
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
        
        
        #FJERNE FLUER
        if res_load < 0.01:
            res_load = 0
            
        if lost_production < 0.01:
            lost_production = 0
    
    
        if bidding_pv[j] == 2: #SELGE
        
            count_sellers_pv += 1
            energy_profit_pv[j] = min(max_transfer, lost_production)
                     
            index_seller_pv.append(j)
                
            
        else:
            if (bidding_pv[j] == 1): #KJØPE
            
                count_buyers_pv += 1
                energy_demand_pv[j] = min(max_transfer, res_load)
    
                index_buyer_pv.append(j)
                
                
                #BIDDINGSTATUS == 0 -> HAR IKKE BEHOV FOR Å KJØPE ELLER SELGE
                
               
        if bidding_battery[j] == 2: #SELGE VED FULLADA BATTERI
         
             count_sellers_battery += 1
             
            
             #Tilgjengelig energi på abtteriet for salg
             energy_profit_battery[j] = min(max_power/timestep, LevelOfCharge-discharge_limit)
             #Level of charge i dette tilfelle er batteristatus etter å ha forynt eget batteri
             #med egen installsjon før budrunden starter
             
             index_seller_battery.append(j)
    
             
        else:
             if (bidding_battery[j] == 1): #KJØPE
             
                 count_buyers_battery += 1 
                 energy_demand_battery[j] = min(max_power, battery_capacity-discharge_limit)
                 
                 index_buyer_battery.append(j)
                 
                 
            #batteriet lades opp/ut ettersom hva som blir igjen
            
             else:
                if (bidding_battery[j] == 3):
                    
                    '''
                    FLEXBATTERI HAR BATTERINIVÅ I MELLOM MAX OG MIN. NOE SOM VIL SI AT DET BÅDE KAN LADES
                    UT OG OPP ETTER BEHOV
                    '''
                    
                    count_buyers_battery_flex += 1 
                    index_flex_buy_battery.append(j)
                   
                else:
                    if (bidding_battery[j] == 4):
                        
                        '''
                        FLEXBATTERI HAR BATTERINIVÅ I MELLOM MAX OG MIN. NOE SOM VIL SI AT DET BÅDE KAN LADES
                        UT OG OPP ETTER BEHOV
                        '''
                        
                        count_sellers_battery_flex += 1 
                        index_flex_sell_battery.append(j)   
    
                        
                    else:
                         if (bidding_battery[j] == 5):
                             
                             count_flex_battery += 1 
                             index_flex_battery.append(j) 
                             
    #HAR NÅ OVERSIKT OVER STATUS PÅ ANLEGG ETTER Å HA FORYNT SEG SELV OG HVILKE BUD SOM HAR BLITT
    #LAGT UT AV HVEM I MARKEDET
    
    
    sum_energy_profit_pv = sum(energy_profit_pv)
    sum_energy_demand_pv = sum(energy_demand_pv)
    #Overskudd og underskudd av momentane verdier
    
    #1.PRI ER Å KVITTE SEG MED MOMENTANT VOVERSKUDD/UNDERSKUDD -> FRA PV
    
    if sum_energy_profit_pv == sum_energy_demand_pv: 
        #Ingen behov for salg av momentan energi. Kan fortsatt ha energiflyt mellom batteri
        
        
       if sum_energy_demand_pv == 0: 
          #Ingen behov for salg av momentan energi. Kan fortsatt ha energiflyt mellom batteri
          
          #OBS, MAXPOWER/ANTALL KJØPERE
          
          for j in index_seller_battery: #OM NOEN BATTERI STÅR FULLE
              
              for i in index_buyer_battery: #KAN VÆRE TOMME OG FLEX BATTERI
              
              
                  E[j]['LevelOfCharge'] -= max_power*0.25
                  E[j]['battery_transfer_discharging'] += max_power*0.25
                  
                  E[i]['LevelOfCharge'] += max_power*0.25
                  E[i]['battery_transfer_charging'] += max_power*0.25
                  
                  
                  
          
          for j in index_flex_sell_battery:
              
              for i in index_flex_buy_battery:
                  
                  transfer = min(max_power*0.25, E[j]['LevelOfCharge'] - flex_lower_limit)
                  E[j]['LevelOfCharge'] -= transfer
                  E[j]['battery_transfer_discharging'] += transfer
                  
                  E[i]['LevelOfCharge'] += transfer
                  E[i]['battery_transfer_charging'] += transfer
        
    
       else: #ENERGI MÅ FØRST UTVEKSLES MOMENTANT
       
           if ((count_buyers_pv != 0) & (count_sellers_pv != 0)):
       
               transfer = min(((sum_energy_demand_pv/count_sellers_pv)/count_buyers_pv), max_transfer)
           
               for j in index_seller_pv:
                   
                   for i in index_buyer_pv:
                       
                       E[j]['lost_production'] -= transfer
                       E[j]['pv_seller_pv'] += transfer
                       
                       
                       
                       E[i]['lost_load'] -= transfer
                       E[i]['pv_buying_pv'] += transfer
        
                       if E[i]['lost_load'] < 0.:
                           
                           rest = -1*E[i]['lost_load'] 
                           E[i]['lost_load'] = 0
                           E[i]['pv_seller_pv'] -= rest
                           E[j]['pv_buyer_pv'] -= rest
                           
         
    
    else:                           
        if ((sum_energy_demand_pv < sum_energy_profit_pv) & ((sum_energy_demand_pv != 0) & (sum_energy_profit_pv != 0))):
           #Det er en større etterspørsel etter forbruk enn det som kan dekkes
             
             if ((count_buyers_pv != 0) & (count_sellers_pv != 0)):
            
                 transfer = min(((sum_energy_demand_pv/count_sellers_pv)/count_buyers_pv), max_transfer)
           
                 #Det kan være noen anlegg som har overskudd, selv om summen er i underskudd
                 for j in index_seller_pv:
                   
                   for i in index_buyer_pv:
                        
                       transfer_power = min(transfer, E[j]['lost_production'])
                       E[j]['lost_production'] -= transfer_power
                       E[j]['pv_seller_pv'] += transfer_power
                       
                       
                       
                       
                       E[i]['lost_load'] -= transfer_power
                       E[i]['pv_buyer_pv'] += transfer_power
                       sum_energy_demand_pv -= transfer_power
                       
                       if E[i]['lost_load'] == 0:
                           
                           count_buyers_pv -= 1
                                                  
                
                       if E[i]['lost_load'] < 0.:
                           
                           rest = -1*E[i]['lost_load'] 
                           E[i]['lost_load'] = 0
                           E[i]['pv_seller_pv'] -= rest
                           E[j]['pv_buyer_pv'] -= rest
                           
                           #transfer += rest
    

        else:
             if ((sum_energy_demand_pv > sum_energy_profit_pv) & ((sum_energy_demand_pv != 0) & (sum_energy_profit_pv != 0))):
               #Det er en større etterspørsel etter forbruk enn det som kan dekkes
               #For eksempel når noen hytter står tomme
               
               if ((count_buyers_pv != 0) & (count_sellers_pv != 0)):
               
                   transfer = min(((sum_energy_demand_pv/count_sellers_pv)/count_buyers_pv), max_transfer)
                   
                   for j in index_seller_pv:
                       
                       for i in index_buyer_pv:
                           
                           transfer_power = min(transfer, E[j]['lost_production'])
                           E[j]['lost_production'] -= transfer_power
                           E[j]['pv_seller_pv'] += transfer_power
                           
                           
                           
                           E[i]['lost_load'] -= transfer_power
                           E[i]['pv_buyer_pv'] += transfer_power
                    
                           if E[i]['lost_load'] < 0.:
                               
                               rest = -1*E[i]['lost_load'] 
                               E[i]['lost_load'] = 0
                               E[i]['pv_buyer_pv'] -= rest
                               E[j]['pv_seller_pv'] -= rest
                               #transfer += rest
                                    


    if ((count_buyers_pv != 0) & (count_sellers_battery != 0)): 
          
              
              transfer = min(((sum_energy_demand_pv/count_sellers_battery)/count_buyers_pv), max_transfer)
          
              for j in index_seller_battery: #OM NOEN BATTERI STÅR FULLE
                               
                  for i in index_buyer_pv: 
               
                   transfer_power = min(transfer, E[j]['LevelOfCharge']/0.25)
                   E[j]['LevelOfCharge'] -= transfer_power*0.25
                   E[j]['battery_transfer_discharging'] += transfer_power*0.25
                   
                   E[i]['lost_load'] -= transfer_power
                   
                   if E[i]['lost_load'] == 0:
                       
                       count_buyers_pv -= 1
         
            
            
    if ((count_buyers_pv != 0) & (count_sellers_battery_flex != 0)):            
                         
                
                transfer = min(((sum_energy_demand_pv/count_sellers_battery_flex)/count_buyers_pv), max_transfer)
                
                         
                for j in index_flex_sell_battery: #OM NOEN BATTERI STÅR FULLE
                     
                     for i in index_buyer_pv: #KAN VÆRE TOMME OG FLEX BATTERI
                     
                         transfer_power = min(transfer, E[j]['LevelOfCharge']/0.25)
                         E[j]['LevelOfCharge'] -= transfer_power*0.25
                         E[j]['battery_transfer_discharging'] += transfer_power*0.25
                       
                         
                         E[i]['lost_load'] -= transfer_power/0.25
                        
                        
                         if E[i]['lost_load'] == 0:
                             
                             count_buyers_pv -= 1
                                             
         
            
    if ((count_sellers_pv != 0) & (count_buyers_battery_flex != 0)):                                
                                
                   for j in index_seller_pv:
                         
                         for i in index_flex_buy_battery:
                             
                                 transfer = min(max_transfer, E[j]['lost_production']*0.25)
                                 E[j]['lost_production'] -= transfer/0.25
                                 E[j]['pv_seller_battery'] += transfer/0.25
                                 
                                 E[i]['LevelOfCharge'] += transfer
                                 E[i]['battery_transfer_charging'] += transfer
                                 E[i]['pv_buyer_battery'] += transfer
                    
                        
    
    if ((count_sellers_pv != 0) & (count_buyers_battery != 0)): 
               
                   for j in index_seller_pv:
                        
                        for i in index_buyer_battery:
                            
                                transfer = min(max_transfer, E[j]['lost_production']*0.25)
                                E[j]['lost_production'] -= transfer/0.25
                                E[j]['pv_seller_battery'] += transfer/0.25
                                                  
                                E[i]['LevelOfCharge'] += transfer
                                E[i]['battery_transfer_charging'] += transfer
                                E[i]['pv_buyer_battery'] += transfer
        
    
    

    if (count_sellers_battery + count_sellers_battery_flex) != 0:
    
        

           for j in index_seller_battery: #OM NOEN BATTERI STÅR FULLE
                
                for i in index_buyer_battery: #KAN VÆRE TOMME OG FLEX BATTERI
                
                
                    E[j]['LevelOfCharge'] -= max_power*0.25
                    E[j]['battery_transfer_discharging'] += max_power*0.25
                    index_seller_battery.remove(j)
                    
                    E[i]['LevelOfCharge'] += max_power*0.25
                    E[i]['battery_transfer_charging'] += max_power*0.25
                    index_buyer_battery.remove(i)
                    
                    
           for j in index_seller_battery: #OM NOEN BATTERI STÅR FULLE
                
                for i in index_flex_buy_battery: #KAN VÆRE TOMME OG FLEX BATTERI
                
                
                    E[j]['LevelOfCharge'] -= max_power*0.25
                    E[j]['battery_transfer_discharging'] += max_power*0.25
                    index_seller_battery.remove(j)
                    
                    E[i]['LevelOfCharge'] += max_power*0.25
                    E[i]['battery_transfer_charging'] += max_power*0.25
                    index_flex_buy_battery.remove(i)
           
            
           for j in index_seller_battery: #OM NOEN BATTERI STÅR FULLE
                
                for i in index_flex_battery: #KAN VÆRE TOMME OG FLEX BATTERI
                
                    E[j]['LevelOfCharge'] -= max_power*0.25
                    E[j]['battery_transfer_discharging'] += max_power*0.25
                    index_seller_battery.remove(j)
                    
                    E[i]['LevelOfCharge'] += max_power*0.25
                    E[i]['battery_transfer_charging'] += max_power*0.25
                            
           
           for j in index_flex_sell_battery: #OM NOEN BATTERI STÅR FULLE
                 
                 for i in index_buyer_battery: #KAN VÆRE TOMME OG FLEX BATTERI
                 
                 
                     E[j]['LevelOfCharge'] -= max_power*0.25
                     E[j]['battery_transfer_discharging'] += max_power*0.25
                     index_flex_sell_battery.remove(j)
                     
                     E[i]['LevelOfCharge'] += max_power*0.25
                     E[i]['battery_transfer_charging'] += max_power*0.25 
                     index_buyer_battery.remove(i) 
                     
                     
           for j in index_flex_sell_battery: #OM NOEN BATTERI STÅR FULLE
                 
                 for i in index_flex_buy_battery: #KAN VÆRE TOMME OG FLEX BATTERI
                 
                 
                     E[j]['LevelOfCharge'] -= max_power*0.25
                     E[j]['battery_transfer_discharging'] += max_power*0.25
                     index_flex_sell_battery.remove(j)
                     
                     E[i]['LevelOfCharge'] += max_power*0.25
                     E[i]['battery_transfer_charging'] += max_power*0.25 
                     index_flex_buy_battery.remove(i)           
           
            
           for j in index_flex_battery: #OM NOEN BATTERI STÅR FULLE
                
                for i in index_buyer_battery: #KAN VÆRE TOMME OG FLEX BATTERI
                
                
                    E[j]['LevelOfCharge'] -= max_power*0.25
                    E[j]['battery_transfer_discharging'] += max_power*0.25
                    index_seller_battery.remove(j)
                    
                    E[i]['LevelOfCharge'] += max_power*0.25
                    E[i]['battery_transfer_charging'] += max_power*0.25
                    
                    
           for j in index_flex_battery: #OM NOEN BATTERI STÅR FULLE
                
                for i in index_flex_buy_battery: #KAN VÆRE TOMME OG FLEX BATTERI
                
                
                    E[j]['LevelOfCharge'] -= max_power*0.25
                    E[j]['battery_transfer_discharging'] += max_power*0.25
                    index_seller_battery.remove(j)
                    
                    E[i]['LevelOfCharge'] += max_power*0.25
                    E[i]['battery_transfer_charging'] += max_power*0.25         
                    
                    
           
         
    
    
    
    return(E)







