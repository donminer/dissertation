import sys
import amf
import amf.misc as misc

FM_TRAINING_ITERATIONS = 1
FM_QUERY_ITERATIONS = 2

# EXPERIMENTS:
#  For each regression X data set size:
#   1. FM Training Time
FMTRAININGTIME = 1
#   2. FM Accuracy
FMACCURACY = 2
#   3. FM Query Time
FMQUERYTIME = 3


#   4. RM Training Time
RMTRAININGTIME = 4
#   5. RM Accuracy vs. FM
RMACCURACYFM = 5
#   6. RM Accuracy vs. ABM Run
RMACCURACYABM = 6
#   7. RM Query Time
RMQUERYTIME = 7


class Experiment(object):
   def __init__(self, config_file_path):
      fh = open(sys.argv[1])

      execd = {}
      exec(fh.read(), execd)

      self.datafile = execd['DATA_FILE']
      self.training_sizes = execd['TRAINING_SIZES']
      self.validation_size = execd['VALIDATION_SIZE']
      self.regressions = execd['REGRESSIONS']
      self.num_dep = execd['NUM_DEPENDENT']


      self.results = Results(self)

   def run(self):
      print >> sys.stderr, "Loading data set <%s>" % self.datafile
      full_data = amf.data.load(self.datafile)

      ###

      print >> sys.stderr, "Testing FM Training Time"
      for (reg, params), tsize in self.each_combo():
         label = labelize(reg, params)

         for i in xrange(FM_TRAINING_ITERATIONS):
            dataset, = amf.data.random_subsets(full_data, [tsize])

            fm = amf.ForwardMapping(reg, params, self.num_dep)

            t = misc.StopWatch()
            fm.train(dataset)
            t = t.read()
            print >> sys.stderr, '   Regression <%s> took %.2f seconds to train on tsize=<%d>' \
               % (label, t, tsize)

            self.results.report(label, tsize, FMTRAININGTIME, t)

      ###

      print >> sys.stderr, "Creating training sets and validation set"
      sets = amf.data.random_subsets(full_data, self.training_sizes + [self.validation_size])
      training_sets = sets[:-1]
      validation_set = sets[-1]

      ###

      print >> sys.stderr, "Testing the accuracy and speed of the forward mapping"
      for (reg, params), tsize in self.each_combo():
         label = labelize(reg, params)

         for i in xrange(FM_QUERY_ITERATIONS):
            print >> sys.stderr, "   Testing <%s> with dataset of size %d" % (label, tsize)
            dataset, val = amf.data.random_subsets(full_data, [tsize, self.validation_size])

            # might as well measure the training time here, too
            fm = amf.ForwardMapping(reg, params, self.num_dep)
            t = misc.StopWatch()
            fm.train(dataset)
            t = t.read()
            #print >> sys.stderr, "      Regression <%s> took %.2f seconds to train on tsize=<%d>" \
            #   % (label, t, tsize)

            self.results.report(label, tsize, FMTRAININGTIME, t)

            #print >> sys.stderr, "      Running queryies..."
            for config, yval in val:
               t = misc.StopWatch()
               p = fm.predict(config)
               t = t.read()
               deviation = tuple( pv - yvalv  for pv,  yvalv in zip(p, yval) )
               self.results.report(label, tsize, FMACCURACY, deviation)
               self.results.report(label, tsize, FMQUERYTIME, t)
            #print >> sys.stderr, "      Done"

         print >> sys.stderr, "      Average Error:", \
               self.results.average(label, tsize, FMACCURACY, m = (lambda l : tuple( abs(p) for p in l )) )
         print >> sys.stderr, "      Average Query Time:", \
               self.results.average(label, tsize, FMQUERYTIME)
      ###

      print >> sys.stderr, "Testing RM Training Time"
      for (reg, params), tsize in self.each_combo():
         label = labelize(reg, params)   

      ###

      print >> sys.stderr, "Done"
      

   def each_combo(self):
      for reg in self.regressions:
         for tsize in self.training_sizes:
            yield (reg, tsize)

def labelize(reg, parameters):
   return misc.stripspaces(reg.name + repr(parameters))



class Results(object):
   def __init__(self, exp_obj):
      self._exp = exp_obj

      # initialize the dictionaries...
      self._results = {}
      for reg, params in self._exp.regressions:
         label = labelize(reg, params)

         for training_size in self._exp.training_sizes:
            # for each regression / training size pair, 
            key = (label, training_size)

            self._results[key] = [ None ] + [ [] for idx in range(7) ]




# "exp_no" refers to the above key...
   def report(self, reg_label, tsize, exp_no, value):
      self._results[(reg_label, tsize)][exp_no].append(value)

   def average(self, reg_label, tsize, exp_no, m = lambda x: x):
      l = self._results[(reg_label, tsize)][exp_no]

      lm = map(m, l)

      if type(lm[0]) is tuple or type(lm[0]) is list:
         # Each item is a list of items (i.e., this is a matrix)
         return misc.col_average(lm)

      else:
         # Each item is an individual
         return misc.average(lm)



exp = Experiment(sys.argv[1])

exp.run()

