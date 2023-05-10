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
