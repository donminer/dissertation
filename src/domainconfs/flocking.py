import amf.regression as r

EXPERIMENT_NAME = "Flocking"

DATA_FILE = '../data/domaindata/processed_flocking.txt'
TRAINING_SIZES = range(30, 360, 30)
VALIDATION_SIZE = 100
REGRESSIONS = ( (r.kNN, []), (r.LOESS, [.05, 1]) )
RM_GRANULARITIES = range(15, 45, 5)

NUM_DEPENDENT = 1
