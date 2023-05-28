# -*- coding: utf-8 -*-
"""
Created on Mon May 22 11:10:59 2023

@author: 张中杰
"""
import numpy as np
import itertools

HUPs = []

def initialList(db, minutil):
    #The structure to store utility information of every item
    HeaderTable = {}
    
    #for the ith transaction
    for i in range(len(db)):
        
        #compute the TWU of every itemset in this transaction
        twu = sum([item_u[0] for item_u in db[i]])
        for item_u in db[i]:
            item = item_u[1]
            utility = item_u[0]
            if item not in HeaderTable.keys():
                
                #pat: the itemset represented by this item, if the prefix is empty
                #     this itemset is (item, ). If the prefix is A, the pat is
                #     tuple(A+[item])
                #tidset: the bool array to store transactions containing the itemset
                #len: the number of transaction containing the itemset
                #list: containing the (utility, ru, tid) of this itemset
                HeaderTable[item] = {'pat':(item,),
                                    'tidset':np.zeros(len(db)).astype(bool), 
                                     'twu':twu, 
                                     'utility': utility, 
                                     'ru':0,
                                     'transN':1,
                                     'len':0,
                                     'list':[]}
            else:
                HeaderTable[item]['twu'] += twu
                HeaderTable[item]['utility'] += utility
                HeaderTable[item]['transN'] += 1
    
    
    #delete those items whose twu is less than minimum utility
    items = list(HeaderTable.keys())[:]
    for item in items:
        if HeaderTable[item]['twu']<minutil:
            del HeaderTable[item]
        else:
            HeaderTable[item]['list'] = np.zeros((HeaderTable[item]['transN'], 3)).astype(int)
            HeaderTable[item]['len'] = HeaderTable[item]['transN']
            
    items = list(HeaderTable.keys())[:]
    twus = [HeaderTable[item]['twu'] for item in items]
    SList = [item for _, item in sorted(zip(twus, items), reverse = True)]
    items = list(HeaderTable.keys())[:]
    
    for i in range(len(db)):
        transaction = db[i]
        transaction = list(filter(lambda x: x[1] in items, transaction))
        twus = [HeaderTable[item_u[1]]['twu'] for item_u in transaction]
        transaction = [item_u for _, item_u in sorted(zip(twus,transaction), reverse = True)]
        ru = 0
        for item_u in transaction:
            item = item_u[1]
            utility = item_u[0]
            HeaderTable[item]['tidset'][i] =  True
            HeaderTable[item]['ru'] += ru
            ru += utility
            idx = HeaderTable[item]['len'] - HeaderTable[item]['transN']
            HeaderTable[item]['list'][idx, 0] = utility
            HeaderTable[item]['list'][idx, 1] = ru
            HeaderTable[item]['list'][idx, 2] = i
            HeaderTable[item]['transN'] -= 1
            
            
    return HeaderTable, SList

def ConstructUBP(P, Px, Py):
    ubpxy = {'pat': tuple(list(Px['pat']) + [Py['pat'][-1]]),
            'tidset':0, 
             'twu':0, 
             'utility': 0, 
             'ru':0, 
             'list':{}}
    
    #Obtain the intersection of transaction by the bool operation
    ubpxy['tidset'] = Px['tidset'] & Py['tidset']
    
    #if the intersection is not empty
    if sum(ubpxy['tidset']) > 0:
        PxTrans = Px['list'][ubpxy['tidset'][Px['list'][:,2]]]
        PyTrans = Py['list'][ubpxy['tidset'][Py['list'][:,2]]]
        ubpxy['list'] = PyTrans
        ubpxy['list'][:,0] = ubpxy['list'][:,0] +PxTrans[:,0]
        if len(P)>0:
            PTrans = P['list'][ubpxy['tidset'][P['list'][:,2]]]
            ubpxy['list'][:,0] = ubpxy['list'][:,0] - PTrans[:,0]
        ubpxy['utility'] = sum(ubpxy['list'][:,0])
        ubpxy['ru'] = sum(ubpxy['list'][:,1])
    
    return ubpxy

def Search(setPx, P, minutil):
    for Px in reversed(setPx):
        if Px['utility'] >= minutil:
            HUPs.append((Px['pat'], Px['utility']))
        if Px['utility'] + Px['ru'] >= minutil:
            setPxy = []
            for Py in setPx:
                if Py['pat'] == Px['pat']:
                    break
                ubpxy = ConstructUBP(P, Px, Py)
                setPxy.append(ubpxy)
            Search(setPxy, Px, minutil)    

def getHup(db, minutil):
    HUPs.clear()
    HeaderTable, SList = initialList(db, minutil)
    P = {}
    setPx = []
    for item in SList:
        setPx.append(HeaderTable[item])
    Search(setPx, {}, minutil)
    return 0
