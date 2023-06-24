# -*- coding: utf-8 -*-
"""
Created on Mon May 22 11:10:59 2023

@author: 张中杰
"""
import numpy as np
import itertools
from itertools import combinations

HUPs = []
EUCS = {}

def initialList(db, minutil):#, pcount, psize):
    #The structure to store utility information of every item
    HeaderTable = {}
    
    #Initial the EUCS to store the twu of patterns with length 2
    EUCS.clear()
    
    #for the ith transaction
    for i in range(len(db)):
        
        #compute the TWU of every itemset in this transaction
        twu = sum([item_u[0] for item_u in db[i]])
        
        #for every item of this transaction
        for item_u in db[i]:
            
            #obtain the item name
            item = item_u[1]
            
            #obtain the utility of this item
            utility = item_u[0]
            if item not in HeaderTable.keys():
                
                #pat: the itemset represented by this item, if the prefix is empty
                #     this itemset is (item, ). If the prefix is A, the pat is
                #     tuple(A+[item])
                #tidset: the bool array to store transactions containing the itemset
                #len: the number of transaction containing the itemset
                
                #transN: a counter
                #Suru: the utility + remain_utility of every partition
                #LA: 
                #list: containing the (utility, ru, tid) of this itemset
                HeaderTable[item] = {'pat':(item,),
                                    'tidset':-1,#np.zeros(len(db)).astype(bool), 
                                     'twu':twu, 
                                     'utility': utility, 
                                     'ru':0,
                                     'transN':1,
                                     'len':0,
                                     #'Suru':np.zeros(pcount).astype(int),
                                     'LA':[],
                                     'list':[]}
            else:
                #update the twu
                HeaderTable[item]['twu'] += twu
                #update the utility
                HeaderTable[item]['utility'] += utility
                #update the Counter
                HeaderTable[item]['transN'] += 1
    
    
    #delete those items whose twu is less than minimum utility
    items = list(HeaderTable.keys())[:]
    for item in items:
        if HeaderTable[item]['twu']<minutil:
            del HeaderTable[item]
        else:
            #for the item whose twu > minutil, initialize its tidset
            HeaderTable[item]['tidset'] = np.zeros(len(db)).astype(bool)
            
            #for the tiem whose twu > minutil, initialize its list
            HeaderTable[item]['list'] = np.zeros((HeaderTable[item]['transN'], 3)).astype(int)
            
            #The number of transactions contianing this tiem is stored in the Count transN
            HeaderTable[item]['len'] = HeaderTable[item]['transN']
    
    #sort the items based on twus
    items = list(HeaderTable.keys())[:]
    twus = [HeaderTable[item]['twu'] for item in items]
    SList = [item for _, item in sorted(zip(twus, items), reverse = True)]
    items = list(HeaderTable.keys())[:]
    
    
    for i in range(len(db)):
        
        #count current partition
        #t_pcount = int(i/psize)
        
        #for every transaction, delete those items whose twu < minutil, and sort them based on SList
        transaction = db[i]
        transaction = list(filter(lambda x: x[1] in items, transaction))
        indexes = [SList.index(item_u[1]) for item_u in transaction]
        transaction = [item_u for _, item_u in sorted(zip(indexes,transaction))]
        ru = 0
        
        twu = sum([item_u[0] for item_u in transaction])
        
        #Initialize the EUCS
        for pat2 in combinations([item_u[1] for item_u in db[i]], 2):
            pat2 = list(pat2)
            pat2.sort()
            keypat2 = tuple(pat2)
            if keypat2 not in EUCS.keys():
                EUCS[keypat2] = twu
            else:
                EUCS[keypat2] += twu
        
        #for every item in this transaction
        for item_u in transaction:
            item = item_u[1]
            utility = item_u[0]
            HeaderTable[item]['tidset'][i] =  True
            HeaderTable[item]['ru'] += ru
            
            idx = HeaderTable[item]['len'] - HeaderTable[item]['transN']
            HeaderTable[item]['list'][idx, 1] = ru
            
            ru += utility
            #HeaderTable[item]['Suru'][t_pcount] += ru
            
            
            HeaderTable[item]['list'][idx, 0] = utility
            
            HeaderTable[item]['list'][idx, 2] = i
            HeaderTable[item]['transN'] -= 1
            
            
    return HeaderTable, SList, EUCS

