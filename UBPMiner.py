# -*- coding: utf-8 -*-
"""
Created on Mon May 22 11:10:59 2023

@author: 张中杰
"""
import numpy as np
import itertools

def initialList(db, minutil):
    HeaderTable = {}
    for i in range(len(db)):
        if i%1000 == 0:
            print(i)
        twu = sum([item_u[0] for item_u in db[i]])
        for item_u in db[i]:
            item = item_u[1]
            utility = item_u[0]
            if item not in HeaderTable.keys():
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
        if i%1000 == 0:
            print(i)
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
    
    ubpxy['tidset'] = Px['tidset'] & Py['tidset']
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
            print(Px['pat'], Px['utility'])
        if Px['utility'] + Px['ru'] >= minutil:
            setPxy = []
            for Py in setPx:
                if Py['pat'] == Px['pat']:
                    break
                ubpxy = ConstructUBP(P, Px, Py)
                setPxy.append(ubpxy)
            Search(setPxy, Px, minutil)    

def UBPMiner(db, minutil):
    HeaderTable, SList = initialList(db, minutil)
    P = {}
    setPx = []
    for item in SList:
        setPx.append(HeaderTable[item])
    Search(setPx, {}, minutil)
    return 0

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

UBPMiner(test2,9)
