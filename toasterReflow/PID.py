"""
 PID.py
 Alexander Hiam
 Apache 2.0 License

 A simple Python PID controller object.
"""

from time import time

class PID(object):
  def __init__(self, kp, ki, kd=0):
    self.kp = kp
    self.ki = ki
    self.kd = kd
    self.reset()

  def reset(self):
    self.last_time = time()
    self.last_error = 0

  def calculateState(self, current_val, set_val):
    error = set_val - current_val
    de = error - self.last_error
    dt = time() - self.last_time
    return self.kp*error + (self.ki*error*dt) + (self.kd*(de/dt if dt else 0))
