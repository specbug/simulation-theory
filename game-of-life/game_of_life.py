#!/usr/bin/env python
# coding: utf-8

# In[101]:


import sys
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors
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
from IPython.display import HTML

plt.style.use('ggplot')


# In[102]:

print(sys.argv)

prun = sys.argv[1]
population_rt = int(sys.argv[2]) # population root
epochs = int(sys.argv[3]) # no. of ticks
p_life = float(sys.argv[4]) # seed prob of life
g_fig_size = (12, 12) # fig size


# In[103]:


life_board = np.random.choice([0, 1], p=[1-p_life, p_life], size=(population_rt, population_rt))
life_board.shape


# In[104]:


life_board[:5, :5]


# In[105]:


def plot_world_grid(grid, camera, n_colors=2, fig_shape=g_fig_size):
    if camera is None:
        plt.figure(figsize=fig_shape)
    cmap = colors.ListedColormap([(0.93, 0.93, 0.93), (1., 0.27, 0.27), (1., 0.87, 0.89), (0.6, 0.6, 0.6)], N=n_colors)
    plt.pcolor(grid[::-1], cmap=cmap, edgecolors='w', linewidths=1)
    ax = plt.gca()
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    if camera is not None:
        camera.snap()
    return


# In[106]:


plot_world_grid(life_board.copy(), None)


# In[98]:


def get_neighours(grid, pos, k=1):
    i, j = pos
    list_neighbours = []
    
    candidates = [(i-k, j-k), (i-k, j), (i-k, j+k), 
                  (i, j-k), (i, j+k), 
                  (i+k, j-k), (i+k, j), (i+k, j+k)]
    for (r, c) in candidates:
        if 0<=r<len(grid) and 0<=c<len(grid):
            list_neighbours.append((r, c))
            
    return list_neighbours


# In[99]:


life_board_sim = life_board.copy()
fig = plt.figure(figsize=g_fig_size)
camera = Camera(fig)
plot_world_grid(life_board_sim.copy(), camera)

for _ in range(epochs):
    print(f'{"#"*10} Epoch {_}')
    for i in range(population_rt):
        for j in range(population_rt):
            field_value = sum([life_board[n] for n in get_neighours(life_board.copy(), (i, j))])
            if field_value in [2, 3]:
                if life_board[i][j] == 0 and field_value == 3:
                    life_board_sim[i][j] = 1
            else:
                life_board_sim[i][j] = 0
    plot_world_grid(life_board_sim.copy(), camera)
    life_board = life_board_sim.copy()
    if life_board.sum() == 0:
        break


# In[100]:


if os.path.exists(f'visual_{prun}.gif'):
    os.remove(f'visual_{prun}.gif')
animation = camera.animate(interval=10, blit=False)
animation.save(f'visual_{prun}.gif', writer=PillowWriter(fps=7, bitrate=20))

