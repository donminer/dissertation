import amf.regression as r

EXPERIMENT_NAME = "AIDS"

DATA_FILE = '../data/domaindata/processed_aids.txt'
TRAINING_SIZES = range(30, 330, 30)
VALIDATION_SIZE = 1000
REGRESSIONS = ( (r.kNN, []), (r.LOESS, [.05, 1]) )
RM_GRANULARITIES = range(15, 65, 10)

NUM_DEPENDENT = 4
