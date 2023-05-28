# -*- coding: utf-8 -*-
"""
Created on Sat May 27 11:18:05 2023

@author: 张中杰
"""

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
        db.append(list(zip(line_[2], line_[0])))
        
    return db