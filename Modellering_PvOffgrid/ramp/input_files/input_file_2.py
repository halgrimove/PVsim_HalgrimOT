# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 13:42:46 2022

@author: halgr
"""

from ramp.core.core import User, np
User_list = []

'''
This example input file represents an whole village-scale community,
adapted from the data used for the Journal publication. It should provide a 
complete guidance to most of the possibilities ensured by RAMP for inputs definition,
including specific modular duty cycles and cooking cycles. 
For examples related to "thermal loads", see the "input_file_2".
'''

#Create new user classes
Oppvarming = User("Oppvarming",1)
User_list.append(Oppvarming)

Lys = User("Lys",1)
User_list.append(Lys)

Varmtvann = User("Varmtvann",1)
User_list.append(Varmtvann)

Vannpumpe = User("Vannpumpe",1)
User_list.append(Vannpumpe)

Stikk = User("Stikk",1)
User_list.append(Stikk)

#KATEGORI 2 HYTTA

#----------------------------------------------------------------------

#Oppvarming
N1_Oppvarming_panelovn_400W = Oppvarming.Appliance(Oppvarming,2,400,2,360,0.2,30,3)

N1_Oppvarming_panelovn_400W.windows([0,480],[1200,1440])
N1_Oppvarming_panelovn_400W.specific_cycle_1(400,60,0,60)
N1_Oppvarming_panelovn_400W.specific_cycle_2(400,60,0,60)
N1_Oppvarming_panelovn_400W.specific_cycle_3(400,60,0,60)
N1_Oppvarming_panelovn_400W.cycle_behaviour([0,120],[120,240],[240,360],[360,480],[1200,1320],[1320,1440])

#---------------------------------------------------------------------

#Lys
N1_Lys_taklampe_4W = Lys.Appliance(Lys,4,4,2,270,0.2,60,'no',3)
N1_Lys_vegglampe_4W = Lys.Appliance(Lys,4,3.6,2,270,0.2,60,'no',3)

N1_Lys_taklampe_4W.windows([390,660],[1080,1350]) #12 timer vindu
N1_Lys_taklampe_4W.specific_cycle_1(4,45,0,45)
N1_Lys_taklampe_4W.specific_cycle_2(4,45,0,45)
N1_Lys_taklampe_4W.specific_cycle_3(4,45,0,45)
N1_Lys_taklampe_4W.cycle_behaviour([390,480],[480,570],[570,660],[1080,1170],[1170,1260],[1260,1350])

N1_Lys_vegglampe_4W.windows([390,660],[1080,1350]) #12 timer vindu
N1_Lys_vegglampe_4W.specific_cycle_1(3.6,45,0,45)
N1_Lys_vegglampe_4W.specific_cycle_2(3.6,45,0,45)
N1_Lys_vegglampe_4W.specific_cycle_3(3.6,45,0,45)
N1_Lys_vegglampe_4W.cycle_behaviour([390,480],[480,570],[570,660],[1080,1170],[1170,1260],[1260,1350])

#------------------------------------------------------------------------

#Vannpumpe
N1_Vannpumpe_115W = Vannpumpe.Appliance(Vannpumpe,1,115,3,120,0.2,40)
N1_Vannpumpe_115W.windows([540,600],[720,780],0.35,[1020,1080])

#------------------------------------------------------------------------

#Varmtvann
N1_Varmtvann_43min = Varmtvann.Appliance(Varmtvann,1,2000,3,43,0.5,10)
N1_Varmtvann_43min.windows([540,600],[900,980],0.35,[1140,1200])

#------------------------------------------------------------------------

#TV
N1_TV_17W = Stikk.Appliance(Stikk,1,17,2,60,0.2,30)
N1_TV_17W.windows([510,540],[1200,1260],0.35)

#---------------------------------------------------------------------------

#Mobillading
N2_Lader_3 = Stikk.Appliance(Stikk,3,20,1,39,0.2,39)
N2_Lader_3.windows([510,600],[0,0],0.35)

#---------------------------------------------------------------------------

#Kjøleskap
N1_Kjøleskap_30W = Stikk.Appliance(Stikk,1,30.3,1,720,0.2,15,'yes',3)
N1_Kjøleskap_30W.windows([0,1440],[0,0])
N1_Kjøleskap_30W.specific_cycle_1(30,120,0,120)
N1_Kjøleskap_30W.specific_cycle_2(30,120,0,120)
N1_Kjøleskap_30W.specific_cycle_3(30,120,0,120)
N1_Kjøleskap_30W.cycle_behaviour([0,240],[240,480],[480,720],[720,960],[960,1200],[1200,1440])

#----------------------------------------------------------------------------

#Ovn
N1_Komfyr_30min = Stikk.Appliance(Stikk,1,1800,1,30,0.2,30)
N1_Komfyr_30min.windows([1020,1140],[0,0],0.35)



