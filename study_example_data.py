#! /usr/bin/env python3
'''
Analysing Victoire's original dataset
'''
import numpy as np, matplotlib.pyplot as plt
import pandas as pd
import pdb

import victoire_utils as v_ut
import pat3.plot_utils as p3_pu

traj_df = pd.read_csv("/home/poine/work/victoire/B737.csv", sep=';', decimal=",", encoding='latin_1')#, nrows=1e3)
#traj_df.rename(columns={"ALTITUDE STD [FT] [FT]": "alt", "COMPUTED AIRSPEED [KT] [KT]": "cas"}, inplace=True)
print(traj_df.info())

pdb.set_trace()
#print(traj_df.columns)
#print(traj_df.columns)
#print(traj_df.dtypes)
#print(traj_df)
#print(traj_df['Time'])
if 1:
    v_ut.plot_map(traj_df); plt.savefig('/tmp/orig_b737_map.png')
if 1:
    fig, axes = v_ut.plot_chronograms(traj_df); plt.savefig('/tmp/orig_b737_chrono.png')
if 1:
    sid, roi = 0, slice(20000,22000)
    fig, axes = v_ut.analyse_sensor(traj_df, sid, roi); plt.savefig('/tmp/orig_b737_alt.png')
# sid, roi = 1, slice(20000,22000)
# fig, axes = v_ut.analyse_sensor(traj_df, sid, roi)
# sid, roi = 2, slice(20000,22000)
# fig, axes = v_ut.analyse_sensor(traj_df, sid, roi)
# sid, roi = 3, slice(20000,22000)
# fig, axes = v_ut.analyse_sensor(traj_df, sid, roi)
# sid, roi = 4, slice(20000,22000)
# fig, axes = v_ut.analyse_sensor(traj_df, sid, roi)
# sid, roi = 5, slice(20000,22000)
# fig, axes = v_ut.analyse_sensor(traj_df, sid, roi)
# sid, roi = 6, slice(20000,22000)
# fig, axes = v_ut.analyse_sensor(traj_df, sid, roi)
# sid, roi = 7, slice(20000,22000)
# fig, axes = v_ut.analyse_sensor(traj_df, sid, roi)
# sid, roi = 8, slice(20000,22000)
# fig, axes = v_ut.analyse_sensor(traj_df, sid, roi)


plt.show()
