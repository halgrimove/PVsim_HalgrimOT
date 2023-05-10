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


#Create new appliances


#Oppvarming
#Legge til duty cycle



#---------------------------------------------------------------------------


#NIVÅ1
#OVN PÅ SOVEROM
N1_Oppvarming_panelovn_400W = Oppvarming.Appliance(Oppvarming,2,1440,2,360,0.2,30, 'yes',3)
#Under klassen oppvarming, 2 stk, 1440W, 2 vindu, 360 minutter brukstid, 20% tilfeldighet på brukstid, 
#Er på iminst 30 minutter, 'yes'->Alle ovnene er på på likt, 3 duty cycle modelleres

N1_Oppvarming_panelovn_400W.windows([0,480],[1200,1440])
#De to vinduene er fra 00:00-08:00 og 20:00-00:00 -> Totalt 12 timer med vindu
N1_Oppvarming_panelovn_400W.specific_cycle_1(400,60,0,60)
N1_Oppvarming_panelovn_400W.specific_cycle_2(400,60,0,60)
N1_Oppvarming_panelovn_400W.specific_cycle_3(400,60,0,60)
#Tre like vinduer med 400W i 1 time, 0W av i neste timen -> Et vindu varer i 2 timer -> Totalt 6 timer med alle 3 vindu
N1_Oppvarming_panelovn_400W.cycle_behaviour([0,120],[120,240],[240,360],[360,480],[1200,1320],[1320,1440])
#Hvert vindu skjer 2 ganger -> Totalt 6 vindu -> Totalt 12 timer -> totalt 6 timer på
#Et vindu kan kun repeteres to ganger i løpet av et døgn


#NIVÅ2
#OVN PÅ SOVEROM
N2_Oppvarming_panelovn_700W = Oppvarming.Appliance(Oppvarming,3,700,2,360,0.2,60,'yes',3)
N2_Oppvarming_panelovn_700W.windows([0,480],[1200,1440])
#Totalt vindu stemmer med duty cycle
#Tre vinduer på 2 timer med 1 time på/av -> 6 timer på
N2_Oppvarming_panelovn_700W.specific_cycle_1(700,60,0,60)
N2_Oppvarming_panelovn_700W.specific_cycle_2(700,60,0,60)
N2_Oppvarming_panelovn_700W.specific_cycle_3(700,60,0,60)
N2_Oppvarming_panelovn_700W.cycle_behaviour([0,120],[120,240],[240,360],[360,480],[1200,1320],[1320,1440])


#OVN I STUE/KJØKKEN
N2_Oppvarming_panelovn_400W = Oppvarming.Appliance(Oppvarming,1,400,2,210,0.2,30,'yes',2)
N2_Oppvarming_panelovn_400W.windows([480,640],[1140,1320])
#08:00-10:00 og 19:00-22:00 vindu
#Totalt vindu stemmer med duty cycle
#Tre vinduer på 2 timer med 1 time på/av -> 6 timer på
N2_Oppvarming_panelovn_400W.specific_cycle_1(400,30,0,30)
N2_Oppvarming_panelovn_400W.specific_cycle_2(400,90,0,90)
N2_Oppvarming_panelovn_400W.cycle_behaviour([480,560],[560,640],[1140,1230],[1230,1320])
#HVER CYCLE KAN ASSOSIERES MED TO VINDU


#NIVÅ3
N3_Oppvarming_panelovn_700W = Oppvarming.Appliance(Oppvarming,4,700,2,360,0.2,60,'yes',3)
N3_Oppvarming_panelovn_700W.windows([0,480],[1200,1440])
#Totalt vindu stemmer med duty cycle
#Tre vinduer på 2 timer med 1 time på/av -> 6 timer på
N3_Oppvarming_panelovn_700W.specific_cycle_1(700,60,0,60)
N3_Oppvarming_panelovn_700W.specific_cycle_2(700,60,0,60)
N3_Oppvarming_panelovn_700W.specific_cycle_3(700,60,0,60)
N3_Oppvarming_panelovn_700W.cycle_behaviour([0,120],[120,240],[240,360],[360,480],[1200,1320],[1320,1440])


N3_Oppvarming_panelovn_400W = Oppvarming.Appliance(Oppvarming,1,400,2,210,0.2,30,'yes',2)
N3_Oppvarming_panelovn_400W.windows([480,640],[1140,1320])
#08:00-10:00 og 19:00-22:00 vindu
#Totalt vindu stemmer med duty cycle
#Tre vinduer på 2 timer med 1 time på/av -> 6 timer på
N3_Oppvarming_panelovn_400W.specific_cycle_1(400,30,0,30)
N3_Oppvarming_panelovn_400W.specific_cycle_2(400,90,0,90)
N3_Oppvarming_panelovn_400W.cycle_behaviour([480,560],[560,640],[1140,1230],[1230,1320])


