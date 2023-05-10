# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 17:00:33 2023

@author: halgr
"""

import numpy as np

def trade_pv2bat(sum_profit, sum_demand, index_seller_pv, index_buyers_battery, count_seller_pv, count_buyers_battery, deltakere, E, param, time):
    
    x_trans = np.zeros(deltakere)
    y_trans = np.zeros(deltakere)
    
    
    count_trade_max = 0
    count_buyer_max = 0
    count_trade_max2 = 0 
    count_buyer_max2 = 0
    count_trade_max3 = 0 
    count_buyer_max3 = 0
    count_trade_max4 = 0 
    count_buyer_max4 = 0
    count_trade_max5 = 0 
    count_buyer_max5 = 0
    
    index_trade_max = [] 
    index_buyer_max = []
    index_trade_max2 = [] 
    index_buyer_max2 = []
    index_trade_max3 = [] 
    index_buyer_max3 = []
    index_trade_max4 = [] 
    index_buyer_max4 = []
    index_trade_max5 = [] 
    index_buyer_max5 = []
    
    rest = 0
    
    count_seller_pv = len(index_seller_pv)
    count_buyers_battery = len(index_buyers_battery)

    
 
        
    if (count_seller_pv != 0):
        
        init_trans = sum_profit/count_seller_pv
        for i in index_seller_pv:
            
            if E[i]['lost_production'] >= init_trans:
            
                x_trans[i] = init_trans
                count_trade_max += 1
                index_trade_max.append(i)
                
            else:
                if E[i]['lost_production']  < init_trans:
                    
                    x_trans[i] = E[i]['lost_production'] 
                    rest += init_trans-E[i]['lost_production'] 
         
        
        if (rest != 0) & (count_trade_max != 0):
            
            add_trade = rest/count_trade_max
            rest = 0
            for i in index_trade_max:
                
                if E[i]['lost_production']  >= (init_trans + add_trade):
                
                    x_trans[i] = init_trans + add_trade
                    count_trade_max2 += 1
                    index_trade_max2.append(i)
                    
                else:
                    if E[i]['lost_production']  < (init_trans + add_trade):
                        
                        x_trans[i] = E[i]['lost_production'] 
                        rest += init_trans + add_trade-E[i]['lost_production']
                    
                        
        if (rest != 0) & (count_trade_max2 != 0):
            
            add_trade2 = rest/count_trade_max2
            rest = 0
            for i in index_trade_max2:
            
               
                if E[i]['lost_production']  >= (init_trans + add_trade + add_trade2):
                
                    x_trans[i] = init_trans + add_trade + add_trade2
                    count_trade_max3 += 1
                    index_trade_max3.append(i)
                    
                else:
                    if E[i]['lost_production'] < (init_trans + add_trade + add_trade2):
                        
                        x_trans[i] = E[i]['lost_production'] 
                        rest += init_trans + add_trade + add_trade2-E[i]['lost_production']  
                     
                        
        if (rest != 0) & (count_trade_max3 != 0):
            
            add_trade3 = rest/count_trade_max3
            rest = 0
            for i in index_trade_max3:
                
                if E[i]['lost_production']  >= (init_trans + add_trade + add_trade2 + add_trade3):
                
                    x_trans[i] = init_trans + add_trade + add_trade2 + add_trade3
                    count_trade_max4 += 1
                    index_trade_max4.append(i)
                    
                else:
                    if E[i]['lost_production']  < (init_trans + add_trade + add_trade2 + add_trade3):
                        
                        x_trans[i] = E[i]['lost_production'] 
                        rest += init_trans + add_trade + add_trade2 + add_trade3-E[i]['lost_production']                  
                    
        if (rest != 0) & (count_trade_max4 != 0):
        
            add_trade4 = rest/count_trade_max4
            rest = 0
            for i in index_trade_max4:
                
                if E[i]['lost_production']  >= (init_trans + add_trade + add_trade2 + add_trade3 + add_trade4):
                
                    x_trans[i] = init_trans + add_trade + add_trade2 + add_trade3 + add_trade4
                    count_trade_max5 += 1
                    index_trade_max5.append(i)
                    
                else:
                    if E[i]['lost_production']  < (init_trans + add_trade + add_trade2 + add_trade3 + add_trade4):
                        
                        x_trans[i] = E[i]['lost_production'] 
                        rest += init_trans + add_trade + add_trade2 + add_trade3 + add_trade4 -E[i]['lost_production']                   
   
                                     
   
    #-----------------------------------------------------------------------------------------------
    
    if count_buyers_battery != 0:
        
        rest = 0
        init_trans = (sum(x_trans)*0.25)/count_buyers_battery
        for i in index_buyers_battery:
            
            
            if (E[i]['LevelOfCharge'] + init_trans) < param[i]['BatteryCapacity']:
            
                y_trans[i] = init_trans
                count_buyer_max += 1
                index_buyer_max.append(i)
                
            else:
                if (E[i]['LevelOfCharge'] + init_trans) >= param[i]['BatteryDischargeLimit']:
                    
                    y_trans[i] = param[i]['BatteryCapacity'] - E[i]['LevelOfCharge']
                    rest += max(0, (init_trans - y_trans[i]))
         
        
        if (rest != 0) & (count_buyer_max != 0):
            
            add_trade = (rest/count_buyer_max)
            rest = 0
            for i in index_buyers_battery:
                
                if (E[i]['LevelOfCharge'] + init_trans + add_trade) < param[i]['BatteryCapacity']:
                
                    y_trans[i] = init_trans + add_trade
                    count_buyer_max2 += 1
                    index_buyer_max2.append(i)
                    
                else:
                    if (E[i]['LevelOfCharge'] + init_trans + add_trade) >= param[i]['BatteryDischargeLimit']:
                        
                        y_trans[i] = param[i]['BatteryCapacity'] - E[i]['LevelOfCharge'] + init_trans 
                        rest += max(0, (init_trans + add_trade - y_trans[i]))
                    
                        
        if (rest != 0) & (count_buyer_max2 != 0):
            
            add_trade2 = (rest/count_buyer_max2)
            rest = 0
            for i in index_buyers_battery:
                
                if (E[i]['LevelOfCharge'] + init_trans + add_trade + add_trade2) < param[i]['BatteryCapacity']:
                
                    y_trans[i] = init_trans + add_trade + add_trade2
                    count_buyer_max3 += 1
                    index_buyer_max3.append(i)
                    
                else:
                    if (E[i]['LevelOfCharge'] + init_trans + add_trade + add_trade2) >= param[i]['BatteryCapacity']:
                        
                        y_trans[i] = param[i]['BatteryCapacity'] - E[i]['LevelOfCharge'] + init_trans + add_trade
                        rest += max(0, (init_trans + add_trade + add_trade2 - y_trans[i]))
                        
                        
        if (rest != 0) & (count_buyer_max3 != 0):
            
            add_trade3 = rest/count_buyer_max3
            rest = 0
            for i in index_buyers_battery:
                
                if (E[i]['LevelOfCharge'] + init_trans + add_trade + add_trade2  + add_trade3) < param[i]['BatteryCapacity']:
                
                    y_trans[i] = init_trans + add_trade + add_trade2 + add_trade3
                    count_buyer_max4 += 1
                    index_buyer_max4.append(i)
                    
                else:
                    if (E[i]['LevelOfCharge'] + init_trans + add_trade + add_trade2 + add_trade3) >= param[i]['BatteryCapacity']:
                        
                        y_trans[i] = param[i]['BatteryCapacity'] - E[i]['LevelOfCharge'] + init_trans + add_trade + add_trade2
                        rest += max(0, (init_trans + add_trade + add_trade2 + add_trade3 - y_trans[i]))
                        
                    
        if (rest != 0) & (count_buyer_max4 != 0):
        
            add_trade4 = rest/count_buyer_max4
            rest = 0
            for i in index_buyers_battery:
               
               if (E[i]['LevelOfCharge'] + init_trans + add_trade + add_trade2  + add_trade3 + add_trade4) < param[i]['BatteryCapacity']:
               
                   y_trans[i] = init_trans + add_trade + add_trade2 + add_trade3 + add_trade4
                   count_buyer_max5 += 1
                   index_buyer_max5.append(i)
                   
               else:
                   if (E[i]['LevelOfCharge'] + init_trans + add_trade + add_trade2 + add_trade3 + add_trade4) >= param[i]['BatteryDischargeLimit']:
                       
                       y_trans[i] = param[i]['BatteryCapacity'] - E[i]['LevelOfCharge'] + init_trans + add_trade + add_trade2 + add_trade3
                       rest += max(0, (init_trans + add_trade + add_trade2 + add_trade3 + add_trade4 - y_trans[i]))
                                     
       
    
   
    rest_profit = sum_profit - sum(x_trans)
    rest_demand = sum_demand

    seller_trade = x_trans #power
    buyer_trade = y_trans #energy
    
    '''
    
    if time == 4639:
        
        print(index_seller_pv)
        print(index_buyers_battery)
        print('FØR ENERGIDELING')
        print('-----------------------------------------------------------')
        print('Tapt produkjson for hytte 2: {:.5g} kW'.format(E[2]['lost_production']))
        print('Tapt produkjson  for hytte 3: {:.5g} kW'.format(E[3]['lost_production']))
        print('Tapt produkjson  for hytte 4: {:.5g} kW'.format(E[4]['lost_production']))
        print('Batteristatus for hytte 0: {:.5g} kWh'.format(E[0]['LevelOfCharge']))
        print('------------------------------------------------------------')
        print('Salgsandel per PV [kW]:', seller_trade)
        print('Kjøpsandel per batteri [kWh]:', buyer_trade)
   
    ''' 
    

    return seller_trade, buyer_trade, rest_profit, rest_demand 