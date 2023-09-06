# -*- coding: utf-8 -*-
"""
Created on Sat Jun 17 23:56:53 2023

@author: 张中杰
"""

import numpy as np
from collections import Counter
import Hamm
import UBP_Miner
import EFIM
import HUI_PR
import getspmf



def hoeffding_size(epsilon,delta):
    return int(np.ceil(np.log(2/delta)/(2*epsilon*epsilon)))

def sampling(db, scale, expand_scale):
    sample = []
    uti = list(map(lambda x: sum([item_u[0] for item_u in x]),db))
    utii = uti[:]
    uti = np.array(uti)/sum(uti)
    for i in range(len(uti)):
        if i>0:
            uti[i] = uti[i-1]+uti[i] 
    rdv = np.random.rand(scale)
    sample_ids = list(map(lambda x: np.searchsorted(uti,x,side="right"),rdv))
    
    idCounter = Counter(sample_ids)
    
    #sample_ids_dict = Counter(sample_ids)
    sample = list(map(lambda x: [(int(item_u[0]*idCounter[x]*expand_scale/utii[x]), item_u[1]) for item_u in db[x]],idCounter.keys()))
    return sample


def getHup(alg, db, epsilon, delta, rate):
    expand_scale = 10000
    scale = hoeffding_size(epsilon,delta)
    sample = sampling(db, scale, expand_scale)
    L = scale*rate*expand_scale
    if alg == 'Hamm':
        Hamm.getHup(sample,L)
        HUPs = [(res[0],res[1]/(scale*expand_scale)) for res in Hamm.HUPs]
        return HUPs
    elif alg == 'UBP_Miner':
        UBP_Miner.getHup(sample,L,len(sample)/512)
        HUPs = [(res[0],res[1]/(scale*expand_scale)) for res in UBP_Miner.HUPs]
        return HUPs       
    elif alg == 'EFIM':
        EFIM.getHup(sample,L)
        HUPs = [(res[0],res[1]/(scale*expand_scale)) for res in EFIM.HUPs]
        return HUPs
    elif alg == 'HUI_PR':
        HUI_PR.getHup(sample,L)
        HUPs = [(res[0],res[1]/(scale*expand_scale)) for res in HUI_PR.HUPs]
        return HUPs          
    return 0
