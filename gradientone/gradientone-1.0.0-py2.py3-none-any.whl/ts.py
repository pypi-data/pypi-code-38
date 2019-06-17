import base

logger = base.logger

import sys
sys.stderr = open('tserr.log', 'w')
sys.stdout = open('tsout.log', 'w')
print('print test')
logger.info('logger test')
logger.critical('crit test')
raise ValueError
