"""
Simulation initializers and partitioners into multiple processes.
"""

from datetime import datetime as dt
import multiprocessing as mp
import sys

import numpy as np
import pandas as pd
from PhyPy802dot11adComponents import AWGN, Scrambler, Demapper, Decoder

from Input.InputDB import InputDB
from Helpers import get_Rm_and_Rc_from_MCS
from Log import LogIndividualMCSAndEbNo


def run_simulation_RX_loop(
        log,
        MCS,
        Eb_N0_db_list,
        demapping_algorithm,
        decoding_algorithm,
        max_decoder_iterations,
        allow_early_exit,
        min_bit_erors,
        max_transmitted_bits,
        min_sent_packets,
        process_pool_size ):
    """ Run simulated RX loop for the input parameters and all provided EbNo values.

    Spawn a new process for every EbNo value (concurency limited by pool size).
    Upon every pool execution, evaluate the returned bit errors. Quit if zero bit errors are returned.
    """

    # Batch-simulate sub-parts based on the list of EbNo values
    K = process_pool_size # Pool size
    N = np.ceil(Eb_N0_db_list.size / K).astype(int) # Number of sub-sequences
    for n in range(N):
        Eb_N0_db_sub_list = Eb_N0_db_list[n*K:(n+1)*K] # Overshooting indexes are automatically omitted

        # Generate the arguments for the simulation processes
        args = []
        for Eb_N0_db in Eb_N0_db_sub_list:
            args.append((
                log,
                MCS,
                Eb_N0_db,
                demapping_algorithm,
                decoding_algorithm,
                max_decoder_iterations,
                allow_early_exit,
                min_bit_erors,
                max_transmitted_bits,
                min_sent_packets
            ))

        # Run K-simulations and evaluate the results. Need (star)map to get the return values.
        with mp.Pool(K) as p:
            res = p.starmap(simulate_RX_loop, args)
        if not np.all(res): break # No errors detected -> break



def simulate_RX_loop(
        log,
        MCS,
        Eb_N0_db,
        demapping_algorithm,
        decoding_algorithm,
        max_decoder_iterations,
        allow_early_exit,
        min_bit_erors,
        max_transmitted_bits,
        min_sent_packets ):
    """Simulate transmission over noisy channel for a single combination of input parameters.
    """

    time_started = dt.now()

    # Set the log destination
    log.set_filepath(MCS, Eb_N0_db, demapping_algorithm, decoding_algorithm, max_decoder_iterations, allow_early_exit)

    # Redirect stdout to file
    sys.stdout = open(f'{log.get_universal_filepath()}_std.out', 'w')

    # Set pre-generated input TX sequence location and reset index to zero
    db = InputDB('Input/Sequence')
    input_sequence_index = 0

    # Extract Rc and Rm from MCS
    Rm, Rc = get_Rm_and_Rc_from_MCS(MCS)

    # Init channel
    awgn = AWGN()
    awgn.set_Eb_N0_db(Eb_N0_db)

    # Init scrambler
    scrambler = Scrambler()

    # Init demapper
    demapper = Demapper()
    demapper.set_modulation_rate(Rm)
    demapper.set_demapping_algorithm(demapping_algorithm)

    # Init decoder
    decoder = Decoder()
    decoder.set_code_rate(Rc)
    decoder.set_decoding_algorithm(decoding_algorithm)
    decoder.set_max_iterations(max_decoder_iterations)
    decoder.set_early_exit_flag(allow_early_exit)

    # Init error and transmitted bit counter
    bit_errors_total = 0
    transmitted_bits_total = 0
    sent_packets_total = 0

    # Init results storage
    results_columns = ['bit_errors', 'packet_errors', 'transmitted_bits', 'decoder_iterations']
    results = pd.DataFrame(columns=results_columns)

    while True:

        print( f'{dt.isoformat(dt.now())} | {MCS} | {Eb_N0_db}' )
        print( f'\t{bit_errors_total}' )
        print( f'\t{transmitted_bits_total}' )
        sys.stdout.flush()

        # Break when at least one of the three criteria is met
        # if np.all((bit_errors_total > min_bit_erors) + (transmitted_bits_total > max_transmitted_bits):
        if bit_errors_total >= min_bit_erors or transmitted_bits_total >= max_transmitted_bits:
            if sent_packets_total >= min_sent_packets:
                break

        # Get pre-generated TX sequence
        bit_sequence, mapped_sequence, scrambler_register = db.read( MCS, input_sequence_index )
        payload_length = bit_sequence.size

        # Add noise
        noisy_sequence, noise_variance = awgn.add_noise_to_sequence(mapped_sequence, Rm, Rc)

        # Receive (interpret) sequence
        demapped_sequence = demapper.demap_sequence( noisy_sequence, noise_variance )
        decoded_sequence, decoder_iterations = decoder.decode_sequence( demapped_sequence )
        scrambler.set_register(scrambler_register)
        descrambled_sequence = scrambler.scramble( decoded_sequence )

        bit_errors = np.sum(descrambled_sequence[:payload_length] != bit_sequence[:payload_length])
        packet_errors = int(bit_errors > 0)
        transmitted_bits = payload_length
        decoder_iterations_avg = np.average(decoder_iterations) # Average iterations per packet

        bit_errors_total += bit_errors
        transmitted_bits_total += transmitted_bits
        sent_packets_total += 1

        data = np.array([[bit_errors, packet_errors, transmitted_bits, decoder_iterations_avg]])
        # data = np.array([[0, 0, 0, 0]])
        results = results.append(
            pd.DataFrame(
                data=data,
                index=[input_sequence_index],
                columns=results_columns
            )
        )

        input_sequence_index += 1

    time_ended =  dt.now()

    log.save_data(
        results, MCS, Eb_N0_db
    )

    log.save_metadata(
        MCS=MCS,
        Eb_N0_db=Eb_N0_db,
        demapping_algorithm=demapping_algorithm,
        decoding_algorithm=decoding_algorithm,
        max_decoder_iterations=max_decoder_iterations,
        allow_early_exit=allow_early_exit,
        min_bit_erors=min_bit_erors,
        max_transmitted_bits=max_transmitted_bits,
        min_sent_packets=min_sent_packets,
        payload_length=payload_length,
        Rm=Rm,
        Rc=Rc,
        time_started=dt.isoformat(time_started),
        time_ended=dt.isoformat(time_ended)
    )

    return bit_errors_total
