# -*- coding: utf-8 -*-
"""
Created on Mon May 15 13:02:46 2023

@author: 张中杰
"""

import numpy as np
from itertools import combinations

HUPs = []

#Count the utility of a pattern in a transaction
def utilityIntrans(pat, trans):
    return sum([item_u[0] for item_u in filter(lambda item_u: item_u[1] in pat, trans)])

def PseudoProject(HeaderTable, UList, SList, patN, x):
    #initialize the header table, which stores the information when the prefix is patN+x
    HeaderTable_ = {}
    
    #for every item in SList
    for item in SList:
        
        #if the item is not the extention of x, break
        if item == x:
            break
        
        #Initialize the HeaderTable_
        HeaderTable_[item] = {'support':0, 
                              'utility':0,
                              'noprefixutility': 0,
                              'twu':0, 
                              'uBfpe':0, 
                              'link':[]}
    
    #for every transaction of x's projected database
    for trans_idx in HeaderTable[x]['link']:
        
        #Obtain the transaction from UList
        trans = UList[trans_idx[0]]
        
        #Obtain the location of x in this transaction 
        x_num = trans_idx[1]
        
        #compute the utility of patN+x in this transaction
        utilityPatNt = utilityIntrans(patN, trans) + trans[x_num][0]
        
        #the accumulate utility is initialized as the utility of patN+x
        ESum = utilityPatNt
        for i in range(len(trans[:x_num])):
            item = trans[i][1]
            HeaderTable_[item]['support'] += 1
            HeaderTable_[item]['utility'] += trans[i][0] + utilityPatNt
            HeaderTable_[item]['noprefixutility'] += trans[i][0]
            ESum += trans[i][0]
            HeaderTable_[item]['uBfpe'] += ESum
        for i in range(len(trans[:x_num])):
            item = trans[i][1]
            HeaderTable_[item]['twu'] += ESum
            HeaderTable_[item]['link'].append((trans_idx[0],i))
    return HeaderTable_

def buildTSCAUL(db, minutil):
    
    #the HeaderTable store information of every item
    HeaderTable = {}
    
    #scan DB and accumulate the TWU of each item in DB
    for transaction in db:
        
        #compute the twu for all the items in this transaction
        utilities = [item_u[0] for item_u in transaction]
        twu = sum(utilities)
        
        #for every item in this transaction
        for item_u in transaction:
            
            #Obtain the item's name
            item = item_u[1]
            
            #Obtain the utility of this item
            utility = item_u[0]
            
            #If item is not in HeaderTable, initialize it
            if item not in HeaderTable.keys():
                HeaderTable[item] = {'support':1, 
                                     'utility':utility,
                                     'noprefixutility': utility,
                                     'twu':twu, 
                                     'uBfpe':utility, 
                                     'link':[]}
            else:
                HeaderTable[item]['support'] += 1
                HeaderTable[item]['utility'] += utility
                HeaderTable[item]['noprefixutility'] += utility
                HeaderTable[item]['uBfpe'] += utility
                HeaderTable[item]['twu'] += twu
    
    #Sort items by the TWU descend
    twus = [HeaderTable[item]['twu'] for item in HeaderTable.keys()]
    SList = [item for _, item in sorted(zip(twus, HeaderTable.keys()), reverse = True)]
    
    #Initialize the database
    UList = []
    
    #for the t_num-th transaction in database
    for t_num in range(len(db)):
        
        #Obtain the transaction
        transaction = db[t_num]
        
        #sort the item in such transaction by the TWU descend
        twus = [HeaderTable[item_u[1]]['twu'] for item_u in transaction]
        transaction = [item_u for _, item_u in sorted(zip(twus,transaction), reverse = True)]
        
        #for this transaction, initialize the extention utility
        ru = 0
        
        #add this transaction to the UList
        UList.append(transaction)
        
        #for the x_num-th item in this transaction
        for x_num in range(len(transaction)):
            
            #Obtain this item
            item = transaction[x_num][1]
            
            #Obtain the utility of this item
            utility = transaction[x_num][0]
            
            #Update the remain utility of this item
            HeaderTable[item]['uBfpe'] += ru
            
            #Update the projected database of this item
            HeaderTable[item]['link'].append((t_num,x_num))
            
            #the variable used to update the remain utility of next item
            ru += utility                
    
    return HeaderTable, UList, SList

#Judge If the Clousure is satisfied
def if_Clousure(W, patN, patNsupport, HeaderTable, minutil):
    for item in W:
        if HeaderTable[item]['support'] != patNsupport or HeaderTable[item]['utility'] < minutil:
            return False
    return True

#Judge if the singleton is satisfied
def if_Singleton(W, patN, patNutil, patNsupport, HeaderTable, minutil):
    for item in W:
        if HeaderTable[item]['support'] != patNsupport:
            return 0, False
    
    utils = [HeaderTable[item]['utility'] for item in W]
    
    uWX = sum(utils) - (len(W)-1)*patNutil
    
    minW = min(utils) - patNutil
    return uWX, uWX >= minutil and uWX < minutil + minW
    

#Deep first search
def DFS(HeaderTable, UList, patN, patNutil, patNsupport, minutil, SList):
    if patNutil >= minutil:
        HUPs.append((patN, patNutil))
        #print()
    W = []
    for item in SList:
        if item in patN:
            break
        if HeaderTable[item]['twu'] >= minutil:
            W.append(item)
    
    if len(W) > 0:      
        # Clousure
        if if_Clousure(W, patN, patNsupport, HeaderTable, minutil):
            for length in range(1,len(W)+1):
                pats = combinations(W, length)
                for pat in pats:
                    util = sum([HeaderTable[item]['utility'] for item in pat])
                    HUPs.append((list(pat)+patN, util-(length-1)*patNutil))
                    
        # Singleton
        else:
            uWX, if_Singe = if_Singleton(W, patN, patNutil, patNsupport, HeaderTable, minutil)
            if if_Singe:
                HUPs.append((W+patN, uWX))
            else:
                for i in range(len(W)):
                    item = W[-1-i]
                    #HeaderTable stores the information when the prefix is patN
                    #HeaderTable_ stores the information when the prefix is patN+item
                    HeaderTable_ = PseudoProject(HeaderTable, UList, SList, patN, item)
                    
                    #Deep first search
                    #The HeaderTable[item]['utility'] is the utility of patN+item
                    #The HeaderTable[item]['support'] is the utility of patN+item
                    DFS(HeaderTable_, UList, patN+[item], HeaderTable[item]['utility'], HeaderTable[item]['support'], minutil, SList)

def getHup(db, minutil):
    HUPs.clear()
    
    #build TS{} and omiga from D and XUT
    HeaderTable, UList, SList = buildTSCAUL(db, minutil)
    DFS(HeaderTable, UList, [], 0, 0, minutil, SList)
            
