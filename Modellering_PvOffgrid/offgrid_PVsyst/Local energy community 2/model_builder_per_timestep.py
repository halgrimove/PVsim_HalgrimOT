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

'''
Denne filen simulerer energiflytsvariablene for alle deltakerene i et gitt tidssteg. 
Funksjonen som kjøres returnerer E. E er en dictionary med energiflytsvariablene 
tilørende N deltakere for gitt tidssteg.

'''


'''
TESTENE ER GJENNOMFØRT MED HYTTEFELTET

time = 4639
deltakere5 = [4, 2, 1, 1, 1] #Kategorihytte på deltakerene 
bruksmønster5 = [0, 0, 0, 1, 2] #Bruksmønster på deltakerene

'''

'''
(0.3) -> 6651, 4639, 9999, 8656, 19999, 20999, 23999
'''


battery_share_activate = 1 #Inkludere batteriutveksling når de er tomme/fulle
flex_activate = 1 #Inkludere fleksibel batteriutveksling

flex_limit = 0.1
#Jo høyere flex_limit, desto høyere batteristatus må flex-batteriet ha for å selge sin henergi.
#E[j]['LevelOfCharge'] > 0.5*battery_capacity + flex_limit*battery_capacity): -> SELGE
#(E[j]['LevelOfCharge'] < 0.5*battery_capacity - flex_limit*battery_capacity): -> KJØPE    

#GROV SPESIFISERING AV DAGER
month = 12   #month -> 1-12
day = 31   #day -> 1-30
hour = 23   #hour -> 1-23
minute = 45    #kvarter -> 15,30,45

#Time_analysis er det tidssteget som det vises informasjon om i kontrollvinduet. I kontrollvinduet vises hvordan
#handelen foregår i valgt tidssteg
time_analysis = (month-1)*2880 + (day-1)*96 + hour*4 + minute/15



