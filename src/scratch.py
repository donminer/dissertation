import sys

import amf
import amf.misc as misc
import os.path

# Comment this out to have debug messages shown.
sys.stderr = open('/dev/null', 'w')


def test_fm(reg_method, parameters, dataset_path, training_size, evaluation_size):
   print >> sys.stderr, "Testing a [%s] forward mapping on the [%s] data set." % (reg_method.name, dataset_path)
   print >> sys.stderr, "Training data set size:", training_size
   print >> sys.stderr, "Evaluation data set size:", evaluation_size

   # initialize the data set
   all_data = amf.data.load(dataset_path)
   training, validation = amf.data.random_subsets(all_data, [training_size, evaluation_size])

   # initialize the forward mapping with kNN
   knn = amf.ForwardMapping(reg_method, parameters)

   # Run the tests
   error_list, time_per = amf.evaluation.eval_fm(knn, training, validation)
   print >> sys.stderr, "Each query took about", time_per, "seconds."

   # calculate some stats on the errors

   errors = error_list.errors()
   devias = error_list.deviations()
   column = misc.to_columns(devias)

   avg = misc.col_average(errors)
   print >> sys.stderr, "The everage error was", avg

   bias = misc.col_average(devias)
   print >> sys.stderr, "The average deviation (bias) was", bias

   print >> sys.stderr, "The worst error was", misc.col_max(errors)
   print >> sys.stderr, "The lowest error was", misc.col_min(errors)

   boxplots = []
   for col in column:
      boxplot = misc.boxplot(col)
      boxplots.append(boxplot)
      print >> sys.stderr, "A box-whisker plot of the deviations:", boxplot


   for col in range(len(column)):
      # print out a data row that can be redirected to a data set sort of thing
      mi, lq, me, uq, ma = boxplots[col]
      nums_to_print = (avg[col], bias[col], mi, lq, me, uq, ma)
      print "%s:slp%d" % (os.path.basename(dataset_path), col),
      print "%s:%s" % (reg_method.name, misc.stripspaces(repr(parameters)) ), 
      print "%d:%d" % (training_size, evaluation_size),
      print " ".join(["%.10f"] * len(nums_to_print)) % nums_to_print

   ##### This is the way a data row looks:
  #  <data set name>:<property number>
  #    <regression>:<parameters>
  #    <training size>:<evaluation size>
  #    <average error> <bias> <min> <lower quartile> <median> <upper quartile> <max>


def test_fires_fm_knn():
   test_fm(amf.regression.kNN, [5], '../data/fires.txt', 100, 500)


def test_fm_multi(regressions, dataset, training_sizes, evaluation_size):
   pass




def main():
   # Please don't inject malicious code here. Thanks!
   exec(sys.argv[1] + "(" + ( "" if len(sys.argv) == 1 else ",".join(sys.argv[2:]) ) + ")") 

if __name__ == "__main__":
   main()
