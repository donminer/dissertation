import sys
import amf
import amf.misc as misc
import time
import os
import numpy
import math

FM_TRAINING_ITERATIONS = 3
FM_QUERY_ITERATIONS = 14
RM_TRAINING_ITERATIONS = 3



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


# the amount to scale the y scale by
MAGIC_YSCALE_FM_ACCURACY = .275

OUTPUT_DIR = None



def sigmoid(p, x1):
   """
   p[0] - minimum asymptote
   p[1] - max asymptote
   p[2] - growth rate
   p[3] - location of the inflexion point
   """
   return p[0] + (p[1] - p[0]) / (1 + math.e ** (-p[2] * (x1 - p[3])))

class Experiment(object):
   def __init__(self, config_file_path):
      fh = open(sys.argv[1]).read()

      execd = {}
      exec(fh, execd)

      self.datafile = execd['DATA_FILE']
      self.training_sizes = sorted(execd['TRAINING_SIZES'])
      self.validation_size = execd['VALIDATION_SIZE']
      self.regressions = execd['REGRESSIONS']
      self.num_dep = execd['NUM_DEPENDENT']
      self.rm_granularities = sorted(execd['RM_GRANULARITIES'])
      self.name = execd['EXPERIMENT_NAME']

      global OUTPUT_DIR
      OUTPUT_DIR = '../data/test_domain_results/' + self.name + repr(int(time.time())) + "/"
      os.mkdir(OUTPUT_DIR)
      info = open(OUTPUT_DIR + 'info.txt', 'w')

      print >> info, """
FM_TRAINING_ITERATIONS = %d
FM_QUERY_ITERATIONS = %d
RM_TRAINING_ITERATIONS = %d
""" % ( FM_TRAINING_ITERATIONS, FM_QUERY_ITERATIONS, RM_TRAINING_ITERATIONS )

      print >> info, '\n\nContents of %s :\n%s\n\n' % (config_file_path, fh.replace('\n', '\n> '))

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
               ## THIS IS DIFFERENT FOR AIDS ##

               #print p
               #raw_input('...')

               avg_error = sum(abs(sigmoid(p, tZ) - sigmoid(yval, tZ)) for tZ in range(100))/100.0

               self.results.fm_report(label, tsize, FMACCURACY, avg_error)
               self.results.fm_report(label, tsize, FMQUERYTIME, t)
            #print >> sys.stderr, "      Done"

         #print >> sys.stderr, "      Average Error:", \
         #      self.results.average(label, tsize, FMACCURACY, m = (lambda l : tuple( abs(p) for p in l )) )
         #print >> sys.stderr, "      Average Query Time:", \
         #      self.results.average(label, tsize, FMQUERYTIME)
      ###

   

      print >> sys.stderr, "\nDone"

   def each_combo(self):
      for reg in self.regressions:
         for tsize in self.training_sizes:
            yield (reg, tsize)

   def make_plots(self):
      self.results.make_plot_FMTRAININGTIME()
      self.results.make_plot_FMACCURACY()
      self.results.make_plot_FMQUERYTIME()
      #self.results.make_plot_RMTRAININGTIME()
      #self.results.make_plot_RMACCURACYFM()
      #self.results.make_plot_RMQUERYTIME()
      #self.results.make_plot_RMACCURACYABM()

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
set terminal png nocrop enhanced size 400, 400
set output "plot.png"
set xlabel "Data Set Size"
set ylabel "Training Time (Seconds)"
set key top left
set title "Forward Mapping Training Time (%s)"
""" % self._exp.name

      mi = int(numpy.floor(2 * self._exp.training_sizes[0] - self._exp.training_sizes[1]))
      ma = int(numpy.ceil(2 * self._exp.training_sizes[-1] - self._exp.training_sizes[-2]))
      print >> gnuplot_script, "set xrange [%d:%d]" % (mi, ma)

      print >> gnuplot_script, 'plot ',

      first = True
      for reg, params in self._exp.regressions:
         label = labelize(reg, params)

         if first:
            first = False
         else:
            print >> gnuplot_script, ", ",

         out_file = open(plot_dir + "%s" % reg.name, 'w')
         print >> gnuplot_script, '"%s" with errorbars' % reg.name,

         for training_size in self._exp.training_sizes:
            key = (label, training_size)

            # this is the list of times
            times = self._fm_results[key][exp_no]

            # average them
            avg, lower, upper = misc.errorbars(times)
            
            print >> out_file, "%d %f %f %f" % (training_size, avg, lower, upper)

         out_file.close()

      print >> gnuplot_script, '\n',
      gnuplot_script.close()

      curdir = os.path.abspath('.')
      os.chdir(plot_dir)
      os.system('gnuplot ' + 'plot.gp')
      os.chdir(curdir)


   def make_plot_FMACCURACY(self):
      # This graph shows the time spent training vs. the data set size

      # THIS ONLY DOES ONE SLP RIGHT NOW!!! (for fires!)  TODO FIXME

      exp_no = FMACCURACY

      plot_dir = OUTPUT_DIR + "fm_accuracy/"
      os.mkdir(plot_dir)

      # gotta find the max deviation seen, ever, so that I can make all the
      # graphs have the same y-scale

      maerr = 0.0
      for reg, params in self._exp.regressions:
         label = labelize(reg, params)

         for training_size in self._exp.training_sizes:
            key = (label, training_size)

            maxerror = max([ abs(x) for x in self._fm_results[key][exp_no]]) # FIXME

            maerr = max(maerr, maxerror)

      for reg, params in self._exp.regressions:
         label = labelize(reg, params)

         gnuplot_script = open(plot_dir + 'plot-%s.gp' % reg.name, 'w')
         print >> gnuplot_script, """
