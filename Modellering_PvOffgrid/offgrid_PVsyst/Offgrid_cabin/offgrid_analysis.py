"""
Created on Mon Feb  6 13:07:10 2023

@author: halgr
"""

#-------------------------------------------------------------------------------------------

'''
DENNE FUNKSJONEN PRINTER UT TALL-ANALYSER FOR HELE SIMULERINGEN
'''

#-------------------------------------------------------------------------------------------

def print_analysis(E, demand, pv, param):
    
    
    #-------------------------------------------------------------------------------------------
    
    
    timestep = param['timestep']
    
    #GJØRE OM EFFEKTVERDIENE I "E" OM TIL ENERGIVERDIER OG SUMMERE ALLE VERIDIENE 
    #ENERGIFLYT MELLOM KOMPONENTER GJENNOM HELE SIMULERINGEN
    sum_demand = sum(demand) * timestep 
    sum_pv = sum(pv) * timestep
    sum_inv2load = sum(E['inv2load'])*timestep
    sum_pv2store = sum(E['pv2store'])*timestep
    sum_pv2inv = sum(E['pv2inv'])*timestep
    sum_store2inv = sum(E['store2inv'])*timestep
    sum_lost_load = sum(E['lost_load'])*timestep
    sum_lost_production = sum(E['lost_production'])*timestep
    
    #TAP     
    tap_batteri = sum_pv2store - sum_store2inv
    tap_inverter = sum_store2inv + sum_pv2inv - sum_inv2load

    #PRODUKSJON = FORBRUK
    energy_balance = sum_pv - (sum_lost_production + tap_batteri + tap_inverter + sum_inv2load) 

    #FJERNE "FLUER"
    if energy_balance < 1:
        energy_balance = 0
        
        
    #-------------------------------------------------------------------------------------------

    print()
    print('---------------------------------------------------------------')
    print ('Estimert årlig forbruk: {:.3g} kWh'.format(sum_demand))     
    print ('Energi ut av inverter: {:.3g} kWh'.format(sum_inv2load)) 
    print ('Forbruk anlegget ikke klarer å dekke: {:.3g} kWh'.format(sum_lost_load))
    print('---------------------------------------------------------------')    
    print ('Potensiell produksjon fra PV: {:.3g} kWh'.format(sum_pv)) 
    print ('Produksjon som går til spille: {:.3g} kWh'.format(sum_lost_production)) 
    print ('Tap i batteri: {:.3g} kWh'.format(tap_batteri))
    print ('Tap i inverter: {:.3g} kWh'.format(tap_inverter)) 
    print('---------------------------------------------------------------')
    print ('Energibalanse (skal bli null): {:.3g} kWh'.format(energy_balance)) 
    print()
    
    #-------------------------------------------------------------------------------------------

    return