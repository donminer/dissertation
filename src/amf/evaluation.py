# evaluation.py contains all the tests used to evaluate AMF's performance.

import fm
import numpy
import misc
import sys
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
   sys.stderr.write("|" + " "*40 + "|\n")
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