set terminal png nocrop enhanced size 400, 400
set output "plot-%s.png"
set xlabel "Data Set Size"
set ylabel "Median Error"
set key top right
set title "Forward Mapping Accuracy (%s)"
""" % (reg.name, self._exp.name)

         mi = int(numpy.floor(2 * self._exp.training_sizes[0] - self._exp.training_sizes[1]))
         ma = int(numpy.ceil(2 * self._exp.training_sizes[-1] - self._exp.training_sizes[-2]))
         print >> gnuplot_script, "set xrange [%d:%d]" % (mi, ma)
         print >> gnuplot_script, "set yrange [0:%.4f]" % (maerr * 1.1 * MAGIC_YSCALE_FM_ACCURACY)

         print >> gnuplot_script, 'plot ',

         out_file = open(plot_dir + "%s" % reg.name, 'w')
         print >> gnuplot_script, '"%s" with errorbars' % reg.name,

         for training_size in self._exp.training_sizes:
            key = (label, training_size)

            # this is the list of deviations
            errors = [ abs(x) for x in self._fm_results[key][exp_no]] # FIXME

            # average them
            median, lower, upper = misc.doublesided(errors)
            
            print >> out_file, "%d %f %f %f" % (training_size, median, lower, upper)

         out_file.close()
         print >> gnuplot_script, '\n',
         gnuplot_script.close()
         
         curdir = os.path.abspath('.')
         os.chdir(plot_dir)
         os.system('gnuplot ' + 'plot-%s.gp' % reg.name)
         os.chdir(curdir)



   def make_plot_FMQUERYTIME(self):
      # This graph shows the time spent training vs. the data set size

      exp_no = FMQUERYTIME

      plot_dir = OUTPUT_DIR + "fm_query_time/"
      os.mkdir(plot_dir)

      gnuplot_script = open(plot_dir + 'plot.gp', 'w')
      print >> gnuplot_script, """
