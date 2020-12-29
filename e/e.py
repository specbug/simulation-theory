#!/usr/bin/env python
# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from time import time

def ci(mean, std, n, confidence=0.95):
    z_val = round(stats.norm.ppf(confidence+((1-confidence)/2)), 3)
    return round(mean - z_val * std / np.sqrt(n), 5), round(mean + z_val * std / np.sqrt(n), 5)

def get_n(std, n, w=0.001, confidence=0.95):
    z_val = round(stats.norm.ppf(confidence+((1-confidence)/2)), 3)
    return int(np.ceil(((2*z_val*std)/w)**2))

def sim_e(iterations):
    sim_logger = []
    
    for i in range(1, iterations+1):
        r_v = 0
        n = 0
        while r_v<=1.0:
            r_v += np.random.uniform()
            n += 1
        sim_logger.append(n)
        
    return sim_logger

# init simulation
iterations = 10000
T0 = time()
sim_logger = sim_e(iterations)
print('Simulation time for', iterations, 'iterations:', round(time()-T0, 3), 's\n')

sim_loc = np.mean(sim_logger)
sim_scale = round(np.std(sim_logger), 4)
sim_ci = ci(sim_loc, sim_scale, iterations)
w = 0.01
optimal_n = get_n(sim_scale, iterations, w=w)
print('Value of e after', iterations, 'iterations:', sim_loc , '±', sim_scale)
print('95% Confidence interval: '+ str(sim_ci) + ' [' + str(round(sim_ci[1]-sim_ci[0], 5)) + ']')
print('Required iterations to achieve a narrower width (say '+str(w)+'): ' + str(optimal_n))

print('\n' + '-'*50 + '\n')

# simulating again for a narrower variance
print('Simulating again with optimal iterations...')
T0 = time()
sim_logger = sim_e(optimal_n)
print('Simulation time for', optimal_n, 'iterations:', round(time()-T0, 3), 's\n')

sim_loc = np.mean(sim_logger)
sim_scale = round(np.std(sim_logger), 4)
sim_ci = ci(sim_loc, sim_scale, optimal_n)
print('Value of e after', optimal_n, 'iterations:', sim_loc , '±', sim_scale)
print('95% Confidence interval: '+ str(sim_ci) + ' [' + str(round(sim_ci[1]-sim_ci[0], 5)) + ']')

plt.figure(figsize=(16, 5))
plt.plot(np.cumsum(np.array(sim_logger))/range(1, len(sim_logger)+1), c='r')
plt.xlabel('iteration')
plt.legend(['e'])
plt.show()
