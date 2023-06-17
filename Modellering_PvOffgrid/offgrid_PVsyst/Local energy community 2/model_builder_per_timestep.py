# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 09:28:18 2023

@author: halgr
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 15:53:18 2023

@author: halgr
"""

import numpy as np
import pandas as pd

import trade_pv2pv as trade_pv2pv
import trade_flex2pv as trade_flex2pv
import trade_batt2pv as trade_batt2pv
import trade_pv2batt as trade_pv2batt
import trade_flex2flex as trade_flex2flex
#Inneholder filer som redegjør rettferdig handel mellom deltakerene i markedet

#FJERNE DENNE VED FEILSØKING AV KODEN OM NOEN ÅR
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

'''
Denne filen simulerer energiflytsvariablene for alle deltakerene i et gitt tidssteg. 
Funksjonen som kjøres returnerer E. E er en dictionary med energiflytsvariablene 
tilørende N deltakere for tidssteget.
'''


#----------------------------------------
#aktiverer deling
energy_model_activate = 1

battery_share_activate = 0
flex_activate =  0

flex_limit = 0.4
#Jo høyere flex_limit, desto høyere batteristatus må flex-batteriet ha for å selge sin henergi.
#E[j]['LevelOfCharge'] > 0.5*battery_capacity + flex_limit*battery_capacity): -> SELGE
#E[j]['LevelOfCharge'] < 0.5*battery_capacity - flex_limit*battery_capacity): -> KJØPE  

#-----------------------------------------
  

#Grov spesifisering av hvilken dag det skal skrives ut handelsverdier for
#i kontrollvinduet
month = 9   #month -> 1-12
day = 15   #day -> 1-30
hour = 7   #hour -> 1-23
minute = 45    #kvarter -> 15,30,45

time_analysis = (month-1)*2880 + (day-1)*96 + hour*4 + minute/15



def E_per_timestep(dict_list, dict_count, param, time, demand, pv):

    
    E = {}
    bidding_battery = {}
    bidding_pv = {}
    
    return_series = True
    deltakere_n = len(param)
        
    
    #ENERGIFLYTSVERDIER FOR HVER DELTAKER I TIDSSTEGET "TIME" BEREGNES FØRST FØR DELING
    #----------------------------------------------------------------------------------------
    for x in range(len(param)):
        
    
        discharge_limit = param[x]['BatteryDischargeLimit']
        max_power_inverter = param[x]['MaxPowerInverter']
        max_power_battery = param[x]['MaxPower']
        
        
        if time == 0:
            
            #Initiell batteristatus
            LevelOfCharge_previous = 0.8*param[x]['BatteryCapacity']
        
        else:
            
            #Batteristatus etter forrige tidssteg
            LevelOfCharge_previous = dict_list[time-1][x]['LevelOfCharge']
            
            
        if LevelOfCharge_previous < discharge_limit:
            
            LevelOfCharge_previous = discharge_limit    
    

        
        #DEFINERE VARIABLER
        battery_capacity = param[x]['BatteryCapacity']
        n_bat = param[x]['BatteryEfficiency']
        n_inv = param[x]['InverterEfficiency']
        timestep = param[x]['timestep']
        
        
        #Her er virkningsgrad tatt med. De er tatt med i dette steget der deltaker forsyner seg selv
        pv2inv = np.minimum(pv[x][time], demand[x][time]/n_inv) 
        res_pv = np.maximum(pv[x][time] - demand[x][time]/n_inv, 0) 
        inv2load = pv2inv * n_inv
        res_load = (demand[x][time] - pv2inv * n_inv) 


        #1. prioritet etter at momentant forburk er dekket -> Forsyne eget batteri
        #FORSYNE EGET BATTERI
        if LevelOfCharge_previous >= battery_capacity:  
                    pv2store = 0 
            
        else: #BATTERIET ER IKKE FULT, MEN VIL OVERSTIGE MAX KAPASITET VED OPPLADING I GITT TIDSSTEG
                if (LevelOfCharge_previous + (res_pv * timestep)) > battery_capacity:
                    
                    #KAN MAX LADE OPP DET SOM ER IGJEN FØR BATTERIET NÅR MAX KAPASITET
                    pv2store = min((battery_capacity - LevelOfCharge_previous)/timestep, max_power_battery)
                    #OPPLADING PÅ EGET BATTERI BEGRENSES AV MAX LADEEFFEKT

    
                else: #BATTERIET ER IKKE FULT OG VIL IKKE OVERTIGE MAX KAPASITET VED OPPLADNING I GITT TIDSSTEG
                    #BEGRENSES AV MAX LADING PÅ BATTERI
                    pv2store = min(res_pv, max_power_battery)
             
        #Energi som flyter gjennom inverter og til å dekke eget forbruk     
        store2inv = min((LevelOfCharge_previous/timestep-discharge_limit/timestep), res_load/n_inv, max_power_battery)  

        
        #LADE OPP DET MAN KAN MED EGET OVERSKUDD
        LevelOfCharge = min(LevelOfCharge_previous - (store2inv - pv2store*n_bat) * timestep,  # DC - pv2store*n_bat
                                   battery_capacity)

        #-------------------------------------------------------------------------------------------
        
        
        #EFFEKT TIL FORBRUK. 
        inv2load = inv2load + store2inv*n_inv
        
        
        #EFFEKT SOM KAN SELGES PÅ MARKEDET
        lost_production = res_pv - pv2store    
            
        #EFFEKT SOM KAN KJØPES PÅ MARKEDET
        lost_load = demand[x][time] - inv2load  
        
        #DEKLARERE VERDIER FOR PLOTTING
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
        
      
        #Energiflytsverdiene legges til i "E" for deltaker x i tidssteg (før energideling)
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
        
        
       #Etablere bud-vektorene for deltaker x
        if ((LevelOfCharge < battery_capacity) & (LevelOfCharge > discharge_limit)) :      
        
                      bidding_battery[x] = 3 #KAN KJØPE OG SELGE, MELLOMTING!
        
        else:
            if LevelOfCharge == discharge_limit: 
          
          
                bidding_battery[x] = 1 #BUY
          
            else:
                if LevelOfCharge == battery_capacity:
                                  
                    bidding_battery[x] = 2 #SELL
             
        if (lost_production > 0): 
        
               bidding_pv[x] = 2 #sell
                   
        else: 
            if (lost_load > 0): 
                    
                   bidding_pv[x] = 1 #buy
  
            else:
                
                bidding_pv[x] = 0 #Ingen handel
                
                
        #GI ALLE ELEMENTENE I "E" SAMME INDEX SOM "PV" OG "DEMAND". NØDVENDIG FOR PLOTTING.
        if not return_series:
            E_pd = {}
            for k, v in E.items(): 
                E_pd[k] = pd.Series(v, index=pv.index)
            E = E_pd
            
         #-------------------------------------------------------------------------------------------
    


    '''
    NÅR KODEN HAR KOMMET HIT, ER DET I TIDSSTEGET ITERERT GJENNOM ALLE DELTAKERENE FØR HANDEL. ALLE DELTAKERENE 
    HAR FORSYNT SEG SELV SÅ LANGT DE REKKER SAMT ETABLERT KJØPE/SELGE BUD.
    '''
    
    #-------------------------------------------------------------------------------------------
    #DEKLARERE VARIABLER,VEKTORER OG INDEX-VEKTORER 
    count_sellers_pv = 0
    count_buyers_pv = 0
    count_sellers_battery = 0
    count_buyers_battery = 0
    count_battery_buy_flex = 0
    count_battery_sell_flex = 0
    count_flex_battery = 0
    
    energy_profit_pv = np.zeros(deltakere_n)
    energy_demand_pv = np.zeros(deltakere_n)
    
    index_seller_pv = []
    index_buyer_pv = []
    index_seller_battery = []
    index_buyer_battery = [] #default like mange som antall deltakere
    index_flex_buy_battery = []
    index_flex_sell_battery = []
    index_flex_battery = []
    
  
    
    #-------------------------------------------------------------------------------------------
    #Registrere hvlike bud deltager "j" legger ut i markedet
    for j in range(len(param)):  
        
        
        #ENERGIFLYTVARIABLER FOR DELTAKEREN SOM ER GJELDENE FOR ITERASJONSSTEGET
        lost_production = E[j]['lost_production'] #BORTKASTET SOLENERGI
        res_load = E[j]['lost_load'] #LAST SOM IKKE BLIR DEKKET
        LevelOfCharge = E[j]['LevelOfCharge'] #BATTERISTATUS ETTER Å HA EVENTUELT LADET SEG SELV
        discharge_limit = param[j]['BatteryDischargeLimit'] #MINUM BATTERNIVÅ
        battery_capacity = param[j]['BatteryCapacity'] #MAX OPP/UTLADNINGSEFFEKT AV BATTERI
        
    
        if bidding_pv[j] == 2: #PV-bud, salg
        
            #TELLE ANTALL "SELGERE"
            count_sellers_pv += 1
            
            #REGISTRERE HVOR MYE (kW) DELTAKEREN SELGER 
            energy_profit_pv[j] = lost_production
                     
            #REGISTRERE SELGERENS INDEX
            index_seller_pv.append(j)
                
            
        else:
            if (bidding_pv[j] == 1): #PV-bud, kjøpe
            
                
                count_buyers_pv += 1
                energy_demand_pv[j] = res_load
                
                
                index_buyer_pv.append(j)
                
               
        if bidding_battery[j] == 2: #Fult batteri, selge
         
             count_sellers_battery += 1
             index_seller_battery.append(j)
    
             
        else:
             if (bidding_battery[j] == 1): #Tomt batteri, kjøpe
             
                 count_buyers_battery += 1 
                 index_buyer_battery.append(j)
                 
                 
            
             else:
                if (bidding_battery[j] == 3): #Flex-batteri
                    
             
                    count_flex_battery += 1 
                    index_flex_battery.append(j)
          
                         
    #TOTAL MENGDE EFFEKT TIL SALGS OG KJØP I TIDSSTEGET
    sum_energy_profit_pv = sum(energy_profit_pv)
    sum_energy_demand_pv = sum(energy_demand_pv)
    
    #-------------------------------------------------------------------------------------------   
         
   
    '''
    SIDEN ANLEGGET INITIELT FORSYNER SEG SELV, GÅR OVERSKUDDS-PV I FØRSTE OMGANG TIL Å LADE OPP EGET BATTERIET. I SITUASJONENE DER DET ER 
    OVERSKUDSS-PV IGJEN ETTER AT DELTAKEREN HAR FORSYNT SEG SELV, MÅ ENTEN BATTERIET VÆRE FULT ELLER AT DET ER NOE IGJEN ETTER AT 
    BATTERIET ER LADET OPP MED MAKSIMAL LADEEFFEKT.
    '''
    
    
    #KODELINJE SOM SKILLER FLEXBATTERIENE BASERT PÅ FLEXLIMIT OG BATTERISTATUS. NOEN FLEXBATTERI STILLER SEG
    #I POSISJON TIL KJØP OG NOEN STILLER SEG I POSISJON TIL SALG.
    
    for j in index_flex_battery:  
    
        if (E[j]['LevelOfCharge'] > (0.5*battery_capacity + flex_limit*battery_capacity)):
        
            index_flex_sell_battery.append(j)
            
            
        elif (E[j]['LevelOfCharge'] < (0.5*battery_capacity - flex_limit*battery_capacity)):
            
            index_flex_buy_battery.append(j)
           
            
    #Telle flex (selge) og flex (kjøpe)
    count_battery_sell_flex = len(index_flex_sell_battery)
    count_battery_buy_flex = len(index_flex_buy_battery)

    #-------------------------------------------------------------------------------------------       
    #HANDELEN MELLOM STARTER. IF-SETNINGENE LEGGES FREM I PRIORITERINGS-REKKEFØLGEN FOR KJØP OG SALG LAGT FREM I
    #MASTEROPPGAVEN
    
   
    #Dersom et PV-anlegg har lagt ut et kjøpe-bud, vil det bety at batteriet i egen installasjon har ladet seg ut så langt det
    #rekker før handelen starter (store2inv). Kodelinjen nedenfor fjerner et eventuelt flex-batteri som selger dersom batteriet
    #allerede har forsyn egen installasjon.
    
    #Fjerne like element.
    #EGENTLIG ER BATTERY_SELL OG BATTERY_BUY UNØDVENDIG I KODEN. DETTE FORDI FLEX_BUY OG FLEX_SELL DEKKER DETTE
    common_elements = set(index_buyer_pv) & set(index_flex_sell_battery)
    
    for element in common_elements:
        index_flex_sell_battery.remove(element)
                                  

    common_elements = set(index_buyer_pv) & set(index_seller_battery)
    
    for element in common_elements:
        index_seller_battery.remove(element)
                                  
    
    #Skirve ut verdier i kontrollvinduet for ønsket tidssteg.
    if time == time_analysis:
        
            print()
            print('ENERGIFLYTSVERDIER (FØR DELING) I TIDSSTEG {:.5g}'.format(time))
            print('Date and time: {:.3g}.{:.3g} {:.3g}:{:.3g}'.format(day,month,hour,minute))
            print('---------------------------------------------------------------------')
            
            for i in range(len(param)):
            
                
                print('Ikke dekt last for hytte {:.3g}: {:.3g} kW'.format(i,E[i]['lost_load']))
                
            
            for i in range(len(param)):
                
                print('Produksjonsoverskudd for hytte {:.3g}: {:.3g} kW'.format(i, E[i]['lost_production']))
                

            for i in range(len(param)):
                
                print('Batteristatus for hytte {:.3g}: {:.3g} kWh'.format(i, E[i]['LevelOfCharge']))
                

            print()
            print('ENERGIHANDEL I TIDSSTEG {:.5g}'.format(time))
            print('Date and time: {:.3g}.{:.3g} {:.3g}:{:.3g}'.format(day,month,hour,minute))
            print('---------------------------------------------------------------------')
            print('PV-bud (selge):', index_seller_pv)
            print('PV-bud (kjøpe): ', index_buyer_pv)
            print()
            print('Batteri-bud (selge):', index_seller_battery)
            print('Batteri-bud (kjøpe): ', index_buyer_battery)
            print()
            print('Flex-bud (selge): ', index_flex_sell_battery)
            print('Flex-bud (kjøpe):', index_flex_buy_battery)
            print()
            print('Totalt overskudd av PV i markedet: {:.3g} kW'.format(sum_energy_profit_pv))
            print('Samlet estimert forbruk som ikke blir dekt: {:.3g} kW'.format(sum_energy_demand_pv))
            print('---------------------------------------------------------------------')
            print()
    
    
    
    #NEDENFOR STARTER HANDELEN MELLOM DELTAKERENE. KODEN BEVEGER SEG NEDOVER ETTER HVILKE BUD SOM HAR HØYESTE PRIORITET
    #----------------------------------------------------------------------------------------
    
    #Variabelen som aktiverer energideling
    if energy_model_activate == 1:
    
        #DERSOM DET FINNES KJØPERE OG SELGERE AV MOMENTAN PV
        if (len(index_buyer_pv) != 0) & (len(index_seller_pv) != 0):
            
            #Oppdaterer tellevariabelen
            dict_count['pv2pv'] += 1
            
            #TRADE_PV2PV PÅSER RETTFERDIG HANDEL MELLOM PV-ANLEGG (SE MASTEROPPGAVE)  
            #SELLER_TRANSFER OG BUYER_TRANSFER ER LISTER SOM INNEHOLDER ANDELEN ENERGI SOM OVERFØRES FOR HVER DELTAKER
            seller_transfer, buyer_transfer, rest_profit, rest_demand = trade_pv2pv.trade_pv2pv(sum_energy_profit_pv, sum_energy_demand_pv, index_buyer_pv, index_seller_pv, count_buyers_pv, count_sellers_pv, len(param), E)
            
            #Spesifisering av hvilken handel som foregår, hvilke salgsandeler som er i spill og totalt underskudd/overskudd av momentan energi i tidssteget
            if (time == time_analysis):         
        
                print('Type handel: pv2pv')
                print('Salgsandeler [kW]: ', seller_transfer)
                print('Kjøpsandeler [kW]: ', buyer_transfer)
                print('Totalt overskudd av PV i markedet: {:.3g} kW'.format(sum_energy_profit_pv))
                print('Samlet estimert forbruk som ikke blir dekt: {:.3g} kW'.format(sum_energy_demand_pv))
                print('---------------------------------------------------------------------')
                print()
            
            #FØRSTE PRIORITERING. MOMENTAN UTVEKLSING MELLOM PV-ANLEGG MED OVERSKUDD OG UNDERSKUDD
            for j in index_seller_pv: #SELGER MED INDEX J
    
              if (time == time_analysis):       
            
                print('Produksjonsoverskudd for hytte {:.3g} (FØR HANDEL): {:.3g} kW'. format(j, E[j]['lost_production']))
              
              E[j]['lost_production'] -= seller_transfer[j]
              
              '''
              if E[j]['lost_production'] < 0.001:
                    
                    E[j]['lost_production'] = 0
              '''      
              
              if (time == time_analysis): 
               
                  print('Produksjonsoverskudd for hytte {:.3g} (ETTER HANDEL): {:.3g} kW'. format(j, E[j]['lost_production']))  
                  
                
              E[j]['pv_sell_pv'] += seller_transfer[j] #TIL PLOTTING
              
              
                
            for i in index_buyer_pv: #KJØPER MED INDEX I
                    
                    if (time == time_analysis):       
                  
                      print('Estimert forbruk som ikke blir dekt for hytte {:.3g} (FØR HANDEL): {:.3g} kW'. format(i, E[i]['lost_load']))
                      
                    
                    E[i]['lost_load'] -= buyer_transfer[i]
                    E[i]['pv_buy_pv'] += buyer_transfer[i] #TIL PLOTTING
            
                    '''      
                    if E[i]['lost_load'] < 0.001:
                        
                        E[i]['lost_load'] = 0
                    '''
                        
                    if (time == time_analysis):       
                      
                      print('Estimert forbruk som ikke blir dekt for hytte {:.3g} (ETTER HANDEL): {:.3g} kW'. format(i, E[i]['lost_load']))   
        
                    
            if time == time_analysis:
                    
               print('---------------------------------------------------------------------')     
               
            sum_energy_demand_pv = rest_demand #DET SOM I TIDSSTEGET ER IGJEN AV "FORBURK SOM IKKE BLIR DEKT" ETTER HANDELEN
            sum_energy_profit_pv = rest_profit #DET SOM I TIDSSTEGET ER IGJEN AV OVERSKUDDSEFFEKT ETTER HANDELEN
            
            #Oppdatere index-vektorene 
            x = []
    
            for j in index_seller_pv:
                 
                 if E[j]['lost_production'] != 0:
                     
                     x.append(j)
                     
            index_seller_pv = x
             
            x = []
             
            for i in index_buyer_pv:
                 
                 
                 if E[i]['lost_load'] != 0:
                     
                     x.append(i)
                     
            index_buyer_pv = x       
                  
            #Bud i marekdet etter handelen         
            if time == time_analysis:
                
                   print()
                   print('PV-bud (selge):', index_seller_pv)
                   print('PV-bud (kjøpe): ', index_buyer_pv)
                   print()
                   print('Batteri-bud (selge):', index_seller_battery)
                   print('Batteri-bud (kjøpe): ', index_buyer_battery)
                   print()
                   print('Flex-bud (selge): ', index_flex_sell_battery)
                   print('Flex-bud (kjøpe):', index_flex_buy_battery)
                   print()
                   print('Totalt overskudd av PV i markedet: {:.3g} kW'.format(sum_energy_profit_pv))
                   print('Samlet estimert forbruk som ikke blir dekt: {:.3g} kW'.format(sum_energy_demand_pv))
                   print('---------------------------------------------------------------------')
                   print()
           
           
            
        #Hvis batteriutveksling er aktivert
        if battery_share_activate == 1:   
        
            if (len(index_seller_battery) != 0) & (len(index_buyer_pv) != 0):   
                
                dict_count['bat2pv'] += 1
                seller_trade, buyer_trade, rest_profit, rest_demand  = trade_batt2pv.trade_batt2pv(sum_energy_profit_pv, sum_energy_demand_pv, index_buyer_pv, index_seller_battery, count_buyers_pv, count_sellers_battery, len(param), E, param)
                
                
                if (time == time_analysis):         
            
                    print('Type handel: bat2pv')
                    print('Salgsandeler [kWh]: ', seller_trade)
                    print('Kjøpsandeler  [kW]: ', buyer_trade)
                    print('Totalt overskudd av PV i markedet: {:.3g} kW'.format(sum_energy_profit_pv))
                    print('Samlet estimert forbruk som ikke blir dekt: {:.3g} kW'.format(sum_energy_demand_pv))
                    print('---------------------------------------------------------------------')
                    print()
                
                #ANDRE PRIORITET. FULLE BATTERI SELGER TIL MOMENTAN PV
                for j in index_seller_battery:
                         
                  if (time == time_analysis):       
                
                    print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g} kW'. format(j, E[j]['LevelOfCharge']))
                    
                  E[j]['LevelOfCharge'] -= seller_trade[j] #ENERGY
                    
                  
                  if (time == time_analysis):       
                
                    print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g} kW'. format(j, E[j]['LevelOfCharge']))
                    
                  E[j]['battery_sell_pv'] += seller_trade[j] 
                    
                    
                for i in index_buyer_pv:
                    
                        if (time == time_analysis):       
                      
                          print('Estimert forbruk som ikke blir dekt for hytte {:.3g} (FØR HANDEL): {:.3g} kW'. format(i, E[i]['lost_load']))    
                    
                        E[i]['lost_load'] -= buyer_trade[i]
                        
                        '''
                        if E[i]['lost_load'] < 0.001:
                            
                            E[i]['lost_load'] = 0
                        '''
                        
                        if (time == time_analysis):       
                      
                          print('Estimert forbruk som ikke blir dekt for hytte {:.3g} (ETTER HANDEL): {:.3g} kW'. format(i, E[i]['lost_load']))
                        
                        E[i]['pv_buy_battery'] += buyer_trade[i] #POWER      
                        
                    
                        
                if time == time_analysis:
                        
                   print('---------------------------------------------------------------------')         
                        
                sum_energy_demand_pv = rest_demand
                sum_energy_profit_pv = rest_profit  
                        
                x = []
                
                for j in index_seller_battery:
                    
                    
                    if E[j]['LevelOfCharge'] == param[j]['BatteryCapacity']:
                        
                        x.append(j)
                    
                    else:
                        
                        index_flex_sell_battery.append(j)
                        
                index_seller_battery = x
                
                x = []
                
                for i in index_buyer_pv:
                    
                    
                    if E[i]['lost_load'] != 0:
                        
                        x.append(i)
                        
                index_buyer_pv = x  
                
              
                if time == time_analysis:
                    
                        print()
                        print('PV-bud (selge):', index_seller_pv)
                        print('PV-bud (kjøpe): ', index_buyer_pv)
                        print()
                        print('Batteri-bud (selge):', index_seller_battery)
                        print('Batteri-bud (kjøpe): ', index_buyer_battery)
                        print()
                        print('Flex-bud (selge): ', index_flex_sell_battery)
                        print('Flex-bud (kjøpe):', index_flex_buy_battery)
                        print()
                        print('Totalt overskudd av PV i markedet: {:.3g} kW'.format(sum_energy_profit_pv))
                        print('Samlet estimert forbruk som ikke blir dekt: {:.3g} kW'.format(sum_energy_demand_pv))
                        print('---------------------------------------------------------------------')
                        print()
                
            
        #Hvis flex- og batteri-utveksling er aktivert          
        if (flex_activate == 1) & (battery_share_activate == 1):  
            
            
            if (len(index_flex_sell_battery) != 0) & (len(index_buyer_pv) != 0):  
            
                dict_count['flex2pv'] += 1
                seller_trade, buyer_trade, rest_profit, rest_demand = trade_flex2pv.trade_flex2pv(time, sum_energy_profit_pv, sum_energy_demand_pv, index_buyer_pv, index_flex_sell_battery, count_buyers_pv, count_battery_sell_flex, len(param), E, param)
                
                
                if (time == time_analysis):         
            
                    print('Type handel: flex2pv')
                    print('Salgsandeler [kWh] :', seller_trade)
                    print('Kjøpsandeler  [kW] :', buyer_trade)
                    print('Totalt overskudd av PV i markedet: {:.3g} kW'.format(sum_energy_profit_pv))
                    print('Samlet estimert forbruk som ikke blir dekt: {:.3g} kW'.format(sum_energy_demand_pv))
                    print('---------------------------------------------------------------------')
                    print()
                
                #TREDJE PRIORITET. FLEX-BATTERI SELGER TIL MOMENTAN PV
                for j in index_flex_sell_battery:
                    
                            if (time == time_analysis):       
                          
                              print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.5g} kW'. format(j, E[j]['LevelOfCharge']))
                    
                            E[j]['LevelOfCharge'] -= seller_trade[j]
                            
                            if (time == time_analysis):       
                          
                              print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.5g} kW'. format(j, E[j]['LevelOfCharge']))
                            
                            E[j]['battery_sell_pv'] += seller_trade[j]   
                            
                    
                for i in index_buyer_pv:
                                
                            if (time == time_analysis):       
                          
                              print('Estimert forbruk som ikke blir dekt for hytte {:.3g} (FØR HANDEL): {:.3g} kW'. format(i, E[i]['lost_load']))                       
                            
                            E[i]['lost_load'] -= buyer_trade[i]
                            
                            '''
                            if E[i]['lost_load'] < 0.001:
                                
                                E[i]['lost_load'] = 0
                            '''
                            
                            if (time == time_analysis):       
                          
                              print('Estimert forbruk som ikke blir dekt for hytte {:.3g} (ETTER HANDEL): {:.3g} kW'. format(i, E[i]['lost_load']))    
                              
                            E[i]['pv_buy_battery'] += buyer_trade[i]     
                            
                          
                            
                if time == time_analysis:
                        
                   print('---------------------------------------------------------------------')             
                                
                sum_energy_demand_pv = rest_demand
                sum_energy_profit_pv = rest_profit  
                
                x = []
                
                for j in index_flex_sell_battery:
                    
                    
                    if E[j]['LevelOfCharge'] > 0.5*param[i]['BatteryCapacity'] + flex_limit*param[j]['BatteryCapacity']:
                        
                        x.append(j)
                        
                    elif E[j]['LevelOfCharge'] < 0.5*param[i]['BatteryCapacity'] - flex_limit*param[j]['BatteryCapacity']:
                        
                        index_flex_buy_battery.append(j)    
                        
                        
                index_flex_sell_battery = x
                
                x = []
                
                for i in index_buyer_pv:
                    
                    
                    if E[i]['lost_load'] != 0:
                        
                        x.append(i)
                        
                index_buyer_pv = x
                
                if time == time_analysis:
                    
                        print()
                        print('PV-bud (selge):', index_seller_pv)
                        print('PV-bud (kjøpe): ', index_buyer_pv)
                        print()
                        print('Batteri-bud (selge):', index_seller_battery)
                        print('Batteri-bud (kjøpe): ', index_buyer_battery)
                        print()
                        print('Flex-bud (selge): ', index_flex_sell_battery)
                        print('Flex-bud (kjøpe):', index_flex_buy_battery)
                        print()
                        print('Totalt overskudd av PV i markedet: {:.3g} kW'.format(sum_energy_profit_pv))
                        print('Samlet estimert forbruk som ikke blir dekt: {:.3g} kW'.format(sum_energy_demand_pv))
                        print('---------------------------------------------------------------------')
                        print()
                
          
                        
        if battery_share_activate == 1:
                                      
            if (len(index_seller_pv) != 0) & (len(index_buyer_battery) != 0):
                
                dict_count['pv2bat'] += 1
                #ANLEGG MED OVERSKUDD SOM FØRSTEPRIORITET?
                seller_trade, buyer_trade, rest_profit, rest_demand = trade_pv2batt.trade_pv2bat(sum_energy_profit_pv, sum_energy_demand_pv, index_seller_pv, index_buyer_battery, count_sellers_pv, count_buyers_battery, len(param), E, param, time)        
    
                if (time == time_analysis):         
                    
                    
                    print('Type handel: pv2bat')
                    print('Salgsandeler  [kW] :', seller_trade)
                    print('Kjøpsandeler [kWh] :', buyer_trade)
                    print('Totalt overskudd av PV i markedet: {:.3g} kW'.format(sum_energy_profit_pv))
                    print('Samlet estimert forbruk som ikke blir dekt: {:.3g} kW'.format(sum_energy_demand_pv))
                    print('---------------------------------------------------------------------')
                    print()
                    
                #PV-anlegg selger til tomme batteri    
                for j in index_seller_pv:
                    
                    
                    if (time == time_analysis):       
                    
                        print('Produksjonsoverskudd for hytte {:.3g} (FØR HANDEL): {:.3g} kW'. format(j, E[j]['lost_production']))
                    
                    
                    E[j]['lost_production'] -= seller_trade[j]
                    
                    '''
                    if  E[j]['lost_production'] < 0.001:
                        
                        E[j]['lost_production'] = 0
                    
                    '''
    
                    
                    if (time == time_analysis):       
                
                        print('Produksjonsoverskudd for hytte {:.3g} (ETTER HANDEL): {:.3g} kW'. format(j, E[j]['lost_production']))
                    
                    E[j]['pv_sell_battery'] += seller_trade[j]
                
                    
                    
                for i in index_buyer_battery:
                        
                    
                        if (time == time_analysis):       
                      
                          print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g} kW'. format(i, E[i]['LevelOfCharge']))
                    
                        E[i]['LevelOfCharge'] += buyer_trade[i]
                        
                        
                        if (time == time_analysis):       
                      
                          print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g} kW'. format(i, E[i]['LevelOfCharge']))
                        
                        E[i]['battery_buy_pv'] += buyer_trade[i]
                          
                        
                if time == time_analysis:
                        
                   print('---------------------------------------------------------------------')       
                       
                sum_energy_demand_pv = rest_demand
                sum_energy_profit_pv = rest_profit
                
                
                x = []
                
                for j in index_seller_pv:
                    
                    
                    if E[j]['lost_production'] != 0:
                        
                        x.append(j)
                        
                index_seller_pv = x
                
                x = []
                
                for i in index_buyer_battery:
                    
                    
                    if E[i]['LevelOfCharge'] == param[i]['BatteryDischargeLimit']:
                        
                        x.append(i)
                        
                    else:
                        
                        index_flex_buy_battery.append(i)    
                        
                index_buyer_battery = x
                
                
                if time == time_analysis:
                    
                        print()
                        print('PV-bud (selge):', index_seller_pv)
                        print('PV-bud (kjøpe): ', index_buyer_pv)
                        print()
                        print('Batteri-bud (selge):', index_seller_battery)
                        print('Batteri-bud (kjøpe): ', index_buyer_battery)
                        print()
                        print('Flex-bud (selge): ', index_flex_sell_battery)
                        print('Flex-bud (kjøpe):', index_flex_buy_battery)
                        print()
                        print('Totalt overskudd av PV i markedet: {:.3g} kW'.format(sum_energy_profit_pv))
                        print('Samlet estimert forbruk som ikke blir dekt: {:.3g} kW'.format(sum_energy_demand_pv))
                        print('---------------------------------------------------------------------')
                        print()
                
                
            
        
        if (flex_activate == 1) & (battery_share_activate == 1):
            
            
            if (len(index_flex_buy_battery) != 0) & (len(index_seller_pv) != 0):
            
                dict_count['pv2flex'] += 1
                seller_trade, buyer_trade, rest_profit, rest_demand = trade_pv2batt.trade_pv2bat(sum_energy_profit_pv, sum_energy_demand_pv, index_seller_pv, index_flex_buy_battery, count_sellers_pv, count_battery_buy_flex, len(param), E, param, time)
        
        
                if (time == time_analysis):         
            
                    print('Type handel: pv2flex')
                    print('Salgsandeler  [kW] : ', seller_trade)
                    print('Kjøpsandeler [kWh] :', buyer_trade)
                    print('Totalt overskudd av PV i markedet: {:.3g} kW'.format(sum_energy_profit_pv))
                    print('Samlet estimert forbruk som ikke blir dekt: {:.3g} kW'.format(sum_energy_demand_pv))
                    print('---------------------------------------------------------------------')
                    print()
                    
                #PV-anlegg selger til flex-batteri     
                for j in index_seller_pv:
                    
                    if (time == time_analysis):       
                    
                        print('Produksjonsoverskudd for hytte {:.3g} (FØR HANDEL): {:.3g} kW'. format(j, E[j]['lost_production']))
                    
                    E[j]['lost_production'] -= seller_trade[j]
                    
                    '''
                    if E[j]['lost_production'] < 0.001:
                        
                        E[j]['lost_production'] = 0
                    '''
                    
                    if (time == time_analysis):       
                    
                        print('Produksjonsoverskudd for hytte {:.3g} (ETTER HANDEL): {:.3g} kW'. format(j, E[j]['lost_production']))
                    
                    E[j]['pv_sell_battery'] += seller_trade[j]
                
                    
                    
                for i in index_flex_buy_battery:
                        
                        if (time == time_analysis):       
                      
                          print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g} kW'. format(i, E[i]['LevelOfCharge']))
                        
                        E[i]['LevelOfCharge'] += buyer_trade[i]
                        
                        if (time == time_analysis):       
                      
                          print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g} kW'. format(i, E[i]['LevelOfCharge']))
                        
                        E[i]['battery_buy_pv'] += buyer_trade[i]
                             
                        
                if time == time_analysis:
                        
                   print('---------------------------------------------------------------------')      
        
                sum_energy_demand_pv = rest_demand
                sum_energy_profit_pv = rest_profit  
                
                x = []
                
                for j in index_seller_pv:
                    
                    
                    if E[j]['lost_production'] != 0:
                        
                        x.append(j)
                        
                index_seller_pv = x
                
                x = []
                
                for i in index_flex_buy_battery:
                    
                    
                    if E[i]['LevelOfCharge'] < 0.5*param[i]['BatteryCapacity'] - flex_limit*param[i]['BatteryCapacity']:
                        
                        x.append(i)
                        
                    elif E[j]['LevelOfCharge'] > 0.5*param[i]['BatteryCapacity'] + flex_limit*param[j]['BatteryCapacity']:
                        
                        index_flex_sell_battery.append(j)    
                        
                index_flex_buy_battery = x
                
                
                if time == time_analysis:
                    
                        print()
                        print('PV-bud (selge):', index_seller_pv)
                        print('PV-bud (kjøpe): ', index_buyer_pv)
                        print()
                        print('Batteri-bud (selge):', index_seller_battery)
                        print('Batteri-bud (kjøpe): ', index_buyer_battery)
                        print()
                        print('Flex-bud (selge): ', index_flex_sell_battery)
                        print('Flex-bud (kjøpe):', index_flex_buy_battery)
                        print()
                        print('Totalt overskudd av PV i markedet: {:.3g} kW'.format(sum_energy_profit_pv))
                        print('Samlet estimert forbruk som ikke blir dekt: {:.3g} kW'.format(sum_energy_demand_pv))
                        print('---------------------------------------------------------------------')
                        print()
                
           
            
        if battery_share_activate == 1:
                  
            if (len(index_seller_battery) != 0) & (len(index_buyer_battery) != 0):
                
                dict_count['bat2bat'] += 1
                seller_trade, buyer_trade, rest_profit, rest_demand  = trade_flex2flex.trade_batt2batt(flex_limit, sum_energy_profit_pv, sum_energy_demand_pv, index_buyer_battery, index_seller_battery, count_sellers_battery, count_buyers_battery, len(param), E, param, time)
               
                
                
                if (time == time_analysis):         
            
                    print('Type handel: bat2bat')
                    print('Salgsandeler [kWh] : ', seller_trade)
                    print('Kjøpsandeler [kWh] : ', buyer_trade)
                    print('Totalt overskudd av PV i markedet: {:.3g} kW'.format(sum_energy_profit_pv))
                    print('Samlet estimert forbruk som ikke blir dekt: {:.3g} kW'.format(sum_energy_demand_pv))
                    print('---------------------------------------------------------------------')
                    print()
                    
                #Fulle batteri selger til tomme batteri
                for j in index_seller_battery:
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g} kW'. format(j, E[j]['LevelOfCharge']))
                    
                    E[j]['LevelOfCharge'] -= seller_trade[j]
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g} kW'. format(j, E[j]['LevelOfCharge']))
                    
                    E[j]['battery_sell_battery'] += seller_trade[j]
                    
                    #FLEX BATTERI SOM KJØPER
                for i in index_buyer_battery:
                   
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g} kW'. format(i, E[i]['LevelOfCharge']))
                   
                    E[i]['LevelOfCharge'] += buyer_trade[i]
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g} kW'. format(i, E[i]['LevelOfCharge']))
                    
                    E[i]['battery_buy_battery'] += buyer_trade[i]       
                    
                    
                if time == time_analysis:
                        
                   print('---------------------------------------------------------------------')
                    
                sum_energy_demand_pv = rest_demand
                sum_energy_profit_pv = rest_profit   
                 
                x = []
                 
                for j in index_seller_battery:
                     
                     
                     if E[j]['LevelOfCharge'] == param[j]['BatteryDischargeLimit']:
                         
                         x.append(j)
                         
                     else:
                         
                         index_flex_buy_battery.append(j)    
                         
                index_seller_battery = x
                 
                x = []
                 
                for j in index_buyer_battery:
                     
                     
                     if E[j]['LevelOfCharge'] == param[j]['BatteryCapacity']:
                         
                         x.append(j)
                         
                     else:
                         
                         index_flex_sell_battery.append(j)    
                         
                index_buyer_battery = x
                
                
                if time == time_analysis:
                    
                        print()
                        print('PV-bud (selge):', index_seller_pv)
                        print('PV-bud (kjøpe): ', index_buyer_pv)
                        print()
                        print('Batteri-bud (selge):', index_seller_battery)
                        print('Batteri-bud (kjøpe): ', index_buyer_battery)
                        print()
                        print('Flex-bud (selge): ', index_flex_sell_battery)
                        print('Flex-bud (kjøpe):', index_flex_buy_battery)
                        print()
                        print('Totalt overskudd av PV i markedet: {:.3g} kW'.format(sum_energy_profit_pv))
                        print('Samlet estimert forbruk som ikke blir dekt: {:.3g} kW'.format(sum_energy_demand_pv))
                        print('---------------------------------------------------------------------')
                        print()
                
            
        
        if (flex_activate == 1) & (battery_share_activate == 1):    
            
            
            if (len(index_flex_sell_battery) != 0) & (len(index_buyer_battery) != 0):
                   
                dict_count['flex2bat'] += 1
                #FLEX BATTERI SOM SELGER           
                seller_trade, buyer_trade, rest_profit, rest_demand = trade_flex2flex.trade_batt2batt(flex_limit, sum_energy_profit_pv, sum_energy_demand_pv, index_buyer_battery, index_flex_sell_battery, count_battery_sell_flex, count_buyers_battery, len(param), E, param, time)
               
                if (time == time_analysis):         
            
                    print('Type handel: flex2bat')
                    print('Salgsandeler [kWh] :', seller_trade)
                    print('Kjøpsandeler [kWh] :', buyer_trade)
                    print('Totalt overskudd av PV i markedet: {:.3g} kW'.format(sum_energy_profit_pv))
                    print('Samlet estimert forbruk som ikke blir dekt: {:.3g} kW'.format(sum_energy_demand_pv))
                    print('---------------------------------------------------------------------')
                    print()
                
                #Flex-batteri selger til tomme batteri
                for j in index_flex_sell_battery:
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g} kW'. format(j, E[j]['LevelOfCharge']))
                    
                    E[j]['LevelOfCharge'] -= seller_trade[j]
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g} kW'. format(j, E[j]['LevelOfCharge']))
                    
                    E[j]['battery_sell_battery'] += seller_trade[j]
                    
                    #FLEX BATTERI SOM KJØPER
                for i in index_buyer_battery:
                        
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g} kW'. format(i, E[i]['LevelOfCharge']))
                        
                    E[i]['LevelOfCharge'] += buyer_trade[i]
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g} kW'. format(i, E[i]['LevelOfCharge']))
                    
                    E[i]['battery_buy_battery'] += buyer_trade[i]       
                
                
                if time == time_analysis:
                        
                   print('---------------------------------------------------------------------')    
                    
                sum_energy_demand_pv = rest_demand
                sum_energy_profit_pv = rest_profit  
                 
                x = []
                 
                for j in index_flex_sell_battery:
                     
                     
                     if E[j]['LevelOfCharge'] > 0.5*param[i]['BatteryCapacity'] + flex_limit*param[j]['BatteryCapacity']:
                         
                         x.append(j)
                         
                     elif E[j]['LevelOfCharge'] < 0.5*param[i]['BatteryCapacity'] - flex_limit*param[j]['BatteryCapacity']:
                         
                         index_flex_buy_battery.append(j)    
                         
                index_flex_sell_battery = x
                 
                x = []
                 
                for j in index_buyer_battery:
                     
                     
                     if E[j]['LevelOfCharge'] == param[j]['BatteryDischargeLimit']:
                         
                         x.append(j)
                         
                     else:
                         
                         index_flex_buy_battery.append(j)    
                         
                index_buyer_battery = x
                
                if time == time_analysis:
                    
                        print()
                        print('PV-bud (selge):', index_seller_pv)
                        print('PV-bud (kjøpe): ', index_buyer_pv)
                        print()
                        print('Batteri-bud (selge):', index_seller_battery)
                        print('Batteri-bud (kjøpe): ', index_buyer_battery)
                        print()
                        print('Flex-bud (selge): ', index_flex_sell_battery)
                        print('Flex-bud (kjøpe):', index_flex_buy_battery)
                        print()
                        print('Totalt overskudd av PV i markedet: {:.3g} kW'.format(sum_energy_profit_pv))
                        print('Samlet estimert forbruk som ikke blir dekt: {:.3g} kW'.format(sum_energy_demand_pv))
                        print('---------------------------------------------------------------------')
                        print()
                
        
        
                
            if (len(index_flex_buy_battery) != 0) & (len(index_seller_battery) != 0):
                
                dict_count['bat2flex'] += 1
                seller_trade, buyer_trade, rest_profit, rest_demand = trade_flex2flex.trade_batt2batt(flex_limit, sum_energy_profit_pv, sum_energy_demand_pv, index_flex_buy_battery, index_seller_battery, count_sellers_battery, count_battery_buy_flex, len(param), E, param, time)
               
                if (time == time_analysis):         
            
                    print('Type handel: bat2flex')
                    print('Salgsandeler [kWh] :', seller_trade)
                    print('Kjøpsandeler [kWh] :', buyer_trade)
                    print('Totalt overskudd av PV i markedet: {:.3g} kW'.format(sum_energy_profit_pv))
                    print('Samlet estimert forbruk som ikke blir dekt: {:.3g} kW'.format(sum_energy_demand_pv))
                    print('---------------------------------------------------------------------')
                    print()
                
                #Fulle batteri selger til flex-batteri
                for j in index_seller_battery:
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g} kW'. format(j, E[j]['LevelOfCharge']))
                    
                    E[j]['LevelOfCharge'] -= seller_trade[j]
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g} kW'. format(j, E[j]['LevelOfCharge']))
                    
                    E[j]['battery_sell_battery'] += seller_trade[j]
                    
                    #FLEX BATTERI SOM KJØPER
                for i in index_flex_buy_battery:
                        
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g} kW'. format(i, E[i]['LevelOfCharge']))
        
                    E[i]['LevelOfCharge'] += buyer_trade[i]
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g} kW'. format(i, E[i]['LevelOfCharge']))
                    
                    E[i]['battery_buy_battery'] += buyer_trade[i]       
                 
                    
                if time == time_analysis:
                        
                   print('---------------------------------------------------------------------')
                    
                sum_energy_demand_pv = rest_demand
                sum_energy_profit_pv = rest_profit  
                 
                x = []
                 
                for j in index_seller_battery:
                     
                     
                     if E[j]['LevelOfCharge'] == param[j]['BatteryCapacity']:
                         
                         x.append(j)
                         
                     else:
                         
                         index_flex_sell_battery.append(j)    
                         
                index_seller_battery = x
                 
                x = []
                 
                for j in index_flex_buy_battery:
                     
                     
                     if E[j]['LevelOfCharge'] < flex_limit*param[j]['BatteryCapacity']:
                         
                         x.append(j)
                      
                     else:
                         
                         index_flex_sell_battery.append(j)    
                         
                index_flex_buy_battery = x
                
                
                if time == time_analysis:
                    
                        print()
                        print('PV-bud (selge):', index_seller_pv)
                        print('PV-bud (kjøpe): ', index_buyer_pv)
                        print()
                        print('Batteri-bud (selge):', index_seller_battery)
                        print('Batteri-bud (kjøpe): ', index_buyer_battery)
                        print()
                        print('Flex-bud (selge): ', index_flex_sell_battery)
                        print('Flex-bud (kjøpe):', index_flex_buy_battery)
                        print()
                        print('Totalt overskudd av PV i markedet: {:.3g} kW'.format(sum_energy_profit_pv))
                        print('Samlet estimert forbruk som ikke blir dekt: {:.3g} kW'.format(sum_energy_demand_pv))
                        print('---------------------------------------------------------------------')
                        print()
                
        
                
            if (len(index_flex_buy_battery) != 0) & (len(index_flex_sell_battery) != 0):    
            
                dict_count['flex2flex'] += 1
                seller_trade, buyer_trade, rest_profit, rest_demand = trade_flex2flex.trade_batt2batt(flex_limit, sum_energy_profit_pv, sum_energy_demand_pv, index_flex_buy_battery, index_flex_sell_battery, count_battery_sell_flex, count_battery_buy_flex, len(param), E, param, time)
               
                if (time == time_analysis):         
            
                    print('Type handel: flex2flex')
                    print('Salgsandeler [kWh] :', seller_trade)
                    print('Kjøpsandeler [kWh] :', buyer_trade)
                    print('Totalt overskudd av PV i markedet: {:.3g} kW'.format(sum_energy_profit_pv))
                    print('Samlet estimert forbruk som ikke blir dekt: {:.3g} kW'.format(sum_energy_demand_pv))
                    print('---------------------------------------------------------------------')
                    print()
               
                #Flex-batteri selger til flex-batteri
                for j in index_flex_sell_battery:
                        
                        if (time == time_analysis):       
                      
                          print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g} kW'. format(j, E[j]['LevelOfCharge']))
                    
                        E[j]['LevelOfCharge'] -= seller_trade[j]
                        
                        if (time == time_analysis):       
                      
                          print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g} kW'. format(j, E[j]['LevelOfCharge']))
                        
                        E[j]['battery_sell_battery'] += seller_trade[j]
                        
    
                for i in index_flex_buy_battery:
                       
                        if (time == time_analysis):       
                      
                          print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g} kW'. format(i, E[i]['LevelOfCharge']))
                              
                        E[i]['LevelOfCharge'] += buyer_trade[i]
                        
                        if (time == time_analysis):       
                      
                          print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g} kW'. format(i, E[i]['LevelOfCharge']))
                        
                        E[i]['battery_buy_battery'] += buyer_trade[i]       
                                                          
                
                if time == time_analysis:
                        
                   print('---------------------------------------------------------------------')        
                   
                sum_energy_demand_pv = rest_demand
                sum_energy_profit_pv = rest_profit   
                
                x = []
                
                for j in index_flex_sell_battery:
                    
                    
                    if E[j]['LevelOfCharge'] > 0.5*param[i]['BatteryCapacity'] + flex_limit*param[j]['BatteryCapacity']:
                        
                        x.append(j)
                        
                    elif E[j]['LevelOfCharge'] < 0.5*param[i]['BatteryCapacity'] - flex_limit*param[j]['BatteryCapacity']:
                        
                        index_flex_buy_battery.append(j)    
                        
                index_flex_sell_battery = x
                
                x = []
                
                for j in index_flex_buy_battery:
                    
                    
                    if E[j]['LevelOfCharge'] < 0.5*param[i]['BatteryCapacity'] - flex_limit*param[j]['BatteryCapacity']:
                        
                        x.append(j)
                        
                    elif E[j]['LevelOfCharge'] > 0.5*param[i]['BatteryCapacity'] + flex_limit*param[j]['BatteryCapacity']:
                        
                        index_flex_sell_battery.append(j)
                        
                index_flex_buy_battery = x
                
                if time == time_analysis:
                    
                        print()
                        print('PV-bud (selge):', index_seller_pv)
                        print('PV-bud (kjøpe): ', index_buyer_pv)
                        print()
                        print('Batteri-bud (selge):', index_seller_battery)
                        print('Batteri-bud (kjøpe): ', index_buyer_battery)
                        print()
                        print('Flex-bud (selge): ', index_flex_sell_battery)
                        print('Flex-bud (kjøpe):', index_flex_buy_battery)
                        print()
                        print('Totalt overskudd av PV i markedet: {:.3g} kW'.format(sum_energy_profit_pv))
                        print('Samlet estimert forbruk som ikke blir dekt: {:.3g} kW'.format(sum_energy_demand_pv))
                        print('---------------------------------------------------------------------')
                        print()
                
             
                
        #Energiflytsverdier i tidssteget etter energideling   
        if time == time_analysis:
            
                print()
                print('ENERGIFLYTSVERDIER (ETTER DELING) I TIDSSTEG {:.5g}'.format(time))
                print('Date and time: {:.3g}.{:.3g} {:.3g}:{:.3g}'.format(day,month,hour,minute))
                print('---------------------------------------------------------------------')
                
                for i in range(len(param)):
                
                    
                    print('Ikke dekt last for hytte {:.3g}: {:.3g} kW'.format(i,E[i]['lost_load']))
                    
                
                for i in range(len(param)):
                    
                    print('Produksjonsoverskudd for hytte {:.3g}: {:.3g} kW'.format(i, E[i]['lost_production']))
                    
    
                for i in range(len(param)):
                    
                    print('Batteristatus for hytte {:.3g}: {:.3g} kWh'.format(i, E[i]['LevelOfCharge']))
        
                print()
                
                
        
    
    return(E, dict_count)
    





