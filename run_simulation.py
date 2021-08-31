#! /usr/bin/env python3
'''

'''
import jsbsim
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pdb

import pat3.plot_utils as p3_pu
import victoire_utils as v_ut

# run aircraft simulation
#fdm, res = v_ut.run_simulation(tf=120.)
#fdm, res = v_ut.run_simulation2('/home/poine/src/jsbsim/scripts/c3104.xml', tf=600.)
fdm, res = v_ut.run_simulation2('/home/poine/work/projet_victoire/scenario_2.xml', tf=2000.)

truth_df = pd.DataFrame(res, index=res[:,0], columns=v_ut.columns)

# run sensors simulation
# decimate
scalers = np.rint(1./fdm.get_delta_t()/np.array(v_ut.freqs))
nt, ns = res.shape[0], res.shape[1]-1 
for it in range(nt):
    for i in range(ns):
        if it%scalers[i]!=0: res[it,i+1] = np.nan
# add noise
rng = np.random.default_rng()
for i in range(ns):
    res[:,i+1] += v_ut.stds[i]*rng.standard_normal(len(res))
# quantize ?

#pdb.set_trace()
sens_df = pd.DataFrame(res, index=res[:,0], columns=v_ut.columns)
#print(sens_df.info())
with open('/tmp/foo.csv', 'w') as _f:
    _f.write(sens_df.to_csv(sep=';', decimal=",", encoding='latin_1'))

if 1:
    fig, axes = v_ut.plot_chronograms(sens_df); plt.savefig('/tmp/c310_chrono.png')
if 1:
    sid, roi = 0, slice(4000,8000)
    fig, axes = v_ut.analyse_sensor(sens_df, sid, roi); plt.savefig('/tmp/c310_alt.png')
if 1:
    v_ut.plot_map(sens_df); plt.savefig('/tmp/c310_map.png')
    
plt.show()


