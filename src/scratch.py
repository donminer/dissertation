import sys

import amf
import amf.misc as misc
import os.path
import math

# Comment this out to have debug messages shown.
#sys.stderr = open('/dev/null', 'w')

def test_fires_fm_random():
   amf.evaluation.test_fm("FIRESknn", amf.regression.Random, [0.0, 1.0], '../data/fires.txt', 100, 500)

def test_fires_fm_knn():
   amf.evaluation.test_fm("FIRESknn", amf.regression.kNN, [], '../data/fires.txt', 1000, 1000)

def sigmoid(p, x1):
   return p[0] + (p[1] - p[0]) / (1 + math.e ** (-p[2] * (x1 - p[3])))

def test_fires_fm_nlr():
   init_guess = [0.0, 1.0, .65, 58.3]

   amf.evaluation.test_fm("FIRESnlr", amf.regression.NLR, [sigmoid, init_guess], '../data/fires.txt', 100, 500)

def test_fires_fm_loess():
   for sm in [0, 1, 2, 3, 4, 5]:
      for win in [1.5, 2.0, 3.0]:
         amf.evaluation.test_fm("FIRESloess", amf.regression.LOESS, [win, sm], '../data/fires.txt', 100, 500)

def plotpoints_loess_fm_fires():
   fm = amf.ForwardMapping(amf.regression.LOESS, [1.0, 1], 1)
   data = amf.data.load('../data/fires.txt')
   subset = amf.data.random_subsets(data, [400])[0]

   fm.train(subset)

   for x in misc.xfrange(45.0, 75.0, .1):
      print x, fm.predict((x,))[0]

def plotpoints_knn_fm_fires():
   fm = amf.ForwardMapping(amf.regression.kNN, [55], 3)
   data = amf.data.load('../data/fires.txt')
   subset = amf.data.random_subsets(data, [400])[0]

   fm.train(subset)

   for x in misc.xfrange(45.0, 75.0, .1):
      print x, fm.predict((x,))[0]

def test_fm_multi(regressions, dataset_path, training_sizes, evaluation_size, num_trials = 1):
   """
   regressions is a list of tuples with (<regression>, <parameters>)
   """

   loaded_data = amf.data.load(dataset_path)
   name = os.path.basename(dataset_path).split('.', 1)[0].upper()

   for regression, parameters in regressions:
      for training_size in training_sizes:
         for i in xrange(num_trials):
            amf.evaluation.test_fm(name, regression, parameters, loaded_data, training_size, evaluation_size)
            
def test_fm_multi_fires():
   test_fm_multi([(amf.regression.kNN, [6])], '../data/fires.txt', range(20,200, 2), 2000, 1)

def test_rm():
   fm = amf.ForwardMapping(amf.regression.LOESS, [1.0, 1], 1)
   data = amf.data.load('../data/fires.txt')
   subset = amf.data.random_subsets(data, [400])[0]

   print "Training now..."

   fm.train(subset)

   print "Done training"

   rm = amf.ReverseMapping(fm, [(45.0, 75.0)], 100.0)


   print rm.intersections(0, .5)
   print rm.intersections(0, .94)


def main():
   # Please don't inject malicious code here. Thanks!
   exec(sys.argv[1] + "(" + ( "" if len(sys.argv) == 1 else ",".join(sys.argv[2:]) ) + ")") 

if __name__ == "__main__":
   main()
