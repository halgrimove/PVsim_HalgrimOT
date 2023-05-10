# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 10:13:49 2023

@author: halgr

"""
import numpy as np


def energysharing_per_timestep(E, param, biddingstatus_PV, biddingstatus_battery, timestep):
    
    '''
    BIDDINGSTATUS INNEHOLDER VERDIER SOM TILSVARER OM ANLEGG OG BATTERI VIL KJØPE/SELGE I DET GITTE TIDSSTEG
    '''
    
    deltakere = len(param)
    
    #VARIABLER SOM HOLDER STYR PÅ HVOR MANGE SOM KJØPER OG SELGER I HVERT TIDSSTEG
    count_sellers_PV = 0
    count_buyers_PV = 0
    count_sellers_battery = 0
    count_buyers_battery = 0
    count_buyers_battery_flex = 0
    
    #OVERSKUDD/UNDERSKUDD AV ENERGI HOS DE ULIKE DELTAKERENE
    energy_profit_pv = np.zeros(deltakere)
    energy_demand_pv = np.zeros(deltakere)
    energy_profit_battery = np.zeros(deltakere)
    energy_demand_battery = np.zeros(deltakere)
    
    #INDEX (HVILKEN DELTAKER) LISTER SOM HOLDER STYR PÅ HVILKEN INDEX DE ULIKE DELTAKERENE I MARKEDET HAR
    #INDEX VIL VÆRE DET SAMME SOM "HVILKEN DELTAKER"
    seller_index_pv = []
    buyer_index_pv = []
    seller_index_battery = []
    buyer_index_battery = [] #default like mange som antall deltakere
    flex_index_battery = []
    
   
    #-------------------------------------------------------------------------------------------------------------       
    
    
    
    for j in range(deltakere):  
        
        
        lost_production = E[j]['lost_production'] #BORTKASTET SOLENERGI
        res_load = E[j]['lost_load'] #LAST SOM IKKE BLIR DEKKET
        LevelOfCharge = E[j]['LevelOfCharge'] #BATTERISTATUS
        BatteryDischargeLimit = param[j]['BatteryDischargeLimit'] #MINUM BATTERNIVÅ
        bat_size_e_adj = param[j]['BatteryCapacity'] #MAX OPP/UTLADNINGSEFFEKT AV BATTERI
        max_power = param[0]['MaxPower']
    
        
        #FJERNE FLUER
        if res_load[timestep] < 0.01:
            res_load[timestep] = 0
            
        if lost_production[timestep] < 0.01:
            lost_production[timestep] = 0


        if biddingstatus_PV[j] == 2: #SELGE
        
            count_sellers_PV += 1
            energy_profit_pv[j] = lost_production[timestep]
                     
            seller_index_pv.append(j)
                
            
        else:
            if (biddingstatus_PV[j] == 1): #KJØPE
            
                count_buyers_PV += 1
                energy_demand_pv[j] = res_load[timestep]

                buyer_index_pv.append(j)
                
                
                #BIDDINGSTATUS == 0 -> HAR IKKE BEHOV FOR Å KJØPE ELLER SELGE
                
               
        if biddingstatus_battery[j] == 2: #SELGE
         
             count_sellers_battery += 1
             energy_profit_battery[j] = LevelOfCharge[timestep-1]-BatteryDischargeLimit
             
             if energy_profit_battery[j] < BatteryDischargeLimit:
                 
                 energy_profit_battery[j] = 0
             
             
             seller_index_battery.append(j)
    
             
        else:
             if (biddingstatus_battery[j] == 1): #KJØPE
             
                 count_buyers_battery += 1 
                 energy_demand_battery[j] = bat_size_e_adj-BatteryDischargeLimit
                 
                 buyer_index_battery.append(j)
                 
                 
            #batteriet lades opp/ut ettersom hva som blir igjen
            
             else:
                if (biddingstatus_battery[j] == 0):
                    
                    '''
                    FLEXBATTERI HAR BATTERINIVÅ I MELLOM MAX OG MIN. NOE SOM VIL SI AT DET BÅDE KAN LADES
                    UT OG OPP ETTER BEHOV
                    '''
                    
                    count_buyers_battery_flex += 1 
                    flex_index_battery.append(j)
                    
    
    sum_energy_profit_pv = sum(energy_profit_pv) 
    #DEN TOTALE OVERSKUDDET AV SOLENERGI I HYTTEFELTET
    
    sum_energy_demand_pv = sum(energy_demand_pv)
    #DEN TOTALE ETTERSPØRSELEN ETTER ENERGI FOR Å DEKKE ESTIMERT FORBRUK
   
    
    if sum_energy_profit_pv == sum_energy_demand_pv: 
    
        '''
        OVERSKUDDET AV SOL I HYTTEFELTET TILSVARER AKURATT UNDERSKUDDET AV FORBRUK. NOE SOM VIL SI AT I DET GITTE TIDS-
        STEGET VIL ALT OVERSKUDD UTVEKSELS MED UNDERSKUDD. LOST_LOAD OG LOST_PRODUCTION VIL BEGGE FÅ VERDIEN 0.
        DETTE SKJER TYPISK KUN NÅR BEGGE VERDIENE ER 0.
        '''
                
        if sum_energy_profit_pv == 0:
            
            '''
            OVERSKUDD OG UNDERSKUDD ER NULL SAMTIDIG
            '''
            
            #MAX EFFEKTFLYT I BATTERIENE, SLIK AT DE IKKE KAN LADES UT/OPP UENDELIG MYE.
            
            for j in seller_index_battery:
                
                transfer_battery_energy_limit = param[0]['MaxPower']*0.25 
                
                for i in buyer_index_battery:
                             
                    E[j]['LevelOfCharge'][timestep] -= transfer_battery_energy_limit
                    
                    if (E[j]['LevelOfCharge'][timestep] < param[j]['BatteryDischargeLimit']):
                        #DERSOM BATTERIET HAR BLITT LADET UT UNDER MINIMUM
                    
                        
                        rest = param[j]['BatteryDischargeLimit'] - E[j]['LevelOfCharge'][timestep]
                        E[j]['LevelOfCharge'][timestep] = param[j]['BatteryDischargeLimit']
                        transfer_battery_energy_limit -= rest
                        #EN RESTENERGI VIL ETTERALTES
                        
                        if transfer_battery_energy_limit < 0:
                            
                            transfer_battery_energy_limit = 0
                        
                    
                    E[i]['LevelOfCharge'][timestep] += transfer_battery_energy_limit   
                    
                    if E[i]['LevelOfCharge'][timestep] < param[i]['BatteryDischargeLimit']:
                                
                                   E[i]['LevelOfCharge'][timestep] = param[i]['BatteryDischargeLimit']
                                   
                    else:
                        if E[i]['LevelOfCharge'][timestep] > param[i]['BatteryCapacity']:
                                    
                                    E[i]['LevelOfCharge'][timestep] = param[i]['BatteryCapacity']
                
            
            
            for j in flex_index_battery:
                
                transfer_battery_energy_limit = param[0]['MaxPower']*0.25 
                
                for i in buyer_index_battery:
                
                    E[j]['LevelOfCharge'][timestep] -= transfer_battery_energy_limit
                    
                   
                    if (E[j]['LevelOfCharge'][timestep] < param[j]['BatteryDischargeLimit']):
                        #DERSOM BATTERIET HAR BLITT LADET UT UNDER MINIMUM
                    
                        rest = param[j]['BatteryDischargeLimit'] - E[j]['LevelOfCharge'][timestep]
                        E[j]['LevelOfCharge'][timestep] = param[j]['BatteryDischargeLimit']
                        transfer_battery_energy_limit -= rest
                        #EN RESTENERGI VIL ETTERALTES
                        
                        if transfer_battery_energy_limit < 0:
                            
                            transfer_battery_energy_limit = 0
                    
                    
                    E[i]['LevelOfCharge'][timestep] += transfer_battery_energy_limit  
                    
                    if E[i]['LevelOfCharge'][timestep] < param[i]['BatteryDischargeLimit']:
                        
                           E[i]['LevelOfCharge'][timestep] = param[i]['BatteryDischargeLimit']
                           
                    else:
                        if E[i]['LevelOfCharge'][timestep] > param[i]['BatteryCapacity']:
                            
                            E[i]['LevelOfCharge'][timestep] = param[i]['BatteryCapacity']
                       
                    
        else: #OVERSKUDD OG UNDERSKUDD ER IKKE NULL SAMTIDIG, MEN EN ANNEN VERDI
        
            for j in seller_index_pv:
  
                for j in buyer_index_pv:
                    
                        E[i]['lost_production'][timestep] = 0
                        E[j]['lost_load'][timestep] = 0
                        #ENERGIEN UTVEKSLES OG INGENTING 
               
                        
            #DET KAN FORTSATT FOREKOMME UTVEKSLING MELLOM BATTERIENE
            transfer_battery_energy_limit = param[0]['MaxPower']*0.25 
            
            for j in seller_index_battery:
                
                for i in buyer_index_battery:
                             
                    E[j]['LevelOfCharge'][timestep] -= transfer_battery_energy_limit
                    
                    if (E[j]['LevelOfCharge'][timestep] < param[j]['BatteryDischargeLimit']):
                        #DERSOM BATTERIET HAR BLITT LADET UT UNDER MINIMUM
                    
                        rest = param[j]['BatteryDischargeLimit'] - E[j]['LevelOfCharge'][timestep]
                        E[j]['LevelOfCharge'][timestep] = param[j]['BatteryDischargeLimit']
                        transfer_battery_energy_limit -= rest
                        #EN RESTENERGI VIL ETTERALTES
                        
                        if transfer_battery_energy_limit < 0:
                            
                            transfer_battery_energy_limit = 0
                    
                    
                    E[i]['LevelOfCharge'][timestep] += transfer_battery_energy_limit 
                    
                    if E[i]['LevelOfCharge'][timestep] < param[i]['BatteryDischargeLimit']:
                        
                           E[i]['LevelOfCharge'][timestep] = param[i]['BatteryDischargeLimit']
                           
                    else:
                        if E[i]['LevelOfCharge'][timestep] > param[i]['BatteryCapacity']:
                            
                            E[i]['LevelOfCharge'][timestep] = param[i]['BatteryCapacity']
                
                
            for j in flex_index_battery:
                
                for i in buyer_index_battery:
                
                    E[j]['LevelOfCharge'][timestep] -= transfer_battery_energy_limit
                    
                    if (E[j]['LevelOfCharge'][timestep] < param[j]['BatteryDischargeLimit']):
                        #DERSOM BATTERIET HAR BLITT LADET UT UNDER MINIMUM
                    
                        rest = param[j]['BatteryDischargeLimit'] - E[j]['LevelOfCharge'][timestep]
                        E[j]['LevelOfCharge'][timestep] = param[j]['BatteryDischargeLimit']
                        transfer_battery_energy_limit -= rest
                        #EN RESTENERGI VIL ETTERALTES
                        
                        if transfer_battery_energy_limit < 0:
                            
                            transfer_battery_energy_limit = 0
                    
                    
                    E[i]['LevelOfCharge'][timestep] += transfer_battery_energy_limit 
                    
                    if E[i]['LevelOfCharge'][timestep] < param[i]['BatteryDischargeLimit']:
                        
                           E[i]['LevelOfCharge'][timestep] = param[i]['BatteryDischargeLimit']
                           
                    else:
                        if E[i]['LevelOfCharge'][timestep] > param[i]['BatteryCapacity']:
                            
                            E[i]['LevelOfCharge'][timestep] = param[i]['BatteryCapacity']
                        
                     

    #-------------------------------------------------------------------------------------------------------------        
            
    else:
        if sum_energy_profit_pv > sum_energy_demand_pv: 
            #DET FINNES MER OVERSKUDD AV SOLENERGI ENN UNDERSKUDD AV FORBRUK I HYTTEFELTET
            
            #FJERNE FLUER
            if (sum_energy_profit_pv-sum_energy_profit_pv) < 0.001:
                
                energytransfer_per_participant = 0
            
            else:
                
                energytransfer_per_participant = min(((sum_energy_demand_pv/count_sellers_PV)/count_buyers_PV), max_power)
                #HER PRIORITERES PV-KJØPERE (ENERGI TIL FORBURUK) FØR BATTERI KJØPERE
                #SELGES LIKE MYE FRA HVERT PV ANLEGG, OG LIKE MYE TIL HVERT ANLEGG SOM VIL KJØPE
            
            surplus_energy = sum_energy_profit_pv-sum_energy_demand_pv
            #HVA SOM BLIR TIL OVERS ETTER AT OVERSKUDDSSOL HAR DEKKET OPP TIL ET NIVÅ AV TAPT FORBURK.
            #DETTE MÅ LADES PÅ ULIKE BATTERIER I HYTTEFELTET


            for j in seller_index_pv:
                
                for i in buyer_index_pv:
                

                 E[j]['lost_production'][timestep] -= energytransfer_per_participant
                 E[i]['lost_load'][timestep] = 0 
                 #SIDEN DET I DETTE TILFELLE ER OVERSKUDD AV SOLENERGI VERSUS FORBURK, VIL ALL TATPT LAST BLI DEKT
              

            if ((count_sellers_battery != 0) & (count_buyers_battery_flex != 0)):
                #DET FINNES BÅDE FLEX OG VANLIGE BATTERIER I HYTTEFELTET SOM VIL SELGE SIN ENERGI. FLEX BATTERI TRENGER IKKE NØDVENDIGVIS 
                #VÆRE FULLADET, I MOTSETNING TIL VANLIGE "SELLERS". 
                
                count_buyers_battery_flex = 0
                #FLEX BATTERIET HAR ANDRE PRIORITET. LADES KUN UT DETSROM DET ER NOE TIL OVERS ETTER AT ALLE 
                #FULL-LADETE BATTERIER HAR GJORT SITT
                
                
                
                if (count_buyers_battery+count_buyers_battery_flex) == 0:
                
                    battery_buying_transfer = 0
                    
                else:
                
                    
                    battery_buying_transfer = min(((surplus_energy/(count_buyers_battery+count_buyers_battery_flex))*0.25), max_power*0.25)
                    #DET SELGES LIKE MYE FRA HVERT BATTERI, ENERGI PER BATTERI AVHENGER AV ANTALL BATTERIER SOM VIL SELGE
           
         
                for j in seller_index_battery:
                     
                     for i in buyer_index_battery:
                        
  
                        E[j]['LevelOfCharge'] -= battery_buying_transfer
                        
                        if (E[j]['LevelOfCharge'][timestep] < param[j]['BatteryDischargeLimit']):
                            #DERSOM BATTERIET HAR BLITT LADET UT UNDER MINIMUM
                        
                            rest = param[j]['BatteryDischargeLimit'] - E[j]['LevelOfCharge'][timestep]
                            E[j]['LevelOfCharge'][timestep] = param[j]['BatteryDischargeLimit']
                            battery_buying_transfer -= rest
                            
                            if battery_buying_transfer < 0:
                                
                                battery_buying_transfer = 0
                            #EN RESTENERGI VIL ETTERALTES
                        
                        
                        E[i]['LevelOfCharge'][timestep] += battery_buying_transfer
                        
                        if E[i]['LevelOfCharge'][timestep] < param[i]['BatteryDischargeLimit']:
                            
                               E[i]['LevelOfCharge'][timestep] = param[i]['BatteryDischargeLimit']
                               
                        else:
                            if E[i]['LevelOfCharge'][timestep] > param[i]['BatteryCapacity']:
                                
                                E[i]['LevelOfCharge'][timestep] = param[i]['BatteryCapacity']
                        
                    
                       
                       
            else:
                if (count_buyers_battery+count_buyers_battery_flex) == 0:
                    #INGEN BATTERI VIL KJØPE
                
                    battery_buying_transfer = 0
                    
                else:
                    
                    battery_buying_transfer = min(((surplus_energy/(count_buyers_battery+count_buyers_battery_flex))*0.25), max_power*0.25)
                    
           
         
                for j in flex_index_battery:
                     
                     for i in buyer_index_battery:
                        
                        
                
                        E[j]['LevelOfCharge'] -= battery_buying_transfer
                        
                        if (E[j]['LevelOfCharge'][timestep] < param[j]['BatteryDischargeLimit']):
                            #DERSOM BATTERIET HAR BLITT LADET UT UNDER MINIMUM
                        
                            rest = param[j]['BatteryDischargeLimit'] - E[j]['LevelOfCharge'][timestep]
                            E[j]['LevelOfCharge'][timestep] = param[j]['BatteryDischargeLimit']
                            battery_buying_transfer -= rest
                            #EN RESTENERGI VIL ETTERALTES
                            
                            if battery_buying_transfer < 0:
                                
                                battery_buying_transfer = 0
                        
                        E[i]['LevelOfCharge'][timestep] += battery_buying_transfer
                        
                        if E[i]['LevelOfCharge'][timestep] < param[i]['BatteryDischargeLimit']:
                            
                               E[i]['LevelOfCharge'][timestep] = param[i]['BatteryDischargeLimit']
                               
                        else:
                            if E[i]['LevelOfCharge'][timestep] > param[i]['BatteryCapacity']:
                                
                                E[i]['LevelOfCharge'][timestep] = param[i]['BatteryCapacity']
                       
                    
                      
      #-------------------------------------------------------------------------------------------------------------           
                
        else:
             if sum_energy_profit_pv < sum_energy_demand_pv: 
                 #DET ER ET STØRRE UNDERSKUDD AV FORBRUK ENND ET ER OVERSKUDD AV SOL
              
                 transfer_pv = np.zeros(deltakere)
               
                    
                 #-----------------------------------------------------------------------------------------
                 
                 if (len(seller_index_pv) > 0): 
                     #DET FINNES DELTAKERE SOM VIL SELGE SOLENERGI
                     
                     for j in seller_index_pv:
                         
                        
                         transfer_pv[j] = E[j]['lost_production'][timestep] 
                         E[j]['lost_production'][timestep] -= transfer_pv[j] 
                         #ALL OVERSKUDD FRA SOLENERGI SELGES
                         

                     sum_transfer_pv = sum(transfer_pv)
                     #TOTAL MENGDE SOLENERGI SOM LEGGES UT FOR SALG
                     
                     transfer_pv_per_participant = min((sum_transfer_pv/count_buyers_PV), max_power)
                     #SELGES LIKE MYE TIL HVER KJØPER
                             
                     
                     for j in buyer_index_pv:                  
                         
                         
                     
                         E[j]['lost_load'][timestep] -= transfer_pv_per_participant 
            

                     lost_load = sum(energy_demand_pv)-sum_transfer_pv 
                     #ENERGIEN SOM BLIR TIL Å DEKKE DET TOTALE UNDERSKUDDET AV FORBRUK NÅR DE SOM HAR
                     #OVERSKUDD HAR SOLGT
                     
                     if (count_buyers_battery+count_buyers_battery_flex) == 0:
                     
                         lost_load_battery_transfer = 0
                         
                     else:
                     
                         lost_load_battery_transfer = min(((lost_load/(count_buyers_battery+count_buyers_battery_flex))*0.25), max_power*0.25)
                         #ENERGIEN SOM LADES UT FRA HVERT BATTERI SOM SELGER
                     
                     
                     if len(seller_index_battery) > 0:
                     #HVIS NOEN BATTERIER SELGER (ER FULLADET)
                         
                         for j in seller_index_battery: #1. prioritet
                         
                             for i in buyer_index_pv:
                                 
                                 
                                 E[j]['LevelOfCharge'][timestep] -= lost_load_battery_transfer
                                 
                                 if (E[j]['LevelOfCharge'][timestep] < param[j]['BatteryDischargeLimit']):
                                     #DERSOM BATTERIET HAR BLITT LADET UT UNDER MINIMUM
                                 
                                     rest = param[j]['BatteryDischargeLimit'] - E[j]['LevelOfCharge'][timestep]
                                     E[j]['LevelOfCharge'][timestep] = param[j]['BatteryDischargeLimit']
                                     lost_load_battery_transfer -= rest
                                     #EN RESTENERGI VIL ETTERALTES
                                     
                                     if lost_load_battery_transfer < 0:
                                         
                                         lost_load_battery_transfer = 0
                                 
                                 #ENERGI FRA ET NABOBATTERI TIL ANLEGG 
                                 E[i]['lost_load'][timestep] -= lost_load_battery_transfer/0.25
                                 
                                 
                                 if E[i]['lost_load'][timestep] < 0:
                                     
                                     #DERSOM ENERGIEN FRA BATTERIET VIL DEKKE MER ENN DET DET SOM TRENGS 
                                     #FOR Å DEKKE FORBRUKET I EN INSTALLASJON. OPPSTÅR EN REST PÅ SAMME MÅTEN SOM
                                     #OVENFOR
                                     
                                     rest = -1*E[i]['lost_load'][timestep] 
                                     E[i]['lost_load'][timestep] = 0
                                     lost_load_battery_transfer += rest*0.25
                             
                                 
                     if len(flex_index_battery) > 0:
                     #HVIS NOEN BATTERIER SELGER (IKKE FULLADET)
                     
                             for j in flex_index_battery:

                                 for i in buyer_index_pv:
                                 
                              
                                     E[j]['LevelOfCharge'][timestep] -= lost_load_battery_transfer
                                     
                                     
                                     if (E[j]['LevelOfCharge'][timestep] < param[j]['BatteryDischargeLimit']):
                                         #DERSOM BATTERIET HAR BLITT LADET UT UNDER MINIMUM
                                     
                                         rest = param[j]['BatteryDischargeLimit'] - E[j]['LevelOfCharge'][timestep]                                  
                                         E[j]['LevelOfCharge'][timestep] = param[j]['BatteryDischargeLimit']
                                         lost_load_battery_transfer -= rest
                                         #EN RESTENERGI VIL ETTERALTES
                                         
                                         if lost_load_battery_transfer < 0:
                                             
                                             lost_load_battery_transfer = 0
                                        
                                     E[i]['lost_load'][timestep] -= lost_load_battery_transfer/0.25
                                     #ENERGIEN SOM BATTERIET FORSYNER
                                     
                                     if E[i]['lost_load'][timestep] < 0:
                                         
                                         #DERSOM ENERGIEN FRA BATTERIET VIL DEKKE MER ENN DET DET SOM TRENGS 
                                         #FOR Å DEKKE FORBRUKET I EN INSTALLASJON. OPPSTÅR EN REST PÅ SAMME MÅTEN SOM
                                         #OVENFOR
                                         
                                         rest = -1*E[i]['lost_load'][timestep] 
                                         E[i]['lost_load'][timestep] = 0
                                         lost_load_battery_transfer += rest*0.25
                                 
                                 
                 else:
                      if (count_sellers_battery + count_buyers_battery_flex) > 0:
                          #INGEN MOMENTAN OVERSKUDD AV SOLENERGI, KUN BATTERIER SOM KAN BIDRA TIL SALG
                          
                          #if (count_buyers_PV >= (count_buyers_battery_flex + count_sellers_battery)):
                          
                          transfer_energy = min((sum_energy_demand_pv-sum_energy_profit_pv), max_power)
                          

                          #transfer_per_battery_2per_pv = ((transfer_energy/(count_sellers_battery+count_buyers_battery_flex))/count_buyers_PV)*0.25
                          #ENERGI HVERT BATTERI SOM SELGER LADES UT MED
                          
                          
                          if len(seller_index_battery) > 0:
                              #FULLADET BATTERI LADES UT
                           
                              for j in seller_index_battery: #1. prioritet
                                                     
                                      transfer_per_battery_2per_pv = min((((transfer_energy/(count_sellers_battery+count_buyers_battery_flex))/count_buyers_PV)*0.25), max_power*0.25)
                                
                                      for i in buyer_index_pv: 
                                      

                                        E[j]['LevelOfCharge'][timestep] -= transfer_per_battery_2per_pv
                                        
                                        if (E[j]['LevelOfCharge'][timestep] < param[j]['BatteryDischargeLimit']):
                                            #DERSOM BATTERIET HAR BLITT LADET UT UNDER MINIMUM
                                        
                                            rest = param[j]['BatteryDischargeLimit'] - E[j]['LevelOfCharge'][timestep]
                                            E[j]['LevelOfCharge'][timestep] = param[j]['BatteryDischargeLimit']
                                            transfer_per_battery_2per_pv -= rest
                                            
                                            if transfer_per_battery_2per_pv < 0:
                                                
                                                transfer_per_battery_2per_pv = 0
                                
                                            #EN RESTENERGI VIL ETTERALTES
                                        
                                        E[i]['lost_load'][timestep] -= transfer_per_battery_2per_pv/0.25
                                        
                                        
                                        
                                        if E[i]['lost_load'][timestep] < 0:
                    
                                            #UNNGÅ NEGATIVE TALL
                                            rest = -1*E[i]['lost_load'][timestep] 
                                            E[i]['lost_load'][timestep] = 0
                                            transfer_per_battery_2per_pv += rest*0.25
                                        
                                    
                          if len(flex_index_battery) > 0:
                              #FELX BATTERI LADES UT
                              
                                  for j in flex_index_battery:
                                      
                                      
                                      transfer_per_battery_2per_pv = min((((transfer_energy/(count_sellers_battery+count_buyers_battery_flex))/count_buyers_PV)*0.25), max_power*0.25)
                                          
                                      for i in buyer_index_pv: 
                                          
    
                                              E[j]['LevelOfCharge'][timestep] -= transfer_per_battery_2per_pv
                                              
                                              
                                              if (E[j]['LevelOfCharge'][timestep] < param[j]['BatteryDischargeLimit']):
                                                  #DERSOM BATTERIET HAR BLITT LADET UT UNDER MINIMUM
                                              
                                                  rest = param[j]['BatteryDischargeLimit'] - E[j]['LevelOfCharge'][timestep]
                                                  E[j]['LevelOfCharge'][timestep] = param[j]['BatteryDischargeLimit']
                                                  transfer_per_battery_2per_pv -= rest
                                                  
                                                  if transfer_per_battery_2per_pv < 0.01:
                                                      
                                                      transfer_per_battery_2per_pv = 0
                                                  
                                                  
                                                  #EN RESTENERGI VIL ETTERALTES
                                              
                                              
                                              E[i]['lost_load'][timestep] -= transfer_per_battery_2per_pv/0.25
                                                 
    
                                              if (E[i]['lost_load'][timestep] < 0):
                                                      
                                                      #UNNGÅ NEGATIVE TALL
                                                      rest = -1*E[i]['lost_load'][timestep] 
                                                      E[i]['lost_load'][timestep] = 0
                                                      transfer_per_battery_2per_pv += rest*0.25
                                                  
                       
                                              '''
                                              else:
           
                                                  E[j]['LevelOfCharge'][timestep] -= transfer_per_battery_2per_pv
                                                  
                                                  if (E[j]['LevelOfCharge'][timestep] < param[j]['BatteryDischargeLimit']):
                                                      #DERSOM BATTERIET HAR BLITT LADET UT UNDER MINIMUM
                                                  
                                                      rest = param[j]['BatteryDischargeLimit'] - E[j]['LevelOfCharge'][timestep]
                                                      E[j]['LevelOfCharge'][timestep] = param[j]['BatteryDischargeLimit']
                                                      transfer_per_battery_2per_pv -= rest
                                                      #EN RESTENERGI VIL ETTERALTES
                                                  
                                                  E[i]['lost_load'][timestep] -= transfer_per_battery_2per_pv/0.25
                                                  
                                                  if (E[i]['lost_load'][timestep] < 0):
                                                      
                                                      #UNNGÅ NEGATIV TALL
                                                      rest = -1*E[i]['lost_load'][timestep] 
                                                      E[i]['lost_load'][timestep] = 0
                                                      transfer_per_battery_2per_pv += rest*0.25
                                              '''
                                                

    
       
                                          
    return E
    
            
            