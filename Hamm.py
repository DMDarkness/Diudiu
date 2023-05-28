# -*- coding: utf-8 -*-
"""
Created on Fri May 12 21:34:38 2023

@author: 张中杰
"""

import numpy as np

HUPs = []

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
    
    # insert the branch transaction into the TV tree
    def insertbranch(self, transaction, brau):
        
        #locate to the root of tree
        currentnode = self.root
        
        #obtain the utilities of the transaction
        utilities = np.array([item_u[0] for item_u in transaction])
        
        #calculate the twu of every itemset contained by this transaction
        twu = sum(utilities)
        
        #initialize the remain utility
        ru = 0
        
        #for every item in the transaction
        for item_u in transaction:
            
            #get the item name
            item = item_u[1]
            
            #update the remain utility and twu of this item
            #brau is the utility of the prefix itemset
            self.HeaderTable[item]['ru'] += ru
            self.HeaderTable[item]['twu'] += twu+brau
            ru += item_u[0]
            
            #if item is not the current node's children
            if item not in currentnode.childrennames:
                
                #build a new node
                newnode = Node(item,brau,np.zeros(1),0,currentnode)
                
                #update the headertable
                self.HeaderTable[item]['link'].append(newnode)
                
                #add the new node to the children of crrent node
                currentnode.children.append(newnode)
                currentnode.childrennames.append(item)
                
                #let the current node be the new node
                currentnode = newnode
                
            #if the item is current node's children
            else:
                for node in currentnode.children:
                    
                    #find such child node
                    if node.item == item:
                        
                        #the utility of prefix itemset
                        node.brau += brau
                        
                        #let the current node be the new node
                        currentnode = node
                        break
                    
        #if the current node has not upos
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
        #the trans looks like [5, (1,'a'),(5,'b'), ...]
        trans = [node.upos[-1]+node.brau]
        
        #start to obtain the sub transaction based on the prefix xP
        currentnode = node
        idx = -1
        twu = sum(node.upos)+node.brau
        while currentnode.parent.item != 'root':
            idx = idx - 1
            
            utility = node.upos[idx]+trans[0]
            item = currentnode.parent.item
            
            if item not in HeaderTable.keys():
                #the utility is the utility of xP+item
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
            #print((pat, utility))
            HUPs.append((pat, utility))
        if tv.HeaderTable[x]['ru']+utility<minutil:
            delete_nodes(tv, x)
        if tv.HeaderTable[x]['ru']+utility>=minutil:
            tv_ = construct_(tv, x, minutil)
            if len(tv_.root.children) > 0:
                mine(tv_, pat, minutil)
            delete_nodes(tv, x)
    return 0

def getHup(db, minutil):
    HUPs.clear()
    tv = construct(db,minutil)
    mine(tv,[],minutil)
