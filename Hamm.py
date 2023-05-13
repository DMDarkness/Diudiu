# -*- coding: utf-8 -*-
"""
Created on Fri May 12 21:34:38 2023

@author: 张中杰
"""

import numpy as np

def readspmfdata(data):
    file = open(data)
    
    db = []
    return db

class Node:
    def __init__(self, item, brau, upos, link, parent):
        self.item = item
        self.brau = brau
        self.upos = upos
        self.link = link
        self.children = []
        self.childrennames = []
        self.parent = parent
    
    def addchild(self, node):
        self.children.append(node)
        

        
class TV:
    def __init__(self, SList, HeaderTable, T, P):
        self.SList = SList
        self.HeaderTable = HeaderTable
        
        self.T = T
        self.root = T
        self.P = P
        
        for item in self.HeaderTable.keys():
            self.HeaderTable[item]['twu'] = 0
    
    def insertbranch(self, transaction, brau):
        currentnode = self.root
        utilities = np.array([item_u[0] for item_u in transaction])
        ru = 0
        for item_u in transaction:
            item = item_u[1]
            
            self.HeaderTable[item]['ru'] += ru
            self.HeaderTable[item]['twu'] += sum(utilities)+brau
            ru += item_u[0]
            if item not in currentnode.childrennames:
                newnode = Node(item,brau,np.zeros(1),0,currentnode)
                self.HeaderTable[item]['link'].append(newnode)
                currentnode.children.append(newnode)
                currentnode.childrennames.append(item)
                currentnode = newnode
            else:
                for node in currentnode.children:
                    if node.item == item:
                        node.brau += brau
                        currentnode = node
                        break
        if sum(currentnode.upos) == 0:
            currentnode.upos = utilities
        else:
            currentnode.upos = currentnode.upos+utilities
                
def construct_(tv, x, minutil):
    HeaderTable = {}
    
    #build conditional transaction database and build HeaderTable
    db = []
    for node in tv.HeaderTable[x]['link']:
        
        #the branch utility of xP is the utility of x plus the utility of P in the branch
        trans = [node.upos[-1]+node.brau]
        currentnode = node
        idx = -1
        twu = sum(node.upos)
        while currentnode.parent.item != 'root':
            idx = idx - 1
            
            utility = node.upos[idx]+trans[0]
            item = currentnode.parent.item
            
            if item not in HeaderTable.keys():
                HeaderTable[item] = {'utility':utility, 'twu':twu, 'ru':0, 'link':[]}
            else:
                HeaderTable[item]['utility'] += utility
                HeaderTable[item]['twu'] += twu
            
            trans.insert(1,(node.upos[idx],item))
            currentnode = currentnode.parent
        db.append(trans)
            
    #
    #collect the set S of items with TWU>=minutil
    
    items = list(HeaderTable.keys())[:]
    for item in items:
        if HeaderTable[item]['twu']<minutil:
            del HeaderTable[item]
            
    items = list(HeaderTable.keys())[:]
    
    SList = list(filter(lambda item: item in items, tv.SList))
    
    T = Node('root',0,np.zeros(1),0,0)
    P = []
    tv_ = TV(SList, HeaderTable, T, P)
    
    for trans in db:
        brau = trans[0]
        transaction = trans[1:]
        transaction = list(filter(lambda x: x[1] in items, transaction))
        
        #insert a branch from selected items into TV.T
        
        if len(transaction)>0:
            tv_.insertbranch(transaction, brau)
        
    return tv_

def construct(db, minutil):
    HeaderTable = {}
    #scan DB and accumulate the TWU of each item in DB
    
    for transaction in db:
        utilities = [item_u[0] for item_u in transaction]
        twu = sum(utilities)
        for item_u in transaction:
            item = item_u[1]
            utility = item_u[0]
            if item not in HeaderTable.keys():
                HeaderTable[item] = {'utility':utility, 'twu':twu, 'ru':0, 'link':[]}
            else:
                HeaderTable[item]['utility'] += utility
                HeaderTable[item]['twu'] += twu
                
    #collect the set S of items with TWU>=minutil
    
    items = list(HeaderTable.keys())[:]
    for item in items:
        if HeaderTable[item]['twu']<minutil:
            del HeaderTable[item]
    
    #sort S in the TWU descending order as SList
    
    items = list(HeaderTable.keys())[:]
    twus = [HeaderTable[item]['twu'] for item in items]
    SList = [item for _, item in sorted(zip(twus, items), reverse = True)]
    
    items = list(HeaderTable.keys())[:]
    #initialize TV.HT, TV.T and TV.P
    
    T = Node('root',0,np.zeros(1),0,0)
    P = []
    tv = TV(SList, HeaderTable, T, P)
    
    #for each T in DB do
    for transaction in db:
        
        #select items(with utilities) from T in S
        transaction = list(filter(lambda x: x[1] in items, transaction))
        indexes = [SList.index(item_u[1]) for item_u in transaction]
        transaction = [item_u for _, item_u in sorted(zip(indexes,transaction))]
        
        #insert a branch from selected items into TV.T
        tv.insertbranch(transaction, 0)
        
    return tv

def delete_nodes(tv, x):
    for node in tv.HeaderTable[x]['link']:
        M = node.parent
        if sum(M.upos) == 0:
            M.upos = node.upos[:-1]
        else:
            M.upos = M.upos+node.upos[:-1]
        
    return 0

def mine(tv, P, minutil):
    for x in reversed(tv.SList):
        pat = P+[x]
        utility = tv.HeaderTable[x]['utility']
        if utility >= minutil:
            #HUP.append((pat,utility))
            print((pat, utility))
        if tv.HeaderTable[x]['ru']+utility<minutil:
            delete_nodes(tv, x)
        if tv.HeaderTable[x]['ru']+utility>=minutil:
            tv_ = construct_(tv, x, minutil)
            if len(tv_.root.children) > 0:
                mine(tv_, pat, minutil)
            delete_nodes(tv, x)
    return 0

def getHup(db, minutil):
    tv = construct(db,minutil)
    mine(tv,[],minutil)

test = [[(4,'a'),(2,'b'),(6,'c')],
        [(4,'a'),(2,'b'),(3,'c'),(1,'d')],
        [(2,'b'),(1,'d'),(1,'e')],
        [(1,'d'),(1,'e')],
        [(2,'a'),(4,'b'),(2,'e')],
        [(6,'a')],
        [(1,'d'),(1,'e')]
        ]

getHup(test,0)
