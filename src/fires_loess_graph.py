# Plot points showing different ks for loess with the fires domain

# data set size = 100

import os
import amf
import amf.misc as misc

try:
   os.mkdir('../data/plots/fires_loess_graph')
except OSError:
   # directory already exists
   pass

def plotpoints_loess_fm_fires():

   data = amf.data.load('../data/fires.txt')
   subset = amf.data.random_subsets(data, [200])[0]

   window = .5
   for i in range(3):
      fm = amf.ForwardMapping(amf.regression.LOESS, [window, 1], 1)
      fm.train(subset)
      out = open('../data/plots/fires_loess_graph/window=%.1f' % window, 'w')

      for x in misc.xfrange(45.0, 75.0, .1):
         print >> out, x, fm.predict((x,))[0]

      window += .5
   gpscript = open('../data/plots/fires_loess_graph/plot.gp' ,'w')

   print >> gpscript, """
set xr [45.0:75.0]
set yr [0.0:1.0]
plot 'window=0.5' with lines, 'window=1.0' with lines, 'k=1.5' with lines
"""

plotpoints_loess_fm_fires()