def ConstructUBP(P, Px, Py, minutil):#, pcount, psize, ldb
    ubpxy = {'pat': tuple(list(Px['pat']) + [Py['pat'][-1]]),
            'tidset':-1,#np.zeros(len(Px['tidset'])).astype(bool), 
             'twu':0, 
             'utility': 0, 
             'ru':0, 
             #'Suru':np.zeros(pcount).astype(int),
             'list':{}}
    
    #Obtain the intersection of transaction by the bool operation
    #ubpxy['tidset'] = np.zeros(len(db)).astype(bool)
    
    # for t_pcount in range(pcount):
    #     #Suru-Prune
    #     if Px['Suru'][t_pcount] > 0 and Py['Suru'][t_pcount] > 0:
    #         start = t_pcount*psize
    #         end = (t_pcount+1)*psize
    #         ubpxy['tidset'][start:end] = Px['tidset'][start:end] & Py['tidset'][start:end]
    ubpxy['tidset'] = Px['tidset'] & Py['tidset']
    
    
    
    #if the intersection is not empty
    if sum(ubpxy['tidset']) > 0:
        #obtain the transaction info of trans which contains Px
        PxTrans = Px['list'][ubpxy['tidset'][Px['list'][:,2]]]
        
        #LA-Prune & Suru-Prune
        if sum(PxTrans[:,0] + PxTrans[:,1]) >= minutil:
        
            #obtain the transaction info of trans which contains Py
            PyTrans = Py['list'][ubpxy['tidset'][Py['list'][:,2]]]
            ubpxy['list'] = PyTrans
            ubpxy['list'][:,0] = ubpxy['list'][:,0] +PxTrans[:,0]
            if len(P)>0:
                PTrans = P['list'][ubpxy['tidset'][P['list'][:,2]]]
                ubpxy['list'][:,0] = ubpxy['list'][:,0] - PTrans[:,0]
            ubpxy['utility'] = sum(ubpxy['list'][:,0])
            ubpxy['ru'] = sum(ubpxy['list'][:,1])
            
            
            # for t_pcount in range(pcount):
            #     start = t_pcount*psize
            #     end = (t_pcount+1)*psize
            #     t_p_idx = (ubpxy['list'][:,2] < end) & (ubpxy['list'][:,2] >= start)
                
            #     ubpxy['Suru'][t_pcount] = sum(ubpxy['list'][t_p_idx,0]+ubpxy['list'][t_p_idx,1])
    
    return ubpxy

def EUCS_Prune(x, y, EUCS, minutil):
    #y = paty[-1]
    #x = patx[-1]
    #for x in patx:
    pat2 = [x,y]
    pat2.sort()
    keypat = tuple(pat2)
    if keypat not in EUCS.keys():
        return True
    elif EUCS[keypat] < minutil:
        return True
    return False

# def PU_Prune(Px, Py, minutil):
#     PUxru = sum(Px['Suru'][Py['Suru'] > 0])
#     if PUxru < minutil:
#         return True
#     return False


def Search(setPx, P, minutil, EUCS):#, pcount, psize, ldb):
    if len(P.keys()) > 0:
        print('Cond: ', P['pat'])
    
    for Px in reversed(setPx):
        if Px['utility'] >= minutil:
            print('HUP: ',Px['pat'])
            HUPs.append((Px['pat'], Px['utility']))

        if Px['utility'] + Px['ru'] >= minutil:
            setPxy = []
            for Py in setPx:
                if Py['pat'] == Px['pat']:
                    break
                #EUCS Prune
                if not EUCS_Prune(Px['pat'][-1], Py['pat'][-1], EUCS, minutil):
                    #PU Prune
                    #if not PU_Prune(Px, Py, minutil):
                    ubpxy = ConstructUBP(P, Px, Py, minutil)#pcount, psize, ldb, 
                    #LA-Prune
                    if ubpxy['utility'] + ubpxy['ru'] > 0:
                        setPxy.append(ubpxy)
            Search(setPxy, Px, minutil, EUCS)#, pcount, psize, ldb)    

def getHup(db, minutil):#, psize):
    #clear the HUPs
    HUPs.clear()
    #obtain the length of dataset
    ldb = len(db)
    #Compute the count of partition based on psize
    #pcount = int(np.ceil(len(db)/psize))
    
    #Initialize
    HeaderTable, SList, EUCS = initialList(db, minutil)#, pcount, psize)
    print(SList)
    P = {}
    setPx = []
    for item in SList:
        setPx.append(HeaderTable[item])
    Search(setPx, {}, minutil, EUCS)#, pcount, psize, ldb)
    return 0
