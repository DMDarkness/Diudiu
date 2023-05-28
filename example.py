# -*- coding: utf-8 -*-
"""
Created on Sun May 28 22:57:31 2023

@author: 张中杰
"""

import Hamm
import d2HUP
import HUI_PR
import UBP_Miner
import EFIM
import getspmf

test = [[(4,'a'),(2,'b'),(6,'c')],
        [(4,'a'),(2,'b'),(3,'c'),(1,'d')],
        [(2,'b'),(1,'d'),(1,'e')],
        [(1,'d'),(1,'e')],
        [(2,'a'),(4,'b'),(2,'e')],
        [(6,'a')],
        [(1,'d'),(1,'e')]
        ]

test2 = [[(2,'a'),(2,'b'),(4,'c'),(2,'d')],
        [(4,'b')],
        [(2,'a'),(4,'b'),(1,'d')],
        [(2,'c')],
        [(2,'a')],
        [(4,'a'),(2,'c'),(3,'d')],
        [(2,'a'),(2,'b'),(6,'c')]
        ]

test3 = [[(5,'a'),(1,'c'),(2,'d')],
         [(10,'a'),(6,'c'),(6,'e'),(5,'g')],
         [(5,'a'),(4,'b'),(1,'c'),(12,'d'),(3,'e'),(5,'f')],
         [(8,'b'),(3,'c'),(6,'d'),(3,'e')],
         [(4,'b'),(2,'c'),(3,'e'),(2,'g')]]

db = getspmf.ToMemory('mushroom_utility_SPMF.txt')

Hamm.getHup(db, 500000)
result1 = Hamm.HUPs

d2HUP.getHup(db, 500000)
result2 = d2HUP.HUPs

HUI_PR.getHup(db, 500000)
result3 = HUI_PR.HUPs

UBP_Miner.getHup(db, 500000)
result4 = UBP_Miner.HUPs

EFIM.getHup(db, 500000)
result5 = EFIM.HUPs