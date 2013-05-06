"""
 Reflow profiles are defined here using simple rules.
"""

DEFAULT_LEADED = {
  'pre_soak' : {
    'target' : 100,
    'slope'  : 1.5
  },
  'soak' : {
    'target'   : 150,
    'duration' : 90
  },
  'ramp_up' : {
    'target' : 235,
    'slope'  : 2
  },
  'peak' : {
    'duration' : 20
  },
  'cool' : {
    'target' : 100,
    'slope' : -5
  }
}

DEFAULT_LEADFREE = {
  'pre_soak' : {
    'target' : 150,
    'slope'  : 1.5
  },
  'soak' : {
    'target'   : 200,
    'duration' : 100
  },
  'ramp_up' : {
    'target' : 250,
    'slope'  : 1.25
  },
  'peak' : {
    'duration' : 30
  },
  'cool' : {
    'target' : 100,
    'slope' : -5
  }
}
