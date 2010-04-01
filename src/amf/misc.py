# misc.py has a bunch of random functions that are used now and then.
#  This is intended as a set of "helper" tools, and probably do not need to be used by the user
#  (hence, why it is not imported in __init__.py

def distance(v1, v2):
   if len(v1) != len(v2):
      raise ValueError, "distance: vectors %s and %s are different lengths." % (repr(v1), repr(v2))

   return sum( (x2 - x1)**2 for x1, x2 in zip(v1, v2) ) / float(len(v1))

