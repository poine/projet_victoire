#! /usr/bin/env python3
'''

'''
import sys, argparse, logging
import numpy as np, pandas as pd, matplotlib.pyplot as plt
import jsbsim

import pdb

#import pat3.plot_utils as p3_pu
import victoire_utils as v_ut

LOG = logging.getLogger(__name__)

XML_NOTIFY = '''<notify format="kml">
        <property caption="Latitude        "> position/lat-geod-deg </property>
        <property caption="Longitude       "> position/long-gc-deg  </property>
        <property caption="Altitude        "> position/h-agl-ft     </property>
        <property caption="Airspeed (keas) "> velocities/ve-kts     </property>
        <property caption="Distance to WP  "> guidance/wp-distance  </property>
      </notify>
'''

class Scenario:
    def __init__(self):
        self.name = 'C310-01A takeoff run'
        self.description = 'For testing autopilot capability'
        self.aircraft = 'c310'
        self.initialize = 'ellington'
        self.time_step = 0.02
        self.max_duration = 3600
        self.waypoints = []
        
        

    def _write_waypoint(self, _id, _pass_dist=700.):
        _txt = f'''
    <event name="Set waypoint {_id+1}">
      <description>
        When closer than { _pass_dist} feet to waypoint {_id} {self.wp_names[_id-1]}, set waypoint {_id+1} {self.wp_names[_id]}.
        and alt {self.alts[_id]} feet
      </description>
      <condition>
        guidance/wp-distance lt 700
        ap/active-waypoint eq {_id}
      </condition>
      <!--<set name="ap/altitude_setpoint" action="FG_EXP" value="{self.alts[_id]:.1f}" tc="10.0"/>-->
      <set name="ap/altitude_setpoint" value="{self.alts[_id]:.1f}"/>
      <set name="guidance/target_wp_latitude_rad" value="{np.deg2rad(self.waypoints[_id][0])}"/>
      <set name="guidance/target_wp_longitude_rad" value="{np.deg2rad(self.waypoints[_id][1])}"/>
      <set name="ap/active-waypoint" value="{_id+1}"/>
      {XML_NOTIFY}
    </event>
'''
        return _txt

        
    def write_xml(self, filename):
        _hdr = f'''<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="http://jsbsim.sf.net/JSBSimScript.xsl"?>
<runscript xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:noNamespaceSchemaLocation="http://jsbsim.sf.net/JSBSimScript.xsd"
    name="{self.name}">
    
  <description>{self.description}</description>
  <use aircraft="{self.aircraft}" initialize="{self.initialize}"/>
  
  <run start="0.0" end="{self.max_duration}" dt="{self.time_step}">
'''


        _takeoff = f'''
  <event name="Start engine">
      <description>
        Start engine and set initial heading and waypoints, turn on heading-hold mode.
      </description>
      <condition>simulation/sim-time-sec  ge  0.25</condition>
      <set name="fcs/mixture-cmd-norm[0]" value="1"/>
      <set name="fcs/mixture-cmd-norm[1]" value="1"/>
      <set name="fcs/advance-cmd-norm[0]" value="1.0"/>
      <set name="fcs/advance-cmd-norm[1]" value="1.0"/>
      <set name="propulsion/magneto_cmd" value="3"/>
      <set name="fcs/throttle-cmd-norm[0]" value="1.0"/>
      <set name="fcs/throttle-cmd-norm[1]" value="1.0"/>
      <set name="propulsion/starter_cmd" value="1"/>
      <!--<set name="ap/altitude_setpoint" action="FG_EXP" value="{self.alts[0]}" tc="10.0"/>-->
      <set name="ap/altitude_setpoint" value="{self.alts[0]}"/>
      <set name="ap/attitude_hold" value="0"/>
      <set name="guidance/target_wp_latitude_rad" value="{np.deg2rad(self.waypoints[0][0])}"/>
      <set name="guidance/target_wp_longitude_rad" value="{np.deg2rad(self.waypoints[0][1])}"/>
      <set name="ap/heading_setpoint" value="0"/>
      <set name="ap/heading-setpoint-select" value="0"/>
      <set name="ap/heading_hold" value="1"/>
      <set name="ap/active-waypoint" value="0"/>
      <notify format="kml">
        <property caption="Latitude       "> position/lat-geod-deg </property>
        <property caption="Longitude      "> position/long-gc-deg </property>
        <property caption="Airspeed (keas)"> velocities/ve-kts </property>
      </notify>
    </event>

    <event name="Enable altitude hold (preconfigured to {self.alts[0]} ft).">
      <condition>velocities/vc-fps ge 145.0</condition>
      <set name="ap/altitude_hold" value="1"/>
      <notify format="kml">
        <property caption="Latitude       "> position/lat-geod-deg </property>
        <property caption="Longitude      "> position/long-gc-deg </property>
        <property caption="Airspeed (keas)"> velocities/ve-kts </property>
      </notify>
    </event>
    
    <event name="Raise landing gear">
      <condition>position/h-agl-ft  ge  40</condition>
      <set name="gear/gear-cmd-norm" value="0"/>
      <notify format="kml">
        <property caption="Latitude       "> position/lat-geod-deg </property>
        <property caption="Longitude      "> position/long-gc-deg </property>
        <property caption="Airspeed (keas)"> velocities/ve-kts </property>
      </notify>
    </event>
    
    <event name="Head to first waypoint">
      <description>
        Set heading hold to selected waypoint (setpoint) instead of
        previously specified heading when altitude surpasses 800 feet.
      </description>
      <condition>position/h-agl-ft  ge  800</condition>
      <set name="ap/heading-setpoint-select" value="1"/>
      <set name="ap/active-waypoint" value="1"/>
      <notify format="kml">
        <property caption="Latitude        "> position/lat-geod-deg </property>
        <property caption="Longitude       "> position/long-gc-deg  </property>
        <property caption="Altitude        "> position/h-agl-ft     </property>
        <property caption="Airspeed (keas) "> velocities/ve-kts     </property>
        <property caption="Distance to WP  "> guidance/wp-distance  </property>
      </notify>
    </event>
'''
        _end = f'''
    <event name="Terminate">
      <description>
        Terminate simulation when the aircraft reaches last waypoint.
      </description>
      <condition>
        guidance/wp-distance lt 500
        ap/active-waypoint eq {len(self.waypoints)}
      </condition>
      <set name="simulation/terminate" value="1"/>
      <notify format="kml">
        <property caption="Latitude       "> position/lat-geod-deg </property>
        <property caption="Longitude      "> position/long-gc-deg </property>
        <property caption="Airspeed (keas)"> velocities/ve-kts </property>
      </notify>
    </event>
'''
        _footer = '''  </run>
</runscript>
'''
        LOG.info(f' saving xml to {filename}')
        with open(filename, 'w') as _f:
            _f.write(_hdr)
            _f.write(_takeoff)
            for _i in range(len(self.waypoints)-1, 0, -1):
                print(_i)
                _f.write(self._write_waypoint(_i))
            # order of events matters! wtf???
            #for _i, _wp in enumerate(self.waypoints[1:]):
            #    _f.write(self._write_waypoint(_i+1))
            _f.write(_end)
            _f.write(_footer)


