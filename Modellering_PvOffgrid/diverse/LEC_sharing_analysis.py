# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 10:13:49 2023

@author: halgr

"""
import numpy as np


def energysharing_per_timestep_analysis(E, param, biddingstatus_PV, biddingstatus_battery, timestep):
    
    deltakere = len(param)
    
    
    count_sellers_PV = 0
    count_buyers_PV = 0
    count_sellers_battery = 0
    count_buyers_battery = 0
    count_buyers_battery_flex = 0
    
    energy_profit_pv = np.zeros(deltakere)
    energy_demand_pv = np.zeros(deltakere)
    
    energy_profit_battery = np.zeros(deltakere)
    energy_demand_battery = np.zeros(deltakere)
    
    seller_index_pv = []
    buyer_index_pv = []
    seller_index_battery = []
    buyer_index_battery = [] #default like mange som antall deltakere
    flex_index_battery = []
    
   
    #-------------------------------------------------------------------------------------------------------------       
    
    
    
    for j in range(deltakere):  
        
        #OBS, LOST PRODUCTION ER EFFEKTEN SOM BLIR IGJEN ETTER Å HA LADET EGET BATTERI
        lost_production = E[j]['lost_production'] #ENDRE
        res_load = E[j]['lost_load']
        LevelOfCharge = E[j]['LevelOfCharge']
        BatteryDischargeLimit = param[j]['BatteryDischargeLimit']
        bat_size_e_adj = param[j]['BatteryCapacity']
    
        #print('Before {}'.format(E[j]['res_pv'][timestep]))


        if biddingstatus_PV[j] == 2: #sell
        
            count_sellers_PV += 1
            energy_profit_pv[j] = lost_production[timestep]
            
            
            seller_index_pv.append(j)
                
            
        else:
            if (biddingstatus_PV[j] == 1):
            
                count_buyers_PV += 1
                energy_demand_pv[j] = res_load[timestep]
                
               
                buyer_index_pv.append(j)
                
                
                #biddingstatus_PV == 0 -> doesnt sell or buy
                
               
        if biddingstatus_battery[j] == 2: #sell
         
             count_sellers_battery += 1
             energy_profit_battery[j] = LevelOfCharge[timestep-1]-BatteryDischargeLimit
             
             
             seller_index_battery.append(j)
            
             
             
        else:
             if (biddingstatus_battery[j] == 1): #buy
             
                
                 count_buyers_battery += 1 
                 energy_demand_battery[j] = bat_size_e_adj-BatteryDischargeLimit
                 
              
                 buyer_index_battery.append(j)
                 
                 
                 
            #batteriet lades opp/ut ettersom hva som blir igjen
            
             else:
                if (biddingstatus_battery[j] == 0):
                    
                    
                    count_buyers_battery_flex += 1 
                    flex_index_battery.append(j)
                    
    #print('ffffffffffffffffffffffffffff')
    #print(count_buyers_PV)
    #print(count_buyers_battery)
    #print(count_buyers_battery_flex)
    #print()
    sum_energy_profit_pv = sum(energy_profit_pv) #sendes til nabo (buyers) eller lades på abtteri
    sum_energy_demand_pv = sum(energy_demand_pv)
    print()
    print('Total overskudd fra sol etter at anleggene har dekket eget forbruk: {:.3g}kWh'.format(sum_energy_profit_pv*0.25)) #summen av all overskudds sol
    print('Totalt underskudd av last blant hyttene: {:.3g}kWh'.format(sum_energy_demand_pv*0.25)) #summen av all last som ikke er dekket     
    print()
    print('Bidding status PV:') 
    print(biddingstatus_PV) #summen av all overskudds sol
    print('Bidding status battery:') 
    print(biddingstatus_battery)
    print()
    print('Pv buyers: {:.3g}'.format(count_buyers_PV)) 
    print('Pv sellers: {:.3g}'.format(count_sellers_PV)) 
    print('Battery buyers: {:.3g}'.format(count_buyers_battery)) 
    print('Battery sellers: {:.3g}'.format(count_sellers_battery)) 
    print('Flex Battery: {:.3g}'.format(count_buyers_battery_flex)) 
    
    if sum_energy_profit_pv == sum_energy_demand_pv: #SELLES AKURATT LIKE MYE SOM DET KJØPES AV NABOER AV MOMENTAN PRODUSKJON
    #alt overskudd går til å dekke andres forbruk    
        
        if sum_energy_profit_pv == 0:
            
            print()
            print('Overskudd fra sol og underskudd av forbruk er i tidsøyblikket lik 0')
            print('Energiflyt mellom batteriene kan fortsatt forekomme')
            print()
            
            
            transfer_battery_energy_limit = 1 #kWh
            #Hvor mye som maksimalt kan lades ut/opp av batteri
            
            
            for j in seller_index_battery:
                
                for i in buyer_index_battery:
                
                    print('Batteri i hytte {:.3g} selger:'.format(j))
                    print('Batteri i hytte {:.3g} kjøper:'.format(i))
                    print('-------------------------------------------------')
                    print('Batteristatus for selger før salg: {:.3g}kWh'.format(E[j]['LevelOfCharge'][timestep]))
                    print('Batteristatus for kjøper før salg: {:.3g}kWh'.format(E[i]['LevelOfCharge'][timestep]))
                    
                    E[j]['LevelOfCharge'][timestep] -= transfer_battery_energy_limit
                    
                    E[i]['LevelOfCharge'][timestep] += transfer_battery_energy_limit   
                    
                    print('Batteristatus for selger etter salg: {:.3g}kWh'.format(E[j]['LevelOfCharge'][timestep]))
                    print('Batteristatus for kjøper etter salg: {:.3g}kWh'.format(E[i]['LevelOfCharge'][timestep]))         
                    print('-------------------------------------------------')
            
            for j in flex_index_battery:
                
                for i in buyer_index_battery:
                
                    print('Batteri (flex) i hytte {:.3g} selger:'.format(j))
                    print('Batteri i hytte {:.3g} kjøper:'.format(i))
                    print('-------------------------------------------------')
                    print('Batteristatus for selger før salg: {:.3g}kWh'.format(E[j]['LevelOfCharge'][timestep]))
                    print('Batteristatus for kjøper før salg: {:.3g}kWh'.format(E[i]['LevelOfCharge'][timestep]))
                    
                    E[j]['LevelOfCharge'][timestep] -= transfer_battery_energy_limit
                    E[i]['LevelOfCharge'][timestep] += transfer_battery_energy_limit   
                    
                    print('Batteristatus for selger etter salg: {:.3g}kWh'.format(E[j]['LevelOfCharge'][timestep]))
                    print('Batteristatus for kjøper etter salg: {:.3g}kWh'.format(E[i]['LevelOfCharge'][timestep]))         
                    print('-------------------------------------------------')
              
                    
        else:
        
            for j in seller_index_pv:
  
                for j in buyer_index_pv:
                    
                    
                        print('Hytte {:.3g} selger momentan produksjon:'.format(j))
                        print('Hytte {:.3g} kjøper momentan produksjon:'.format(i))
                        print('-------------------------------------------------')
                        print('Tapt produksjon i gitt tidssteg for selger før salg: {:.3g}kWh'.format(E[i]['lost_production'][timestep]*0.25))
                        print('Tapt last i gitt tidssteg for kjøper før salg: {:.3g}kWh'.format(E[j]['lost_load'][timestep]*0.25))
                        
                        E[i]['lost_production'][timestep] = 0
                        E[j]['lost_load'][timestep] = 0
                        
                        print('Tapt last i gitt tidssteg for kjøper etter salg: {:.3g}kWh'.format(E[i]['lost_load'][timestep]*0.25))
                        print('-------------------------------------------------')
                        
            
            
    #-------------------------------------------------------------------------------------------------------------        
            
    else:
        if sum_energy_profit_pv > sum_energy_demand_pv: #PRODUSERES MER ENERGI ENN DET KREVES
            #SELLES TIL NABOER PLUSS AT DET ER OVERSKUDD IGJEN
            
            energytransfer_per_participant = (sum_energy_demand_pv/count_sellers_PV)/count_buyers_PV
            #Kan ha både pv og batteri kjøpere. Pv prioriteres
            
            surplus_energy = sum_energy_profit_pv-sum_energy_demand_pv
            #Hva som blir igjen etter at momentan last er dekket

            
            for j in seller_index_pv:
                
                for i in buyer_index_pv:
                
                 print()
                 print('Hytte {:.3g} selger momentan produksjon'.format(j))
                 print('Hytte {:.3g} kjøper momentan produksjon'.format(i))
                 print('-------------------------------------------------')
                 print('Tapt produksjon i gitt tidssteg for selger før salg: {:.3g}kWh'.format(E[j]['lost_production'][timestep]*0.25))
                 print('Tapt last i gitt tidssteg for kjøper før salg: {:.3g}kWh'.format(E[i]['lost_load'][timestep]*0.25))

                 E[j]['lost_production'][timestep] -= energytransfer_per_participant
                 E[i]['lost_load'][timestep] = 0 #Alt dekkes
              
                 print('Tapt produksjon i gitt tidssteg for selger etter salg: {:.3g}kWh'.format(E[j]['lost_production'][timestep]*0.25))
                 print('Tapt last i gitt tidssteg for kjøper etter salg: {:.3g}kWh'.format(E[i]['lost_load'][timestep]*0.25))
                 print('-------------------------------------------------')
                 print('Overskud av energi etter at momentan last er dekket (som kan lades på batteri): {:.3g}kWh'.format(surplus_energy*0.25))
                

            if (count_sellers_battery != 0) & (count_buyers_battery_flex != 0):
                
                count_buyers_battery_flex = 0
                #flex batteriet lades kun ut om ingen andre batteri kan selge (og noen vil kjøpe)
                
                battery_buying_transfer = surplus_energy/(count_buyers_battery+count_buyers_battery_flex)
           
         
                for j in seller_index_battery:
                     
                     for i in buyer_index_battery:
                        
                        
                        print('-----------------------------------------------------')
                        print('ENERGIFLYT FRA BATTERI')
                        print('Batteri {:.3g} lades ut:'.format(j))
                        print('Hytte {:.3g} kjøper:'.format(i))
                        print('Batteristatus for selger før salg: {:.3g}kWh'.format(E[j]['LevelOfCharge'][timestep]))
                        print('Batteristatus for kjøper før salg: {:.3g}kWh'.format(E[i]['LevelOfCharge'][timestep]))
                        
                        E[j]['LevelOfCharge'] -= battery_buying_transfer
                        E[i]['LevelOfCharge'][timestep] += battery_buying_transfer
                    
                        print('Batteristatus for selger etter salg: {:.3g}kWh'.format(E[j]['LevelOfCharge'][timestep]))
                       
            else:
                  
                battery_buying_transfer = surplus_energy/(count_buyers_battery+count_buyers_battery_flex)
           
         
                for j in flex_index_battery:
                     
                     for i in buyer_index_battery:
                        
                        
                        print('-----------------------------------------------------')
                        print('ENERGIFLYT FRA BATTERI')
                        print('Batteri (flex) {:.3g} lades ut:'.format(j))
                        print('Hytte {:.3g} kjøper:'.format(i))
                        print('Batteristatus for selger før salg: {:.3g}kWh'.format(E[j]['LevelOfCharge'][timestep]))
                        print('Batteristatus for kjøper før salg: {:.3g}kWh'.format(E[i]['LevelOfCharge'][timestep]))
                        
                        E[j]['LevelOfCharge'] -= battery_buying_transfer
                        E[i]['LevelOfCharge'][timestep] += battery_buying_transfer
    
                    
                        print('Batteristatus for selger etter salg: {:.3g}kWh'.format(E[j]['LevelOfCharge'][timestep]))
                        print('Batteristatus for kjøper før salg: {:.3g}kWh'.format(E[i]['LevelOfCharge'][timestep]))
      #-------------------------------------------------------------------------------------------------------------           
                
        else:
             if sum_energy_profit_pv < sum_energy_demand_pv: 
                 #PRODUSERES MINDRE TOTALT SETT I HYTTEFELTET ENN DET KREVES, BATTERI MÅ LADES UT
              
                 transfer_pv = np.zeros(deltakere)
                 print()
                 print('Index PV buyers:')
                 print(buyer_index_pv)
                 print('Index PV sellers:')
                 print(seller_index_pv)
                 print('Index battery buyers:')
                 print(buyer_index_battery)
                 print('Index battery sellers:')
                 print(seller_index_battery)
                 print('Index flex battery (can both sell and buy):')
                 print(flex_index_battery)
                 print()
                    
                 #-----------------------------------------------------------------------------------------
                 
                 if (len(seller_index_pv) > 0): 
                     #det er noe sol i hyttefeltet til salgs
                     
                     for j in seller_index_pv:
                         
                         print('ENERGIFLYT DIREKTE MELLOM PV-ANLEGG')
                         print('Hytte {:.3g} legger ut energi for salg:'.format(j))
                         print('Overskudd av momentan energi for selger før salg: {:.3g}kWh'.format(E[j]['lost_production'][timestep]*0.25))
                         
                         transfer_pv[j] = E[j]['lost_production'][timestep] 
                         E[j]['lost_production'][timestep] -= transfer_pv[j] 
                         
                         print('Overskudd av momentan energi for selger etter salg: {:.3g}kWh'.format(E[j]['lost_production'][timestep]*0.25))
                         #Alt selges for de/den som har overskudd
                             
                     sum_transfer_pv = sum(transfer_pv)
                     #total mengde som er legges ut for salg
                             
                     for j in buyer_index_pv:                  
                         
                         
                         print('Hytte {:.3g} kjøper energi:'.format(j))
                         transfer_pv_per_participant = sum_transfer_pv/count_buyers_PV
                         
                         print('Underskudd av momentan energi for kjøper etter salg: {:.3g}kWh'.format(E[j]['lost_load'][timestep]*0.25))
                         
                         E[j]['lost_load'][timestep] -= transfer_pv_per_participant 
            
                         print('Underskudd av momentan energi for kjøper etter salg: {:.3g}kWh'.format(E[j]['lost_load'][timestep]*0.25))
                  #-----------------------------------------------------------------------------------------
  
    
    
                     lost_load = sum(energy_demand_pv)-sum_transfer_pv 
                     #DET SOM ER IGJEN ETTER AT ALL OVERSKUDDSSOL HAR GJORT SITT
                     
                     lost_load_battery_transfer = (lost_load/(count_buyers_battery+count_buyers_battery_flex))*0.25
                     #DET SOM SKAL LADES UT FRA HVERT BATTERI SOM SELGER
                     
                     if len(seller_index_battery) > 0:
                      
                         for j in seller_index_battery: #1. prioritet
                         
                             for i in buyer_index_pv:
                                 
                                 print('-----------------------------------------------------')
                                 print('ENERGIFLYT FRA BATTERI')
                                 print('Batteri {:.3g} selger:'.format(j))
                                 print('Hytte {:.3g} kjøper:'.format(i))
                                 print('Batteristatus for selger før salg: {:.3g}kWh'.format(E[j]['LevelOfCharge'][timestep]))
                                 print('Tapt last før kjøper før salg: {:.3g}kWh'.format(E[i]['lost_load'][timestep]*0.25))
                                 
                                 E[j]['LevelOfCharge'][timestep] -= lost_load_battery_transfer
                                 E[i]['lost_load'][timestep] -= lost_load_battery_transfer
                                 
                                 print('Batteristatus for selger etter salg: {:.3g}kWh'.format(E[j]['LevelOfCharge'][timestep]))
                                 print('Tapt last før kjøper etter salg: {:.3g}kWh'.format(E[i]['lost_load'][timestep]*0.25))
                                 
                     if len(flex_index_battery) > 0:
                             
                             for j in flex_index_battery:

                                 for i in buyer_index_pv:
                                 
                                     print('-----------------------------------------------------')
                                     print('ENERGIFLYT FRA BATTERI')
                                     print('Batteri (flex) {:.3g} lades ut:'.format(j))
                                     print('Hytte {:.3g} kjøper:'.format(i))
                                     print('Batteristatus for selger før salg: {:.3g}kWh'.format(E[j]['LevelOfCharge'][timestep]))
                                     print('Tapt last før kjøper før salg: {:.3g}kWh'.format(E[i]['lost_load'][timestep]*0.25))
                                     
                                     E[j]['LevelOfCharge'][timestep] -= lost_load_battery_transfer
                                     
                                     
                                     if (E[j]['LevelOfCharge'][timestep] < param[j]['BatteryDischargeLimit']):
                                     
                                         y = param[j]['BatteryDischargeLimit'] - E[j]['LevelOfCharge'][timestep]
                                         E[j]['LevelOfCharge'][timestep] = param[j]['BatteryDischargeLimit']
                                         lost_load_battery_transfer -= y
                                        
                                     E[i]['lost_load'][timestep] -= lost_load_battery_transfer/0.25
                                     
                                     if E[i]['lost_load'][timestep] < 0:
                                         
                                         #Ved å dele baterieffekten likt på de to anleggene vil vi dekke mer
                                         #enn nødvendig på det ene. Denne kodelinjen fikser dette.
                                         
                                         x = -1*E[i]['lost_load'][timestep] 
                                         E[i]['lost_load'][timestep] = 0
                                         lost_load_battery_transfer += x*0.25
                                 
                                     print('Batteristatus for selger etter salg: {:.3g}kWH'.format(E[j]['LevelOfCharge'][timestep]))
                                     print('Tapt last før kjøper etter salg: {:.3g}kWh'.format(E[i]['lost_load'][timestep]*0.25))
                 else:
                      if (count_sellers_battery + count_buyers_battery_flex) > 0:
                          #Det er ikke noe overskuddssol igjen, kun batterier bidrar
                          
                          #if (count_buyers_PV >= (count_buyers_battery_flex + count_sellers_battery)):
                          
        
                          transfer_energy = sum_energy_demand_pv-sum_energy_profit_pv
                  
                          transfer_per_battery_2per_pv = (transfer_energy/(count_sellers_battery+count_buyers_battery_flex))/count_buyers_PV
                          
                          
                          if len(seller_index_battery) > 0:
                           
                              for j in seller_index_battery: #1. prioritet
                                                                    
                                      for i in buyer_index_pv: 
                                      
                                      
                                        print('-----------------------------------------------------')
                                        print('ENERGIFLYT FRA BATTERI')
                                        print('Batteri {:.3g} lades ut:'.format(j))
                                        print('Hytte {:.3g} kjøper:'.format(i))
                                        print('Batteristatus for selger før salg: {:.3g}kWh'.format(E[j]['LevelOfCharge'][timestep]))
                                        print('Tapt last for kjøper før salg: {:.3g}kWh'.format(E[i]['lost_load'][timestep]*0.25))    
                                      
                                        E[j]['LevelOfCharge'][timestep] -= transfer_per_battery_2per_pv*0.25
                                        E[i]['lost_load'][timestep] -= transfer_per_battery_2per_pv
                                        
                                        if E[i]['lost_load'][timestep] < 0:
                                            
                                            #Ved å dele baterieffekten likt på de to anleggene vil vi dekke mer
                                            #enn nødvendig på det ene. Denne kodelinjen fikser dette.
                                            
                                            x = -1*E[i]['lost_load'][timestep] 
                                            E[i]['lost_load'][timestep] = 0
                                            transfer_per_battery_2per_pv += x
                                        
                                        print('Batteristatus for selger etter salg: {:.3g}kWh'.format(E[j]['LevelOfCharge'][timestep]))
                                        print('Tapt last for kjøper etter salg: {:.3g}kWh'.format(E[i]['lost_load'][timestep]*0.25))
                                      
                          if len(flex_index_battery) > 0:
                                  
                                  for j in flex_index_battery:
                                      
                                      for i in buyer_index_pv: 
                                      
                                    
                                          print('Batteri (flex) i hytte {:.3g} selger'.format(j))
                                          print('Anlegg i hytte {:.3g} kjøper:'.format(i))
                                          print('-----------------------------------------------------')
                                          print('Batteristatus for selger før salg: {:.3g}kWh'.format(E[j]['LevelOfCharge'][timestep]))
                                          
                                          x = E[j]['LevelOfCharge'][timestep] - transfer_per_battery_2per_pv*0.25
                                          #Batteriet kan ikke lades under minimum
                                          
                                          if x < param[j]['BatteryDischargeLimit']:     
                                          
                                              E[j]['LevelOfCharge'][timestep] = param[j]['BatteryDischargeLimit']
                                              
                                              print('Batteristatus for selger etter salg: {:.3g}kWh'.format(E[j]['LevelOfCharge'][timestep]))
                                              print('Tapt last i gitt tidssteg for kjøper før salg: {:.3g}kWh'.format(E[i]['lost_load'][timestep]*0.25))
                                              
                                              E[i]['lost_load'][timestep] -= (E[j]['LevelOfCharge'][timestep]-(param[j]['BatteryDischargeLimit']))/0.25
                                              
                
                                              
                                              if (E[i]['lost_load'][timestep] < 0):
                                                  
                                                  #Ved å dele baterieffekten likt på de to anleggene vil vi dekke mer
                                                  #enn nødvendig på det ene. Denne kodelinjen fikser dette.
                                                  
                                                  x = -1*E[i]['lost_load'][timestep] 
                                                  E[i]['lost_load'][timestep] = 0
                                                  transfer_per_battery_2per_pv += x
                                              
                                              print('Tapt last i gitt tidssteg for kjøper etter salg: {:.3g}kWh'.format(E[i]['lost_load'][timestep]*0.25))
                                              
                                              tapt_produksjon = E[j]['LevelOfCharge'][timestep] - transfer_per_battery_2per_pv*0.25 + param[j]['BatteryDischargeLimit']
                                              
                                              print('Tapt produksjon i hyttefeltet for gitt tidssteg: {:.3g}Wh'.format(tapt_produksjon*0.25*1000))
                                              print()
                              
                             
                                          else:
       
                                              E[j]['LevelOfCharge'][timestep] -= transfer_per_battery_2per_pv*0.25
                                              
                                              print('Batteristatus for selger etter: {:.3g}kWh'.format(E[j]['LevelOfCharge'][timestep]))
                                              print('Tapt last i gitt tidssteg for kjøper før salg: {:.3g}kWh'.format(E[i]['lost_load'][timestep]*0.25))
                                              
                                              E[i]['lost_load'][timestep] -= transfer_per_battery_2per_pv
                                              
                                              if (E[i]['lost_load'][timestep] < 0):
                                                  
                                                  #Ved å dele baterieffekten likt på de to anleggene vil vi dekke mer
                                                  #enn nødvendig på det ene. Denne kodelinjen fikser dette.
                                                  
                                                  x = -1*E[i]['lost_load'][timestep] 
                                                  E[i]['lost_load'][timestep] = 0
                                                  transfer_per_battery_2per_pv += x
                                              
                                              print('Tapt last i gitt tidssteg for kjøper etter salg: {:.3g}kWh'.format(E[i]['lost_load'][timestep]*0.25))
                                              print()
                              
                                           
                   
   
                   
    return E
    
            
            