#Gulvvarme
N3_Oppvarming_gulvvarme_1500W = Oppvarming.Appliance(Oppvarming,1,1500,1,720,0.2,120,'yes',3)
N3_Oppvarming_gulvvarme_1500W.windows([0,1440],[0,0])
#MÅ INKLUDERE [0,0] VEKTOR OM DET BARE TAS MED ET STORT VINDU
N3_Oppvarming_gulvvarme_1500W.specific_cycle_1(1500,120,0,120)
N3_Oppvarming_gulvvarme_1500W.specific_cycle_2(1500,120,0,120)
N3_Oppvarming_gulvvarme_1500W.specific_cycle_3(1500,120,0,120)
N3_Oppvarming_gulvvarme_1500W.cycle_behaviour([0,240],[240,480],[480,720],[720,960],[960,1200],[1200,1440])



#---------------------------------------------------------------------------

#Lys
N1_Lys_taklampe_4W = Lys.Appliance(Lys,4,4,2,270,0.2,60,'no',3)
#270 -> 4,5 timer med lys
N1_Lys_vegglampe_4W = Lys.Appliance(Lys,4,3.6,2,270,0.2,60,'no',3)
#6 timer med lys

N1_Lys_taklampe_4W.windows([390,660],[1080,1350]) #12 timer vindu
N1_Lys_taklampe_4W.specific_cycle_1(4,45,0,45)
N1_Lys_taklampe_4W.specific_cycle_2(4,45,0,45)
N1_Lys_taklampe_4W.specific_cycle_3(4,45,0,45)
#Tre vindu på 1,5 time
N1_Lys_taklampe_4W.cycle_behaviour([390,480],[480,570],[570,660],[1080,1170],[1170,1260],[1260,1350])
#6:30-11:00, 18:00-22:30 vindu

N1_Lys_vegglampe_4W.windows([390,660],[1080,1350]) #12 timer vindu
N1_Lys_vegglampe_4W.specific_cycle_1(3.6,45,0,45)
N1_Lys_vegglampe_4W.specific_cycle_2(3.6,45,0,45)
N1_Lys_vegglampe_4W.specific_cycle_3(3.6,45,0,45)
#Tre vindu på 1,5 time
N1_Lys_vegglampe_4W.cycle_behaviour([390,480],[480,570],[570,660],[1080,1170],[1170,1260],[1260,1350])
#6:30-11:00, 18:00-22:30 vindu

#-----------------------------------------------------------------

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

#------------------------------------------------------------------

N3_Lys_taklampe_40W = Lys.Appliance(Lys,2,40,2,360,0.2,60,'no',3)
N3_Lys_taklampe_28W = Lys.Appliance(Lys,6,28,2,360,0.2,60,'no',3)
N3_Lys_vegglampe_4W = Lys.Appliance(Lys,6,3.6,2,360,0.2,60,'no',3)
N3_Lys_utelys_15W = Lys.Appliance(Lys,4,15,2,840,0,480,'yes')

N3_Lys_taklampe_40W.windows([360,720],[1020,1380]) #12 timer vindu
N3_Lys_taklampe_40W.specific_cycle_1(40,60,0,60)
N3_Lys_taklampe_40W.specific_cycle_2(40,60,0,60)
N3_Lys_taklampe_40W.specific_cycle_3(40,60,0,60)
N3_Lys_taklampe_40W.cycle_behaviour([360,480],[480,600],[600,720],[1020,1140],[1140,1260],[1260,1380])
#06:00-12:00, 17:00-23:00

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


#---------------------------------------------------------------------------