set terminal png nocrop enhanced size 400, 400
set output "plot.png"
set xlabel "Data Set Size"
set ylabel "Average Query Time (Seconds)"
set key top left
set title "Forward Mapping Query Time (%s)"
""" % self._exp.name

      mi = int(numpy.floor(2 * self._exp.training_sizes[0] - self._exp.training_sizes[1]))
      ma = int(numpy.ceil(2 * self._exp.training_sizes[-1] - self._exp.training_sizes[-2]))
      print >> gnuplot_script, "set xrange [%d:%d]" % (mi, ma)

      print >> gnuplot_script, 'plot ',

      first = True
      for reg, params in self._exp.regressions:
         label = labelize(reg, params)

         if first:
            first = False
         else:
            print >> gnuplot_script, ", ",

         out_file = open(plot_dir + "%s" % reg.name, 'w')
         print >> gnuplot_script, '"%s" with errorbars' % reg.name,

         for training_size in self._exp.training_sizes:
            key = (label, training_size)

            # this is the list of times
            times = self._fm_results[key][exp_no]

            # average them
            avg, lower, upper = misc.errorbars(times)
            
            print >> out_file, "%d %f %f %f" % (training_size, avg, lower, upper)

         out_file.close()

      print >> gnuplot_script, '\n',
      gnuplot_script.close()

      curdir = os.path.abspath('.')
      os.chdir(plot_dir)
      os.system('gnuplot ' +'plot.gp')
      os.chdir(curdir)

   def make_plot_RMTRAININGTIME(self):
      # This graph shows the time spent training vs. the data set size

      exp_no = RMTRAININGTIME

      plot_dir = OUTPUT_DIR + "rm_training_time/"
      os.mkdir(plot_dir)

      gnuplot_script = open(plot_dir + 'plot.gp', 'w')
      print >> gnuplot_script, """
set terminal png nocrop enhanced size 400, 400
set output "plot.png"
set xlabel "Granularity"
set ylabel "Average Training Time (Seconds)"
set nokey
set title "Reverse Mapping Training Time (%s)"
""" % self._exp.name

      mi = int(numpy.floor(2 * self._exp.rm_granularities[0] - self._exp.rm_granularities[1]))
      ma = int(numpy.ceil(2 * self._exp.rm_granularities[-1] - self._exp.rm_granularities[-2]))
      print >> gnuplot_script, "set xrange [%d:%d]" % (mi, ma)

      print >> gnuplot_script, 'plot "rm_times" with errorbars, "rm_times" with lines',

      out_file = open(plot_dir + "rm_times", 'w')

      for gran in self._exp.rm_granularities:
         times = self._rm_results[gran][exp_no]

         avg, lower, upper = misc.errorbars(times)

         print >> out_file, "%d %f %f %f" % (gran, avg, lower, upper)


      out_file.close()

      print >> gnuplot_script, '\n',
      gnuplot_script.close()

      curdir = os.path.abspath('.')
      os.chdir(plot_dir)
      os.system('gnuplot ' +'plot.gp')
      os.chdir(curdir)


   def make_plot_RMACCURACYFM(self):
      # This graph shows the time spent training vs. the data set size

      exp_no = RMACCURACYFM

      plot_dir = OUTPUT_DIR + "rm_accuracyfm/"
      os.mkdir(plot_dir)

      gnuplot_script = open(plot_dir + 'plot.gp', 'w')
      print >> gnuplot_script, """
