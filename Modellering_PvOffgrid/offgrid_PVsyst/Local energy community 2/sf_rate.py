# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 16:02:04 2023

@author: halgr
"""

import numpy as np

def sf_rate_sharing(sum_lost_load, demand):
    
    deltakere = len(sum_lost_load)
    sf_rate_post = np.zeros(deltakere)
    
    for i in range(deltakere):
        
        sf_rate_post[i] = (sum(demand[i])-sum_lost_load[i])/sum(demand[i])


    return sf_rate_post*100




def sf_rate(E, demand):
    
    deltakere = len(demand)
    
    sf_rate = np.zeros(deltakere)
    
    for i in range(deltakere):
        
        inv2load = sum(demand[i])-sum(E[i]['lost_load'])
        sf_rate[i] = inv2load/sum(demand[i])
        
    return sf_rate*100