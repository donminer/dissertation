# rm.py contains the ReverseMapping

import misc

class ReverseMapping(object):
   def __init__(self, trained_fm, ranges, granularity):

      self.fm = trained_fm
      self.granularity = float(granularity)
      self.ranges = ranges
      self.steps = tuples( (ma - mi) / self.granularity for mi, ma in self.ranges )

      # the dimensionality of the configuration space
      self.dim = len(ranges)

      self.knot_vals = []
      self.knots = []
      self.build_knots(self.knot_vals, ())
      self.knot_vals = tuple(self.knots)


   def build_knots(self, parent, dim_vals):
      cur_dim = len(dim_vals)

      cur_dim_min = self.ranges[cur_dim][0]
      cur_dim_max = self.ranges[cur_dim][1]
      cur_dim_step = (cur_dim_max - cur_dim_min) / self.granularity

      for this_dim_val in misc.xfrange(cur_dim_min, cur_dim_max, cur_dim_step):

         new_vector = dim_vals + (this_dim_val,)

         # we've got more dimensions, so just keep adding to the structure
         if cur_dim < (self.dim - 1):
            newlist = []
            parent.append(newlist)
            self.build_knots(newlist, new_vector)
            newlist = tuple(newlist)

         # we've hit the last dimensions, let's find the knot
         else:
            parent.append(self.fm.predict(new_vector))
            self.knots.append(new_vector)

   def cube_at_root(self, root):
      """ Returns the members of this cube with this point as its root. """
      cube = [root]


   def __cube_at_root_helper__(self, root, ()):
      pass
