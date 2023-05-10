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



#KATEGORI 1 HYTTE
#------------------------------------------------------------------

#Oppvarming
N1_Oppvarming_panelovn_400W = Oppvarming.Appliance(Oppvarming,2,400,2,360,0.2,30,3)


#To panelovner på 400W, fungerende i 2 vindu, total brukstid 360 minutter med tilfeldighet på +- 20%, 
#er på i minst 30 minutter etter at den er slått på, 3 duty cycles beskriver ovnens bruk


N1_Oppvarming_panelovn_400W.windows([0,480],[1200,1440])


#Ovnen sine 2 vindu er mellom 00:00-08:00 og 20:00-midnatt


N1_Oppvarming_panelovn_400W.specific_cycle_1(400,60,0,60)
N1_Oppvarming_panelovn_400W.specific_cycle_2(400,60,0,60)
N1_Oppvarming_panelovn_400W.specific_cycle_3(400,60,0,60)


#Tre (maksimalt) sykluser er modellert. Ovnen er på i 1 time, før den skrur seg av i en time. Hvert syklus repeterer seg i 
#to (maksimalt) vindu

N1_Oppvarming_panelovn_400W.cycle_behaviour([0,120],[120,240],[240,360],[360,480],[1200,1320],[1320,1440])


#De åtte vinduene ovnene er aktive. To vindu per syklus.


#---------------------------------------------------------------------

#Lys
N1_Lys_taklampe_4W = Lys.Appliance(Lys,4,4,2,270,0.2,60,'no',3)
N1_Lys_vegglampe_4W = Lys.Appliance(Lys,4,3.6,2,270,0.2,60,'no',3)

N1_Lys_taklampe_4W.windows([390,660],[1080,1350]) #12 timer vindu
N1_Lys_taklampe_4W.specific_cycle_1(4,45,0,45)
N1_Lys_taklampe_4W.specific_cycle_2(4,45,0,45)
N1_Lys_taklampe_4W.specific_cycle_3(4,45,0,45)
N1_Lys_taklampe_4W.cycle_behaviour([390,480],[480,570],[570,660],[1080,1170],[1170,1260],[1260,1350])

N1_Lys_vegglampe_4W.windows([390,660],[1080,1350], 0.2) #Lagt inn en variasjon på vindu på 20%!
N1_Lys_vegglampe_4W.specific_cycle_1(3.6,45,0,45)
N1_Lys_vegglampe_4W.specific_cycle_2(3.6,45,0,45)
N1_Lys_vegglampe_4W.specific_cycle_3(3.6,45,0,45)
N1_Lys_vegglampe_4W.cycle_behaviour([390,480],[480,570],[570,660],[1080,1170],[1170,1260],[1260,1350])


#Lys er modellert til å være på i 4,5 timer ila dagen. Med syklus 45 minutt på/av i vinduene 06:30-11:00 og 18:00-22:30 med 
#20% variasjon. Dette tas nok ikke hensyn til når det brukes sykluser med spesifiserte vindu, men er nok viktig at vinduet som angis
#er i samsvar med vinduene som spesifisert for syklusene.


#------------------------------------------------------------------------

#Vannpumpe
N1_Vannpumpe_115W = Vannpumpe.Appliance(Vannpumpe,1,115,3,120,0.2,20) 
N1_Vannpumpe_115W.windows([540,600],[720,780],0.35,[1020,1080])


#Lagt inn 3 vindu for bruk av varmepumpe, men en variasjon på start/slutt på vindu til å være 35%. Er også lagt inn 20% variasjon på
#brukstid. Pumpene er minst på i 20 minutter når de er skrudd på.


#------------------------------------------------------------------------

#Varmtvann
N1_Varmtvann_43min = Varmtvann.Appliance(Varmtvann,1,2000,3,43,0.2,10)
N1_Varmtvann_43min.windows([540,600],[900,980],0.35,[1140,1200])


#Lagt inn 3 vindu for bruk av varmtvann, men en variasjon på start/slutt på vindu til å være 35%. Er også lagt in 20% variasjon på 
#brukstid. Tankene er minst på i 10 minutter.


#------------------------------------------------------------------------

#Mobillader
N1_Lader_2 = Stikk.Appliance(Stikk,2,20,1,39,0.2,39)
N1_Lader_2.windows([510,570],[0,0],0.35) #08:30-09:30




