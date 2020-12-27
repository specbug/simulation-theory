#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import random
from PIL import Image
import glob
import matplotlib.colors
import seaborn as sns
from matplotlib import animation
from matplotlib.animation import PillowWriter
from celluloid import Camera
import os
from time import time

plt.style.use('ggplot')

state_dict = {
    'susceptible': 0,
    'incubation': 1,
    'symptomatic': 2,
    'recovered': 3,
    'deceased': 4,
    'self_quarantined': 5
}

outbreak_start_date = '2020-01-01'
population_rt = 130 # population = population_rt**2
population = population_rt**2
r_naught = 1.9 # transmission factor
fataity_rate = 0.002 # probability of death (post infection)
hospital_capacity = 0.2*population # as a percentage of the population
self_quarantine_rate = 0.3 # percentage (susceptible) population self quarantined
self_quarantine_strictness = 0.7
self_quarantine_start_buffer = 0.2*population # percentage symptomatic population after which self quarantine starts
encounters_per_day = 2 # avg encounters per day
travel_radius = 23 # as percentage of units of the world (1 unit = 1 square)
incubation_period = 6 # days with presymptomatic behaviour
symptomatic_days = 4 # after which a patient either recovers or dies

class Human():
    def __init__(self, state, days_exposed, days_sick, quarantine):
        self.state = state
        self.days_exposed = days_exposed
        self.days_sick = days_sick
        self.quarantine = quarantine

cvals  = [0, 1, 2, 3, 4, 5]
colors = ['lightgray', 'pink', 'red', 'green', 'black', 'blue']
norm=plt.Normalize(min(cvals),max(cvals))
tuples = list(zip(map(norm,cvals), colors))
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", tuples)

def plot_world_grid(grid, camera, cmap=cmap, norm=norm):
    grid = [[i.state for i in j] for j in world_grid]
    if camera is None:
        plt.figure(figsize=(12, 12))
    plt.imshow(grid, cmap=cmap, norm=norm, interpolation='none', aspect='equal')
    ax=plt.gca()
    ax.set_xticks(np.arange(-.5, len(grid), 1))
    ax.set_yticks(np.arange(-.5, len(grid), 1))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid(color='w', linestyle='-', linewidth=1, alpha=0.7)
    if camera is not None:
        camera.snap()
    return

world_grid = []
patient_zero = (np.random.randint(0, population_rt-1), np.random.randint(0, population_rt-1))

for i in range(population_rt):
    row_grid = []
    for j in range(population_rt):
        if i == patient_zero[0] and j == patient_zero[1]:    
            this_human = Human(state=1, days_exposed=1, days_sick=0, quarantine=False)
        else:
            this_human = Human(state=0, days_exposed=0, days_sick=0, quarantine=False)
        row_grid.append(this_human)
        
    world_grid.append(row_grid)
plot_world_grid(world_grid.copy(), None)

def get_neighours(grid, pos, size, k):
    i, j = pos
    list_neighbours = []
    
    candidates = [(i-k, j-k), (i-k, j), (i-k, j+k), 
                  (i, j+k), 
                  (i+k, j+k), (i+k, j), (i+k, j-k), 
                  (i, j-k)]
    for (r, c) in candidates:
        if 0<=r<len(grid) and 0<=c<len(grid) and grid[r][c] == 0:
            list_neighbours.append((r, c))
            
    list_neighbours = random.sample(list_neighbours, min(len(list_neighbours), size))
            
    return list_neighbours


logger = pd.DataFrame(columns=['Date', 'Total Susceptible', 'Total Exposed', 'Total Sick', 'Total Recovered', 'Total Dead', 'Total SelfQuarantined'])
init_date = pd.to_datetime(outbreak_start_date)
logger = logger.append({
    'Date': str(init_date.date()),
    'Total Susceptible': len(list(zip(*np.where(np.array([[i.state for i in j] for j in world_grid])==0)))),
    'Total Exposed': len(list(zip(*np.where(np.array([[i.state for i in j] for j in world_grid])==1))))
}, sort=False, ignore_index=True)

fig = plt.figure(figsize=(12, 12))
camera = Camera(fig)
plot_world_grid(world_grid.copy(), camera)
self_quar_flag = False
temp_fatality_rate = fataity_rate
r_naught_variation = list(set([int(round(i)) for i in np.random.normal(r_naught, 0.4, size=1000)]))

T = time()

print('Simulating the pandemic...')

