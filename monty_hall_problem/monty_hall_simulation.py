#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

reward_door = 2
door_list = [1, 2, 3]
choice_list = ['switch', 'stay']
n_iter = 100000
experiment_journal = {}


for i in range(n_iter):
    init_door = np.random.choice(door_list)

    opened_door = np.random.choice(list(set(door_list) - {reward_door, init_door}))
    
    choice_taken = np.random.choice(choice_list)
    
    if choice_taken == 'switch':
        new_door = list(set(door_list) - {opened_door, init_door})[0]
    else:
        new_door = init_door
    
    if choice_taken not in experiment_journal.keys():
        experiment_journal[choice_taken] = experiment_journal.get(choice_taken, {})
    
    if new_door == reward_door:
        experiment_journal[choice_taken]['won'] = experiment_journal[choice_taken].get('won' , 0) + 1
    
    experiment_journal[choice_taken]['played'] = experiment_journal[choice_taken].get('played' , 0) + 1


print('Performed', n_iter, 'simulations', '\n')

for i in choice_list:
    print('choosing strategy', i, ',')
    print('Player won', str(round((experiment_journal[i]['won']/experiment_journal[i]['played'])*100, 2)) + '% times', '\n')
