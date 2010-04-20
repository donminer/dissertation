import amf.regression as r

EXPERIMENT_NAME = "Sheep"

DATA_FILE = '../data/domaindata/processed_wolfsheep_noextinct2.txt'
TRAINING_SIZES = range(40, 50, 40)
VALIDATION_SIZE = 10
REGRESSIONS = ( (r.kNN, []), )
RM_GRANULARITIES = range(5, 25, 5)

NUM_DEPENDENT = 3
