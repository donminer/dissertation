# This script takes each row of a data set and processes it for use with AMF
import sys
from amf.regression import NLR
import math

no_entry = "NOENTRY"

def map_flocking(tokens):
   """
   The flocking data set looks like this:
   0     1     2     3
   FLOAT FLOAT FLOAT LIST
   It takes the average of the list and returns it with the independent variables.
   """

   avg = sum(tokens[3]) / len(tokens[3])
   
   return (tokens[0], tokens[1], tokens[2], avg)

def map_wolfsheep(tokens):
   """
   The wolf sheep predation data looks like this:

      wolf-reproduce  sheep-reproduce  wolf-gain-from-food  sheep-gain-from-food  grass-regrowth-time
      0               1                2                    3                     4
      FLOAT           FLOAT            FLOAT                FLOAT                 FLOAT

      #wolves   #sheep
      5         6
      LIST      LIST

      The output is:
      i0 i1 i2 i3 i4 wolf-extinct wolf-population-nowolf sheep-population sheep-variance
   """
   
   i0, i1, i2, i3, i4, wolves, sheep = tokens

   wolf_extinct = 1.0 if wolves[-1] == 0.0 else 0.0
   wolf_population_nowolf = sum(wolves) / len(wolves) if not wolf_extinct else no_entry

   sheep_population = sum(sheep) / len(sheep) if not wolf_extinct else no_entry

   sheep_variance = numpy.var(sheep) if not wolf_extinct else no_entry

   return i0, i1, i2, i3, i4, wolf_extinct, wolf_population_nowolf, sheep_population, sheep_variance


def map_aids(tokens):
   """
   The aids data looks like this:

   condom-use  test-ferquency  hiv-  hiv+
   0           1               2     3
   FLOAT       FLOAT           LIST  LIST

   the output is:
   i0 i1  p0 p1 p2 p3

   """

   def sigmoid(p, x1):
      """
      p[0] - minimum asymptote
      p[1] - max asymptote
      p[2] - growth rate
      p[3] - location of the inflexion point
      """
      return p[0] + (p[1] - p[0]) / (1 + math.e ** (-p[2] * (x1 - p[3])))

   def negsigmoid(p, x1):
      return 300 - sigmoid(p, x1)


   def find_closest(data, val):
      distances = [ (abs(item - val), idx) for idx, item in enumerate(data) ]
      distances.sort()
      closest = [ idx for dist, idx in distances if dist == distances[0][0] ]

      return sum(closest) / len(closest)

   
   use, freq, hivminus, hivplus = tokens

   # 0 because it starts near 0
   # hivplus[-1] because the value will end up at hivplus[-1]
   # 1.0 is just a random guess
   # the inflection point is going to be able halfway there...
   guessp = [0.0, hivplus[-1], .01, find_closest(hivplus, (hivplus[-1] - hivplus[0])/ 2.0)  ]
   guessm = [300 - hivminus[0], 300 - hivminus[-1], .01, find_closest(hivminus, (hivminus[-1] - hivminus[0])/2.0) ]

   nlr_hivminus = NLR(negsigmoid, guessm)
   nlr_hivplus = NLR(sigmoid, guessp)

   nlr_hivminus.train([ ((x,), y) for x,y in enumerate(hivminus)])
   nlr_hivplus.train([ ((x,), y) for x,y in enumerate(hivplus)])

   hmf = open('hivminus.txt', 'w')
   hmf.write("\n".join("%d %f" % x for x in enumerate(hivminus)))
   hmf.close()

   hpf = open('hivplus.txt', 'w')
   hpf.write("\n".join("%d %f" % x for x in enumerate(hivplus)))
   hpf.close()

   #print ("plot %f + (%f - "+repr(nlr_hivminus.opt[0])+") / (1 + 2.7182 ** (-%f * (x - %f))), ") % tuple(nlr_hivminus.opt),
   print ("plot 300 - (%f + (%f - "+repr(nlr_hivminus.opt[0])+") / (1 + 2.7182 ** (-%f * (x - %f)))), ") % tuple(nlr_hivminus.opt),
   #print (repr(nlr_hivplus.opt[1])+" - (%f + (%f - "+repr(nlr_hivplus.opt[0])+") / (1 + 2.7182 ** (-%f * (x - %f)))), 'hivplus.txt' with dots, 'hivminus.txt' with dots") % tuple(nlr_hivplus.opt)
   print ("(%f + (%f - "+repr(nlr_hivplus.opt[0])+") / (1 + 2.7182 ** (-%f * (x - %f)))), 'hivplus.txt' with dots, 'hivminus.txt' with dots") % tuple(nlr_hivplus.opt)


   raw_input('..')



def linear_scale(dataset):
   """Linearly scales an entire data set to a range of 0-1"""

   maxs = list(dataset[0])
   mins = list(dataset[0])

   for datarow in dataset:
      for idx, item in enumerate(datarow):
         if item == no_entry: continue

         maxs[idx] = max(maxs[idx], item)
         mins[idx] = min(mins[idx], item)

   return [ [ (no_entry if item == no_entry else(item - mins[idx]) / (maxs[idx] - mins[idx])) for idx, item in enumerate(datarow) ] for datarow in dataset ]

def parse(data_file_path):
   """
   Applies 'map_function' to each row (as a string) of a data set.
   'map_function' should takes a list of tokens as the only parameter and return a string as the only parameter.
   Prints out the new data set.
   """

   return [ [ float(token) if token.find(',') == -1 else [ float(item) for item in token.split(',') ] for token in line.split() ] for line in open(data_file_path).xreadlines() ]

def dump(dataset):
   print "\n".join( " ".join(str(item) for item in row) for row in dataset)

def process_flocking():
   parsed = parse(sys.argv[2])

   averaged = map(map_flocking, parsed)

   scaled = linear_scale(averaged)

   dump(scaled)

def process_wolfsheep():
   parsed = parse(sys.argv[2])

   averaged = map(map_wolfsheep, parsed)

   scaled = linear_scale(averaged)

   dump(scaled)
   
def process_aids():
   parsed = parse(sys.argv[2])

   averaged = map(map_aids, parsed)

   scaled = linear_scale(averaged)

   dump(scaled)




exec(sys.argv[1] + "()")
