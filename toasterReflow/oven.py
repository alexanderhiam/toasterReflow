"""
 This file provides the main Oven class. 
 Alexander Hiam

 Apache 2.0 license
"""

import sys

from config import *
from profiles import *
from PID import *

from bbio import *
#from MAX31855 import *
from fs9721 import Client

class Oven(object):
  def __init__(self, heater_pin, temp_cs, temp_clk, temp_data,  fan_pin=None):
    self.heater_pin = heater_pin
    self.fan_pin= fan_pin
    #self.thermocouple = MAX31855(temp_data, temp_clk, temp_cs, TEMP_OFFSET)
    self.thermocouple = Client('/dev/ttyUSB0')
    self.pid = PID(PID_KP, PID_KI, PID_KD)

    pinMode(heater_pin, OUTPUT)
    if (fan_pin): pinMode(fan_pin, OUTPUT)
    else: self.fan_state = "disabled"
    self.heatOff()
    self.fanOff()
    addToCleanup(self.stop)

    self.current_phase = ''
    self.current_step = 0

    self.realtime_data = []
    self.error = ''
    self.abort = False
    self.solder_type = LEADED

  def run(self, profile=None, solder_type=LEADED):
    """ Runs a single reflow cycle using the given profile if provided, or the 
        default profile for the given solder type. """
    self.abort = False
    self.error = ''
    if (not profile):
      if (solder_type == LEADED): profile = DEFAULT_LEADED
      elif (solder_type == LEADFREE): profile = DEFAULT_LEADFREE
    self.solder_type = solder_type

    reflow_map = self.generateMap(profile, solder_type)
    # Count the number of data points in the reflow map:
    n_points = 0
    for i in PHASES:
      n_points += len(reflow_map[i])

    # Initialize the realtime data array:
    self.realtime_data = []

    self.pid.reset()
    time_step_s = TIME_STEP_MS / 1000.0

    current_total_step = 0
    for phase in PHASES:
      self.current_phase = phase
      self.current_step = 0
      for target in reflow_map[phase]:

        if (self.abort):
          self.stop()
          self.error = "Manually aborted."
          print "**Reflow aborted!"
          return

        # Just using a 'bang-bang' type control for initial testing, I'll
        # switch to the PID soon:
        #state = self.pid.calculateState(self.getTemp(), i)
        temp = self.getTemp()
        if (temp == None):
          self.stop()
          self.error = self.thermocoule.error
          print self.error
          return
        # Record current temp:
        self.realtime_data.append([current_total_step*time_step_s, temp])
        # Bang-bang for now:
        if (temp < target):
          self.heatOn()
          self.fanOff()
          print "%s  -  temp: %f, target: %f  -  on" % (phase, self.getTemp(), target)
        else:
          print "%s  -  temp: %f, target: %f  -  off" % (phase, self.getTemp(), target)
          self.heatOff()
          self.fanOn()
        delay(TIME_STEP_MS)
        self.current_step += 1
        current_total_step += 1

    self.error = ''
    self.current_phase = ''
    self.current_step = 0

  def stop(self):
    """ Flags the current phase to stop if it is being run in a separate thrad. """
    self.current_phase = ''
    self.current_step = 0
    self.heatOff()
    self.fanOff()

  def heatOn(self):
    digitalWrite(self.heater_pin, HEATER_ON)
    self.heat_state = "on"

  def heatOff(self):
    digitalWrite(self.heater_pin, HEATER_ON^1)
    self.heat_state = "off"

  def fanOn(self):
    if (self.fan_pin): 
      digitalWrite(self.fan_pin, FAN_ON)
      self.fan_state = "on"

  def fanOff(self):
    if (self.fan_pin):
      digitalWrite(self.fan_pin, FAN_ON^1)
      self.fan_state = "off"

  def getTemp(self):
    for i in range(10):
      # readTempC() return None if error; try a few times to make
      # sure error isn't just a hiccup before aborting current reflow.
      temp = self.thermocouple.getMeasurement().value
      if temp:
        if (temp > 100): print '\n%s\n' % temp
        return temp
    # There was an error reading the temperature, abort:
    print "**Error reading thermocouple:\n %s" % \
          self.thermocouple.error
    self.heatOff()
    return None

  def generateMap(self, profile, solder_type=None):
    """ Generates and returns reflow map given a profile config dict. """
    if not solder_type: solder_type = self.solder_type
    reflow_map = {}
    start_temp = self.getTemp()
    if (start_temp == None):
      # Error getting temperature, assume room temperature:
      start_temp = 25.0

    for phase in range(len(PHASES)):
      tmin = LIMITS[PHASES[phase]]['tmin'][solder_type]
      tmax = LIMITS[PHASES[phase]]['tmax'][solder_type]

      dmin = LIMITS[PHASES[phase]]['dmin'][solder_type]
      dmax = LIMITS[PHASES[phase]]['dmax'][solder_type]

      slopemin = LIMITS[PHASES[phase]]['slopemin'][solder_type]
      slopemax = LIMITS[PHASES[phase]]['slopemax'][solder_type]

      config = profile[PHASES[phase]]

      target_temp = config.get('target')
      if (not target_temp):
        assert phase > 0, "**Profile must contain pre_soak target_temp, aborting!"
        target_temp = start_temp
      
      duration = config.get('duration')
      slope = config.get('slope')
      assert duration or slope,\
        "**duration or slope required for every phase; missing from %s, aborting!"%\
        (PHASES[phase])

      if (not duration):
        # Calculate duration from slope
        duration = float(target_temp-start_temp)/slope
      elif (not slope):
        # Calculate slope from duration
        slope = float(target_temp-start_temp)/duration

      #print "%s duration=%f" % (PHASES[phase], duration)
      #print "%s slope=%f" % (PHASES[phase], slope)
      #print "%s start_temp=%f" % (PHASES[phase], start_temp)
      #print "%s target_temp=%f\n" % (PHASES[phase], target_temp)

      # Create map of the current phase:
      f = lambda ms : slope * float(ms/1000.0) + start_temp
      n_steps = int((duration*1000.0)/TIME_STEP_MS)
      reflow_map[PHASES[phase]] = []
      for x in range(n_steps): reflow_map[PHASES[phase]].append(f(x*TIME_STEP_MS))

      start_temp = target_temp
    return reflow_map
