"""
Generate random sequences and their corresponding TX (mapped) sequences.

"""

import numpy as np
from tqdm import tqdm
from phy802dot11adOptimizedComponents import Scrambler, Encoder, Mapper

from Helpers import get_Rm_and_Rc_from_MCS, get_MCS_list
from InputDB import InputDB

PAYLOAD_LEN = 262_143 * 8
NUM_OF_SEQ = 50
SEED = 0

# Read MCS csv and filter out supported MCSs
MCS = get_MCS_list()

db = InputDB('Sequence')

scrambler = Scrambler()
scrambler.set_register(scrambler.generate_pseudorandom_seed())
encoder = Encoder()
mapper = Mapper()


r = np.random.RandomState(SEED)  # Get mapped sequences for the same input data

tqdm_total = tqdm(range(NUM_OF_SEQ*MCS.size), desc = 'Total progress', leave=False)

for i in range(NUM_OF_SEQ):

    raw_bit_sequence = r.randint(0, 2, PAYLOAD_LEN, dtype=np.uint8)

    for mcs in MCS:

        tqdm_total.update(1)

        Rm, Rc = get_Rm_and_Rc_from_MCS(mcs)  # Extract Rc and Rm
        encoder.set_code_rate(Rc)
        mapper.set_modulation_rate(Rm)

        padded_payload_length = int(np.ceil(PAYLOAD_LEN / (Rc * 672)) * Rc * 672)  # Payload length changes with every code rate
        padding_len = padded_payload_length - PAYLOAD_LEN
        bit_sequence = np.concatenate(( raw_bit_sequence, np.zeros((padding_len), dtype=np.uint8) ))

        # Random reset scrambler every time and save the register value
        scrambler.set_register(scrambler.generate_pseudorandom_seed())
        scrambler_register = scrambler.get_register()

        scrambled_sequence = scrambler.scramble(bit_sequence)
        encoded_sequence = encoder.encode_sequence(scrambled_sequence)
        mapped_sequence = mapper.map_sequence(encoded_sequence)

        db.write( raw_bit_sequence, mapped_sequence, scrambler_register, mcs, i )
