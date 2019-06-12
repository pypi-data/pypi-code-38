import math
from random import random

import numpy as np


def visualize(alloc, num_sockets):
    d = len(alloc[0])
    n = num_sockets
    b = d // n

    for t in range(n):
        S1 = [' '] * (b // 2)
        S2 = [' '] * (b // 2)
        for job_id, job in enumerate(alloc):
            for i in range(t * b, (t + 1) * b):
                if job[i] == 1:
                    if (i - b) % 2 == 0:
                        S1[(i - b) // 2] = str(job_id + 1)
                    else:
                        S2[(i - b) // 2] = str(job_id + 1)
        print('| ' + ' | '.join(S1) + ' |')
        print('| ' + ' | '.join(S2) + ' |')
        if (t < n - 1):
            print('| ' + '-' * len(' | '.join(S1)) + ' |')