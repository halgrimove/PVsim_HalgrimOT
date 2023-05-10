# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 11:49:16 2023

@author: halgr
"""
import numpy as np
import pandas as pd


def bidding_status_per_timestep(E, param, timestep):
    
    
      times = len(E[0]['inv2load'])
      pv2inv = {}
      res_pv = {}
      pv2store = {}
      res_load = {}
      LevelOfCharge = {}
      lost_production = {}
      battery_charging = {}
      battery_discharging = {}
      
      bat_size_e_adj = {}
      bat_size_p_adj = {}
      n_bat = {}
      n_inv = {}
      time = {}
      BatteryDischargeLimit = {}
    
      bidding_status_PV = np.zeros(len(param))
      #bidding_status_PV[0] = np.zeros(times) #deltaker 1
      #bidding_status_PV[1] = np.zeros(times) #deltaker 2
      #bidding_status_PV[0] = np.zeros(times) #deltaker 1
      #bidding_status_PV[2] = np.zeros(times) #deltaker 2
          
          
      bidding_status_battery = np.zeros(len(param))
      #bidding_status_battery[0] = np.zeros(times)
      #bidding_status_battery[1] = np.zeros(times)
      #bidding_status_battery[2] = np.zeros(times)
      #bidding_status_battery[0][0] = 2 #intiell verdi på batteri
      #bidding_status_battery[1][0] = 2 #initiell verdi på batteri
      #bidding_status_battery[2][0] = 2 #initiell verdi på batteri
     
        
    
    
      for i in range(len(param)):
        
              
            
            lost_production = E[i]['lost_production'][timestep]
            res_load = E[i]['lost_load'][timestep]
            LevelOfCharge = E[i]['LevelOfCharge'][timestep-1]
            
            
            bat_size_e_adj = param[i]['BatteryCapacity']
            bat_size_p_adj = param[i]['MaxPower'] #Max effekt batteriet kan lades/utlades med
            n_bat = param[i]['BatteryEfficiency']
            n_inv = param[i]['InverterEfficiency']
            time = param[i]['timestep']
            BatteryDischargeLimit = param[i]['BatteryDischargeLimit']
            
            
            #print(lost_production)
            #print(res_load)
            
            '''
            if (timestep == 1) & (lost_production > 0):
                    
                    bidding_status_PV[i] = 2
                    
            else:
                if (timestep == 1) & (lost_production > 0):
                        
                        bidding_status_PV[i] = 1
            '''   
                
            if (LevelOfCharge > BatteryDischargeLimit) & (LevelOfCharge < bat_size_e_adj) : 
                
                    bidding_status_battery[i] = 0 #both charge and discharge  
                
            else:
                  if LevelOfCharge == BatteryDischargeLimit: 
                
                
                      bidding_status_battery[i] = 1 #charge
                
                  else:
                                        
                      bidding_status_battery[i] = 2 #discharge
                
                
                #OPPDATERE PV_BIDDING STATUS    
            if (lost_production > 0): #sell
                  
                            bidding_status_PV[i]= 2 #sell
                       
            else: 
                      if (lost_production == 0) & (res_load > 0): 
                              
                             bidding_status_PV[i] = 1 #buy
                              
                             
                #BIDDING_STATUS_PV = 0 -> PV DEKKER FORBRUK, OFTE I SITUASJON
                
         
                
                
      return bidding_status_PV, bidding_status_battery
    