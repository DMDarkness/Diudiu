# -*- coding: utf-8 -*-
"""
Created on Mon May 15 13:02:46 2023

@author: 张中杰
"""

import numpy as np
from itertools import combinations

def utilityIntrans(pat, trans):
    return sum([item_u[0] for item_u in filter(lambda item_u: item_u[1] in pat, trans)])

def PseudoProject(HeaderTable, UList, SList, patN, x):
    HeaderTable_ = {}
    
    for item in SList:
        if item == x:
            break
        HeaderTable_[item] = {'support':0, 'utility':0, 'twu':0, 'uBfpe':0, 'link':[]}
    
    for trans_idx in HeaderTable[x]['link']:
        trans = UList[trans_idx[0]]
        x_num = trans_idx[1]
        utilityPatNt = utilityIntrans(patN, trans) + trans[x_num][0]
        ESum = utilityPatNt
        for i in range(len(trans[:x_num])):
            item = trans[i][1]
            HeaderTable_[item]['support'] += 1
            HeaderTable_[item]['utility'] += trans[i][0] + utilityPatNt
            ESum += trans[i][0]
            HeaderTable_[item]['uBfpe'] += ESum
        for i in range(len(trans[:x_num])):
            item = trans[i][1]
            HeaderTable_[item]['twu'] += ESum
            HeaderTable_[item]['link'].append((trans_idx[0],i))
    return HeaderTable_

def buildTSCAUL(db, minutil):
    HeaderTable = {}
    
    #scan DB and accumulate the TWU of each item in DB
    for transaction in db:
        utilities = [item_u[0] for item_u in transaction]
        twu = sum(utilities)
        for item_u in transaction:
            item = item_u[1]
            utility = item_u[0]
            if item not in HeaderTable.keys():
                HeaderTable[item] = {'support':1, 'utility':utility, 'twu':twu, 'uBfpe':utility, 'link':[]}
            else:
                HeaderTable[item]['support'] += 1
                HeaderTable[item]['utility'] += utility
                HeaderTable[item]['uBfpe'] += utility
                HeaderTable[item]['twu'] += twu
                
    twus = [HeaderTable[item]['twu'] for item in HeaderTable.keys()]
    SList = [item for _, item in sorted(zip(twus, HeaderTable.keys()), reverse = True)]
    
    UList = []
    
    for t_num in range(len(db)):
        transaction = db[t_num]
        twus = [HeaderTable[item_u[1]]['twu'] for item_u in transaction]
        transaction = [item_u+[item_u[0]] for _, item_u in sorted(zip(twus,transaction), reverse = True)]
        ru = 0
        UList.append(transaction)
        for x_num in range(len(transaction)):
            item = transaction[x_num][1]
            utility = transaction[x_num][0]
            HeaderTable[item]['uBfpe'] += ru
            HeaderTable[item]['link'].append((t_num,x_num))
            ru += utility                
    
    return HeaderTable, UList, SList

def if_Clousure(W, patN, patNsupport, HeaderTable, minutil):
    for item in W:
        if HeaderTable[item]['support'] != patNsupport or HeaderTable[item]['utility'] < minutil:
            return False
    return True

def if_Singleton(W, patN, patNutil, patNsupport, HeaderTable, minutil):
    utils = [HeaderTable[item]['utility'] for item in W]
    uWX = sum(utils)+patNutil
    minW = min(utils)
    return uWX >= minutil and uWX < minutil + minW
    

def DFS(HeaderTable, UList, patN, patNutil, patNsupport, minutil, SList):
    if patNutil >= minutil:
        print((patN, patNutil))
    W = []
    for item in SList:
        if item in patN:
            break
        if HeaderTable[item]['uBfpe'] >= minutil:
            W.append(item)
            
    # Clousure
    if if_Clousure(W, patN, patNsupport, HeaderTable, minutil):
        for length in range(1,len(W)+1):
            pats = combinations(W, length)
            for pat in pats:
                util = sum([HeaderTable[item]['utility'] for item in pat])
                print((list(pat)+patN, util-(length-1)*patNutil))
                
    # Singleton
    elif if_Singleton(W, patN, patNutil, patNsupport, HeaderTable, minutil):
        print((W+patN, sum([HeaderTable[item]['utility'] for item in W]) + patNutil))
    else:
        for i in range(len(W)):
            item = W[-1-i]
            HeaderTable_ = PseudoProject(HeaderTable, UList, SList, patN, item)
            DFS(HeaderTable_, UList, patN+[item], HeaderTable[item]['utility'], HeaderTable[item]['support'], minutil, SList)

def d2HUP(db, minutil):
    HeaderTable, UList, SList = buildTSCAUL(db, minutil)
    DFS(HeaderTable, UList, [], 0, 0, minutil, SList)
            

test = [[[2,'a'],[2,'b'],[4,'c'],[2,'d']],
        [[4,'b']],
        [[2,'a'],[4,'b'],[1,'d']],
        [[2,'c']],
        [[2,'a']],
        [[4,'a'],[2,'c'],[3,'d']],
        [[2,'a'],[2,'b'],[6,'c']]
        ]

d2HUP(test, 9)