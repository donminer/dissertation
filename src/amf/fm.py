# fm.py contains the ForwardMapping frontend.

import data

# This thing is the Forward Mapping
class ForwardMapping(object):

   # pass in the regression algorithm that we will be using, along with any initialization parameters
   def __init__(self, regression_class, init_parameters, num_dependent):
      """
      Initialized a forward mapping.
      Pass in the regression class to be used, the initial parameters for initlializing this reg class.
      Also, pass the the number of dependent variables the data set will have.
      """

      self.mappers = [ regression_class(*init_parameters) for i in range(num_dependent)]


   def train(self, training_set):
      training_sets = data.split_dep(training_set)

      for mapper, tset in zip(self.mappers, training_sets):
         mapper.train(tset)

   def predict(self, configuration):
      return [ mapper.predict(configuration) for mapper in self.mappers ]