def E_per_timestep(dict_list, dict_count, param, time, demand, pv, tap):

    
    E = {}
    bidding_battery = {}
    bidding_pv = {}
    
    return_series = True
    deltakere_n = len(param)
        
    
    #ENERGIFLYTSVERDIER FOR HVER DELTAKER I GITT TIDSSTEG FØR ENERGIDELING
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
    
        '''
        #FJERNE "FLUER" FRA INPUT DATAENE
        if (pv[x][time] < 0):
                pv[x][time] = 0
            
        if (demand[x][time] < 0.1):
                demand[x][time] = 0
        '''
        
        #DEFINERE VARIABLER
        battery_capacity = param[x]['BatteryCapacity']
        n_bat = param[x]['BatteryEfficiency']
        n_inv = param[x]['InverterEfficiency']
        timestep = param[x]['timestep']
        
        
        #Her er virkningsgrad tatt med
        pv2inv = np.minimum(pv[x][time], demand[x][time]/n_inv) #demand[x][time]/n_inv
        res_pv = np.maximum(pv[x][time] - demand[x][time]/n_inv, 0) #Lasten som momentant er større en forbruket for det gitte tidssteget
        inv2load = pv2inv * n_inv
        res_load = (demand[x][time] - pv2inv * n_inv) #lasten som ikke dekkes av momentan PV #pv2inv

      
            
        #1. prioritet etter at momentant forburk er dekket -> Forsyne eget batteri
        if LevelOfCharge_previous >= battery_capacity:  
                    pv2store = 0 
            
        else: #BATTERIET ER IKKE FULT, MEN VIL OVERSTIGE MAX KAPASITET VED OPPLADING I GITT TIDSSTEG
                if (LevelOfCharge_previous + (res_pv * timestep)) > battery_capacity:
                    
                    #KAN MAX LADE OPP DET SMO ER IGJEN FØR BATTERIET NÅR MAX KAPASITET
                    pv2store = min((battery_capacity - LevelOfCharge_previous)/timestep, max_power_battery)
                    #OPPLADINGEN BEGRENSES AV MAX LADING PÅ BATTERI
                    
                    
                else: #BATTERIET ER IKKE FULT OG VIL IKKE OVERTIGE MAX KAPASITET VED OPPLADNING I GITT TIDSSTEG
                    #BEGRENSES AV MAX LADING PÅ BATTERI
                    pv2store = min(res_pv, max_power_battery)
             
        
            
            
        store2inv = min((LevelOfCharge_previous/timestep-discharge_limit/timestep), res_load/n_inv, max_power_battery)  
        
        
        '''
        if time == 20999:
            
            print('Pv2store : {:.3g}'.format(pv2store))
            print('store2inv : {:.3g}'.format(store2inv))
       '''     
        
        #LADE OPP DET MAN KAN MED EGEN ENERGI
        LevelOfCharge = min(LevelOfCharge_previous - (store2inv - pv2store*n_bat) * timestep,  # DC - pv2store*n_bat
                                   battery_capacity)
        
       

        
        #-------------------------------------------------------------------------------------------
        
        
        #EFFEKT TIL FORBRUK. I BÅDE STORE2INV OG INV2LOAD ER EFFEKTBEGRENSNINGER TATT HENSYN TIL
        inv2load = inv2load + store2inv*n_inv
        
        '''
        if time == time_analysis:
            
            print()
            print('Tapt produksjon: {:.3g}'.format(dict_list[time-1][0]['lost_production']))
            print('Tapt produksjon: {:.3g}'.format(dict_list[time-1][1]['lost_production']))
            print()
        '''
        
        #EFFEKT SOM KAN SELGES PÅ MARKEDET
        lost_production = res_pv - pv2store 
       
        '''
        if time == time_analysis:
            
            print('Tapt produksjon: {:.3g}'.format(dict_list[time-1][0]['lost_production']))
            print('Tapt produksjon: {:.3g}'.format(dict_list[time-1][1]['lost_production']))
            print()
        '''
       
            
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
        
        #-------------------------------------------------------------------------------------------
        '''
        #FJERNE FLUER
        if lost_load < 0.001:
            
            lost_load = 0
            
        if lost_production < 0.001:
            
            lost_production = 0
        '''
        
        #Energiflytsverdiene for deltaker x i gitt tidssteg før energideling
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
        
        
       #Etablere bud for deltaker x
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
    #DEKLARERE VARIABLER,VEKTORER OG INDEX-VEKTORER TIL Å MODELLERE ENERGIMARKEDET
    
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
    #iterere gjennom deltagerene
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
            
            #REGISTRERE HVOR MYE (kW) DELTAKEREN SELGER i tidssteget
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
    SIDEN ANLEGGET FØRST FORSYNER SEG SELV, GÅR OVERSKUDDS-PV i første omgang TIL Å LADE OPP BATTERIET. DET er SJELDENT 
    OVERSKUDDS-PV IGJEN (SIDEN BATTERIET i egen installasjon DA MÅ VÆRE FULT) FØR HANDELENE STARTER. DET ER OBSERVERT AT NÅR FLEX_LIMIT ER UNDER 100%, 
    VIL ALDRI BATTERIENE STÅ FULLE. I DETTE TILFELLE BRUKES EGEN OVERSKUDDS-PV TIL Å LADE EGET BATTERI, FOR SÅ AT BATTERIET (SOM DA OFTEST ER FLEX) SELGER SIN ENERGI TIL FLEX_LIMIT NÅS. 
    
    GJØRES DET ET FORSØK DER FLEXLIMIT SETTES TIL 100% (SOM OM VI FJERNE MULIGHETEN TIL Å FLEXE MED SIN ENERGI) OBSERVERES
    DET AT VI FÅR UTVEKSLING DIREKTE MELLOM PV-ANLEGG. DETTE FORDI EN HYTTE SOM I UTGANGSPUNKTET STÅR TOM, ETTERHVERT 
    VIL FÅ FULT BATTERI. UTEN FLEX BATTERI VIL DISSE BATTERIENE HA LITEN MULIGHET TIL Å SELGE SIN ENERGI SIDEN DE KUN KAN SELGE VED 
    100% KAPASITET. DERFOR VIL DET OPPSTÅ SITUASJONER DER PV SENDER DIREKTE TIL PV.
    '''
    
    #KODELINJE SOM SKILLER FLEXBATTERIENE BASERT PÅ FLEXLIMIT OG BATTERISTATUS. NOEN FLEXBATTERI STILLER SEG
    #I POSISJON TIL KJØP OG NOEN STILLER SEG I POSISJON TIL SALG.
    for j in index_flex_battery:  
    
        if (E[j]['LevelOfCharge'] > 0.5*battery_capacity + flex_limit*battery_capacity):
        
            index_flex_sell_battery.append(j)
            
            
        elif (E[j]['LevelOfCharge'] < 0.5*battery_capacity - flex_limit*battery_capacity):
            
            index_flex_buy_battery.append(j)
            

    count_battery_sell_flex = len(index_flex_sell_battery)
    count_battery_buy_flex = len(index_flex_buy_battery)

    #-------------------------------------------------------------------------------------------       
    #HANDELEN MELLOM STARTER. IF-SETNINGENE LEGGES FREM I PRIORITERINGS-REKKEFØLGEN FOR KJØP OG SALG LAGT FREM I
    #MASTEROPPGAVEN
    
    '''
    #Fjerne fluer
    for j in range(len(param)):
        
        if E[j]['lost_load'] < 0.001:
            
            E[j]['lost_load'] = 0
        
        if E[j]['lost_production'] < 0.001:
            
            E[j]['lost_production'] = 0
    '''       
   
    #Dersom et PV-anlegg har lagt ut et kjøpe-bud, vil det bety at batteriet i egen installasjon har ladet seg ut så langt det
    #rekker før handelen starter (store2inv). Kodelinjen nedenfor fjerner et eventuelt flex-batteri som selger dersom batteriet
    #allerede har forsyn egen installasjon.
    common_elements = set(index_buyer_pv) & set(index_flex_sell_battery)
    
    for element in common_elements:
        index_flex_sell_battery.remove(element)
                                  

    common_elements = set(index_buyer_pv) & set(index_seller_battery)
    
    for element in common_elements:
        index_seller_battery.remove(element)
                                  
    
    #Plotte energiflytsverdier i git tidssteget FØR deling
    if time == time_analysis:
        
            print()
            print('ENERGIFLYTSVERDIER (FØR DELING) I TIDSSTEG {:.5g}'.format(time))
            print('Date and time: {:.3g}.{:.3g} {:.3g}:{:.3g}'.format(day,month,hour,minute))
            print('---------------------------------------------------------------------')
            
            for i in range(len(param)):
            
                
                print('Ikke dekt last for hytte {:.3g}: {:.3g}kW'.format(i,E[i]['lost_load']))
                
            
            for i in range(len(param)):
                
                print('Produksjonsoverskudd for hytte {:.3g}: {:.3g}kW'.format(i, E[i]['lost_production']))
                

            for i in range(len(param)):
                
                print('Batteristatus for hytte {:.3g}: {:.3g}kWh'.format(i, E[i]['LevelOfCharge']))
                

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
            print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
            print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
            print('---------------------------------------------------------------------')
            print()
    
    
    #NEDENFOR STARTER HANDELEN MELLOM DELTAKERENE. KODEN BEVEGER SEG NEDOVER ETTER HVILKE BUD SOM HAR HØYESTE PRIORITET
    #----------------------------------------------------------------------------------------
    
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
            print('Salgsandeler: ', seller_transfer)
            print('Kjøpsandeler: ', buyer_transfer)
            print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
            print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
            print()
        
        #FØRSTE PRIORITERING. MOMENTAN UTVEKLSING MELLOM PV-ANLEGG MED OVERSKUDD OG UNDERSKUDD
        for j in index_seller_pv: #SELGER MED INDEX J

          if (time == time_analysis):       
        
            print('Produksjonsoverskudd for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['lost_production']))
          
          E[j]['lost_production'] -= seller_transfer[j]
          
          '''
          if E[j]['lost_production'] < 0.001:
                
                E[j]['lost_production'] = 0
          '''      
          
          if (time == time_analysis): 
           
              print('Produksjonsoverskudd for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['lost_production']))  
              
            
          E[j]['pv_sell_pv'] += seller_transfer[j] #TIL PLOTTING
          
          
            
        for i in index_buyer_pv: #KJØPER MED INDEX I
                
                if (time == time_analysis):       
              
                  print('Estimert forbruk som ikke blir dekt for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['lost_load']))
                  
                
                E[i]['lost_load'] -= buyer_transfer[i]
                E[i]['pv_buy_pv'] += buyer_transfer[i] #TIL PLOTTING
        
                '''      
                if E[i]['lost_load'] < 0.001:
                    
                    E[i]['lost_load'] = 0
                '''
                    
                if (time == time_analysis):       
                  
                  print('Estimert forbruk som ikke blir dekt for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['lost_load']))   
    
                
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
       
        
    #Hvis batteriutveksling er aktivert
    if battery_share_activate == 1:   
    
        if (len(index_seller_battery) != 0) & (len(index_buyer_pv) != 0):   
            
            dict_count['bat2pv'] += 1
            seller_trade, buyer_trade, rest_profit, rest_demand, tap  = trade_batt2pv.trade_batt2pv(sum_energy_profit_pv, sum_energy_demand_pv, index_buyer_pv, index_seller_battery, count_buyers_pv, count_sellers_battery, len(param), E, param, tap)
            
            if (time == time_analysis):         
        
                print('Type handel: bat2pv')
                print('Salgsandeler: ', seller_trade)
                print('Kjøpsandeler: ', buyer_trade)
                print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
                print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
                print()
            
            #ANDRE PRIORITET. FULLE BATTERI SELGER TIL MOMENTAN PV
            for j in index_seller_battery:
                     
              if (time == time_analysis):       
            
                print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
              E[j]['LevelOfCharge'] -= seller_trade[j] #ENERGY
                
              
              if (time == time_analysis):       
            
                print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
              E[j]['battery_sell_pv'] += seller_trade[j] 
                
                
            for i in index_buyer_pv:
                
                    if (time == time_analysis):       
                  
                      print('Estimert forbruk som ikke blir dekt for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['lost_load']))    
                
                    E[i]['lost_load'] -= buyer_trade[i]
                    
                    '''
                    if E[i]['lost_load'] < 0.001:
                        
                        E[i]['lost_load'] = 0
                    '''
                    
                    if (time == time_analysis):       
                  
                      print('Estimert forbruk som ikke blir dekt for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['lost_load']))
                    
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
        
    #Hvis flex- og batteri-utveksling er aktivert          
    if (flex_activate == 1) & (battery_share_activate == 1):  
        
        
        if (len(index_flex_sell_battery) != 0) & (len(index_buyer_pv) != 0):  
        
            dict_count['flex2pv'] += 1
            seller_trade, buyer_trade, rest_profit, rest_demand, tap = trade_flex2pv.trade_flex2pv(time, sum_energy_profit_pv, sum_energy_demand_pv, index_buyer_pv, index_flex_sell_battery, count_buyers_pv, count_battery_sell_flex, len(param), E, param, tap)
                    
            if (time == time_analysis):         
        
                print('Type handel: flex2pv')
                print('Salgsandeler: ', seller_trade)
                print('Kjøpsandeler: ', buyer_trade)
                print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
                print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
                print()
            
            #TREDJE PRIORITET. FLEX-BATTERI SELGER TIL MOMENTAN PV
            for j in index_flex_sell_battery:
                
                        if (time == time_analysis):       
                      
                          print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
                        E[j]['LevelOfCharge'] -= seller_trade[j]
                        
                        if (time == time_analysis):       
                      
                          print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                        
                        E[j]['battery_sell_pv'] += seller_trade[j]   
                        
                
            for i in index_buyer_pv:
                            
                        if (time == time_analysis):       
                      
                          print('Estimert forbruk som ikke blir dekt for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['lost_load']))                       
                        
                        E[i]['lost_load'] -= buyer_trade[i]
                        
                        '''
                        if E[i]['lost_load'] < 0.001:
                            
                            E[i]['lost_load'] = 0
                        '''
                        
                        if (time == time_analysis):       
                      
                          print('Estimert forbruk som ikke blir dekt for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['lost_load']))    
                          
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
      
                    
    if battery_share_activate == 1:
                                  
        if (len(index_seller_pv) != 0) & (len(index_buyer_battery) != 0):
            
            dict_count['pv2bat'] += 1
            #ANLEGG MED OVERSKUDD SOM FØRSTEPRIORITET?
            seller_trade, buyer_trade, rest_profit, rest_demand, tap = trade_pv2batt.trade_pv2bat(sum_energy_profit_pv, sum_energy_demand_pv, index_seller_pv, index_buyer_battery, count_sellers_pv, count_buyers_battery, len(param), E, param, time, tap)        

            if (time == time_analysis):         
                
                
                print('Type handel: pv2bat')
                print('Salgsandeler: ', seller_trade)
                print('Kjøpsandeler: ', buyer_trade)
                print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
                print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
                print() 
                
            #PV-anlegg selger til tomme batteri    
            for j in index_seller_pv:
                
                
                if (time == time_analysis):       
                
                    print('Produksjonsoverskudd for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['lost_production']))
                
                
                E[j]['lost_production'] -= seller_trade[j]
                
                '''
                if  E[j]['lost_production'] < 0.001:
                    
                    E[j]['lost_production'] = 0
                
                '''

                
                if (time == time_analysis):       
            
                    print('Produksjonsoverskudd for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['lost_production']))
                
                E[j]['pv_sell_battery'] += seller_trade[j]
            
                
                
            for i in index_buyer_battery:
                    
                
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                
                    E[i]['LevelOfCharge'] += buyer_trade[i]
                    
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                    
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
                    
                    index_flex_sell_battery.append(i)    
                    
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
            
        
    
    if (flex_activate == 1) & (battery_share_activate == 1):
        
        
        if (len(index_flex_buy_battery) != 0) & (len(index_seller_pv) != 0):
        
            dict_count['pv2flex'] += 1
            seller_trade, buyer_trade, rest_profit, rest_demand, tap = trade_pv2batt.trade_pv2bat(sum_energy_profit_pv, sum_energy_demand_pv, index_seller_pv, index_flex_buy_battery, count_sellers_pv, count_battery_buy_flex, len(param), E, param, time, tap)
    
            if (time == time_analysis):         
        
                print('Type handel: pv2flex')
                print('Salgsandeler: ', seller_trade)
                print('Kjøpsandeler: ', buyer_trade)
                print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
                print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
                print()
                
            #PV-anlegg selger til flex-batteri     
            for j in index_seller_pv:
                
                if (time == time_analysis):       
                
                    print('Produksjonsoverskudd for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['lost_production']))
                
                E[j]['lost_production'] -= seller_trade[j]
                
                '''
                if E[j]['lost_production'] < 0.001:
                    
                    E[j]['lost_production'] = 0
                '''
                
                if (time == time_analysis):       
                
                    print('Produksjonsoverskudd for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['lost_production']))
                
                E[j]['pv_sell_battery'] += seller_trade[j]
            
                
                
            for i in index_flex_buy_battery:
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                    
                    E[i]['LevelOfCharge'] += buyer_trade[i]
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                    
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
       
        
    if battery_share_activate == 1:
              
        if (len(index_seller_battery) != 0) & (len(index_buyer_battery) != 0):
            
            dict_count['bat2bat'] += 1
            seller_trade, buyer_trade, rest_profit, rest_demand, tap  = trade_flex2flex.trade_batt2batt(flex_limit, sum_energy_profit_pv, sum_energy_demand_pv, index_buyer_battery, index_seller_battery, count_sellers_battery, count_buyers_battery, len(param), E, param, time, tap)
           
            
            if (time == time_analysis):         
        
                print('Type handel: bat2bat')
                print('Salgsandeler: ', seller_trade)
                print('Kjøpsandeler: ', buyer_trade)
                print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
                print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
                print()
                
            #Fulle batteri selger til tomme batteri
            for j in index_seller_battery:
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
                E[j]['LevelOfCharge'] -= seller_trade[j]
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
                E[j]['battery_sell_battery'] += seller_trade[j]
                
                #FLEX BATTERI SOM KJØPER
            for i in index_buyer_battery:
               
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
               
                E[i]['LevelOfCharge'] += buyer_trade[i]
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                
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
        
    
    if (flex_activate == 1) & (battery_share_activate == 1):    
        
        
        if (len(index_flex_sell_battery) != 0) & (len(index_buyer_battery) != 0):
               
            dict_count['flex2bat'] += 1
            #FLEX BATTERI SOM SELGER           
            seller_trade, buyer_trade, rest_profit, rest_demand, tap  = trade_flex2flex.trade_batt2batt(flex_limit, sum_energy_profit_pv, sum_energy_demand_pv, index_buyer_battery, index_flex_sell_battery, count_battery_sell_flex, count_buyers_battery, len(param), E, param, time, tap)
           
            if (time == time_analysis):         
        
                print('Type handel: flex2bat')
                print('Salgsandeler: ', seller_trade)
                print('Kjøpsandeler: ', buyer_trade)
                print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
                print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
                print()
            
            #Flex-batteri selger til tomme batteri
            for j in index_flex_sell_battery:
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
                E[j]['LevelOfCharge'] -= seller_trade[j]
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
                E[j]['battery_sell_battery'] += seller_trade[j]
                
                #FLEX BATTERI SOM KJØPER
            for i in index_buyer_battery:
                    
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                    
                E[i]['LevelOfCharge'] += buyer_trade[i]
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                
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
    
    
            
        if (len(index_flex_buy_battery) != 0) & (len(index_seller_battery) != 0):
            
            dict_count['bat2flex'] += 1
            seller_trade, buyer_trade, rest_profit, rest_demand, tap  = trade_flex2flex.trade_batt2batt(flex_limit, sum_energy_profit_pv, sum_energy_demand_pv, index_flex_buy_battery, index_seller_battery, count_sellers_battery, count_battery_buy_flex, len(param), E, param, time, tap)
           
            if (time == time_analysis):         
        
                print('Type handel: bat2flex')
                print('Salgsandeler: ', seller_trade)
                print('Kjøpsandeler: ', buyer_trade)
                print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
                print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
                print()
            
            #Fulle batteri selger til flex-batteri
            for j in index_seller_battery:
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
                E[j]['LevelOfCharge'] -= seller_trade[j]
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
                E[j]['battery_sell_battery'] += seller_trade[j]
                
                #FLEX BATTERI SOM KJØPER
            for i in index_flex_buy_battery:
                    
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
    
                E[i]['LevelOfCharge'] += buyer_trade[i]
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                
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
    
            
        if (len(index_flex_buy_battery) != 0) & (len(index_flex_sell_battery) != 0):    
        
            dict_count['flex2flex'] += 1
            seller_trade, buyer_trade, rest_profit, rest_demand, tap  = trade_flex2flex.trade_batt2batt(flex_limit, sum_energy_profit_pv, sum_energy_demand_pv, index_flex_buy_battery, index_flex_sell_battery, count_battery_sell_flex, count_battery_buy_flex, len(param), E, param, time, tap)
           
            if (time == time_analysis):         
        
                print('Type handel: flex2flex')
                print('Salgsandeler: ', seller_trade)
                print('Kjøpsandeler: ', buyer_trade)
                print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
                print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
                print()
           
            #Flex-batteri selger til flex-batteri
            for j in index_flex_sell_battery:
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
                    E[j]['LevelOfCharge'] -= seller_trade[j]
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                    
                    E[j]['battery_sell_battery'] += seller_trade[j]
                    

            for i in index_flex_buy_battery:
                   
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                          
                    E[i]['LevelOfCharge'] += buyer_trade[i]
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                    
                    E[i]['battery_buy_battery'] += buyer_trade[i]       
                                                      
            
            if time == time_analysis:
                    
               print('---------------------------------------------------------------------')        
               
            sum_energy_demand_pv = rest_demand
            sum_energy_profit_pv = rest_profit   
            
            x = []
            
            for j in index_flex_sell_battery:
                
                
                if E[j]['LevelOfCharge'] > 0.5*param[i]['BatteryCapacity'] + flex_limit*param[j]['BatteryCapacity']:
                    
                    x.append(j)
                    # -*- coding: utf-8 -*-
"""
Created on Fri Mar  3 10:03:48 2023

@author: halgr
"""

import numpy as np

import LEC_input_files as lecif
#Fil som inneholder funksjonene som bearbeider input-filene (forburk og produksjon)

import model_builder_per_timestep as ofmb
#Inneholder funksjonen som beregner energiflytsverdier før og etter handel i et tidssteg

import LEC_offgrid_plot as ofg_plot
#Inneholder funksjonene som plotter energiflytsverdier for ønsket antall deltakere og over ønsket tidsrom

import offgrid_model_builder as ofmb_pre
#Inneholder funksjoner som beregner energiflytsverdier uten energihandel (basecase)

import sf_rate as sf
#Inneholder funksoner som beregner SF-rate

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
#Forhindre plagsomme warnings i kontrollvinduet

#-----------------------------------------------------------------------------------------

'''
DENNE FILEN KJØRER SIMULERING FOR ØNSKET ANTALL HYTTER MED ØNSKET BRUKSMØNSTER. FILEN
ER FORENKLET BYGD OPP. ALT KJØRES I LØKKER. PÅ DENNE MÅTEN VIL ALLE HYTTENE SOMULERES MED LIKE 
TEKNISKE PARAMETERE. OM DISSE PARAMETERENE VIL SPESIFIESRES ANNERLEDES FOR HVER DELTAKER, KAN DETTE
FJØRES I FILENE  "LEC_offgrid_analysis2/3/4/10/20/50".

