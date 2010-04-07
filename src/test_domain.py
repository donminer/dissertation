import sys
import amf
import amf.misc as misc
import time
import os

FM_TRAINING_ITERATIONS = 1
FM_QUERY_ITERATIONS = 1
RM_TRAINING_ITERATIONS = 0

OUTPUT_DIR = '../data/test_domain_results/' + repr(int(time.time())) + "/"
os.mkdir(OUTPUT_DIR)
info = open(OUTPUT_DIR + 'info.txt', 'w')

print >> info, """
FM_TRAINING_ITERATIONS = %d
FM_QUERY_ITERATIONS = %d
RM_TRAINING_ITERATIONS = %d
""" % ( FM_TRAINING_ITERATIONS, FM_QUERY_ITERATIONS, RM_TRAINING_ITERATIONS )

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
      fh = open(sys.argv[1]).read()

      print >> info, '\n\nContents of %s :\n%s\n\n' % (config_file_path, fh.replace('\n', '\n> '))

      execd = {}
      exec(fh, execd)

      self.datafile = execd['DATA_FILE']
      self.training_sizes = execd['TRAINING_SIZES']
      self.validation_size = execd['VALIDATION_SIZE']
      self.regressions = execd['REGRESSIONS']
      self.num_dep = execd['NUM_DEPENDENT']
      self.rm_granularities = execd['RM_GRANULARITIES']

      self.results = Results(self)

   def run(self):
      print >> sys.stderr, "\nLoading data set <%s>" % self.datafile
      full_data = amf.data.load(self.datafile)

      ###

      print >> sys.stderr, "\nTesting FM Training Time"
      total = len([ x for x in self.each_combo()])
      count = 0
      for (reg, params), tsize in self.each_combo():
         print >> sys.stderr, " %d/%d " % (count, total),
         count += 1

         label = labelize(reg, params)

         for i in xrange(FM_TRAINING_ITERATIONS):
            dataset, = amf.data.random_subsets(full_data, [tsize])

            fm = amf.ForwardMapping(reg, params, self.num_dep)

            t = misc.StopWatch()
            fm.train(dataset)
            t = t.read()
            #print >> sys.stderr, '   Regression <%s> took %.2f seconds to train on tsize=<%d>' \
            #   % (label, t, tsize)

            self.results.fm_report(label, tsize, FMTRAININGTIME, t)

      ###

      print >> sys.stderr, "\nCreating training sets and validation set"
      sets = amf.data.random_subsets(full_data, self.training_sizes + [self.validation_size])
      training_sets = sets[:-1]
      validation_set = sets[-1]

      ###

      print >> sys.stderr, "\nTesting the accuracy and speed of the forward mapping"
      total = len([ x for x in self.each_combo()])
      count = 0
      for (reg, params), tsize in self.each_combo():
         print >> sys.stderr, " %d/%d " % (count, total),
         count += 1

         label = labelize(reg, params)

         for i in xrange(FM_QUERY_ITERATIONS):
            #print >> sys.stderr, "   Testing <%s> with dataset of size %d" % (label, tsize)
            dataset, val = amf.data.random_subsets(full_data, [tsize, self.validation_size])

            # might as well measure the training time here, too
            fm = amf.ForwardMapping(reg, params, self.num_dep)
            t = misc.StopWatch()
            fm.train(dataset)
            t = t.read()
            #print >> sys.stderr, "      Regression <%s> took %.2f seconds to train on tsize=<%d>" \
            #   % (label, t, tsize)

            self.results.fm_report(label, tsize, FMTRAININGTIME, t)

            #print >> sys.stderr, "      Running queryies..."
            for config, yval in val:
               t = misc.StopWatch()
               p = fm.predict(config)
               t = t.read()
               deviation = tuple( pv - yvalv  for pv,  yvalv in zip(p, yval) )
               self.results.fm_report(label, tsize, FMACCURACY, deviation)
               self.results.fm_report(label, tsize, FMQUERYTIME, t)
            #print >> sys.stderr, "      Done"

         #print >> sys.stderr, "      Average Error:", \
         #      self.results.average(label, tsize, FMACCURACY, m = (lambda l : tuple( abs(p) for p in l )) )
         #print >> sys.stderr, "      Average Query Time:", \
         #      self.results.average(label, tsize, FMQUERYTIME)
      ###

      
      # use the largest training size for this experiment
      tsize = max(self.training_sizes)

      # use kNN for this experiment
      dataset, validation = amf.data.random_subsets(full_data, [tsize, self.validation_size])
      fm = amf.ForwardMapping(amf.regression.kNN, [], self.num_dep)
      fm.train(dataset)
      print >> sys.stderr, "\nTesting RM Training Time, Accuracy and Query Time"

      total = len(self.rm_granularities)
      count = 0

      for gran in self.rm_granularities:
         #print >> sys.stderr, "\n\n GRANULARITY %d !!!" % gran
         print >> sys.stderr, " %d/%d " % (count, total),
         count += 1

         for i in xrange(RM_TRAINING_ITERATIONS):

            # Training Time Experiment
            t = misc.StopWatch()
            rm = amf.ReverseMapping(fm, [(45.0, 75.0)], gran)
            t = t.read()
            #print >> sys.stderr, "took %.2f seconds to train" % t

            self.results.rm_report(gran, RMTRAININGTIME, t)

            # Error vs. Forward Mapping
            for s in rm.simplexes:
               # find the average config
               configs = [ p[0] for p in s.corners]
               avg_config = misc.col_average(configs)

               # find the average value of the SLPs
               slps = [ p[1] for p in s.corners ]
               avg_values = misc.col_average(slps)
            
               deviations = misc.list_sub(avg_values, fm.predict(avg_config))
               #print >> sys.stderr, "deviated %s from the fm" % repr(deviations)

               self.results.rm_report(gran, RMACCURACYFM, deviations)

            # Error vs. ABM
            for config, slp in validation:
               # this only dones one SLP right now!
               dist = rm.distance_to(0, config, slp)

               if dist != None:
                  #print >> sys.stderr, "configuration %s with value %s is %.3f away from the RM" \
                  #   % (repr(config), repr(slp[0]), dist)

                  self.results.rm_report(gran, RMACCURACYABM, dist)


            # Query Time
            for config, slp in validation:
               t = misc.StopWatch()
               rm.all_intersections(slp)
               t = t.read()
               #print >> sys.stderr, "query too %.2f seconds" % t

               self.results.rm_report(gran, RMQUERYTIME, t)

      ###

      print >> sys.stderr, "\nDone"

   def each_combo(self):
      for reg in self.regressions:
         for tsize in self.training_sizes:
            yield (reg, tsize)

   def make_plots(self):
      self.results.make_plot_FMTRAININGTIME()

