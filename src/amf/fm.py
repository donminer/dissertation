# fm.py contains the ForwardMapping frontend.


# This thing is the Forward Mapping
class ForwardMapping(object):

   # pass in the regression algorithm that we will be using, along with any initialization parameters
   def __init__(self, regression_class, init_parameters):
      self.mapper = regression_class(*init_parameters)

   def train(self, training_set):
      self.mapper.train(training_set)

   def predict(self, configuration):
      return self.mapper.predict(configuration)