#
#
ELLINGTON_1 = np.rad2deg([0.517238, -1.662727]) # from demo c310 scenario
ELLINGTON_2 = np.rad2deg([0.517533, -1.663076]) 
ELLINGTON_3 = np.rad2deg([0.507481, -1.660062]) 
ELLINGTON_4 = np.rad2deg([0.511661, -1.653510]) 
ELLINGTON_5 = np.rad2deg([0.516512, -1.660922]) 

class Scenario1(Scenario):
    def __init__(self):
        Scenario.__init__(self)
        self.name = 'Ellington local'
        self.initialize = 'ellington'
        #self.waypoints = [ELLINGTON_1, ELLINGTON_3, ELLINGTON_4, ELLINGTON_5]
        #self.alts      = [1000,               3000,        4000,        5000]
        #self.wp_names  = ['EL1', 'EL3', 'EL4', 'EL5']
        #self.waypoints = [ELLINGTON_1, ELLINGTON_2, ELLINGTON_3, ELLINGTON_4]
        #self.alts      = [1000,        1500,        3000,        4000,      ]
        self.waypoints = [ELLINGTON_1, ELLINGTON_3, ELLINGTON_4]
        self.wp_names  = ['EL1', 'EL3', 'EL4']
        self.alts      = [1200,  5000, 3000]
        self.max_duration = 1*3600
        self.filename = '/home/poine/work/projet_victoire/scenario/scenario_1.xml'


