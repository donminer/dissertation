# Plot points showing different ks for knn with the fires domain

# data set size = 100

import os
import amf
import amf.misc as misc

try:
   os.mkdir('../data/plots/fires_knn_graph')
except OSError:
   # directory already exists
   pass

def plotpoints_knn_fm_fires():

   data = amf.data.load('../data/fires.txt')
   subset = amf.data.random_subsets(data, [200])[0]

   for k in range(5, 30, 5):
      fm = amf.ForwardMapping(amf.regression.kNN, [k], 1)
      fm.train(subset)
      out = open('../data/plots/fires_knn_graph/k=%d' % k, 'w')

      for x in misc.xfrange(45.0, 75.0, .1):
         print >> out, x, fm.predict((x,))[0]

   gpscript = open('../data/plots/fires_knn_graph/plot.gp' ,'w')

   print >> gpscript, """
set xr [45.0:75.0]
set yr [0.0:1.0]
plot 'k=5' with lines, 'k=15' with lines, 'k=25' with lines
"""

plotpoints_knn_fm_fires()