#Varmtvann
N1_Varmtvann_43min = Varmtvann.Appliance(Varmtvann,1,2000,3,43,0.5,10
N1_Varmtvann_43min.windows([540,600],[900,980],0.35,[1140,1200])
                                             
N2_Varmtvann_172min = Varmtvann.Appliance(Varmtvann,1,2000,3,172,0.5,30)
N2_Varmtvann_172min.windows([540,600],[900,1000],0.35,[1140,1250])


#---------------------------------------------------------------------------

#Vannpumpe
N1_Vannpumpe_115W = Vannpumpe.Appliance(Vannpumpe,1,115,3,120,0.2,40)
N1_Vannpumpe_115W.windows([540,600],[720,780],0.35,[1020,1080]) 

N2_Vannpumpe_800W = Vannpumpe.Appliance(Vannpumpe,1,800,3,120,0.2,40)
N2_Vannpumpe_800W.windows([540,600],[720,780],0.35,[1020,1080])

N3_Vannpumpe_800W = Vannpumpe.Appliance(Vannpumpe,1,800,3,240,0.2,40)
N3_Vannpumpe_800W.windows([540,600],[720,780],0.35,[1020,1080]) 


#---------------------------------------------------------------------------

#Lader
N1_Lader_2 = Stikk.Appliance(Stikk,2,20,1,39,0.2,39)
N1_Lader_2.windows([510,570],[0,0],0.35) #08:30-09:30

N2_Lader_3 = Stikk.Appliance(Stikk,3,20,1,39,0.2,39)
N2_Lader_3.windows([510,600],[0,0],0.35) #08:30-10:00

N3_Lader_4 = Stikk.Appliance(Stikk,4,20,1,39,0.2,39)
N3_Lader_4.windows([510,600],[0,0],0.35) 

N4_Lader_5 = Stikk.Appliance(Stikk,5,20,1,39,0.2,39)
N4_Lader_5.windows([510,630],[0,0],0.35) #08:30-10:30


#---------------------------------------------------------------------------

#Kaffetrakter
N1_Kaffe_1080 = Stikk.Appliance(Stikk,1,1080,1,6,0.2,6)
N1_Kaffe_1080.windows([450,480],[0,0],0.35) #07:30-08:00

N2_Kaffe_1080 = Stikk.Appliance(Stikk,1,1080,1,12,0.2,12)
N2_Kaffe_1080.windows([450,480],[0,0],0.35)

#---------------------------------------------------------------------------

#TV
N1_TV_17W = Stikk.Appliance(Stikk,1,17,2,60,0.2,30)
N1_TV_17W.windows([510,540],[1200,1260],0.35)#08:30-09:00,20:00-21:00

N2_TV_29W = Stikk.Appliance(Stikk,1,29,2,90,0.2,30)
N2_TV_29W.windows([510,540],[1200,1260],0.35)

N3_TV_93W = Stikk.Appliance(Stikk,1,93,2,120,0.2,60)
N3_TV_93W.windows([480,540],[1200,1320],0.35)#08:00-09:00,20:00-22:00


#---------------------------------------------------------------------------

#Komfyr
N1_Komfyr_30min = Stikk.Appliance(Stikk,1,1800,1,30,0.2,30)
N1_Komfyr_30min.windows([1020,1140],[0,0],0.35)#17:00-19:00

N2_Komfyr_45min = Stikk.Appliance(Stikk,1,1800,1,45,0.2,30)
N2_Komfyr_45min.windows([1020,1140],[0,0],0.35)

#---------------------------------------------------------------------------

#Platetopp
N1_Platetopp_15min = Stikk.Appliance(Stikk,1,2900,1,15,0.2,15)
N1_Platetopp_15min.windows([1020,1140],[0,0],0.35)#17:00-19:00

N2_Platetopp_45min = Stikk.Appliance(Stikk,1,2900,1,40,0.2,20)
N2_Platetopp_45min.windows([1020,1140],[0,0],0.35)


#---------------------------------------------------------------------------

#Kjøleskap
#Legge til Duty cycle
N1_Kjøleskap_30W = Stikk.Appliance(Stikk,1,30.3,1,720,0.2,15,'yes',3)
N1_Kjøleskap_30W.windows([0,1440],[0,0])
#MÅ INKLUDERE [0,0] VEKTOR OM DET BARE TAS MED ET STORT VINDU
N1_Kjøleskap_30W.specific_cycle_1(30,120,0,120)#To timers syklus på kjøleskapet
N1_Kjøleskap_30W.specific_cycle_2(30,120,0,120)
N1_Kjøleskap_30W.specific_cycle_3(30,120,0,120)
N1_Kjøleskap_30W.cycle_behaviour([0,240],[240,480],[480,720],[720,960],[960,1200],[1200,1440])


N2_Kjøleskap_37W = Stikk.Appliance(Stikk,1,37.2,1,720,0.2,15,'yes',3)
N2_Kjøleskap_37W.windows([0,1440],[0,0])
#MÅ INKLUDERE [0,0] VEKTOR OM DET BARE TAS MED ET STORT VINDU
N2_Kjøleskap_37W.specific_cycle_1(30,120,0,120)#To timers syklus på kjøleskapet
N2_Kjøleskap_37W.specific_cycle_2(30,120,0,120)
N2_Kjøleskap_37W.specific_cycle_3(30,120,0,120)
N2_Kjøleskap_37W.cycle_behaviour([0,240],[240,480],[480,720],[720,960],[960,1200],[1200,1440])