while True:
    
    if len(list(zip(*np.where(np.isin(np.array([[i.state for i in j] for j in world_grid]), [1, 2]))))) == 0:
        break
    
    init_date = init_date + pd.offsets.DateOffset(days=1)
    
    for (r, c) in list(zip(*np.where(np.array([[i.state for i in j] for j in world_grid])==2))):
        world_grid[r][c].days_exposed += 1
        world_grid[r][c].days_sick += 1
        if world_grid[r][c].days_sick >= symptomatic_days:
            world_grid[r][c].state = np.random.choice(a=[3, 4], p=[1-fataity_rate, fataity_rate])            
    
    for (r, c) in list(zip(*np.where(np.array([[i.state for i in j] for j in world_grid])==1))):
        world_grid[r][c].days_exposed += 1
        if world_grid[r][c].days_exposed >= incubation_period:
            world_grid[r][c].state = 2
            world_grid[r][c].days_sick = 1
    
    list_symptomatic = list(zip(*np.where(np.isin(np.array([[i.state for i in j] for j in world_grid]), [1, 2]))))
    
    for (r, c) in list_symptomatic:
        for (i, j) in get_neighours(np.array([[i.state for i in j] for j in world_grid]), (r, c), int(np.random.choice(r_naught_variation)), np.random.choice(a=list(range(1, travel_radius+1)), p=np.array(pd.Series([1/i for i in range(1, travel_radius+1)])/sum([1/i for i in range(1, travel_radius+1)])).tolist())):
            world_grid[i][j].state = 1
            world_grid[i][j].days_exposed = 1    
    
    total_susceptible = len(list(zip(*np.where(np.array([[i.state for i in j] for j in world_grid])==0))))
    total_exposed = len(list(zip(*np.where(np.array([[i.state for i in j] for j in world_grid])==1))))
    total_sick = len(list(zip(*np.where(np.array([[i.state for i in j] for j in world_grid])==2))))
    total_recovered = len(list(zip(*np.where(np.array([[i.state for i in j] for j in world_grid])==3))))
    total_deceased = len(list(zip(*np.where(np.array([[i.state for i in j] for j in world_grid])==4))))
    total_sq = len(list(zip(*np.where(np.array([[i.state for i in j] for j in world_grid])==5))))
    
    logger = logger.append({
        'Date': str(init_date.date()),
        'Total Susceptible': total_susceptible,
        'Total Exposed': total_exposed,
        'Total Sick': total_sick,
        'Total Recovered': total_recovered,
        'Total Dead': total_deceased,
        'Total SelfQuarantined': total_sq 
    }, sort=False, ignore_index=True)
    
    if total_sick >= hospital_capacity:
        fataity_rate = min(0.6, (fataity_rate * 2))
    else:
        fataity_rate = temp_fatality_rate
        
    if total_sick >= self_quarantine_start_buffer or self_quar_flag:
        self_quar_flag = True
        for (r, c) in list(zip(*np.where(np.array([[i.state for i in j] for j in world_grid])==0))):
            world_grid[r][c].state = np.random.choice(a=[0, 5], p=[1-(self_quarantine_rate*self_quarantine_strictness), (self_quarantine_strictness*self_quarantine_rate)])
            
    plot_world_grid(world_grid.copy(), camera)


print('Simulation time:', round(time()-T, 2), 's')

logger.fillna(0, inplace=True)
logger.shape
logger.describe()
logger.to_parquet('logger.parquet')

if os.path.exists('visual.gif'):
    os.remove('visual.gif')
animation = camera.animate(interval=1500, blit=True, repeat_delay=7000)
animation.save('visual.gif', writer=PillowWriter(fps=5, bitrate=2000))


def plot_graph(df):
    plt.figure(figsize=(16, 5))
    plt.plot(df['Date'], df['Total Exposed'], color='pink')
    plt.plot(df['Date'], df['Total Sick'], color='red')
    plt.plot(df['Date'], df['Total Recovered'], color='green')
    plt.plot(df['Date'], df['Total Dead'], color='black')
    plt.plot(df['Date'], df['Total SelfQuarantined'], color='blue')
    plt.legend(['Total Exposed', 'Total Sick', 'Total Recovered', 'Total Dead', 'Total SelfQuarantined'])
    plt.xticks(rotation=90)
    plt.show()
    return

print('Self Quarantined: ' + str(round((logger['Total SelfQuarantined'].values[-1]/population)*100))+'%')
print('Deaths: ' + str(round((logger['Total Dead'].values[-1]/population)*100))+'%')

plot_graph(logger.copy())