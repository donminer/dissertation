# misc.py has a bunch of random functions that are used now and then.
#  This is intended as a set of "helper" tools, and probably do not need to be used by the user
#  (hence, why it is not imported in __init__.py

import time

def distance(v1, v2):
   if len(v1) != len(v2):
      raise ValueError, "distance: vectors %s and %s are different lengths." % (repr(v1), repr(v2))

   return sum( (x2 - x1)**2 for x1, x2 in zip(v1, v2) ) / float(len(v1))

# subtract two lists from one another
def list_sub(v1, v2):
   return tuple( x1 - x2 for x1, x2 in zip(v1, v2) )


class Stopwatch(object):

   def __init__(self):
      self.reset()

   def reset(self):
      self.start_time = time.time()

   def read(self):
      """ Returns the seconds that have elapsed since the stopwatch
      has been reset last"""
      return time.time() - self.start_time
