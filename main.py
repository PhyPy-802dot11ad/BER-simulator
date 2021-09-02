import os
import multiprocessing as mp

import numpy as np

from Simulation import simulate_RX_loop, run_simulation_RX_loop
from Log import LogIndividualMCSAndEbNo


os.nice(10) # Set niceness so other can work on the machine

SUBPROCESS_POOL_SIZE = 4 # Determines how often early stopping will be checked, in terms of EbNo batch simulations.

MIN_ERROR_BITS = 100 # As in MATLAB docs
MAX_TRANSMITTED_BITS = 10**9 # As in MATLAB docs
MIN_SENT_PACKETS = 3 # Custom to smooth out parts of the curve with high BER values

# MIN_ERROR_BITS = 0 # As in MATLAB docs
# MAX_TRANSMITTED_BITS = 10**8 # As in MATLAB docs
# MIN_SENT_PACKETS = 1 # Custom to smooth out parts of the curve with high BER values

Eb_N0_db_list = np.arange(0.0, 15.0, 0.25)

MCS_list = np.array([2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 12.1, 12.3, 12.4, 12.5])
demapping_algorithm = 'decision threshold'
# max_decoder_iterations = 10
max_decoder_iterations = [20, 18, 17, 20, 10, 9, 8, 10, 5, 4, 4, 5, 3, 3, 3] # Corresponding to MCS, just before decoder becomes bottleneck

decoding_algorithm = 'MSA'
allow_early_exit = True

log_dir = 'Log'
log_sub_dirs = os.listdir(log_dir)
try:
    new_dir_idx = int(log_sub_dirs[-1]) + 1
except:
    new_dir_idx = 0
log_sub_dir = f'{new_dir_idx:04d}'

# fun = lambda MCS, Eb_N0_db, demapping_algorithm, max_decoder_iterations: simulate_RX_loop(
#     LogIndividualMCSAndEbNo(parent_dir_path=log_dir, sub_dir_name=log_sub_dir),
#     MCS,
#     Eb_N0_db,
#     demapping_algorithm,
#     decoding_algorithm,
#     max_decoder_iterations,
#     allow_early_exit,
#     MIN_ERROR_BITS,
#     MAX_TRANSMITTED_BITS,
#     MIN_SENT_PACKETS )

fun = lambda MCS, demapping_algorithm, max_decoder_iterations: run_simulation_RX_loop(
    LogIndividualMCSAndEbNo(parent_dir_path=log_dir, sub_dir_name=log_sub_dir),
    MCS,
    Eb_N0_db_list,
    demapping_algorithm,
    decoding_algorithm,
    max_decoder_iterations,
    allow_early_exit,
    MIN_ERROR_BITS,
    MAX_TRANSMITTED_BITS,
    MIN_SENT_PACKETS,
    SUBPROCESS_POOL_SIZE
)

number_of_combinations = MCS_list.size * Eb_N0_db_list.size
print(f'Running {number_of_combinations} sub-processes from a pool with size {MCS_list.size*SUBPROCESS_POOL_SIZE}.')

# for MCS in MCS_list:
#     for Eb_N0_db in Eb_N0_db_list:
#         p = mp.Process(target=fun, args=(MCS, Eb_N0_db, demapping_algorithm, max_decoder_iterations))
#         p.start()
#         # fun(MCS, Eb_N0_db, demapping_algorithm, max_decoder_iterations)

# for MCS in MCS_list:
for MCS, mdi in zip(MCS_list, max_decoder_iterations):
    # p = mp.Process(target=fun, args=(MCS, demapping_algorithm, max_decoder_iterations))
    p = mp.Process(target=fun, args=(MCS, demapping_algorithm, mdi))
    p.start()
    # fun(MCS, demapping_algorithm, max_decoder_iterations)
    # fun(MCS, demapping_algorithm, mdi)
