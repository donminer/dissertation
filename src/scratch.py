import sys

import amf
import amf.misc as misc

def test_fires_fm_knn():
   print "Testing a kNN forward mapping on the fires data set."

   # initialize the fires data set
   all_data = amf.data.load('../data/fires.txt')
   training, validation = amf.data.random_subsets(all_data, [100, 5000])

   # initialize the forward mapping with kNN
   knn = amf.ForwardMapping(amf.regression.kNN, [5])

   # Run the tests
   error_list, time_per = amf.evaluation.eval_fm(knn, training, validation)
   print "Each query took about", time_per, "seconds."

   # calculate some stats on the errors

   errors = error_list.errors()
   devias = error_list.deviations()
   column = misc.to_columns(devias)

   print "The everage error was", misc.col_average(errors)
   print "The average deviation (bias) was", misc.col_average(devias)

   print "The worst error was", misc.col_max(errors)
   print "The lowest error was", misc.col_min(errors)

   for col in column:
      print "A box-whisker plot of the deviations:", misc.boxplot(col)



def main():
   # Please don't inject malicious code here. Thanks!
   exec(sys.argv[1] + "(" + ( "" if len(sys.argv) == 1 else ",".join(sys.argv[2:]) ) + ")") 



if __name__ == "__main__":
   main()
