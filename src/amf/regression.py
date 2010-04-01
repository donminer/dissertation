# regression.py contains the definititon of a pluggable regression algorithm.
#  Also, this file has a bunch of 'built-in' regression methods that can be used
#  as either examples or straight from the box.

import copy
import misc

# This is the basic Interface that other regression objects should inherit from
class Regression(object):
   def train(self, data):
      raise NotImplementedError, "'train' method not implemented."

   def predict(self, configuration):
      raise NotImplementedError, "'predict' method not implemented."


class kNN(Regression):
   def __init__(self, k):
      self.k = k
      self.__data__ = None
      self.ind = None
      self.dep = None

   def train(self, data):
      # kNN just stores the data...
      self.__data__ = copy.deepcopy(data)

      self.ind = len(self.__data__[0][0])
      self.dep = len(self.__data__[0][1])

   def predict(self, configuration):
      nn = self.__find_knn__(configuration)      

      # average each value in each column of the dependent variable data
      avg = tuple( sum(n[1][idx] for n in nn)/float(len(nn)) for idx in range(self.dep) )

      return avg

   # Finds the k nearest neighbors and returns them
   def __find_knn__(self, configuration):
      distances = [ (misc.distance(configuration, entry[0]), idx) for idx, entry in enumerate(self.__data__) ]
      distances.sort()
      
      return tuple( self.__data__[idx] for distance, idx in distances[:self.k] )

