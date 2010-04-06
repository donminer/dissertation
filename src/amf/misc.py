# misc.py has a bunch of random functions that are used now and then.
#  This is intended as a set of "helper" tools, and probably do not need to be used by the user
#  (hence, why it is not imported in __init__.py

import time
import math
import numpy
import sys

def distance(v1, v2):
   if len(v1) != len(v2):
      raise ValueError, "distance: vectors %s and %s are different lengths." % (repr(v1), repr(v2))

   return sum( (x2 - x1)**2 for x1, x2 in zip(v1, v2) ) / float(len(v1))

# subtract two lists from one another
def list_sub(v1, v2):
   return tuple( x1 - x2 for x1, x2 in zip(v1, v2) )

def list_add(v1, v2):
   return tuple( x1 + x2 for x1, x2 in zip(v1, v2) )

def list_multscalar(v1, s):
   """ multiply every element in a list by a scalar """

   return tuple( x1 * s for x1 in v1 )

def col_average(lists):
   return [ col / len(lists) for col in col_sum(lists) ]

def stddev(lists):
   return tuple(numpy.std(l) for l in lists)

def col_sum(lists):
   return col_reduce(lambda x, y: x + y, lists)

def col_max(lists):
   return col_reduce(max, lists)

def col_min(lists):
   return col_reduce(min, lists)


def get_col(lists, col):
   """ Retrieve a single column from a data set as a list. """

   return tuple( row[col] for row in lists )


def col_reduce(function, matrix):
   """ performs a 'reduce' operation on each column of a matrix """

   cur = list(matrix[0])

   for row in matrix[1:]:
      for idx, item in enumerate(row):
         cur[idx] = function(cur[idx], item)

   return tuple(cur)

def to_columns(rows):
   """
   Returns the same data set but organized by columns, instead of rows.
   """
   if len(rows) == 0:
      return None

   cols = []
   for col in range(len(rows[0])):
      cols.append( tuple( row[col] for row in rows ) )

   return tuple(cols)

def round_float(num):
   return int(math.floor(num) + (1.0 if num - math.floor(num) > .5 else 0.0))

def boxplot(stat_list):
   """ Returns the min, lower quartile, median, upper quartile, and max.
   You could make a box and whiskers plot with this!"""

   sorted_list = sorted(stat_list)
   length = len(stat_list)


   return sorted_list[0], \
          sorted_list[round_float(length/4.0)], \
          sorted_list[round_float(length/2.0)], \
          sorted_list[round_float(length*.75)], \
          sorted_list[-1]

class StopWatch(object):
   def __init__(self):
      self.reset()

   def reset(self):
      self.start_time = time.time()

   def read(self):
      """ Returns the seconds that have elapsed since the stopwatch
      has been reset last"""
      return time.time() - self.start_time

def stripspaces(s):
   new_s = ""
   for c in s:
      if not c.isspace():
         new_s += c

   return new_s

def xzip(l1, l2):
   """ the same thing as zip, but as an iterator"""

   minlen = min(len(l1), len(l2))

   for idx in xrange(minlen):
      yield (l1[idx], l2[idx])

def xfrange(start, stop, step):
   if start > stop and step > 0.0 or start < stop and step < 0.0 or step == 0.0:
      sys.stderr.write("Bad start/stop/step! %f %f %f \n" % (start, stop, step))

   else:
      cur = 0.0
      while start + cur * step < stop:
         yield start + cur * step
         cur += 1.0

def binary(n):
   """ Generate all binary numbers of length n """
   out = []
   _binary_helper(n, (), out)
   return tuple(out)

def _binary_helper(n, l, output):
   if n == 0:
      output.append(l)
   else:
      _binary_helper(n-1, l + (0,), output), _binary_helper(n-1, l + (1,), output)

