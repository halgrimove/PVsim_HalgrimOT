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

#Lys
N3_Lys_taklampe_40W = Lys.Appliance(Lys,2,40,2,360,0.2,60,'no',3)
N3_Lys_taklampe_28W = Lys.Appliance(Lys,6,28,2,360,0.2,60,'no',3)
N3_Lys_vegglampe_4W = Lys.Appliance(Lys,6,3.6,2,360,0.2,60,'no',3)
N3_Lys_utelys_15W = Lys.Appliance(Lys,4,15,2,840,0,480,'yes')

N3_Lys_taklampe_40W.windows([360,720],[1020,1380]) #12 timer vindu
N3_Lys_taklampe_40W.specific_cycle_1(40,60,0,60)
N3_Lys_taklampe_40W.specific_cycle_2(40,60,0,60)
N3_Lys_taklampe_40W.specific_cycle_3(40,60,0,60)
N3_Lys_taklampe_40W.cycle_behaviour([360,480],[480,600],[600,720],[1020,1140],[1140,1260],[1260,1380])

N3_Lys_taklampe_28W.windows([360,720],[1020,1380]) #12 timer vindu
N3_Lys_taklampe_28W.specific_cycle_1(28,60,0,60)
N3_Lys_taklampe_28W.specific_cycle_2(28,60,0,60)
N3_Lys_taklampe_28W.specific_cycle_3(28,60,0,60)
N3_Lys_taklampe_28W.cycle_behaviour([360,480],[480,600],[600,720],[1020,1140],[1140,1260],[1260,1380])

N3_Lys_vegglampe_4W.windows([360,720],[1020,1380]) #12 timer vindu
N3_Lys_vegglampe_4W.specific_cycle_1(4,60,0,60)
N3_Lys_vegglampe_4W.specific_cycle_2(4,60,0,60)
N3_Lys_vegglampe_4W.specific_cycle_3(4,60,0,60)
N3_Lys_vegglampe_4W.cycle_behaviour([360,480],[480,600],[600,720],[1020,1140],[1140,1260],[1260,1380])

N3_Lys_utelys_15W.windows([0,480],[1080,1440]) #18:00-08:00, 4 utelys på


#----------------------------------------------------------------------------

#Oppvarming
N3_Oppvarming_panelovn_700W = Oppvarming.Appliance(Oppvarming,4,700,2,360,0.2,60,'yes',3)
N3_Oppvarming_panelovn_700W.windows([0,480],[1200,1440])

N3_Oppvarming_panelovn_700W.specific_cycle_1(700,60,0,60)
N3_Oppvarming_panelovn_700W.specific_cycle_2(700,60,0,60)
N3_Oppvarming_panelovn_700W.specific_cycle_3(700,60,0,60)
N3_Oppvarming_panelovn_700W.cycle_behaviour([0,120],[120,240],[240,360],[360,480],[1200,1320],[1320,1440])

N3_Oppvarming_panelovn_400W = Oppvarming.Appliance(Oppvarming,1,400,2,210,0.2,30,'yes',2)
N3_Oppvarming_panelovn_400W.windows([480,640],[1140,1320])
N3_Oppvarming_panelovn_400W.specific_cycle_1(400,30,0,30) #litt for mye
N3_Oppvarming_panelovn_400W.specific_cycle_2(400,90,0,90)
N3_Oppvarming_panelovn_400W.cycle_behaviour([480,560],[560,640],[1140,1230],[1230,1320])

N3_Oppvarming_gulvvarme_1500W = Oppvarming.Appliance(Oppvarming,1,1500,1,720,0.2,120,'yes',3)
N3_Oppvarming_gulvvarme_1500W.windows([0,1440],[0,0])
#MÅ INKLUDERE [0,0] VEKTOR OM DET BARE TAS MED ET STORT VINDU
N3_Oppvarming_gulvvarme_1500W.specific_cycle_1(1500,120,0,120)
N3_Oppvarming_gulvvarme_1500W.specific_cycle_2(1500,120,0,120)
N3_Oppvarming_gulvvarme_1500W.specific_cycle_3(1500,120,0,120)
N3_Oppvarming_gulvvarme_1500W.cycle_behaviour([0,240],[240,480],[480,720],[720,960],[960,1200],[1200,1440])


#----------------------------------------------------------------------------

#Varmtvann
N2_Varmtvann_172min = Varmtvann.Appliance(Varmtvann,1,2000,3,172,0.5,30)
N2_Varmtvann_172min.windows([540,600],[900,1000],0.35,[1140,1250])

#----------------------------------------------------------------------------

#Vannpumpe
N3_Vannpumpe_800W = Vannpumpe.Appliance(Vannpumpe,1,800,3,240,0.2,40)
N3_Vannpumpe_800W.windows([540,600],[720,780],0.35,[1020,1080]) 

#----------------------------------------------------------------------------

#TV
N3_TV_93W = Stikk.Appliance(Stikk,1,93,2,120,0.2,60)
N3_TV_93W.windows([480,540],[1200,1320],0.35)#08:00-09:00,20:00-22:00

#----------------------------------------------------------------------------

#Mobillading
N3_Lader_4 = Stikk.Appliance(Stikk,4,20,1,39,0.2,39)
N3_Lader_4.windows([510,600],[0,0],0.35) 

#---------------------------------------------------------------------------

#Kjøleskap
N2_Kjøleskap_37W = Stikk.Appliance(Stikk,1,30.3,1,720,0.2,15,'yes',3)
N2_Kjøleskap_37W.windows([0,1440],[0,0])
N2_Kjøleskap_37W.specific_cycle_1(30,120,0,120)
N2_Kjøleskap_37W.specific_cycle_2(30,120,0,120)
N2_Kjøleskap_37W.specific_cycle_3(30,120,0,120)
N2_Kjøleskap_37W.cycle_behaviour([0,240],[240,480],[480,720],[720,960],[960,1200],[1200,1440])

#----------------------------------------------------------------------------

#Ovn
N2_Komfyr_45min = Stikk.Appliance(Stikk,1,1800,1,45,0.2,30)
N2_Komfyr_45min.windows([1020,1140],[0,0],0.35)

#----------------------------------------------------------------------------

#Platetopp
N2_Platetopp_45min = Stikk.Appliance(Stikk,1,2900,1,40,0.2,20)
N2_Platetopp_45min.windows([1020,1140],[0,0],0.35)

#----------------------------------------------------------------------------

#Kaffe
N2_Kaffe_1080 = Stikk.Appliance(Stikk,1,1080,1,12,0.2,12)
N2_Kaffe_1080.windows([450,480],[0,0],0.35)


