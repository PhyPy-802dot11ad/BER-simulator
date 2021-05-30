"""
Test the speed of data fetching from the database. Rerun (average) and repeat multiple times (distribution).

Normally should take tens of milliseconds for a single file. Still faster than generating the entire TX sequence.
"""

import time

import numpy as np
import matplotlib.pyplot as plt
from Helpers import get_Rm_and_Rc_from_MCS, get_MCS_list
from InputDB import InputDB

db = InputDB()
MCS = get_MCS_list()
timing_num = 2
timing_reps = 10

times = np.zeros((MCS.size, timing_reps))

for mcs_idx, mcs in enumerate(MCS):
    for i in range(timing_reps):

        start = time.time()
        for k in range(timing_num): _, __, ___ = db.read( mcs, 0 )
        elapsed = (time.time() - start) / timing_num

        times[mcs_idx, i] = elapsed

# Show results
for mcs_idx, mcs in enumerate(MCS):
    plt.scatter( [mcs]*timing_reps, times[mcs_idx, :] )
plt.xticks(MCS)
plt.show()