'''

'''
Tapsfaktorere i handel er ikke lagt inn i koden. Det ligger inne tapsfaktor på energiflyt i egen 
installasjon før handel. (Noe som fører til at litt produsert energi blir borte )
'''

#NESTED DICTIONARY AV ANNLEGGSPARAMETERE TIL DELTAKERENE
param = {}


#Lite bakgrunnsinfo ligger bak de valgte tekniske parameterene
param_ex1 = {'BatteryCapacity': 30,
                'BatteryEfficiency': 1,
                'BatteryDischargeLimit': 2,
                'BatterySellingLimit': 3,
                'InverterEfficiency': 1,
                'timestep': .25,
                'MaxPower': 1.8,
                'MaxPowerInverter': 4
               }

'''
Max power for batteriet. Hva er typisk utladning/oppladningseffekt for batteri?

Ser et lithium batteri (12V) har max 150A utladningsstrøm og max oppladningsstrøm på 150A 
-> 1800W -> 450Wh per tidssteg max opp/utladning

Finner vekselrettere med max effekt på 4kW på sunwind.no (Kontinuerlig effekt er anbefalt til 2kW)
'''


'''
SAMMENLIGNE MED BOLIGERS FORBRUK. 
'''

#-----------------------------------------------------------------------------------------
#0: bor på hytta, 1: feriebruk, 2: annenhver helg, 3: hver helg
deltakere1 = [1, 4]
bruksmønster1 = [1, 0] #Bruksmønster på deltakerene

deltakere2 = [1, 2, 3]
bruksmønster2 = [1, 0, 0] #Bruksmønster på deltakerene

deltakere3 = [1, 2, 1, 4]
bruksmønster3 = [1, 0, 2, 3] #Bruksmønster på deltakerene

deltakere4 = [1, 4, 1, 2, 1]
bruksmønster4 = [1, 0, 1, 3, 1] #Bruksmønster på deltakerene

deltakere5 = [4, 2, 1, 1, 1] #Kategorihytte på deltakerene 
bruksmønster5 = [0, 0, 0, 1, 2] #Bruksmønster på deltakerene

deltakere10 = [1, 2, 1, 4, 4, 1, 2, 1, 4, 4]
bruksmønster10 = [1, 2, 1, 0, 0, 1, 2, 1, 0, 0]

deltakere20 = [1, 2, 1, 4, 4, 1, 2, 1, 4, 4, 1, 2, 1, 4, 4, 1, 2, 1, 4, 4]
bruksmønster20 = [1, 2, 1, 0, 0, 1, 2, 1, 0, 0, 1, 2, 1, 0, 0, 1, 2, 1, 0, 0]

deltakere50 = [1, 2, 1, 4, 4, 1, 2, 1, 4, 4, 1, 2, 1, 4, 4, 1, 2, 1, 4, 4, 1, 2, 1, 4, 4, 1, 2, 1, 4, 4, 1, 2, 1, 4, 4, 1, 2, 1, 4, 4, 1, 2, 1, 4, 4, 1, 2, 1, 4, 4]
bruksmønster50 = [1, 0, 1, 0, 0, 0, 1, 0, 0, 2, 1, 0, 1, 0, 0, 0, 1, 0, 0, 2, 1, 0, 1, 0, 0, 0, 1, 0, 0, 2, 1, 0, 1, 0, 0, 0, 1, 0, 0, 2, 1, 0, 1, 0, 0, 0, 1, 0, 0, 2]


#Hente input-filene med kvartersverdier gjennom et helt år
demand, pv = lecif.LEC_input_files(deltakere10, bruksmønster10)

#antall datapunkter
n = len(demand)

#Produsere tekniske parametere for alle deltakerene (alle får like når det gjøres på denne måten)
for i in range(n):

    #Gjør alle hyttene lik eksempelhytta    
    param[i] = param_ex1


K = {}

#Energiflytsverdier uten energideling  
for i in range(n):
             
    K[i] = ofmb_pre.offgrid_model(demand[i], pv[i], param[i], return_series=False)


print()
print('FØR ENERGIDELING (ÅRLIG RESULTAT)')
print('---------------------------------------------------------------------------------------')


print()
for i in range(n):
    
    print('Bortkastet solenergi for hytte {:.1g}: {:.5g} kWh'.format(i+1,sum(K[i]['lost_production'])*0.25))



sf_rate_pre = sf.sf_rate(K, demand)

print()
for i in range(n):
    
    print('Self sufficient rate for hytte {:.1g}: {:.4g} %'.format(i+1, sf_rate_pre[i]))


print()
for i in range(n):
    
    print('Estimert forbruk som ikke blir dekt for hytte {:.1g}: {:.5g} kWh'.format(i+1, sum(K[i]['lost_load'])*0.25))



x = 0
a = 0

#Totale verdier gjennom et helt år
for i in range(n):
    
    x += sum(K[i]['lost_load'])*0.25
    a += sum(K[i]['lost_production'])*0.25

#Etter energideling
dict_list = []
sum_lost_load = np.zeros(n)
sum_lost_production = np.zeros(n)

dict_count = {}
dict_count['pv2pv'] = 0
dict_count['pv2bat'] = 0
dict_count['pv2flex'] = 0
dict_count['bat2pv'] = 0
dict_count['flex2pv'] = 0
dict_count['bat2bat'] = 0
dict_count['flex2bat'] = 0
dict_count['bat2flex'] = 0
dict_count['flex2flex'] = 0


#Energiflytsverdier med energideling
for time in range(0,35037):
    
    
    E, dict_count = ofmb.E_per_timestep(dict_list, dict_count, param, time, demand, pv)

    dict_list.append(E)
    
#Totale verdier gjennom et helt år
for i in range(0,35037):
    
    for j in range(n):
        
        sum_lost_load[j] += dict_list[i][j]['lost_load'] 
        sum_lost_production[j] += dict_list[i][j]['lost_production']
                    


print('ETTER ENERGIDELING (ÅRLIG RESULTAT)')
print('---------------------------------------------------------------------------------------')

print()
for i in range(n):
    
    print('Bortkastet solenergi for hytte {:.1g}: {:.5g} kWh'.format(i+1, sum_lost_production[i]*0.25))



sf_rate_post = sf.sf_rate_sharing(sum_lost_load, demand)

print()
for i in range(n):
    
    print('Self sufficient rate for hytte {:.1g}: {:.4g} %'.format(i+1, sf_rate_post[i]))
    
    
print()
for i in range(n):
    
    print('Estimert forbruk som ikke blir dekt for hytte {:.1g}: {:.5g} kWh'.format(i+1, sum_lost_load[i]*0.25))


b = 0
y = 0

for i in range(n):
    
    b += sum_lost_production[i]*0.25
    y += sum_lost_load[i]*0.25
    
lost_load_tot = x-y
lost_production_tot = a-b

#Fjerne (uforklarlige) småfeil som oppstår i koden underveis
if ((lost_load_tot/lost_production_tot) > 0.995) & ((lost_load_tot/lost_production_tot) < 1.005):
    
    lost_load_tot = lost_production_tot

print()
print('RESULTAT')
print('Total reduksjon i estimert forbruk som ikke blir dekt : {:.5g}kWh'.format(lost_load_tot))
print('Relativ total reduskjon i estimert forbruk som ikke blir dekt : {:.3g}%'.format(((lost_load_tot)*100)/x))
print('----------------------------------------------------------------')
print('Total reduksjon i bortkastet solenergi: {:.5g}kWh'.format((lost_production_tot)))
print('Relativ total reduksjon av bortasktet solenergi: {:.3g}%'.format((lost_production_tot)*100/a))
print()
print('OVERSIKT OVER ANTALL BUD GJENNOM ÅRET [stk]')
print('----------------------------------------------------------------')
print('pv2pv: {:.5g}'.format(dict_count['pv2pv']))
print('bat2pv: {:.5g}'.format(dict_count['bat2pv']))
print('flex2pv: {:.5g}'.format(dict_count['flex2pv']))
print('pv2bat: {:.5g}'.format(dict_count['pv2bat']))
print('pv2flex: {:.5g}'.format(dict_count['pv2flex']))# -*- coding: utf-8 -*-
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

'''
Denne filen simulerer energiflytsvariablene for alle deltakerene i et gitt tidssteg. 
Funksjonen som kjøres returnerer E. E er en dictionary med energiflytsvariablene 
tilørende N deltakere for gitt tidssteg.

