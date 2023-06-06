# -*- coding: utf-8 -*-
"""
Created on Sat May 27 11:18:05 2023

@author: 张中杰
"""

def getALLutility(db):
    result = 0
    for trans in db:
        result += sum([item_u[0] for item_u in trans])
    return result

def ToMemory(D):
    f = open(D)
    data = f.read().split('\n')
    if len(data[-1]) == 0:
        data = data[:-1]
    f.close()
    db = []
    for line in data:
        line_ = line.split(':')
        line_[0] = line_[0].split(' ')
        line_[1] = int(line_[1])
        line_[2] = list(map(lambda x: int(x), line_[2].split(' ')))
        
        if len(set(line_[0])) == len(line_[0]):
            trans = list(zip(line_[2], line_[0]))       
            db.append(trans)
        else:
            dict_trans = {}
            for item_idx in range(len(line_[0])):
                if line_[0][item_idx] not in dict_trans.keys():
                    dict_trans[line_[0][item_idx]] = line_[2][item_idx]
                else:
                    dict_trans[line_[0][item_idx]] += line_[2][item_idx]
            newTrans = [(dict_trans[item], item) for item in dict_trans.keys()]
            db.append(newTrans)
        
    return db
