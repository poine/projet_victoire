import numpy as np, matplotlib.pyplot as plt
import jsbsim
import mpl_toolkits.basemap
import pdb

import pat3.plot_utils as p3_pu, pat3.atmosphere as p3_atm

# format of the csv file
columns = ['Time', 'ALTITUDE STD [FT] [FT]', 'COMPUTED AIRSPEED [KT] [KT]',
           'CAPT DISPLAY PITCH ATT (>0= nose up) [DEG]', 'CAPT DISPLAY HEADING [DEG]',
           'CAPT DISPLAY ROLL ATT (>0 = right wing down) [DEG]',
           'LONGITUDINAL ACCELERATION [G] (>0 = acceleration) [G\'s]',
           'LATERAL ACCELERATION [G] (>0 = left side slip) [G\'s]',
           'VERTICAL ACCELERATION (>0 = nose up) [G]',
           '(FDR) Longitude [°]', '(FDR) Latitude [°]']
c_time, c_alt, c_va, c_theta, c_psi, c_phi, c_ax, c_ay, c_az, c_lon, c_lat, c_nb = range(12)
# sensor's characteristics
freqs = [1., 1.,  4., 2., 4., 4., 4., 8., 1., 1.]
stds =  [2., 0.8, 0., 0., 0., 0., 0., 0., 0., 0.]


# plot autopilot inner variables
def plot_dbg(traj_df, dbg):
    fig = plt.figure(tight_layout=True, figsize=[16., 9.])
    nplots = 4
    axes = fig.subplots(nplots, 1, sharex=True)
    for i in range(nplots):
        axes[i].plot(traj_df['Time'], dbg[:,i], '.')
    return fig, axes
    

def plot_chronograms(traj_df):
    fig = plt.figure(tight_layout=True, figsize=[16., 9.])
    nplots = len(traj_df.columns)-1
    axes = fig.subplots(nplots, 1, sharex=True)
    for i in range(nplots):
        axes[i].plot(traj_df['Time'], traj_df[traj_df.columns[i+1]], '.')
        p3_pu.decorate(axes[i], legend=[traj_df.columns[i+1]])
    axes[-1].xaxis.set_label_text('time in s')
    return fig, axes

def plot_map(traj_df, _scen=None):
    # find trajectory's extends
    lon_min, lon_max = traj_df.min()[columns[-2]], traj_df.max()[columns[-2]] 
    lat_min, lat_max = traj_df.min()[columns[-1]], traj_df.max()[columns[-1]]
    # add margin
    lon_min -=0.5; lon_max +=0.5
    lat_min -=0.5; lat_max +=0.5
    fig = plt.figure(tight_layout=True, figsize=[16., 9.])
    axes = fig.subplots(1, 1)
    m = mpl_toolkits.basemap.Basemap(llcrnrlon=lon_min, llcrnrlat=lat_min, urcrnrlon=lon_max, urcrnrlat=lat_max,
                                     rsphere=(6378137.00,6356752.3142),\
                                     resolution='l',projection='merc',\
                                     lat_0=lat_min,lon_0=lon_min,lat_ts=20.)
    if _scen is not None:
        for _wp, _n in zip(_scen.waypoints, _scen.wp_names):
            x, y = m(_wp[1], _wp[0])
            print(_wp, x, y)
            x2, y2 = (-20, 10)
            # plt.text(x, y, _n,fontsize=12,fontweight='bold',
            #          ha='left',va='center',color='k',
            #          bbox=dict(facecolor='b', alpha=0.2))
            plt.annotate(_n, xy=(x, y),  xycoords='data',
                         xytext=(x2, y2), textcoords='offset points',
                         color='r',
                         arrowprops=dict(arrowstyle="fancy", color='g')
            )

    longs, lats = traj_df[columns[-2]].dropna().to_numpy(), traj_df[columns[-1]].dropna().to_numpy()
    #pdb.set_trace()
    m.plot(longs, lats, color='r', latlon=True)
    
    #m.drawgreatcircle(lon_min,lat_min, lon_max,lat_max, linewidth=2,color='b')
    try:
        m.drawcoastlines()
    except ValueError:
        pass # no coast?
    m.drawcountries()
    m.drawmapboundary(fill_color='#99ffff')
    m.fillcontinents(color='#cc9966',lake_color='#99ffff')
    return fig, axes

def _analyse_sensor_timing(traj_df):
    # compute sampling frequencies
    dts, dts_spec = [], []
    for i in range(len(traj_df.columns)-1):
        col = traj_df[traj_df.columns[i+1]]
        ts = traj_df['Time'][np.isfinite(col)].to_numpy()
        dts.append(ts[1:]-ts[:-1]) # compute sampling intervals
        dts_spec.append((np.mean(dts[-1]), np.std(dts[-1])))
        #print(f'{traj_df.columns[i+1]}: {dts_spec[-1][0]:.3f} s {1./dts_spec[-1][0]:.3f} hz')
    return dts, dts_spec