#
# Toulouse - Strasbourg :
# LFBO (TLS) → montée jusqu’à FL160 à Rodez (RZ387) → changement palier LFLN Saint Yan FL200 →
# changement palier FL180 à DJL Dijon → LFGY (descente) →  LFST (SXB)
# FIXME - find real values, i only clicked google map
LFBO_32L = (43.619056, 1.372071)
RODEZ_RZ387 = (44.408507, 2.481449)
LFLN_SAINT_YAN = (46.414853, 4.013574)
DJL_Dijon = (47.268010, 5.094683)
LFGY = (48.266553, 7.007686)
LFST = (48.537800, 7.627180)

class Scenario2(Scenario):
    def __init__(self):
        Scenario.__init__(self)
        self.name = 'Toulouse - Strasbourg'
        self.initialize = 'toulouse_32L'
        self.waypoints = [RODEZ_RZ387, LFLN_SAINT_YAN, DJL_Dijon, LFGY, LFST]
        self.wp_names  = ['RODEZ_RZ387', 'LFLN_SAINT_YAN', 'DJL_Dijon', 'LFGY', 'LFST']
        self.alts      = [5000,        10000,           15000,      3000, 1000]
        self.max_duration = 3*3600
        self.aircraft = 'c310'#'global5000'->fails
        self.filename = '/home/poine/work/projet_victoire/scenario/scenario_2.xml'

#
# Paris - Toulouse
# LFPO (ORY) → montée jusqu’à FL190 à CND  → AMB → changement de palier FL210 → LMG (Limoges) → GAI (descente) → LFBO (TLS)
#
class Scenario3(Scenario):
    def __init__(self):
        Scenario.__init__(self)
        self.name = 'Paris - Toulouse'
        self.initialize = 'toulouse_32L'
        self.waypoints = [RODEZ_RZ387, LFLN_SAINT_YAN, DJL_Dijon, LFGY, LFST]
        self.wp_names  = ['RODEZ_RZ387', 'LFLN_SAINT_YAN', 'DJL_Dijon', 'LFGY', 'LFST']
        self.alts      = [5000,        10000,           15000,      3000, 1000]
        self.max_duration = 3*3600
        self.aircraft = 'c310'#'global5000'->fails
        self.filename = '/home/poine/work/projet_victoire/scenario/scenario_3.xml'

#
# Montpellier - Nantes
# LFMT (MPL) → montée jusqu’à FL200 à MEN → changement palier FL180 à LFBE (BGC374) → la rochelle RL322 (descente) → LFRS (NTS)
class Scenario4(Scenario):
    def __init__(self):
        Scenario.__init__(self)
        self.name = 'Montpellier - Nantes'
        self.initialize = 'toulouse_32L'
        self.waypoints = [RODEZ_RZ387, LFLN_SAINT_YAN, DJL_Dijon, LFGY, LFST]
        self.wp_names  = ['RODEZ_RZ387', 'LFLN_SAINT_YAN', 'DJL_Dijon', 'LFGY', 'LFST']
        self.alts      = [5000,        10000,           15000,      3000, 1000]
        self.max_duration = 3*3600
        self.aircraft = 'c310'#'global5000'->fails
        self.filename = '/home/poine/work/projet_victoire/scenario/scenario_4.xml'

def main(scen_id):
    scen_name = f'Scenario{scen_id}'
    s = globals()[scen_name]()
    #s = Scenario()
    #s = Scenario1()
    #s = Scenario2()
    #s = Scenario3()
    #s = Scenario4()
    print(f'instanciated: {type(s).__name__}')
    s.write_xml(s.filename)


    

if __name__ == '__main__':
    np.set_printoptions(linewidth=500)
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Create a scenario.')
    parser.add_argument('--scen', help='id the scenario', default='1')
    args = parser.parse_args()
    main(args.scen)
