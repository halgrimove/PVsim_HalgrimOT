# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 17:23:19 2023

@author: halgr
"""


import numpy as np

def trade_batt2batt(flex_limit, sum_profit, sum_demand, index_flex_buy_battery, index_flex_sell_battery, count_battery_sell_flex, count_battery_buy_flex, deltakere, E, param, time):
    
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
    
    
    
    if (len(index_flex_sell_battery) != 0):
        
        
        max_power = param[0]['MaxPower']
        init_trans = max_power*0.25
        
        
        for i in index_flex_sell_battery:
            
            
            if (E[i]['LevelOfCharge'] - init_trans) > param[i]['BatteryDischargeLimit']:
            
                x_trans[i] = init_trans
                count_trade_max += 1
                index_trade_max.append(i)
                
            else:
                if (E[i]['LevelOfCharge'] - init_trans) <= param[i]['BatteryDischargeLimit']:
                    
                    x_trans[i] = E[i]['LevelOfCharge'] - param[i]['BatteryDischargeLimit']
                    rest += max(0, (init_trans - x_trans[i]))
         
        
        if (rest != 0) & (count_trade_max != 0):
            
            add_trade = (rest/count_trade_max)
            rest = 0
            for i in index_flex_sell_battery:
                
                if (E[i]['LevelOfCharge'] - init_trans - add_trade) > param[i]['BatteryDischargeLimit']:
                
                    x_trans[i] = init_trans + add_trade
                    count_trade_max2 += 1
                    index_trade_max2.append(i)
                    
                else:
                    if (E[i]['LevelOfCharge'] - init_trans - add_trade) <= param[i]['BatteryDischargeLimit']:
                        
                        x_trans[i] = E[i]['LevelOfCharge'] - param[i]['BatteryDischargeLimit'] + init_trans 
                        rest += max(0, (init_trans + add_trade - x_trans[i]))
                    
                        
        if (rest != 0) & (count_trade_max2 != 0):
            
            add_trade2 = (rest/count_trade_max2)
            rest = 0
            for i in index_flex_sell_battery:
                
                if (E[i]['LevelOfCharge'] - init_trans - add_trade - add_trade2) > param[i]['BatteryDischargeLimit']:
                
                    x_trans[i] = init_trans + add_trade + add_trade2
                    count_trade_max3 += 1
                    index_trade_max3.append(i)
                    
                else:
                    if (E[i]['LevelOfCharge'] - init_trans - add_trade - add_trade2) <= param[i]['BatteryDischargeLimit']:
                        
                        x_trans[i] = E[i]['LevelOfCharge'] - param[i]['BatteryDischargeLimit'] + init_trans + add_trade
                        rest += max(0, (init_trans + add_trade + add_trade2 - x_trans[i]))
                        
        if (rest != 0) & (count_trade_max3 != 0):
            
            add_trade3 = rest/count_trade_max3
            rest = 0
            for i in index_flex_sell_battery:
                
                if (E[i]['LevelOfCharge'] - init_trans - add_trade - add_trade2  - add_trade3) > param[i]['BatteryDischargeLimit']:
                
                    x_trans[i] = init_trans + add_trade + add_trade2 + add_trade3
                    count_trade_max4 += 1
                    index_trade_max4.append(i)
                    
                else:
                    if (E[i]['LevelOfCharge'] - init_trans - add_trade - add_trade2 - add_trade3) <= param[i]['BatteryDischargeLimit']:
                        
                        x_trans[i] = E[i]['LevelOfCharge'] - param[i]['BatteryDischargeLimit'] + init_trans + add_trade + add_trade2
                        rest += max(0, (init_trans + add_trade + add_trade2 + add_trade3 - x_trans[i]))
                        
                    
        if (rest != 0) & (count_trade_max4 != 0):
        
            add_trade4 = rest/count_trade_max4
            rest = 0
            for i in index_flex_sell_battery:
               
               if (E[i]['LevelOfCharge'] - init_trans - add_trade - add_trade2  - add_trade3 - add_trade4) > param[i]['BatteryDischargeLimit']:
               
                   x_trans[i] = init_trans + add_trade + add_trade2 + add_trade3 + add_trade4
                   count_trade_max5 += 1
                   index_trade_max5.append(i)
                   
               else:
                   if (E[i]['LevelOfCharge'] - init_trans - add_trade - add_trade2 - add_trade3 - add_trade4) <= param[i]['BatteryDischargeLimit']:
                       
                       x_trans[i] = E[i]['LevelOfCharge'] - param[i]['BatteryDischargeLimit'] + init_trans + add_trade + add_trade2 + add_trade3
                       rest += max(0, (init_trans + add_trade + add_trade2 + add_trade3 + add_trade4 - x_trans[i]))
                                     
   
    #-----------------------------------------------------------------------------------------------
    
    if len(index_flex_buy_battery)!= 0:
        
        rest = 0
        init_trans = (sum(x_trans))/len(index_flex_buy_battery)
        
        if time == 20999:
            
            print(init_trans)
        
        
        
        for i in index_flex_buy_battery:
            
            
            if E[i]['LevelOfCharge']  >= init_trans:
            
                y_trans[i] = init_trans
                count_buyer_max += 1
                index_buyer_max.append(i)
                
            else:
                if E[i]['LevelOfCharge'] < init_trans:
                    
                    y_trans[i] = E[i]['LevelOfCharge']
                    rest += init_trans-E[i]['LevelOfCharge']
         
        
        if (rest != 0) & (count_buyer_max != 0):
            
            add_trade = rest/count_buyer_max
            rest = 0
            for i in index_buyer_max:
                
                if E[i]['LevelOfCharge'] >= (init_trans + add_trade):
                
                    y_trans[i] = init_trans + add_trade
                    count_buyer_max2 += 1
                    index_buyer_max2.append(i)
                    
                else:
                    if E[i]['LevelOfCharge'] < (init_trans + add_trade):
                        
                        y_trans[i] = E[i]['LevelOfCharge']
                        rest += init_trans + add_trade-E[i]['LevelOfCharge'] 
                        
                    
                        
        if (rest != 0) & (count_buyer_max2 != 0):
            
            add_trade2 = rest/count_buyer_max2
            rest = 0
            for i in index_buyer_max2:
            
               
                if E[i]['LevelOfCharge'] >= (init_trans + add_trade + add_trade2):
                
                    y_trans[i] = init_trans + add_trade + add_trade2
                    count_buyer_max3 += 1
                    index_buyer_max3.append(i)
                    
                else:
                    if E[i]['LevelOfCharge'] < (init_trans + add_trade + add_trade2):
                        
                        y_trans[i] = E[i]['LevelOfCharge']
                        rest += init_trans + add_trade + add_trade2-E[i]['LevelOfCharge'] 
                     
                        
        if (rest != 0) & (count_buyer_max3 != 0):
            
            add_trade3 = rest/count_buyer_max2
            rest = 0
            for i in index_buyer_max3:
            
               
                if E[i]['LevelOfCharge'] >= (init_trans + add_trade + add_trade2 + add_trade3):
                
                    y_trans[i] = init_trans + add_trade + add_trade2 + add_trade3
                    count_buyer_max4 += 1
                    index_buyer_max4.append(i)
                    
                else:
                    if E[i]['LevelOfCharge'] < (init_trans + add_trade + add_trade2 + add_trade3):
                        
                        y_trans[i] = E[i]['LevelOfCharge']
                        rest += init_trans + add_trade + add_trade2 + add_trade3 -E[i]['LevelOfCharge']                  
                    
        if (rest != 0) & (count_buyer_max4 != 0):
            
            add_trade4 = rest/count_buyer_max2
            rest = 0
            for i in index_buyer_max4:
            
               
                if E[i]['LevelOfCharge'] >= (init_trans + add_trade + add_trade2 + add_trade3 + add_trade4):
                
                    y_trans[i] = init_trans + add_trade + add_trade2 + add_trade3 + add_trade4
                    count_buyer_max5 += 1
                    index_buyer_max5.append(i)
                    
                else:
                    if E[i]['LevelOfCharge'] < (init_trans + add_trade + add_trade3 + add_trade4):
                        
                        y_trans[i] = E[i]['LevelOfCharge']
                        rest += init_trans + add_trade + add_trade2 + add_trade3 + add_trade4 - E[i]['LevelOfCharge']    
       
    
   
    rest_profit = sum_profit
    rest_demand = sum_demand

    seller_trade = x_trans #energy
    buyer_trade = y_trans #power
    
    
    '''
    if time == 20999:
            
            print('FØR ENERGIDELING')
            print(index_flex_buy_battery)
            print(index_flex_sell_battery)
            print('-----------------------------------------------------------')
            print('Batteristatus for hytte 2: {:.5g} kWh'.format(E[2]['LevelOfCharge']))
            print('Batteristatus for hytte 3: {:.5g} kWh'.format(E[3]['LevelOfCharge']))
            print('Batteristatus for hytte 4: {:.5g} kWh'.format(E[4]['LevelOfCharge']))
            print('Batteristatus for hytte 0: {:.5g} kWh'.format(E[0]['LevelOfCharge']))
            print('Batteristatus for hytte 1: {:.5g} kWh'.format(E[1]['LevelOfCharge']))
            print('------------------------------------------------------------')
            print('Salgsandel per batteri (flex) [kWH]:', seller_trade)
            print('Kjøpsandel per batteri (flex)  [kWh]:', buyer_trade)
       
    '''    

    return seller_trade, buyer_trade, rest_profit, rest_demand 
