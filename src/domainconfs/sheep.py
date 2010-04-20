import amf.regression as r

EXPERIMENT_NAME = "SHEEP (Wolf Extinction)"

DATA_FILE = '../data/domaindata/processed_wolfsheep_noextinct.txt'
TRAINING_SIZES = range(40, 440, 40)
VALIDATION_SIZE = 200
REGRESSIONS = ( (r.kNN, []), )
RM_GRANULARITIES = range(15, 65, 10)

NUM_DEPENDENT = 4
