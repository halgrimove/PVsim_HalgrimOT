# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 13:34:48 2023

@author: halgr
"""

import pandas as pd



#-------------------------------------------------------------------------------------


timestep = .0167 #et minutt; 1,67 prosent av en time

demand1_W = pd.read_csv('C:/Users\halgr/OneDrive - NTNU/Masteroppgave/Python/Modellering_PvOffgrid/offgrid_PVsyst/input_files/demand_1.csv', index_col=0, squeeze=True)

demand1_kW = demand1_W/1000

energiforbruk_1 = sum(demand1_kW)*timestep
max_effekt_1 = max(demand1_kW)


#-------------------------------------------------------------------------------------


demand2_W = pd.read_csv('C:/Users\halgr/OneDrive - NTNU/Masteroppgave/Python/Modellering_PvOffgrid/offgrid_PVsyst/input_files/demand_2.csv', index_col=0, squeeze=True)

demand2_kW = demand2_W/1000

energiforbruk_2 = sum(demand2_kW)*timestep
max_effekt_2 = max(demand2_kW)


#-------------------------------------------------------------------------------------


demand3_W = pd.read_csv('C:/Users\halgr/OneDrive - NTNU/Masteroppgave/Python/Modellering_PvOffgrid/offgrid_PVsyst/input_files/demand_3.csv', index_col=0, squeeze=True)

demand3_kW = demand3_W/1000

energiforbruk_3 = sum(demand3_kW)*timestep
max_effekt_3 = max(demand3_kW)


#-------------------------------------------------------------------------------------


demand4_W = pd.read_csv('C:/Users\halgr/OneDrive - NTNU/Masteroppgave/Python/Modellering_PvOffgrid/offgrid_PVsyst/input_files/demand_4.csv', index_col=0, squeeze=True)

demand4_kW = demand4_W/1000

energiforbruk_4 = sum(demand4_kW)*timestep
max_effekt_4 = max(demand4_kW)


#-------------------------------------------------------------------------------------


print()
print('Hyttekategori 1:')
print('Energiforbruk: {:.3g} kWh'.format(energiforbruk_1))        
print('Effekttopp: {:.3g} kW'.format(max_effekt_1))

print()
print('Hyttekategori 2:')
print('Energiforbruk: {:.3g} kWh'.format(energiforbruk_2))        
print('Effekttopp: {:.3g} kW'.format(max_effekt_2))

print()
print('Hyttekategori 3:')
print('Energiforbruk: {:.3g} kWh'.format(energiforbruk_3))        
print('Effekttopp: {:.3g} kW'.format(max_effekt_3))

print()
print('Hyttekategori 4:')
print('Energiforbruk: {:.3g} kWh'.format(energiforbruk_4))        
print('Effekttopp: {:.3g} kW'.format(max_effekt_4))



