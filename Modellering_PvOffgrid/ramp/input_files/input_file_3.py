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


#----------------------------------------------------------------------------

#Oppvarming
N2_Oppvarming_panelovn_700W = Oppvarming.Appliance(Oppvarming,3,700,2,360,0.2,60,'yes',3)
N2_Oppvarming_panelovn_700W.windows([0,480],[1200,1440])
N2_Oppvarming_panelovn_700W.specific_cycle_1(700,60,0,60)
N2_Oppvarming_panelovn_700W.specific_cycle_2(700,60,0,60)
N2_Oppvarming_panelovn_700W.specific_cycle_3(700,60,0,60)
N2_Oppvarming_panelovn_700W.cycle_behaviour([0,120],[120,240],[240,360],[360,480],[1200,1320],[1320,1440])


N2_Oppvarming_panelovn_400W = Oppvarming.Appliance(Oppvarming,1,400,2,210,0.2,30,'yes',2)
N2_Oppvarming_panelovn_400W.windows([480,640],[1140,1320])
N2_Oppvarming_panelovn_400W.specific_cycle_1(400,30,0,30)
N2_Oppvarming_panelovn_400W.specific_cycle_2(400,90,0,90)
N2_Oppvarming_panelovn_400W.cycle_behaviour([480,560],[560,640],[1140,1230],[1230,1320])



#----------------------------------------------------------------------------

#Lys
N2_Lys_taklampe_40W = Lys.Appliance(Lys,1,40,2,270,0.2,60,'no',3)
N2_Lys_taklampe_28W = Lys.Appliance(Lys,6,28,2,270,0.2,60,'no',3)
N2_Lys_vegglampe_4W = Lys.Appliance(Lys,6,3.6,2,270,0.2,60,'no',3)

N2_Lys_taklampe_40W.windows([390,660],[1080,1350]) #12 timer vindu
N2_Lys_taklampe_40W.specific_cycle_1(40,45,0,45)
N2_Lys_taklampe_40W.specific_cycle_2(40,45,0,45)
N2_Lys_taklampe_40W.specific_cycle_3(40,45,0,45)
N2_Lys_taklampe_40W.cycle_behaviour([390,480],[480,570],[570,660],[1080,1170],[1170,1260],[1260,1350])

N2_Lys_taklampe_28W.windows([390,660],[1080,1350]) #12 timer vindu
N2_Lys_taklampe_28W.specific_cycle_1(28,45,0,45)
N2_Lys_taklampe_28W.specific_cycle_2(28,45,0,45)
N2_Lys_taklampe_28W.specific_cycle_3(28,45,0,45)
N2_Lys_taklampe_28W.cycle_behaviour([390,480],[480,570],[570,660],[1080,1170],[1170,1260],[1260,1350])

N2_Lys_vegglampe_4W.windows([390,660],[1080,1350]) #12 timer vindu
N2_Lys_vegglampe_4W.specific_cycle_1(4,45,0,45)
N2_Lys_vegglampe_4W.specific_cycle_2(4,45,0,45)
N2_Lys_vegglampe_4W.specific_cycle_3(4,45,0,45)
N2_Lys_vegglampe_4W.cycle_behaviour([390,480],[480,570],[570,660],[1080,1170],[1170,1260],[1260,1350])


#----------------------------------------------------------------------------

#Ovn
N2_Vannpumpe_800W = Vannpumpe.Appliance(Vannpumpe,1,800,3,120,0.2,40)
N2_Vannpumpe_800W.windows([540,600],[720,780],0.35,[1020,1080])


#----------------------------------------------------------------------------

#Mobillading
N2_Lader_3 = Stikk.Appliance(Stikk,3,20,1,39,0.2,39)
N2_Lader_3.windows([510,600],[0,0],0.35)


#----------------------------------------------------------------------------

#Kaffe
N1_Kaffe_1080 = Stikk.Appliance(Stikk,1,1080,1,6,0.2,6)
N1_Kaffe_1080.windows([450,480],[0,0],0.35) #07:30-08:00


#----------------------------------------------------------------------------

#TV
N2_TV_29W = Stikk.Appliance(Stikk,1,29,2,90,0.2,30)
N2_TV_29W.windows([510,540],[1200,1260],0.35)


#----------------------------------------------------------------------------

#Ovn
N1_Komfyr_30min = Stikk.Appliance(Stikk,1,1800,1,30,0.2,30)
N1_Komfyr_30min.windows([1020,1140],[0,0],0.35)


#----------------------------------------------------------------------------

#Platetopp
N1_Platetopp_15min = Stikk.Appliance(Stikk,1,2900,1,15,0.2,15)
N1_Platetopp_15min.windows([1020,1140],[0,0],0.35)#17:00-19:00


#----------------------------------------------------------------------------

#Varmtvann
N2_Varmtvann_172min = Varmtvann.Appliance(Varmtvann,1,2000,3,172,0.5,30)
N2_Varmtvann_172min.windows([540,600],[900,1000],0.35,[1140,1250])

#---------------------------------------------------------------------------

#Kjøleskap
N1_Kjøleskap_30W = Stikk.Appliance(Stikk,1,30.3,1,720,0.2,15,'yes',3)
N1_Kjøleskap_30W.windows([0,1440],[0,0])
N1_Kjøleskap_30W.specific_cycle_1(30,120,0,120)
N1_Kjøleskap_30W.specific_cycle_2(30,120,0,120)
N1_Kjøleskap_30W.specific_cycle_3(30,120,0,120)
N1_Kjøleskap_30W.cycle_behaviour([0,240],[240,480],[480,720],[720,960],[960,1200],[1200,1440])













