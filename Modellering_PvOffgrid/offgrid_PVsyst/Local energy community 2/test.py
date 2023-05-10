# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 15:24:46 2023

@author: halgr
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 14:58:23 2023

@author: halgr
"""
import numpy as np


discharge_limit = 0.5
x = [2,9,0,1]
y = []

sum_profit = 
sum_demand =  
index_buyer_pv =  
index_flex_battery, 
count_buyers_pv, 
count_flex_battery,

def trade_flex2pv(sum_profit, sum_demand, index_buyer_pv, index_flex_battery, count_buyers_pv, count_flex_battery, deltakere):
    
    x_trans = np.zeros(deltakere)
    y_trans = np.zeros(deltakere)
    
    discharge_limit = 0.5
    x = [2,9,4,1]
    
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
    
    
    if (count_flex_battery != 0):
        
        init_trans = (sum_demand/count_flex_battery)*0.25
        print(init_trans)
        for i in index_flex_battery:
            
            if (E[i]['LevelOfCharge'] - init_trans) > param[i]['discharge_limit']:
            
                x_trans[i] = init_trans
                count_trade_max += 1
                index_trade_max.append(i)
                
            else:
                if (E[i]['LevelOfCharge'] - init_trans) <= param[i]['discharge_limit']:
                    
                    x_trans[i] = E[i]['LevelOfCharge'] - param[i]['discharge_limit']
                    rest += max(0, (init_trans - x_trans[i]))
         
        
        if (rest != 0) & (count_trade_max != 0):
            
            add_trade = (rest/count_trade_max)
            rest = 0
            for i in index_flex_battery:
                
                if (E[i]['LevelOfCharge'] - init_trans - add_trade) > param[i]['discharge_limit']:
                
                    x_trans[i] = init_trans + add_trade
                    count_trade_max2 += 1
                    index_trade_max2.append(i)
                    
                else:
                    if (E[i]['LevelOfCharge'] - init_trans - add_trade) <= param[i]['discharge_limit']:
                        
                        x_trans[i] = E[i]['LevelOfCharge'] - param[i]['discharge_limit'] + init_trans 
                        rest += max(0, (init_trans + add_trade - x_trans[i]))
                    
                        
        if (rest != 0) & (count_trade_max2 != 0):
            
            add_trade2 = (rest/count_trade_max2)
            rest = 0
            for i in index_flex_battery:
                
                if (E[i]['LevelOfCharge'] - init_trans - add_trade - add_trade2) > param[i]['discharge_limit']:
                
                    x_trans[i] = init_trans + add_trade + add_trade2
                    count_trade_max3 += 1
                    index_trade_max3.append(i)
                    
                else:
                    if (E[i]['LevelOfCharge'] - init_trans - add_trade - add_trade2) <= param[i]['discharge_limit']:
                        
                        x_trans[i] = E[i]['LevelOfCharge'] - param[i]['discharge_limit'] + init_trans + add_trade
                        rest += max(0, (init_trans + add_trade + add_trade2 - x_trans[i]))
                        
        if (rest != 0) & (count_trade_max3 != 0):
            
            add_trade3 = rest/count_trade_max3
            rest = 0
            for i in index_flex_battery:
                
                if (E[i]['LevelOfCharge'] - init_trans - add_trade - add_trade2  - add_trade3) > param[i]['discharge_limit']:
                
                    x_trans[i] = init_trans + add_trade + add_trade2 + add_trade3
                    count_trade_max4 += 1
                    index_trade_max4.append(i)
                    
                else:
                    if (E[i]['LevelOfCharge'] - init_trans - add_trade - add_trade2 - add_trade3) <= param[i]['discharge_limit']:
                        
                        x_trans[i] = E[i]['LevelOfCharge'] - param[i]['discharge_limit'] + init_trans + add_trade + add_trade2
                        rest += max(0, (init_trans + add_trade + add_trade2 + add_trade3 - x_trans[i]))
                        
                    
        if (rest != 0) & (count_trade_max4 != 0):
        
            add_trade4 = rest/count_trade_max4
            rest = 0
            for i in index_flex_battery:
               
               if (E[i]['LevelOfCharge'] - init_trans - add_trade - add_trade2  - add_trade3 - add_trade4) > param[i]['discharge_limit']:
               
                   x_trans[i] = init_trans + add_trade + add_trade2 + add_trade3 + add_trade4
                   count_trade_max5 += 1
                   index_trade_max5.append(i)
                   
               else:
                   if (E[i]['LevelOfCharge'] - init_trans - add_trade - add_trade2 - add_trade3 - add_trade4) <= param[i]['discharge_limit']:
                       
                       x_trans[i] = E[i]['LevelOfCharge'] - param[i]['discharge_limit'] + init_trans + add_trade + add_trade2 + add_trade3
                       rest += max(0, (init_trans + add_trade + add_trade2 + add_trade3 + add_trade4 - x_trans[i]))
                                     
   
    #-----------------------------------------------------------------------------------------------
    
    if count_buyers_pv != 0:
        
        rest = 0
        init_trans = sum(x_trans)/count_buyers_pv
        for i in index_buyer_pv:
            
            if E[i]['lost_load']  >= init_trans:
            
                y_trans[i] = init_trans
                count_buyer_max += 1
                index_buyer_max.append(i)
                
            else:
                if E[i]['lost_load'] < init_trans:
                    
                    y_trans[i] = E[i]['lost_load']
                    rest += init_trans-E[i]['lost_load']
         
        
        if (rest != 0) & (count_buyer_max != 0):
            
            add_trade = rest/count_buyer_max
            rest = 0
            for i in index_buyer_max:
                
                if E[i]['lost_load'] >= (init_trans + add_trade):
                
                    y_trans[i] = init_trans + add_trade
                    count_buyer_max2 += 1
                    index_buyer_max2.append(i)
                    
                else:
                    if E[i]['lost_load'] < (init_trans + add_trade):
                        
                        y_trans[i] = E[i]['lost_load']
                        rest += init_trans + add_trade-E[i]['lost_load'] 
                        
                    
                        
        if (rest != 0) & (count_buyer_max2 != 0):
            
            add_trade2 = rest/count_buyer_max2
            rest = 0
            for i in index_buyer_max2:
            
               
                if E[i]['lost_load'] >= (init_trans + add_trade + add_trade2):
                
                    y_trans[i] = init_trans + add_trade + add_trade2
                    count_buyer_max3 += 1
                    index_buyer_max3.append(i)
                    
                else:
                    if E[i]['lost_load'] < (init_trans + add_trade + add_trade2):
                        
                        y_trans[i] = E[i]['lost_load']
                        rest += init_trans + add_trade + add_trade2-E[i]['lost_load'] 
                     
                        
        if (rest != 0) & (count_buyer_max3 != 0):
            
            add_trade3 = rest/count_buyer_max2
            rest = 0
            for i in index_buyer_max3:
            
               
                if E[i]['lost_load'] >= (init_trans + add_trade + add_trade2 + add_trade3):
                
                    y_trans[i] = init_trans + add_trade + add_trade2 + add_trade3
                    count_buyer_max4 += 1
                    index_buyer_max4.append(i)
                    
                else:
                    if E[i]['lost_load'] < (init_trans + add_trade + add_trade2 + add_trade3):
                        
                        y_trans[i] = E[i]['lost_load']
                        rest += init_trans + add_trade + add_trade2 + add_trade3 -E[i]['lost_load']                  
                    
        if (rest != 0) & (count_buyer_max4 != 0):
            
            add_trade4 = rest/count_buyer_max2
            rest = 0
            for i in index_buyer_max4:
            
               
                if E[i]['lost_load'] >= (init_trans + add_trade + add_trade2 + add_trade3 + add_trade4):
                
                    y_trans[i] = init_trans + add_trade + add_trade2 + add_trade3 + add_trade4
                    count_buyer_max5 += 1
                    index_buyer_max5.append(i)
                    
                else:
                    if E[i]['lost_load'] < (init_trans + add_trade + add_trade3 + add_trade4):
                        
                        y_trans[i] = E[i]['lost_load']
                        rest += init_trans + add_trade + add_trade2 + add_trade3 + add_trade4 - E[i]['lost_load']    
       
    
   
    rest_profit = sum_profit - sum(x_trans)
    rest_demand = sum_demand - sum(y_trans)
   
    print(x_trans)
    print(y_trans)
    print()
    
    seller_trade = x_trans #energy
    buyer_trade = y_trans #power
    

    return seller_trade, buyer_trade, rest_profit, rest_demand 