def analyse_sensor(traj_df, sid, roi):
   dts, dts_spec = _analyse_sensor_timing(traj_df)

   samples = traj_df[columns[sid+1]].iloc[roi]
   times = traj_df[columns[0]].iloc[roi]
   std, mean = samples.std(), samples.mean()

   fig = plt.figure(tight_layout=True, figsize=[16., 9.])
   fig.canvas.set_window_title(f'{columns[sid+1]}')
   axes = fig.subplots(1, 3)
   axes[0].hist(dts[sid])
   p3_pu.decorate(axes[0], 'Sample time distribution', legend=[f'mean:{dts_spec[sid][0]}\nstd{dts_spec[sid][1]}'])
   axes[1].plot(times, samples, '.')
   p3_pu.decorate(axes[1], xlab='time in s')
   axes[2].hist(samples)
   p3_pu.decorate(axes[2], 'Samples distribution', legend=[f'std:{std}\nmean:{mean}'])
   return fig, axes

# running fdm without a script... bleee
def run_simulation(tf=100.):
    PATH_TO_JSBSIM_FILES="/home/poine/src/jsbsim"
    fdm = jsbsim.FGFDMExec(PATH_TO_JSBSIM_FILES)
    fdm.load_model('737')
    fdm['propulsion/engine[0]/set-running'] = 1
    fdm['propulsion/engine[1]/set-running'] = 1
    fdm['gear/gear-cmd-norm'] = 0
    fdm['gear/gear-pos-norm'] = 0
    fdm['ic/h-sl-ft'] = 30000
    fdm['ic/mach'] = 0.78
    fdm['ic/gamma-deg'] = 0
    fdm.run_ic()
    print( fdm.get_sim_time())
    fdm.run()
    print( fdm.get_sim_time())
    fdm.run()
    print( fdm.get_sim_time())
    fdm['simulation/do_simple_trim'] = 1
    
    dt = fdm.get_delta_t()
    time = np.arange(0, tf, dt)
    res = np.zeros((len(time), 11))
    fdm['ap/altitude_setpoint'] = 29000
    fdm['ap/altitude_hold'] = 1
    fdm['ap/heading_setpoint_deg'] = 45.
    fdm['ap/heading_hold'] = 1
    print(f'running {time[-1]-time[0]:.1f}s simulation at {1/dt:.1f}hz')
    for i,t in enumerate(time):
        fdm.run()
        lla = fdm['position/long-gc-deg'], fdm['position/lat-geod-deg'], fdm['position/geod-alt-ft']
        vels = fdm['velocities/vc-kts'], fdm['aero/alpha-deg']
        euls = fdm['attitude/phi-deg'], fdm['attitude/theta-deg'], fdm['attitude/psi-deg']
        accels = fdm['accelerations/Nx'], fdm['accelerations/Ny'], fdm['accelerations/Nz']
        res[i] = fdm.get_sim_time(), lla[2], vels[0], euls[1], euls[2], euls[0], *accels, lla[0], lla[1]
    print(f'done') 
    return fdm, res


# running fdm with a script, yay!!!
def run_simulation2(script_filename, tf, dbg=False):
    PATH_TO_JSBSIM_FILES="/home/poine/src/jsbsim"
    fdm = jsbsim.FGFDMExec(PATH_TO_JSBSIM_FILES) # this is needed for aircraft definitions ?
    fdm.load_script(script_filename)

    atm = p3_atm.AtmosphereCstWind()
    
    dt = fdm.get_delta_t(); time = np.arange(0, tf, dt)
    res = np.zeros((len(time), c_nb))
    if dbg: _dbg = np.zeros((len(time), 4))
    fdm.run_ic()

    i=0
    while fdm.run() and i<len(res):
        lla = fdm['position/long-gc-deg'], fdm['position/lat-geod-deg'], fdm['position/geod-alt-ft']
        vels = fdm['velocities/vc-kts'], fdm['aero/alpha-deg']
        euls = fdm['attitude/phi-deg'], fdm['attitude/theta-deg'], fdm['attitude/psi-deg']
        accels = fdm['accelerations/Nx'], fdm['accelerations/Ny'], fdm['accelerations/Nz']
        wind_ned = (0, 0, 0)#atm.get_wind_ned((0, 0, 0), 0)
        #for i, wcmp in enumerate(['atmosphere/wind-north-fps', 'atmosphere/wind-east-fps', 'atmosphere/wind-down-fps']):
        #    fdm[wcmp] = wind_ned[i]
        #print(fdm['ap/altitude_hold'], fdm['ap/altitude_setpoint'], fdm['ap/throttle-cmd-norm'], fdm['ap/active-waypoint'])
        #print(fdm['ap/airspeed_setpoint'], ap/airspeed_hold
        res[i] = fdm.get_sim_time(), lla[2], vels[0], euls[1], euls[2], euls[0], *accels, lla[0], lla[1]
        if dbg: _dbg[i] = fdm['ap/altitude_hold'], fdm['ap/altitude_setpoint'], fdm['ap/throttle-cmd-norm'], fdm['ap/active-waypoint']
        i+=1

    if i < len(res): # truncate
        res = res[:i]
        if dbg: _dbg = _dbg[:i]
        print(f'finished early {i*dt} < {tf}')
    #pdb.set_trace()
    return (fdm, res, _dbg) if dbg else (fdm, res)
    #return fdm, res  
