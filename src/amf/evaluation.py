# evaluation.py contains all the tests used to evaluate AMF's performance.

import fm
import numpy
import misc
import sys
import data
from fm import ForwardMapping
import os.path

class ErrorStats(object):
   def __init__(self, entries = None):
      self.error_rows = []

      if entries != None:
         for entry in entries:
            self.add_entry(entry)

   def add(self, config, test_val, predict_val):
      """
      Adds a row to the error set
      """
      self.error_rows.append(_ErrorStatsRow(config, test_val, predict_val))

   def errors(self):
      """
      Returns all the errors in this set
      """
      return tuple( tuple(abs(e) for e in d.deviation) for d in self.error_rows )

   def deviations(self):
      """
      Return all the deviations in this set
      """
      return tuple( d.deviation for d in self.error_rows )


class _ErrorStatsRow(object):
   def __init__(self, config, test_val, predict_val):
      self.config = config
      self.test_val = test_val
      self.predict_val = predict_val
      self.deviation = misc.list_sub(test_val, predict_val)



def eval_fm(initialized_fm, training_set, test_set):
   """
   takes a training set, a test set and an initialized (but not trained) forward
   mapping object.

   Returns a evaluation.ErrorStats object and the amount of time it took
   per query.
   """

   # rename it
   myfm = initialized_fm

   # train it on the training set
   myfm.train(training_set)

   test = ErrorStats()



   sys.stderr.write("Starting Experiment\n")
   sys.stderr.write("%d training instances, %d testing instances\n" \
      % (len(training_set), len(test_set)) )
   sys.stderr.write("|" + " "*42 + "|\n")
   progress_bar_tic = len(test_set)/40
   sys.stderr.write(" ")
   count = 0

   st = misc.StopWatch()

   # for each item in the training set, predict with that configuration and test
   # it against the actually sampled value
   for test_config, test_val in test_set:
      predict_val = myfm.predict(test_config)

      test.add( test_config, test_val, predict_val )

      if count % progress_bar_tic == 0:
         sys.stderr.write("*")
      count += 1

   sys.stderr.write("\n")

   return test, (st.read() / len(test_set))

def test_fm(experiment_name, reg_method, parameters, dataset, training_size, evaluation_size):
   """
   dataset can be already loaded
   """


   print >> sys.stderr, "Testing a [%s] forward mapping for experiment <%s>" % (reg_method.name, experiment_name)
   print >> sys.stderr, "Training data set size:", training_size
   print >> sys.stderr, "Evaluation data set size:", evaluation_size


   # initialize the data set
   if type(dataset) is str:
      all_data = data.load(dataset)
   else:
      all_data = dataset

   # length of zeroth row, index 1 (the dependent variables)
   num_dep = len(all_data[0][1])

   training, validation = data.random_subsets(all_data, [training_size, evaluation_size])

   # initialize the forward mapping with kNN
   knn = ForwardMapping(reg_method, parameters, num_dep)

   # Run the tests
   error_list, time_per = eval_fm(knn, training, validation)
   print >> sys.stderr, "Each query took about", time_per, "seconds."

   # calculate some stats on the errors

   errors = error_list.errors()
   column_err = misc.to_columns(errors)
   #devias = error_list.deviations()
   #column = misc.to_columns(devias)

   avg = misc.col_average(errors)
   print >> sys.stderr, "The average error was", avg

   std = misc.stddev(column_err)
   print >> sys.stderr, "The standard deviation of errors was", std

   #bias = misc.col_average(devias)
   #print >> sys.stderr, "The average deviation (bias) was", bias

   #print >> sys.stderr, "The worst error was", misc.col_max(errors)
   #print >> sys.stderr, "The lowest error was", misc.col_min(errors)

   #boxplots = []
   #for col in column:
   #   boxplot = misc.boxplot(col)
   #   boxplots.append(boxplot)
   #   print >> sys.stderr, "A box-whisker plot of the deviations:", boxplot

   sys.stderr.write("\n")

   output = []

   for col in range(len(column_err)):
      # print out a data row that can be redirected to a data set sort of thing
      #print "%s:%d" % (experiment_name, col),
      #print "%s:%s" % (reg_method.name, misc.stripspaces(repr(parameters)) ), 
      #print "%d:%d" % (training_size, evaluation_size),
      #print "%.10f" % time_per,
      #print "%.10f:%.10f" % (avg[col], std[col])

      output.append((avg[col], std[col]))

   sys.stderr.write("\n\n")

   return output


