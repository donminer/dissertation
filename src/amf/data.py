# data.py contains everything that has to do with dealing with the actual
#  data and manipulating data sets.

import random
import copy
import sys

IND = 5
DEP = 6

def make_vartype(vartype_str):
   """
   Takes a string that labels columns in a data set.
   vartype_string should either have 'i' or 'd' in it, e.g., "iidid"

   i - independent variable
   d - dependent variable
   """
   # replace characters i and d with IND and DEP symbols.
   return tuple( (IND if c == 'i' else DEP) for c in vartype_str.strip() if not c.isspace())

def load(file_name):
   """
   Loads a data set from a file.

   The data set should be space delimited to distinguish columns, and newline
   delimited to distinguish rows.

   The first line should contain something that is to be passed into make_vartype.

   """

   file_h = open(file_name)

   vartype = make_vartype(file_h.readline().strip())

   dataset = []
   # go through each line and parse it
   for line in file_h.xreadlines():
      line = line.strip()

      # ignore empty lines
      if len(line) == 0:
         continue

      sline = line.split()
      if len(sline) != len(vartype):
         sys.stderr.write("Ignored line with wrong number of tokens: " + line + "\n")
         continue

      # split the data into two groups, depending on if they are independent or dependent variables.
      ind_list = []
      dep_list = []
      for idx, item in enumerate(sline):
         (ind_list if vartype[idx] == IND else dep_list).append(float(item) if item != 'NOENTRY' else 'NOENTRY')

   
      dataset.append( ( tuple(ind_list), tuple(dep_list) ) )

   dataset.sort()

   return tuple(dataset)

def random_subsets(data_set, n_list):
   """
   Returns a random subsets of the dataset with sizes specified in the n list.
   There will be no duplicates between subsets.
   """

   if sum(n_list) > len(data_set):
      raise IndexError, "Requested size of subsets, from set of size %d, are too large: %s (total size %d)" % (len (data_set), repr(n_list), sum(n_list))

   # generate a list of the indexes, then shuffle them. I will use these to randomly select from the data set.
   idxs = range(len(data_set))
   random.shuffle(idxs)

   subsets = []
   cur_offset = 0
   for subset_size in n_list:
      subsets.append( tuple(data_set[idx] for idx in idxs[cur_offset:cur_offset + subset_size]) )
      cur_offset += subset_size

   return subsets

def kfold_sets(data_set, k):
   """ Generates k sets of training/data sets for use in k-fold validation.
     Pairs come back as (training, validation)
   """

   validation_size = int(len(data_set) / k)

   shards = random_subsets(data_set, [validation_size] * k)

   for t in range(k):
      validation = shards[t]
      training = reduce(lambda x,y : x+y, shards[:t] + shards[t+1:])
      yield training, validation

def split_dep(data_set):
   """
   Split the data set into one-data-set-per-dependent variable.
   """

   num_dep = len(data_set[0][1])

   sets = [ [] for idx in range(num_dep) ]

   for ind, dep in data_set:
      # for each dependent variable here...
      for d_idx in range(num_dep):
         sets[d_idx].append((ind, dep[d_idx]))

   return sets






