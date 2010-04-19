# rm.py contains the ReverseMapping

import misc
import numpy
import sys

# hack to avoid rounding error
def _round(n):
   return numpy.round(n, 5)

class RMSimplex(object):
   # Simplexes are kind of immutable...

   # The LAST variable of each corner vector is the dependent variable
   #   (this is important)

   def __init__(self, corners):
      """
      A simplex.
      corners should have the form ((ind0, ind1, ...), (dep1, dep2, dep3))
      """

      # We already know which corners are adjanced to which
      #   (each corner shares an edge with every other corner)

      self._corners = tuple(corners)
      
      self._edges = []
      for cidx in range(len(self._corners)):
         corner = self._corners[cidx]

         for oidx in range(cidx + 1, len(self._corners)):
            other_corner = self._corners[oidx]
            
            self._edges.append((corner, other_corner))


      self._edges = tuple(self._edges)

      self._inds = tuple( corner[0] for corner in corners )
      self._deps = tuple( corner[1] for corner in corners )
      self._min = misc.col_min(self._deps)
      self._max = misc.col_max(self._deps)

   @property
   def corners(self):
      return self._corners

   @property
   def edges(self):
      return self._edges

   def contains(self, slp_num, value):
      """Determines if the value for slp_num idx lives inside this simplex."""

      #print self._min[slp_num], '<', value, '<', self._max[slp_num]

      return value > self._min[slp_num] and value < self._max[slp_num]

   def intersections(self, slp_num, value):
      """Returns the approximate places that the value plane intersects with this simplex"""

      if not self.contains(slp_num, value[0]):
         return []

      inters = []

      for scorner, bcorner in self.edges:
         # check to see that this value is inside these edges
         if not (value > scorner[1][slp_num] and value < bcorner[1][slp_num]):
            continue

         # this is the distance between the 2 corner values
         distance = bcorner[1][slp_num] - scorner[1][slp_num]

         # this is the distance from 'value' from the smaller corner
         ratio = (value[slp_num] - scorner[1][slp_num]) / distance
         # if value is close to smaller, this ratio will be close to zero
         # if value is closer to bigger, this ratio will be close to one

         inter = tuple( (1.0-ratio)*s + ratio * b for s, b in zip(scorner[0], bcorner[0]) )
         
         inters.append(inter)

      return tuple(inters)

   def __repr__(self):
      return 'simplex:' + repr(self._edges)

class ReverseMapping(object):
   def __init__(self, trained_fm, ranges, granularity):

      self.fm = trained_fm
      self.granularity = granularity
      self.ranges = ranges
      self.steps = tuple( (ma - mi) / float(self.granularity) for mi, ma in self.ranges )



      # the dimensionality of the configuration space
      self.dim = len(ranges)

      # the dimensionality of the SLP space
      self.slp_dim = None

      self.__bin__ = misc.binary(self.dim)

      self.knots = {}
      self.simplexes = []
      self.build_knots()
      print 'done building knots'
      self.build_simplexes()
      print 'done building simplexes'

   def build_knots(self, idx_vector = (), dim_vals = ()):
      cur_dim = len(dim_vals)

      cur_dim_min = self.ranges[cur_dim][0]
      cur_dim_max = self.ranges[cur_dim][1]
      cur_dim_step = (cur_dim_max - cur_dim_min) / self.granularity

      count = 0
      idx = 0
      for this_dim_val in misc.xfrange(cur_dim_min, cur_dim_max, cur_dim_step):
         new_vector = dim_vals + (this_dim_val,)
         new_idx = idx_vector + (idx,)
         idx += 1

         # we've got more dimensions, so just keep adding to the structure
         if cur_dim < (self.dim - 1):
            self.build_knots(new_idx, new_vector)

         # we've hit the last dimensions, let's find the knot
         else:
            predicted = self.fm.predict(new_vector)

            if self.slp_dim == None:
               self.slp_dim = len(predicted)

            self.knots[new_idx] = predicted

   def build_simplexes(self, col = None):
      for key in sorted(self.knots.keys()):
         # check to see if this root is on the fringe and thus not actually a root
         for idx in key:
            if idx == (self.granularity - 1):
               break
         else:
            sims = self.simplexes_from_cube(key)
            self.simplexes.extend(sims)

   def wiggle(self, root):
      """ Returns the closest point to this root that is an actual root. """
      distance, knot = min( (misc.distance(root, knot), knot)  for knot in self.knots )

      #print >> sys.stderr, "Wiggling point %s to knot %s" % (repr(root), repr(knot))

      return knot


   def cube_at_root(self, root):
      """ Returns the members of this cube with this point as its root. """

      corners = []

      for perm in self.__bin__:
         corner = []
         for idx in xrange(self.dim):
            corner.append(perm[idx] + root[idx])
         corner = tuple(corner)

         val = self.knots[corner]

         corners.append((self.translate_idx(corner), val))

      return tuple(corners)

   def translate_idx(self, vec_idx):
      """ Translates a index to a configuration"""

      corner = []
      for idx in xrange(self.dim):
         corner.append(vec_idx[idx] * self.steps[idx] + self.ranges[idx][0])

      return tuple(corner)


   def simplexes_from_cube(self, root):
      cube_corners = self.cube_at_root(root)
      # cube_at_root always has the first right corner root as [0]
      # at [-1] we have the other right corner root

      # special case for 1 dimensional configuration space
      if self.dim == 1:
         return (RMSimplex(cube_corners),)
      else:
         return RMSimplex(cube_corners[:-1]), RMSimplex(cube_corners[1:])

   def intersections(self, param_num, value):
      out = []
      for simplex in self.simplexes:
         inter = simplex.intersections(param_num, value)
         if len(inter) > 0:
            out.append(inter)

      return tuple(out)

   def all_intersections(self, value):
      """ Finds intersections with each provided SLP """

      return tuple( self.intersections(d, value) for d in range(self.slp_dim) )
         
   def distance_to(self, param_num, config, value):
      # i'm going to cheat for now and just pick the closest intersecting corner
      ints = self.intersections(param_num, value)

      #print 'simplexes', self.simplexes
      #print 'ints', ints
      #raw_input()

      dists = []
      for simplex in ints:
         for i in simplex:
            dists.append( (misc.distance(i, config)) )
   
      if len(dists) == 0:
         #print >> sys.stderr, "BADNESS: no intersections found for %s" % repr(value)
         dist = None
      else:
         dist = min(dists)

      return dist


