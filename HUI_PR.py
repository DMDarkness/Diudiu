# -*- coding: utf-8 -*-
"""
Created on Tue May 23 17:37:08 2023

@author: 张中杰
"""
import getspmf

HUPs = []

def RecusiveSearch(alpha, alphaD, HeaderTable, ni, fi, minutil):
    for item in reversed(ni):
        beta = alpha + [item]
        
        #the dict to store slocU, utility, ssubU and proD of every prefix + item
        #Now the prefix utilities and projected database is stored in HeaderTable
        HeaderTable_ = {}
        
        for it in fi:
            HeaderTable_[it] = {'slocU': 0,
                                'utility': 0,
                                'ssubU': 0,
                                'proD': []}
        
        if HeaderTable[item]['utility'] >= minutil:
            HUPs.append((beta,HeaderTable[item]['utility']))
        
        for idx in HeaderTable[item]['proD']:
            #prUit is the utility of the prefix itemset in this transaction
            prUit = idx[0]
            idx_ = idx[1]
            trans = alphaD[idx_]
            ru = 0
            for item_idx in range(len(trans)):
                item_ = trans[item_idx][1]
                
                if item_ == item:
                    break
                elif item_ in fi:
                    #the utility of prefix+item_ 
                    utility = trans[item_idx][0] + prUit
                    
                    #the strict ru + utility of prefix + item_
                    HeaderTable_[item_]['ssubU'] += utility + ru
                    HeaderTable_[item_]['utility'] += utility
                    
                    #in the next recusive, prefix + item_ is the new prefix
                    HeaderTable_[item_]['proD'].append((utility, idx_))
                    
                    ru += trans[item_idx][0]
            #update slocU
            if item_idx > 0:
                for item_idx_ in range(item_idx-1):
                    item_ = trans[item_idx_][1]
                    if item_ in fi:
                        HeaderTable_[item_]['slocU'] += prUit + ru
        
        fibeta = list(filter(lambda x: HeaderTable_[x]['slocU'] >= minutil, fi))
        nibeta = list(filter(lambda x: HeaderTable_[x]['ssubU'] >= minutil, fi))
        RecusiveSearch(beta, alphaD, HeaderTable_, nibeta, fibeta, minutil)

def getHup(db, minutil):
    HUPs.clear()
    
    #initialize the Counter to record locU, utility and subU of every item
    HeaderTable = {}
    
    #Count locU, utility and subU
    for transaction in db:
        
        #Now the prefix pattern is empty, so the locU equals to the TWU
        locU = sum([item_u[0] for item_u in transaction])
        for item_u in transaction:
            item = item_u[1]
            utility = item_u[0]
            if item not in HeaderTable.keys():
                #the initial project database is empty
                HeaderTable[item] = {'locU': locU, 'utility': utility, 'subU':utility, 'proD': []}
            else:
                HeaderTable[item]['locU'] += locU
                HeaderTable[item]['utility'] += utility
                HeaderTable[item]['subU'] += utility
               
    #Delete those item whose locU/TWU is less than minimum utility          
    items = list(HeaderTable.keys())[:]
    for item in items:
        if HeaderTable[item]['locU']<minutil:
            del HeaderTable[item]
            
    #Sort items according to the TWU by descend
    items = list(HeaderTable.keys())[:]
    twus = [HeaderTable[item]['locU'] for item in items]
    
    #the initial fi contains the items whose TWU is higher than minimum utility
    fi = [item for _, item in sorted(zip(twus, items), reverse = True)]
    
    #update subU and builds the project database for every item in fi
    for i in range(len(db)):
        transaction = db[i]
        transaction = list(filter(lambda x: x[1] in items, transaction))
        twus = [HeaderTable[item_u[1]]['locU'] for item_u in transaction]
        db[i] = [item_u for _, item_u in sorted(zip(twus,transaction), reverse = True)]
        
        ru = 0
        for item_u in db[i]:
            item = item_u[1]
            utility = item_u[0]
            HeaderTable[item]['subU'] += ru
            
            #(utility of the prefix itemset in this transaction, the id of this transaction)
            HeaderTable[item]['proD'].append((utility, i))
            ru += utility
    
    #build the ni based on subU
    ni = []
    for item in fi:
        if HeaderTable[item]['subU']>=minutil:
            ni.append(item)
            
    #recusive mining the high utility itemset
    RecusiveSearch([], db, HeaderTable, ni, fi, minutil)  

    
