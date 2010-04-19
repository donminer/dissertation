import amf.regression as r

EXPERIMENT_NAME = "Flocking"

DATA_FILE = '../data/domaindata/processed_flocking.txt'
TRAINING_SIZES = range(40, 440, 20)
VALIDATION_SIZE = 400
REGRESSIONS = ( (r.kNN, []), (r.LOESS, [.05, 1]) )
RM_GRANULARITIES = range(20, 80, 5)

NUM_DEPENDENT = 1
