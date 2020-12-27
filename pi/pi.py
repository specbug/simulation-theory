#!/usr/bin/env python
# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
from time import time
plt.rcParams['figure.figsize'] = 16, 5

iterations = int(1e2)
n = int(1e5)

def random_sample(i, n):
    local_state = np.random.RandomState(seed=i)
    x = 1-2. * local_state.uniform(0, 1.001, n)
    y = 1-2. * local_state.uniform(0, 1.001, n)
    return 4*sum(x*x+y*y<=1)/n

T10 = time()
sim_logger = Parallel(n_jobs=-1)(delayed(random_sample)(i, n) for i in range(iterations))
print('Simulation time:', round(time()-T10, 3), 's')

sim_graph = np.cumsum(np.array(sim_logger))/range(1, len(sim_logger)+1)
print('\n'.join(['Value of PI after iteration '+str(i+1)+': '+str(p) for i, p in enumerate(sim_graph)]))

plt.figure()
plt.plot(np.cumsum(np.array(sim_logger))/range(1, len(sim_logger)+1))
plt.show()

'''
fig, ax = plt.subplots(1, sharex=True, sharey=True)
plt.scatter(inside_X, inside_Y, c='b', alpha=0.8, axes=ax)
plt.scatter(outside_X, outside_Y, c='r', alpha=0.8, axes=ax)
plt.title('1M')
plt.show()

fig.savefig('pi.png')
'''
