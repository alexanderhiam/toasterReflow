"""
 config.py
 toasterReflow configuration.
"""

INF = float('inf')

HEATER_ON = 1  
FAN_ON = 1

TIME_STEP_MS = 250

PID_KP = 2.0
PID_KI = 1.0
PID_KD = 0.0

# Calibration offset (temp = measured temp + TEMP_OFFSET):
TEMP_OFFSET = 2.365

PHASES = ('pre_soak', 'soak', 'ramp_up', 'peak', 'cool')


# These limits are not currently being used:
LIMITS = {
  "pre_soak" : {
    "tmin"     : [80, 100],
    "tmax"     : [150, 160],
    "dmin"     : [-INF, -INF],
    "dmax"     : [INF, INF],
    "slopemin" : [-INF, -INF],
    "slopemax" : [2.5, 2.5]
  },
  "soak" : {
    "tmin"     : [150, 180],
    "tmax"     : [180, 215],
    "dmin"     : [60, 60],
    "dmax"     : [120, 180],
    "slopemin" : [-INF, -INF],
    "slopemax" : [INF, INF]
  },
  "ramp_up" : {
    "tmin"     : [210, 230],
    "tmax"     : [260, 260],
    "dmin"     : [60, 60],
    "dmax"     : [150, 150],
    "slopemin" : [-INF, -INF],
    "slopemax" : [3, 3]
  },
  "peak" : {
    "tmin"     : [210, 230],
    "tmax"     : [260, 260],
    "dmin"     : [10, 20],
    "dmax"     : [40, 40],
    "slopemin" : [-INF, -INF],
    "slopemax" : [INF, INF]
  },
  "cool" : {
    "tmin"     : [100, 100],
    "tmax"     : [INF, INF],
    "dmin"     : [-INF, -INF],
    "dmax"     : [INF, INF],
    "slopemin" : [-6, -6],
    "slopemax" : [INF, INF]
  }
}
LEADED = 0
LEADFREE = 1