def labelize(reg, parameters):
   return misc.stripspaces(reg.name + repr(parameters))



class Results(object):
   def __init__(self, exp_obj):
      self._exp = exp_obj

      # initialize the dictionaries...
      self._fm_results = {}
      for reg, params in self._exp.regressions:
         label = labelize(reg, params)

         for training_size in self._exp.training_sizes:
            # for each regression / training size pair, 
            key = (label, training_size)

            self._fm_results[key] = [ None ] + [ [] for idx in range(3) ] + [None] * 3

      self._rm_results = {}
      for gran in self._exp.rm_granularities:
         self._rm_results[gran] = [None] * 4 + [ [] for idx in range(4) ]


# "exp_no" refers to the above key...
   def fm_report(self, reg_label, tsize, exp_no, value):
      self._fm_results[(reg_label, tsize)][exp_no].append(value)

   def rm_report(self, granularity, exp_no, value):
      self._rm_results[granularity][exp_no].append(value)

   def make_plot_FMTRAININGTIME(self):
      # This graph shows the time spent training vs. the data set size

      exp_no = FMTRAININGTIME

      plot_dir = OUTPUT_DIR + "fm_training_time/"
      os.mkdir(plot_dir)

      gnuplot_script = open(plot_dir + 'plot.gp', 'w')
      print >> gnuplot_script, """
set xlabel "Data Set Size"
set ylabel "Training Time (Seconds)"
set key top left
"""
      print >> gnuplot_script, 'plot ',


      first = True
      for reg, params in self._exp.regressions:
         label = labelize(reg, params)

         if first:
            first = False
         else:
            print >> gnuplot_script, ", ",


         out_file = open(plot_dir + "%s" % reg.name, 'w')
         print >> gnuplot_script, '"%s" with lines' % reg.name,

         for training_size in self._exp.training_sizes:
            key = (label, training_size)

            # this is the list of times
            times = self._fm_results[key][exp_no]

            # average them
            avg = misc.average(times)
            
            print >> out_file, "%d %.3f" % (training_size, avg)

         out_file.close()

      print >> gnuplot_script, '\n',
      gnuplot_script.close()

exp = Experiment(sys.argv[1])

exp.run()

exp.make_plots()



