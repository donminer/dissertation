import amf.regression as r

EXPERIMENT_NAME = "Fires"

def sigmoid(p, x1):
   return p[0] + (p[1] - p[0]) / (1 + 2.7182818284590451 ** (-p[2] * (x1 - p[3])))

DATA_FILE = '../data/fires.txt'
TRAINING_SIZES = range(25, 125, 25)
VALIDATION_SIZE = 500
REGRESSIONS = ((r.kNN, []), (r.LOESS, [1.0, 1]), (r.NLR, [sigmoid, (0.0, 1.0, .65, 58.0)]))

NUM_DEPENDENT = 1