set terminal png nocrop enhanced size 400, 400
set output "plot.png"
set xlabel "Granularity"
set ylabel "Median Error"
set nokey
set title "Reverse Mapping Accuracy vs. FM (%s)"
""" % self._exp.name

      mi = int(numpy.floor(2 * self._exp.rm_granularities[0] - self._exp.rm_granularities[1]))
      ma = int(numpy.ceil(2 * self._exp.rm_granularities[-1] - self._exp.rm_granularities[-2]))
      print >> gnuplot_script, "set xrange [%d:%d]" % (mi, ma)

      print >> gnuplot_script, 'plot "rm_times" with errorbars, "rm_times" with lines',

      out_file = open(plot_dir + "rm_times", 'w')

      for gran in self._exp.rm_granularities:
         times = self._rm_results[gran][exp_no]

         avg, lower, upper = misc.doublesided( abs(x) for x in times )  # FIXME : only works for 1 parameter!

         print >> out_file, "%d %f %f %f" % (gran, avg, lower, upper)


      out_file.close()

      print >> gnuplot_script, '\n',
      gnuplot_script.close()

      curdir = os.path.abspath('.')
      os.chdir(plot_dir)
      os.system('gnuplot ' +'plot.gp')
      os.chdir(curdir)


   def make_plot_RMQUERYTIME(self):
      # This graph shows the time spent training vs. the data set size

      exp_no = RMQUERYTIME

      plot_dir = OUTPUT_DIR + "rm_query_time/"
      os.mkdir(plot_dir)

      gnuplot_script = open(plot_dir + 'plot.gp', 'w')
      print >> gnuplot_script, """
set terminal png nocrop enhanced size 400, 400
set output "plot.png"
set xlabel "Granularity"
set ylabel "Average Query Time (Seconds)"
set nokey
set title "Reverse Mapping Query Time (%s)"
""" % self._exp.name

      mi = int(numpy.floor(2 * self._exp.rm_granularities[0] - self._exp.rm_granularities[1]))
      ma = int(numpy.ceil(2 * self._exp.rm_granularities[-1] - self._exp.rm_granularities[-2]))
      print >> gnuplot_script, "set xrange [%d:%d]" % (mi, ma)

      print >> gnuplot_script, 'plot "rm_times" with errorbars, "rm_times" with lines',

      out_file = open(plot_dir + "rm_times", 'w')

      for gran in self._exp.rm_granularities:
         times = self._rm_results[gran][exp_no]

         avg, lower, upper = misc.errorbars(times)

         print >> out_file, "%d %f %f %f" % (gran, avg, lower, upper)


      out_file.close()

      print >> gnuplot_script, '\n',
      gnuplot_script.close()

      curdir = os.path.abspath('.')
      os.chdir(plot_dir)
      os.system('gnuplot ' +'plot.gp')
      os.chdir(curdir)


   def make_plot_RMACCURACYABM(self):
      # This graph shows the time spent training vs. the data set size

      exp_no = RMACCURACYABM

      plot_dir = OUTPUT_DIR + "rm_accuracyabm/"
      os.mkdir(plot_dir)

      gnuplot_script = open(plot_dir + 'plot.gp', 'w')
      print >> gnuplot_script, """
set terminal png nocrop enhanced size 400, 400
set output "plot.png"
set xlabel "Granularity"
set ylabel "Median Error"
set nokey
set title "Reverse Mapping Accuracy vs. ABM (%s)"
""" % self._exp.name

      mi = int(numpy.floor(2 * self._exp.rm_granularities[0] - self._exp.rm_granularities[1]))
      ma = int(numpy.ceil(2 * self._exp.rm_granularities[-1] - self._exp.rm_granularities[-2]))
      print >> gnuplot_script, "set xrange [%d:%d]" % (mi, ma)

      print >> gnuplot_script, 'plot "rm_errors" with errorbars, "rm_errors" with lines',

      out_file = open(plot_dir + "rm_errors", 'w')

      for gran in self._exp.rm_granularities:
         times = self._rm_results[gran][exp_no]

         avg, lower, upper = misc.doublesided( abs(x) for x in times )  # FIXME : only works for 1 parameter!

         print >> out_file, "%d %f %f %f" % (gran, avg, lower, upper)


      out_file.close()

      print >> gnuplot_script, '\n',
      gnuplot_script.close()

      curdir = os.path.abspath('.')
      os.chdir(plot_dir)
      os.system('gnuplot ' +'plot.gp')
      os.chdir(curdir)



exp = Experiment(sys.argv[1])

exp.run()

exp.make_plots()