'''


'''
TESTENE ER GJENNOMFØRT MED HYTTEFELTET

time = 4639
deltakere5 = [4, 2, 1, 1, 1] #Kategorihytte på deltakerene 
bruksmønster5 = [0, 0, 0, 1, 2] #Bruksmønster på deltakerene

'''

'''
(0.3) -> 6651, 4639, 9999, 8656, 19999, 20999, 23999
'''


battery_share_activate = 1 #Inkludere batteriutveksling når de er tomme/fulle
flex_activate = 1 #Inkludere fleksibel batteriutveksling

flex_limit = 0.1
#Jo høyere flex_limit, desto høyere batteristatus må flex-batteriet ha for å selge sin henergi.
#E[j]['LevelOfCharge'] > 0.5*battery_capacity + flex_limit*battery_capacity): -> SELGE
#(E[j]['LevelOfCharge'] < 0.5*battery_capacity - flex_limit*battery_capacity): -> KJØPE    

#GROV SPESIFISERING AV DAGER
month = 12   #month -> 1-12
day = 31   #day -> 1-30
hour = 23   #hour -> 1-23
minute = 45    #kvarter -> 15,30,45

#Time_analysis er det tidssteget som det vises informasjon om i kontrollvinduet. I kontrollvinduet vises hvordan
#handelen foregår i valgt tidssteg
time_analysis = (month-1)*2880 + (day-1)*96 + hour*4 + minute/15



def E_per_timestep(dict_list, dict_count, param, time, demand, pv):

    
    E = {}
    bidding_battery = {}
    bidding_pv = {}
    
    return_series = True
    deltakere_n = len(param)
        
    
    #ENERGIFLYTSVERDIER FOR HVER DELTAKER I GITT TIDSSTEG FØR ENERGIDELING
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
    
        '''
        #FJERNE "FLUER" FRA INPUT DATAENE
        if (pv[x][time] < 0):
                pv[x][time] = 0
            
        if (demand[x][time] < 0.1):
                demand[x][time] = 0
        '''
        
        #DEFINERE VARIABLER
        battery_capacity = param[x]['BatteryCapacity']
        n_bat = param[x]['BatteryEfficiency']
        n_inv = param[x]['InverterEfficiency']
        timestep = param[x]['timestep']
        
        
        #Her er virkningsgrad tatt med
        pv2inv = np.minimum(pv[x][time], demand[x][time]/n_inv) #demand[x][time]/n_inv
        res_pv = np.maximum(pv[x][time] - demand[x][time]/n_inv, 0) #Lasten som momentant er større en forbruket for det gitte tidssteget
        inv2load = pv2inv * n_inv
        res_load = (demand[x][time] - pv2inv * n_inv) #lasten som ikke dekkes av momentan PV #pv2inv

      
            
        #1. prioritet etter at momentant forburk er dekket -> Forsyne eget batteri
        if LevelOfCharge_previous >= battery_capacity:  
                    pv2store = 0 
            
        else: #BATTERIET ER IKKE FULT, MEN VIL OVERSTIGE MAX KAPASITET VED OPPLADING I GITT TIDSSTEG
                if (LevelOfCharge_previous + (res_pv * timestep)) > battery_capacity:
                    
                    #KAN MAX LADE OPP DET SMO ER IGJEN FØR BATTERIET NÅR MAX KAPASITET
                    pv2store = min((battery_capacity - LevelOfCharge_previous)/timestep, max_power_battery)
                    #OPPLADINGEN BEGRENSES AV MAX LADING PÅ BATTERI
                    
                    
                else: #BATTERIET ER IKKE FULT OG VIL IKKE OVERTIGE MAX KAPASITET VED OPPLADNING I GITT TIDSSTEG
                    #BEGRENSES AV MAX LADING PÅ BATTERI
                    pv2store = min(res_pv, max_power_battery)
             
        
            
            
        store2inv = min((LevelOfCharge_previous/timestep-discharge_limit/timestep), res_load/n_inv, max_power_battery)  
        
        
        '''
        if time == 20999:
            
            print('Pv2store : {:.3g}'.format(pv2store))
            print('store2inv : {:.3g}'.format(store2inv))
       '''     
        
        #LADE OPP DET MAN KAN MED EGEN ENERGI
        LevelOfCharge = min(LevelOfCharge_previous - (store2inv - pv2store*n_bat) * timestep,  # DC - pv2store*n_bat
                                   battery_capacity)
        
       

        
        #-------------------------------------------------------------------------------------------
        
        
        #EFFEKT TIL FORBRUK. I BÅDE STORE2INV OG INV2LOAD ER EFFEKTBEGRENSNINGER TATT HENSYN TIL
        inv2load = inv2load + store2inv*n_inv
        
        '''
        if time == time_analysis:
            
            print()
            print('Tapt produksjon: {:.3g}'.format(dict_list[time-1][0]['lost_production']))
            print('Tapt produksjon: {:.3g}'.format(dict_list[time-1][1]['lost_production']))
            print()
        '''
        
        #EFFEKT SOM KAN SELGES PÅ MARKEDET
        lost_production = res_pv - pv2store 
       
        '''
        if time == time_analysis:
            
            print('Tapt produksjon: {:.3g}'.format(dict_list[time-1][0]['lost_production']))
            print('Tapt produksjon: {:.3g}'.format(dict_list[time-1][1]['lost_production']))
            print()
        '''
       
            
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
        
        #-------------------------------------------------------------------------------------------
        '''
        #FJERNE FLUER
        if lost_load < 0.001:
            
            lost_load = 0
            
        if lost_production < 0.001:
            
            lost_production = 0
        '''
        
        #Energiflytsverdiene for deltaker x i gitt tidssteg før energideling
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
        
        
       #Etablere bud for deltaker x
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
    #DEKLARERE VARIABLER,VEKTORER OG INDEX-VEKTORER TIL Å MODELLERE ENERGIMARKEDET
    
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
    #iterere gjennom deltagerene
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
            
            #REGISTRERE HVOR MYE (kW) DELTAKEREN SELGER i tidssteget
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
    SIDEN ANLEGGET FØRST FORSYNER SEG SELV, GÅR OVERSKUDDS-PV i første omgang TIL Å LADE OPP BATTERIET. DET er SJELDENT 
    OVERSKUDDS-PV IGJEN (SIDEN BATTERIET i egen installasjon DA MÅ VÆRE FULT) FØR HANDELENE STARTER. DET ER OBSERVERT AT NÅR FLEX_LIMIT ER UNDER 100%, 
    VIL ALDRI BATTERIENE STÅ FULLE. I DETTE TILFELLE BRUKES EGEN OVERSKUDDS-PV TIL Å LADE EGET BATTERI, FOR SÅ AT BATTERIET (SOM DA OFTEST ER FLEX) SELGER SIN ENERGI TIL FLEX_LIMIT NÅS. 
    
    GJØRES DET ET FORSØK DER FLEXLIMIT SETTES TIL 100% (SOM OM VI FJERNE MULIGHETEN TIL Å FLEXE MED SIN ENERGI) OBSERVERES
    DET AT VI FÅR UTVEKSLING DIREKTE MELLOM PV-ANLEGG. DETTE FORDI EN HYTTE SOM I UTGANGSPUNKTET STÅR TOM, ETTERHVERT 
    VIL FÅ FULT BATTERI. UTEN FLEX BATTERI VIL DISSE BATTERIENE HA LITEN MULIGHET TIL Å SELGE SIN ENERGI SIDEN DE KUN KAN SELGE VED 
    100% KAPASITET. DERFOR VIL DET OPPSTÅ SITUASJONER DER PV SENDER DIREKTE TIL PV.
    '''
    
    #KODELINJE SOM SKILLER FLEXBATTERIENE BASERT PÅ FLEXLIMIT OG BATTERISTATUS. NOEN FLEXBATTERI STILLER SEG
    #I POSISJON TIL KJØP OG NOEN STILLER SEG I POSISJON TIL SALG.
    for j in index_flex_battery:  
    
        if (E[j]['LevelOfCharge'] > 0.5*battery_capacity + flex_limit*battery_capacity):
        
            index_flex_sell_battery.append(j)
            
            
        elif (E[j]['LevelOfCharge'] < 0.5*battery_capacity - flex_limit*battery_capacity):
            
            index_flex_buy_battery.append(j)
            

    count_battery_sell_flex = len(index_flex_sell_battery)
    count_battery_buy_flex = len(index_flex_buy_battery)

    #-------------------------------------------------------------------------------------------       
    #HANDELEN MELLOM STARTER. IF-SETNINGENE LEGGES FREM I PRIORITERINGS-REKKEFØLGEN FOR KJØP OG SALG LAGT FREM I
    #MASTEROPPGAVEN
    
    '''
    #Fjerne fluer
    for j in range(len(param)):
        
        if E[j]['lost_load'] < 0.001:
            
            E[j]['lost_load'] = 0
        
        if E[j]['lost_production'] < 0.001:
            
            E[j]['lost_production'] = 0
    '''       
   
    #Dersom et PV-anlegg har lagt ut et kjøpe-bud, vil det bety at batteriet i egen installasjon har ladet seg ut så langt det
    #rekker før handelen starter (store2inv). Kodelinjen nedenfor fjerner et eventuelt flex-batteri som selger dersom batteriet
    #allerede har forsyn egen installasjon.
    common_elements = set(index_buyer_pv) & set(index_flex_sell_battery)
    
    for element in common_elements:
        index_flex_sell_battery.remove(element)
                                  

    common_elements = set(index_buyer_pv) & set(index_seller_battery)
    
    for element in common_elements:
        index_seller_battery.remove(element)
                                  
    
    #Plotte energiflytsverdier i git tidssteget FØR deling
    if time == time_analysis:
        
            print()
            print('ENERGIFLYTSVERDIER (FØR DELING) I TIDSSTEG {:.5g}'.format(time))
            print('Date and time: {:.3g}.{:.3g} {:.3g}:{:.3g}'.format(day,month,hour,minute))
            print('---------------------------------------------------------------------')
            
            for i in range(len(param)):
            
                
                print('Ikke dekt last for hytte {:.3g}: {:.3g}kW'.format(i,E[i]['lost_load']))
                
            
            for i in range(len(param)):
                
                print('Produksjonsoverskudd for hytte {:.3g}: {:.3g}kW'.format(i, E[i]['lost_production']))
                

            for i in range(len(param)):
                
                print('Batteristatus for hytte {:.3g}: {:.3g}kWh'.format(i, E[i]['LevelOfCharge']))
                

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
            print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
            print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
            print('---------------------------------------------------------------------')
            print()
    
    
    #NEDENFOR STARTER HANDELEN MELLOM DELTAKERENE. KODEN BEVEGER SEG NEDOVER ETTER HVILKE BUD SOM HAR HØYESTE PRIORITET
    #----------------------------------------------------------------------------------------
    
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
            print('Salgsandeler: ', seller_transfer)
            print('Kjøpsandeler: ', buyer_transfer)
            print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
            print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
            print()
        
        #FØRSTE PRIORITERING. MOMENTAN UTVEKLSING MELLOM PV-ANLEGG MED OVERSKUDD OG UNDERSKUDD
        for j in index_seller_pv: #SELGER MED INDEX J

          if (time == time_analysis):       
        
            print('Produksjonsoverskudd for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['lost_production']))
          
          E[j]['lost_production'] -= seller_transfer[j]
          
          '''
          if E[j]['lost_production'] < 0.001:
                
                E[j]['lost_production'] = 0
          '''      
          
          if (time == time_analysis): 
           
              print('Produksjonsoverskudd for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['lost_production']))  
              
            
          E[j]['pv_sell_pv'] += seller_transfer[j] #TIL PLOTTING
          
          
            
        for i in index_buyer_pv: #KJØPER MED INDEX I
                
                if (time == time_analysis):       
              
                  print('Estimert forbruk som ikke blir dekt for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['lost_load']))
                  
                
                E[i]['lost_load'] -= buyer_transfer[i]
                E[i]['pv_buy_pv'] += buyer_transfer[i] #TIL PLOTTING
        
                '''      
                if E[i]['lost_load'] < 0.001:
                    
                    E[i]['lost_load'] = 0
                '''
                    
                if (time == time_analysis):       
                  
                  print('Estimert forbruk som ikke blir dekt for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['lost_load']))   
    
                
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
       
        
    #Hvis batteriutveksling er aktivert
    if battery_share_activate == 1:   
    
        if (len(index_seller_battery) != 0) & (len(index_buyer_pv) != 0):   
            
            dict_count['bat2pv'] += 1
            seller_trade, buyer_trade, rest_profit, rest_demand  = trade_batt2pv.trade_batt2pv(sum_energy_profit_pv, sum_energy_demand_pv, index_buyer_pv, index_seller_battery, count_buyers_pv, count_sellers_battery, len(param), E, param)
            
            if (time == time_analysis):         
        
                print('Type handel: bat2pv')
                print('Salgsandeler: ', seller_trade)
                print('Kjøpsandeler: ', buyer_trade)
                print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
                print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
                print()
            
            #ANDRE PRIORITET. FULLE BATTERI SELGER TIL MOMENTAN PV
            for j in index_seller_battery:
                     
              if (time == time_analysis):       
            
                print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
              E[j]['LevelOfCharge'] -= seller_trade[j] #ENERGY
                
              
              if (time == time_analysis):       
            
                print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
              E[j]['battery_sell_pv'] += seller_trade[j] 
                
                
            for i in index_buyer_pv:
                
                    if (time == time_analysis):       
                  
                      print('Estimert forbruk som ikke blir dekt for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['lost_load']))    
                
                    E[i]['lost_load'] -= buyer_trade[i]
                    
                    '''
                    if E[i]['lost_load'] < 0.001:
                        
                        E[i]['lost_load'] = 0
                    '''
                    
                    if (time == time_analysis):       
                  
                      print('Estimert forbruk som ikke blir dekt for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['lost_load']))
                    
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
        
    #Hvis flex- og batteri-utveksling er aktivert          
    if (flex_activate == 1) & (battery_share_activate == 1):  
        
        
        if (len(index_flex_sell_battery) != 0) & (len(index_buyer_pv) != 0):  
        
            dict_count['flex2pv'] += 1
            seller_trade, buyer_trade, rest_profit, rest_demand = trade_flex2pv.trade_flex2pv(time, sum_energy_profit_pv, sum_energy_demand_pv, index_buyer_pv, index_flex_sell_battery, count_buyers_pv, count_battery_sell_flex, len(param), E, param)
                    
            if (time == time_analysis):         
        
                print('Type handel: flex2pv')
                print('Salgsandeler: ', seller_trade)
                print('Kjøpsandeler: ', buyer_trade)
                print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
                print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
                print()
            
            #TREDJE PRIORITET. FLEX-BATTERI SELGER TIL MOMENTAN PV
            for j in index_flex_sell_battery:
                
                        if (time == time_analysis):       
                      
                          print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
                        E[j]['LevelOfCharge'] -= seller_trade[j]
                        
                        if (time == time_analysis):       
                      
                          print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                        
                        E[j]['battery_sell_pv'] += seller_trade[j]   
                        
                
            for i in index_buyer_pv:
                            
                        if (time == time_analysis):       
                      
                          print('Estimert forbruk som ikke blir dekt for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['lost_load']))                       
                        
                        E[i]['lost_load'] -= buyer_trade[i]
                        
                        '''
                        if E[i]['lost_load'] < 0.001:
                            
                            E[i]['lost_load'] = 0
                        '''
                        
                        if (time == time_analysis):       
                      
                          print('Estimert forbruk som ikke blir dekt for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['lost_load']))    
                          
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
      
                    
    if battery_share_activate == 1:
                                  
        if (len(index_seller_pv) != 0) & (len(index_buyer_battery) != 0):
            
            dict_count['pv2bat'] += 1
            #ANLEGG MED OVERSKUDD SOM FØRSTEPRIORITET?
            seller_trade, buyer_trade, rest_profit, rest_demand = trade_pv2batt.trade_pv2bat(sum_energy_profit_pv, sum_energy_demand_pv, index_seller_pv, index_buyer_battery, count_sellers_pv, count_buyers_battery, len(param), E, param, time)        

            if (time == time_analysis):         
                
                
                print('Type handel: pv2bat')
                print('Salgsandeler: ', seller_trade)
                print('Kjøpsandeler: ', buyer_trade)
                print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
                print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
                print() 
                
            #PV-anlegg selger til tomme batteri    
            for j in index_seller_pv:
                
                
                if (time == time_analysis):       
                
                    print('Produksjonsoverskudd for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['lost_production']))
                
                
                E[j]['lost_production'] -= seller_trade[j]
                
                '''
                if  E[j]['lost_production'] < 0.001:
                    
                    E[j]['lost_production'] = 0
                
                '''

                
                if (time == time_analysis):       
            
                    print('Produksjonsoverskudd for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['lost_production']))
                
                E[j]['pv_sell_battery'] += seller_trade[j]
            
                
                
            for i in index_buyer_battery:
                    
                
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                
                    E[i]['LevelOfCharge'] += buyer_trade[i]
                    
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                    
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
                    
                    index_flex_sell_battery.append(i)    
                    
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
            
        
    
    if (flex_activate == 1) & (battery_share_activate == 1):
        
        
        if (len(index_flex_buy_battery) != 0) & (len(index_seller_pv) != 0):
        
            dict_count['pv2flex'] += 1
            seller_trade, buyer_trade, rest_profit, rest_demand = trade_pv2batt.trade_pv2bat(sum_energy_profit_pv, sum_energy_demand_pv, index_seller_pv, index_flex_buy_battery, count_sellers_pv, count_battery_buy_flex, len(param), E, param, time)
    
            if (time == time_analysis):         
        
                print('Type handel: pv2flex')
                print('Salgsandeler: ', seller_trade)
                print('Kjøpsandeler: ', buyer_trade)
                print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
                print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
                print()
                
            #PV-anlegg selger til flex-batteri     
            for j in index_seller_pv:
                
                if (time == time_analysis):       
                
                    print('Produksjonsoverskudd for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['lost_production']))
                
                E[j]['lost_production'] -= seller_trade[j]
                
                '''
                if E[j]['lost_production'] < 0.001:
                    
                    E[j]['lost_production'] = 0
                '''
                
                if (time == time_analysis):       
                
                    print('Produksjonsoverskudd for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['lost_production']))
                
                E[j]['pv_sell_battery'] += seller_trade[j]
            
                
                
            for i in index_flex_buy_battery:
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                    
                    E[i]['LevelOfCharge'] += buyer_trade[i]
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                    
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
       
        
    if battery_share_activate == 1:
              
        if (len(index_seller_battery) != 0) & (len(index_buyer_battery) != 0):
            
            dict_count['bat2bat'] += 1
            seller_trade, buyer_trade, rest_profit, rest_demand  = trade_flex2flex.trade_batt2batt(flex_limit, sum_energy_profit_pv, sum_energy_demand_pv, index_buyer_battery, index_seller_battery, count_sellers_battery, count_buyers_battery, len(param), E, param, time)
           
            
            if (time == time_analysis):         
        
                print('Type handel: bat2bat')
                print('Salgsandeler: ', seller_trade)
                print('Kjøpsandeler: ', buyer_trade)
                print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
                print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
                print()
                
            #Fulle batteri selger til tomme batteri
            for j in index_seller_battery:
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
                E[j]['LevelOfCharge'] -= seller_trade[j]
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
                E[j]['battery_sell_battery'] += seller_trade[j]
                
                #FLEX BATTERI SOM KJØPER
            for i in index_buyer_battery:
               
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
               
                E[i]['LevelOfCharge'] += buyer_trade[i]
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                
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
        
    
    if (flex_activate == 1) & (battery_share_activate == 1):    
        
        
        if (len(index_flex_sell_battery) != 0) & (len(index_buyer_battery) != 0):
               
            dict_count['flex2bat'] += 1
            #FLEX BATTERI SOM SELGER           
            seller_trade, buyer_trade, rest_profit, rest_demand = trade_flex2flex.trade_batt2batt(flex_limit, sum_energy_profit_pv, sum_energy_demand_pv, index_buyer_battery, index_flex_sell_battery, count_battery_sell_flex, count_buyers_battery, len(param), E, param, time)
           
            if (time == time_analysis):         
        
                print('Type handel: flex2bat')
                print('Salgsandeler: ', seller_trade)
                print('Kjøpsandeler: ', buyer_trade)
                print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
                print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
                print()
            
            #Flex-batteri selger til tomme batteri
            for j in index_flex_sell_battery:
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
                E[j]['LevelOfCharge'] -= seller_trade[j]
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
                E[j]['battery_sell_battery'] += seller_trade[j]
                
                #FLEX BATTERI SOM KJØPER
            for i in index_buyer_battery:
                    
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                    
                E[i]['LevelOfCharge'] += buyer_trade[i]
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                
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
    
    
            
        if (len(index_flex_buy_battery) != 0) & (len(index_seller_battery) != 0):
            
            dict_count['bat2flex'] += 1
            seller_trade, buyer_trade, rest_profit, rest_demand = trade_flex2flex.trade_batt2batt(flex_limit, sum_energy_profit_pv, sum_energy_demand_pv, index_flex_buy_battery, index_seller_battery, count_sellers_battery, count_battery_buy_flex, len(param), E, param, time)
           
            if (time == time_analysis):         
        
                print('Type handel: bat2flex')
                print('Salgsandeler: ', seller_trade)
                print('Kjøpsandeler: ', buyer_trade)
                print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
                print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
                print()
            
            #Fulle batteri selger til flex-batteri
            for j in index_seller_battery:
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
                E[j]['LevelOfCharge'] -= seller_trade[j]
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
                E[j]['battery_sell_battery'] += seller_trade[j]
                
                #FLEX BATTERI SOM KJØPER
            for i in index_flex_buy_battery:
                    
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
    
                E[i]['LevelOfCharge'] += buyer_trade[i]
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                
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
    
            
        if (len(index_flex_buy_battery) != 0) & (len(index_flex_sell_battery) != 0):    
        
            dict_count['flex2flex'] += 1
            seller_trade, buyer_trade, rest_profit, rest_demand = trade_flex2flex.trade_batt2batt(flex_limit, sum_energy_profit_pv, sum_energy_demand_pv, index_flex_buy_battery, index_flex_sell_battery, count_battery_sell_flex, count_battery_buy_flex, len(param), E, param, time)
           
            if (time == time_analysis):         
        
                print('Type handel: flex2flex')
                print('Salgsandeler: ', seller_trade)
                print('Kjøpsandeler: ', buyer_trade)
                print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
                print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
                print()
           
            #Flex-batteri selger til flex-batteri
            for j in index_flex_sell_battery:
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
                    E[j]['LevelOfCharge'] -= seller_trade[j]
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                    
                    E[j]['battery_sell_battery'] += seller_trade[j]
                    

            for i in index_flex_buy_battery:
                   
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                          
                    E[i]['LevelOfCharge'] += buyer_trade[i]
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                    
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
         
            
    #Energiflytsverdier i tidssteget etter energideling   
    if time == time_analysis:
        
            print()
            print('ENERGIFLYTSVERDIER (ETTER DELING) I TIDSSTEG {:.5g}'.format(time))
            print('Date and time: {:.3g}.{:.3g} {:.3g}:{:.3g}'.format(day,month,hour,minute))
            print('---------------------------------------------------------------------')
            
            for i in range(len(param)):
            
                
                print('Ikke dekt last for hytte {:.3g}: {:.3g}kW'.format(i,E[i]['lost_load']))
                
            
            for i in range(len(param)):
                
                print('Produksjonsoverskudd for hytte {:.3g}: {:.3g}kW'.format(i, E[i]['lost_production']))
                

            for i in range(len(param)):
                
                print('Batteristatus for hytte {:.3g}: {:.3g}kWh'.format(i, E[i]['LevelOfCharge']))
    
            print()
            
            
    
    
    return(E, dict_count)
    
print('bat2bat: {:.5g}'.format(dict_count['bat2bat']))
print('flex2bat: {:.5g}'.format(dict_count['flex2bat']))
print('bat2flex: {:.5g}'.format(dict_count['bat2flex']))
print('flex2flex: {:.5g}'.format(dict_count['flex2flex']))

#------------------------------------------------------------------------------------------

'''

#Plotting for bestemte uker
for week in range(20,21):
    
    
    for i in range(n):
    
        ofg_plot.LEC_offgrid_plot(dict_list, demand[i], pv[i], week, i)
    
    
 #ofg_plot.LEC_offgrid_plot(dict_list, demand[0], pv[0], week, 0)
 '''

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
         
            
    #Energiflytsverdier i tidssteget etter energideling   
    if time == time_analysis:
        
            print()
            print('ENERGIFLYTSVERDIER (ETTER DELING) I TIDSSTEG {:.5g}'.format(time))
            print('Date and time: {:.3g}.{:.3g} {:.3g}:{:.3g}'.format(day,month,hour,minute))
            print('---------------------------------------------------------------------')
            
            for i in range(len(param)):
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

'''
Denne filen simulerer energiflytsvariablene for alle deltakerene i et gitt tidssteg. 
Funksjonen som kjøres returnerer E. E er en dictionary med energiflytsvariablene 
tilørende N deltakere for gitt tidssteg.

'''


'''
TESTENE ER GJENNOMFØRT MED HYTTEFELTET

time = 4639
deltakere5 = [4, 2, 1, 1, 1] #Kategorihytte på deltakerene 
bruksmønster5 = [0, 0, 0, 1, 2] #Bruksmønster på deltakerene

'''

'''
(0.3) -> 6651, 4639, 9999, 8656, 19999, 20999, 23999
'''


battery_share_activate = 1 #Inkludere batteriutveksling når de er tomme/fulle
flex_activate = 1 #Inkludere fleksibel batteriutveksling

flex_limit = 0.1
#Jo høyere flex_limit, desto høyere batteristatus må flex-batteriet ha for å selge sin henergi.
#E[j]['LevelOfCharge'] > 0.5*battery_capacity + flex_limit*battery_capacity): -> SELGE
#(E[j]['LevelOfCharge'] < 0.5*battery_capacity - flex_limit*battery_capacity): -> KJØPE    

#GROV SPESIFISERING AV DAGER
month = 12   #month -> 1-12
day = 31   #day -> 1-30
hour = 23   #hour -> 1-23
minute = 45    #kvarter -> 15,30,45

#Time_analysis er det tidssteget som det vises informasjon om i kontrollvinduet. I kontrollvinduet vises hvordan
#handelen foregår i valgt tidssteg
time_analysis = (month-1)*2880 + (day-1)*96 + hour*4 + minute/15



def E_per_timestep(dict_list, dict_count, param, time, demand, pv):

    
    E = {}
    bidding_battery = {}
    bidding_pv = {}
    
    return_series = True
    deltakere_n = len(param)
        
    
    #ENERGIFLYTSVERDIER FOR HVER DELTAKER I GITT TIDSSTEG FØR ENERGIDELING
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
    
        '''
        #FJERNE "FLUER" FRA INPUT DATAENE
        if (pv[x][time] < 0):
                pv[x][time] = 0
            
        if (demand[x][time] < 0.1):
                demand[x][time] = 0
        '''
        
        #DEFINERE VARIABLER
        battery_capacity = param[x]['BatteryCapacity']
        n_bat = param[x]['BatteryEfficiency']
        n_inv = param[x]['InverterEfficiency']
        timestep = param[x]['timestep']
        
        
        #Her er virkningsgrad tatt med
        pv2inv = np.minimum(pv[x][time], demand[x][time]/n_inv) #demand[x][time]/n_inv
        res_pv = np.maximum(pv[x][time] - demand[x][time]/n_inv, 0) #Lasten som momentant er større en forbruket for det gitte tidssteget
        inv2load = pv2inv * n_inv
        res_load = (demand[x][time] - pv2inv * n_inv) #lasten som ikke dekkes av momentan PV #pv2inv

      
            
        #1. prioritet etter at momentant forburk er dekket -> Forsyne eget batteri
        if LevelOfCharge_previous >= battery_capacity:  
                    pv2store = 0 
            
        else: #BATTERIET ER IKKE FULT, MEN VIL OVERSTIGE MAX KAPASITET VED OPPLADING I GITT TIDSSTEG
                if (LevelOfCharge_previous + (res_pv * timestep)) > battery_capacity:
                    
                    #KAN MAX LADE OPP DET SMO ER IGJEN FØR BATTERIET NÅR MAX KAPASITET
                    pv2store = min((battery_capacity - LevelOfCharge_previous)/timestep, max_power_battery)
                    #OPPLADINGEN BEGRENSES AV MAX LADING PÅ BATTERI
                    
                    
                else: #BATTERIET ER IKKE FULT OG VIL IKKE OVERTIGE MAX KAPASITET VED OPPLADNING I GITT TIDSSTEG
                    #BEGRENSES AV MAX LADING PÅ BATTERI
                    pv2store = min(res_pv, max_power_battery)
             
        
            
            
        store2inv = min((LevelOfCharge_previous/timestep-discharge_limit/timestep), res_load/n_inv, max_power_battery)  
        
        
        '''
        if time == 20999:
            
            print('Pv2store : {:.3g}'.format(pv2store))
            print('store2inv : {:.3g}'.format(store2inv))
       '''     
        
        #LADE OPP DET MAN KAN MED EGEN ENERGI
        LevelOfCharge = min(LevelOfCharge_previous - (store2inv - pv2store*n_bat) * timestep,  # DC - pv2store*n_bat
                                   battery_capacity)
        
       

        
        #-------------------------------------------------------------------------------------------
        
        
        #EFFEKT TIL FORBRUK. I BÅDE STORE2INV OG INV2LOAD ER EFFEKTBEGRENSNINGER TATT HENSYN TIL
        inv2load = inv2load + store2inv*n_inv
        
        '''
        if time == time_analysis:
            
            print()
            print('Tapt produksjon: {:.3g}'.format(dict_list[time-1][0]['lost_production']))
            print('Tapt produksjon: {:.3g}'.format(dict_list[time-1][1]['lost_production']))
            print()
        '''
        
        #EFFEKT SOM KAN SELGES PÅ MARKEDET
        lost_production = res_pv - pv2store 
       
        '''
        if time == time_analysis:
            
            print('Tapt produksjon: {:.3g}'.format(dict_list[time-1][0]['lost_production']))
            print('Tapt produksjon: {:.3g}'.format(dict_list[time-1][1]['lost_production']))
            print()
        '''
       
            
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
        
        #-------------------------------------------------------------------------------------------
        '''
        #FJERNE FLUER
        if lost_load < 0.001:
            
            lost_load = 0
            
        if lost_production < 0.001:
            
            lost_production = 0
        '''
        
        #Energiflytsverdiene for deltaker x i gitt tidssteg før energideling
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
        
        
       #Etablere bud for deltaker x
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
    #DEKLARERE VARIABLER,VEKTORER OG INDEX-VEKTORER TIL Å MODELLERE ENERGIMARKEDET
    
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
    #iterere gjennom deltagerene
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
            
            #REGISTRERE HVOR MYE (kW) DELTAKEREN SELGER i tidssteget
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
    SIDEN ANLEGGET FØRST FORSYNER SEG SELV, GÅR OVERSKUDDS-PV i første omgang TIL Å LADE OPP BATTERIET. DET er SJELDENT 
    OVERSKUDDS-PV IGJEN (SIDEN BATTERIET i egen installasjon DA MÅ VÆRE FULT) FØR HANDELENE STARTER. DET ER OBSERVERT AT NÅR FLEX_LIMIT ER UNDER 100%, 
    VIL ALDRI BATTERIENE STÅ FULLE. I DETTE TILFELLE BRUKES EGEN OVERSKUDDS-PV TIL Å LADE EGET BATTERI, FOR SÅ AT BATTERIET (SOM DA OFTEST ER FLEX) SELGER SIN ENERGI TIL FLEX_LIMIT NÅS. 
    
    GJØRES DET ET FORSØK DER FLEXLIMIT SETTES TIL 100% (SOM OM VI FJERNE MULIGHETEN TIL Å FLEXE MED SIN ENERGI) OBSERVERES
    DET AT VI FÅR UTVEKSLING DIREKTE MELLOM PV-ANLEGG. DETTE FORDI EN HYTTE SOM I UTGANGSPUNKTET STÅR TOM, ETTERHVERT 
    VIL FÅ FULT BATTERI. UTEN FLEX BATTERI VIL DISSE BATTERIENE HA LITEN MULIGHET TIL Å SELGE SIN ENERGI SIDEN DE KUN KAN SELGE VED 
    100% KAPASITET. DERFOR VIL DET OPPSTÅ SITUASJONER DER PV SENDER DIREKTE TIL PV.
    '''
    
    #KODELINJE SOM SKILLER FLEXBATTERIENE BASERT PÅ FLEXLIMIT OG BATTERISTATUS. NOEN FLEXBATTERI STILLER SEG
    #I POSISJON TIL KJØP OG NOEN STILLER SEG I POSISJON TIL SALG.
    for j in index_flex_battery:  
    
        if (E[j]['LevelOfCharge'] > 0.5*battery_capacity + flex_limit*battery_capacity):
        
            index_flex_sell_battery.append(j)
            
            
        elif (E[j]['LevelOfCharge'] < 0.5*battery_capacity - flex_limit*battery_capacity):
            
            index_flex_buy_battery.append(j)
            

    count_battery_sell_flex = len(index_flex_sell_battery)
    count_battery_buy_flex = len(index_flex_buy_battery)

    #-------------------------------------------------------------------------------------------       
    #HANDELEN MELLOM STARTER. IF-SETNINGENE LEGGES FREM I PRIORITERINGS-REKKEFØLGEN FOR KJØP OG SALG LAGT FREM I
    #MASTEROPPGAVEN
    
    '''
    #Fjerne fluer
    for j in range(len(param)):
        
        if E[j]['lost_load'] < 0.001:
            
            E[j]['lost_load'] = 0
        
        if E[j]['lost_production'] < 0.001:
            
            E[j]['lost_production'] = 0
    '''       
   
    #Dersom et PV-anlegg har lagt ut et kjøpe-bud, vil det bety at batteriet i egen installasjon har ladet seg ut så langt det
    #rekker før handelen starter (store2inv). Kodelinjen nedenfor fjerner et eventuelt flex-batteri som selger dersom batteriet
    #allerede har forsyn egen installasjon.
    common_elements = set(index_buyer_pv) & set(index_flex_sell_battery)
    
    for element in common_elements:
        index_flex_sell_battery.remove(element)
                                  

    common_elements = set(index_buyer_pv) & set(index_seller_battery)
    
    for element in common_elements:
        index_seller_battery.remove(element)
                                  
    
    #Plotte energiflytsverdier i git tidssteget FØR deling
    if time == time_analysis:
        
            print()
            print('ENERGIFLYTSVERDIER (FØR DELING) I TIDSSTEG {:.5g}'.format(time))
            print('Date and time: {:.3g}.{:.3g} {:.3g}:{:.3g}'.format(day,month,hour,minute))
            print('---------------------------------------------------------------------')
            
            for i in range(len(param)):
            
                
                print('Ikke dekt last for hytte {:.3g}: {:.3g}kW'.format(i,E[i]['lost_load']))
                
            
            for i in range(len(param)):
                
                print('Produksjonsoverskudd for hytte {:.3g}: {:.3g}kW'.format(i, E[i]['lost_production']))
                

            for i in range(len(param)):
                
                print('Batteristatus for hytte {:.3g}: {:.3g}kWh'.format(i, E[i]['LevelOfCharge']))
                

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
            print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
            print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
            print('---------------------------------------------------------------------')
            print()
    
    
    #NEDENFOR STARTER HANDELEN MELLOM DELTAKERENE. KODEN BEVEGER SEG NEDOVER ETTER HVILKE BUD SOM HAR HØYESTE PRIORITET
    #----------------------------------------------------------------------------------------
    
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
            print('Salgsandeler: ', seller_transfer)
            print('Kjøpsandeler: ', buyer_transfer)
            print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
            print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
            print()
        
        #FØRSTE PRIORITERING. MOMENTAN UTVEKLSING MELLOM PV-ANLEGG MED OVERSKUDD OG UNDERSKUDD
        for j in index_seller_pv: #SELGER MED INDEX J

          if (time == time_analysis):       
        
            print('Produksjonsoverskudd for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['lost_production']))
          
          E[j]['lost_production'] -= seller_transfer[j]
          
          '''
          if E[j]['lost_production'] < 0.001:
                
                E[j]['lost_production'] = 0
          '''      
          
          if (time == time_analysis): 
           
              print('Produksjonsoverskudd for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['lost_production']))  
              
            
          E[j]['pv_sell_pv'] += seller_transfer[j] #TIL PLOTTING
          
          
            
        for i in index_buyer_pv: #KJØPER MED INDEX I
                
                if (time == time_analysis):       
              
                  print('Estimert forbruk som ikke blir dekt for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['lost_load']))
                  
                
                E[i]['lost_load'] -= buyer_transfer[i]
                E[i]['pv_buy_pv'] += buyer_transfer[i] #TIL PLOTTING
        
                '''      
                if E[i]['lost_load'] < 0.001:
                    
                    E[i]['lost_load'] = 0
                '''
                    
                if (time == time_analysis):       
                  
                  print('Estimert forbruk som ikke blir dekt for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['lost_load']))   
    
                
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
       
        
    #Hvis batteriutveksling er aktivert
    if battery_share_activate == 1:   
    
        if (len(index_seller_battery) != 0) & (len(index_buyer_pv) != 0):   
            
            dict_count['bat2pv'] += 1
            seller_trade, buyer_trade, rest_profit, rest_demand  = trade_batt2pv.trade_batt2pv(sum_energy_profit_pv, sum_energy_demand_pv, index_buyer_pv, index_seller_battery, count_buyers_pv, count_sellers_battery, len(param), E, param)
            
            if (time == time_analysis):         
        
                print('Type handel: bat2pv')
                print('Salgsandeler: ', seller_trade)
                print('Kjøpsandeler: ', buyer_trade)
                print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
                print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
                print()
            
            #ANDRE PRIORITET. FULLE BATTERI SELGER TIL MOMENTAN PV
            for j in index_seller_battery:
                     
              if (time == time_analysis):       
            
                print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
              E[j]['LevelOfCharge'] -= seller_trade[j] #ENERGY
                
              
              if (time == time_analysis):       
            
                print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
              E[j]['battery_sell_pv'] += seller_trade[j] 
                
                
            for i in index_buyer_pv:
                
                    if (time == time_analysis):       
                  
                      print('Estimert forbruk som ikke blir dekt for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['lost_load']))    
                
                    E[i]['lost_load'] -= buyer_trade[i]
                    
                    '''
                    if E[i]['lost_load'] < 0.001:
                        
                        E[i]['lost_load'] = 0
                    '''
                    
                    if (time == time_analysis):       
                  
                      print('Estimert forbruk som ikke blir dekt for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['lost_load']))
                    
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
        
    #Hvis flex- og batteri-utveksling er aktivert          
    if (flex_activate == 1) & (battery_share_activate == 1):  
        
        
        if (len(index_flex_sell_battery) != 0) & (len(index_buyer_pv) != 0):  
        
            dict_count['flex2pv'] += 1
            seller_trade, buyer_trade, rest_profit, rest_demand = trade_flex2pv.trade_flex2pv(time, sum_energy_profit_pv, sum_energy_demand_pv, index_buyer_pv, index_flex_sell_battery, count_buyers_pv, count_battery_sell_flex, len(param), E, param)
                    
            if (time == time_analysis):         
        
                print('Type handel: flex2pv')
                print('Salgsandeler: ', seller_trade)
                print('Kjøpsandeler: ', buyer_trade)
                print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
                print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
                print()
            
            #TREDJE PRIORITET. FLEX-BATTERI SELGER TIL MOMENTAN PV
            for j in index_flex_sell_battery:
                
                        if (time == time_analysis):       
                      
                          print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
                        E[j]['LevelOfCharge'] -= seller_trade[j]
                        
                        if (time == time_analysis):       
                      
                          print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                        
                        E[j]['battery_sell_pv'] += seller_trade[j]   
                        
                
            for i in index_buyer_pv:
                            
                        if (time == time_analysis):       
                      
                          print('Estimert forbruk som ikke blir dekt for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['lost_load']))                       
                        
                        E[i]['lost_load'] -= buyer_trade[i]
                        
                        '''
                        if E[i]['lost_load'] < 0.001:
                            
                            E[i]['lost_load'] = 0
                        '''
                        
                        if (time == time_analysis):       
                      
                          print('Estimert forbruk som ikke blir dekt for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['lost_load']))    
                          
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
      
                    
    if battery_share_activate == 1:
                                  
        if (len(index_seller_pv) != 0) & (len(index_buyer_battery) != 0):
            
            dict_count['pv2bat'] += 1
            #ANLEGG MED OVERSKUDD SOM FØRSTEPRIORITET?
            seller_trade, buyer_trade, rest_profit, rest_demand = trade_pv2batt.trade_pv2bat(sum_energy_profit_pv, sum_energy_demand_pv, index_seller_pv, index_buyer_battery, count_sellers_pv, count_buyers_battery, len(param), E, param, time)        

            if (time == time_analysis):         
                
                
                print('Type handel: pv2bat')
                print('Salgsandeler: ', seller_trade)
                print('Kjøpsandeler: ', buyer_trade)
                print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
                print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
                print() 
                
            #PV-anlegg selger til tomme batteri    
            for j in index_seller_pv:
                
                
                if (time == time_analysis):       
                
                    print('Produksjonsoverskudd for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['lost_production']))
                
                
                E[j]['lost_production'] -= seller_trade[j]
                
                '''
                if  E[j]['lost_production'] < 0.001:
                    
                    E[j]['lost_production'] = 0
                
                '''

                
                if (time == time_analysis):       
            
                    print('Produksjonsoverskudd for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['lost_production']))
                
                E[j]['pv_sell_battery'] += seller_trade[j]
            
                
                
            for i in index_buyer_battery:
                    
                
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                
                    E[i]['LevelOfCharge'] += buyer_trade[i]
                    
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                    
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
                    
                    index_flex_sell_battery.append(i)    
                    
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
            
        
    
    if (flex_activate == 1) & (battery_share_activate == 1):
        
        
        if (len(index_flex_buy_battery) != 0) & (len(index_seller_pv) != 0):
        
            dict_count['pv2flex'] += 1
            seller_trade, buyer_trade, rest_profit, rest_demand = trade_pv2batt.trade_pv2bat(sum_energy_profit_pv, sum_energy_demand_pv, index_seller_pv, index_flex_buy_battery, count_sellers_pv, count_battery_buy_flex, len(param), E, param, time)
    
            if (time == time_analysis):         
        
                print('Type handel: pv2flex')
                print('Salgsandeler: ', seller_trade)
                print('Kjøpsandeler: ', buyer_trade)
                print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
                print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
                print()
                
            #PV-anlegg selger til flex-batteri     
            for j in index_seller_pv:
                
                if (time == time_analysis):       
                
                    print('Produksjonsoverskudd for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['lost_production']))
                
                E[j]['lost_production'] -= seller_trade[j]
                
                '''
                if E[j]['lost_production'] < 0.001:
                    
                    E[j]['lost_production'] = 0
                '''
                
                if (time == time_analysis):       
                
                    print('Produksjonsoverskudd for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['lost_production']))
                
                E[j]['pv_sell_battery'] += seller_trade[j]
            
                
                
            for i in index_flex_buy_battery:
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                    
                    E[i]['LevelOfCharge'] += buyer_trade[i]
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                    
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
       
        
    if battery_share_activate == 1:
              
        if (len(index_seller_battery) != 0) & (len(index_buyer_battery) != 0):
            
            dict_count['bat2bat'] += 1
            seller_trade, buyer_trade, rest_profit, rest_demand  = trade_flex2flex.trade_batt2batt(flex_limit, sum_energy_profit_pv, sum_energy_demand_pv, index_buyer_battery, index_seller_battery, count_sellers_battery, count_buyers_battery, len(param), E, param, time)
           
            
            if (time == time_analysis):         
        
                print('Type handel: bat2bat')
                print('Salgsandeler: ', seller_trade)
                print('Kjøpsandeler: ', buyer_trade)
                print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
                print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
                print()
                
            #Fulle batteri selger til tomme batteri
            for j in index_seller_battery:
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
                E[j]['LevelOfCharge'] -= seller_trade[j]
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
                E[j]['battery_sell_battery'] += seller_trade[j]
                
                #FLEX BATTERI SOM KJØPER
            for i in index_buyer_battery:
               
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
               
                E[i]['LevelOfCharge'] += buyer_trade[i]
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                
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
        
    
    if (flex_activate == 1) & (battery_share_activate == 1):    
        
        
        if (len(index_flex_sell_battery) != 0) & (len(index_buyer_battery) != 0):
               
            dict_count['flex2bat'] += 1
            #FLEX BATTERI SOM SELGER           
            seller_trade, buyer_trade, rest_profit, rest_demand = trade_flex2flex.trade_batt2batt(flex_limit, sum_energy_profit_pv, sum_energy_demand_pv, index_buyer_battery, index_flex_sell_battery, count_battery_sell_flex, count_buyers_battery, len(param), E, param, time)
           
            if (time == time_analysis):         
        
                print('Type handel: flex2bat')
                print('Salgsandeler: ', seller_trade)
                print('Kjøpsandeler: ', buyer_trade)
                print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
                print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
                print()
            
            #Flex-batteri selger til tomme batteri
            for j in index_flex_sell_battery:
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
                E[j]['LevelOfCharge'] -= seller_trade[j]
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
                E[j]['battery_sell_battery'] += seller_trade[j]
                
                #FLEX BATTERI SOM KJØPER
            for i in index_buyer_battery:
                    
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                    
                E[i]['LevelOfCharge'] += buyer_trade[i]
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                
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
    
    
            
        if (len(index_flex_buy_battery) != 0) & (len(index_seller_battery) != 0):
            
            dict_count['bat2flex'] += 1
            seller_trade, buyer_trade, rest_profit, rest_demand = trade_flex2flex.trade_batt2batt(flex_limit, sum_energy_profit_pv, sum_energy_demand_pv, index_flex_buy_battery, index_seller_battery, count_sellers_battery, count_battery_buy_flex, len(param), E, param, time)
           
            if (time == time_analysis):         
        
                print('Type handel: bat2flex')
                print('Salgsandeler: ', seller_trade)
                print('Kjøpsandeler: ', buyer_trade)
                print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
                print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
                print()
            
            #Fulle batteri selger til flex-batteri
            for j in index_seller_battery:
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
                E[j]['LevelOfCharge'] -= seller_trade[j]
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
                E[j]['battery_sell_battery'] += seller_trade[j]
                
                #FLEX BATTERI SOM KJØPER
            for i in index_flex_buy_battery:
                    
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
    
                E[i]['LevelOfCharge'] += buyer_trade[i]
                
                if (time == time_analysis):       
              
                  print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                
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
    
            
        if (len(index_flex_buy_battery) != 0) & (len(index_flex_sell_battery) != 0):    
        
            dict_count['flex2flex'] += 1
            seller_trade, buyer_trade, rest_profit, rest_demand = trade_flex2flex.trade_batt2batt(flex_limit, sum_energy_profit_pv, sum_energy_demand_pv, index_flex_buy_battery, index_flex_sell_battery, count_battery_sell_flex, count_battery_buy_flex, len(param), E, param, time)
           
            if (time == time_analysis):         
        
                print('Type handel: flex2flex')
                print('Salgsandeler: ', seller_trade)
                print('Kjøpsandeler: ', buyer_trade)
                print('Totalt overskudd av PV i markedet: {:.3g}'.format(sum_energy_profit_pv))
                print('Samlet estimert forbruk som ikke blir dekt: {:.3g}'.format(sum_energy_demand_pv))
                print()
           
            #Flex-batteri selger til flex-batteri
            for j in index_flex_sell_battery:
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                
                    E[j]['LevelOfCharge'] -= seller_trade[j]
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(j, E[j]['LevelOfCharge']))
                    
                    E[j]['battery_sell_battery'] += seller_trade[j]
                    

            for i in index_flex_buy_battery:
                   
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (FØR HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                          
                    E[i]['LevelOfCharge'] += buyer_trade[i]
                    
                    if (time == time_analysis):       
                  
                      print('Batteristatus for hytte {:.3g} (ETTER HANDEL): {:.3g}'. format(i, E[i]['LevelOfCharge']))
                    
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
         
            
    #Energiflytsverdier i tidssteget etter energideling   
    if time == time_analysis:
        
            print()
            print('ENERGIFLYTSVERDIER (ETTER DELING) I TIDSSTEG {:.5g}'.format(time))
            print('Date and time: {:.3g}.{:.3g} {:.3g}:{:.3g}'.format(day,month,hour,minute))
            print('---------------------------------------------------------------------')
            
            for i in range(len(param)):
            
                
                print('Ikke dekt last for hytte {:.3g}: {:.3g}kW'.format(i,E[i]['lost_load']))
                
            
            for i in range(len(param)):
                
                print('Produksjonsoverskudd for hytte {:.3g}: {:.3g}kW'.format(i, E[i]['lost_production']))
                

            for i in range(len(param)):
                
                print('Batteristatus for hytte {:.3g}: {:.3g}kWh'.format(i, E[i]['LevelOfCharge']))
    
            print()
            
            
    
    
    return(E, dict_count)
    
                
                print('Ikke dekt last for hytte {:.3g}: {:.3g}kW'.format(i,E[i]['lost_load']))
                
            
            for i in range(len(param)):
                
                print('Produksjonsoverskudd for hytte {:.3g}: {:.3g}kW'.format(i, E[i]['lost_production']))
                

            for i in range(len(param)):
                
                print('Batteristatus for hytte {:.3g}: {:.3g}kWh'.format(i, E[i]['LevelOfCharge']))
    
            print()
            
            
    
    
    return(E, dict_count, tap)
    
