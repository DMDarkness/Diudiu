# -*- coding: utf-8 -*-
"""
Created on Tue May 23 17:37:08 2023

@author: 张中杰
"""

def RecusiveSearch(alpha, alphaD, HeaderTable, ni, fi, minutil):
    for item in reversed(ni):
        beta = alpha + [item]
        
        HeaderTable_ = {}
        
        for it in fi:
            HeaderTable_[it] = {'slocU': 0,
                                'utility': 0,
                                'ssubU': 0,
                                'proD': []}
        
        if HeaderTable[item]['utility'] >= minutil:
            print(beta,HeaderTable[item]['utility'])
        
        for idx in HeaderTable[item]['proD']:
            prUit = idx[0]
            idx_ = idx[1]
            trans = alphaD[idx_]
            ru = 0
            for item_idx in range(len(trans)):
                item_ = trans[item_idx][1]
                
                if item_ == item:
                    break
                elif item_ in fi:
                    utility = trans[item_idx][0] + prUit
                    
                    #HeaderTable_[item_]['slocU'] += (trans[item_idx + 1][1] != item)*ru
                    HeaderTable_[item_]['ssubU'] += utility + ru
                    HeaderTable_[item_]['utility'] += utility
                    HeaderTable_[item_]['proD'].append((utility, idx_))
                    
                    ru += trans[item_idx][0]
            #update slocU
            if item_idx > 0:
                for item_idx_ in range(item_idx-1):
                    item_ = trans[item_idx_][1]
                    HeaderTable_[item_]['slocU'] += ru
        
        fibeta = list(filter(lambda x: HeaderTable_[x]['slocU'] >= minutil, fi))
        nibeta = list(filter(lambda x: HeaderTable_[x]['ssubU'] >= minutil, fi))
        RecusiveSearch(beta, alphaD, HeaderTable_, nibeta, fibeta, minutil)
                    
    return 0

def HUI_PR(db, minutil):
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
            ru = 0
            item = item_u[1]
            utility = item_u[0]
            HeaderTable[item]['subU'] += ru
            HeaderTable[item]['proD'].append((utility, i))
            ru += utility
    
    #build the ni based on subU
    ni = []
    for item in fi:
        if HeaderTable[item]['subU']>=minutil:
            ni.append(item)
            
    #recusive mining the high utility itemset
    RecusiveSearch([], db, HeaderTable, ni, fi, minutil)  

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

HUI_PR(test3*200000, 1)      