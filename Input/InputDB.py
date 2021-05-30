import os

import numpy as np


class InputDB():

    def __init__(self, storage_path):
        self.storage = storage_path

    def write(self, raw_bit_sequence, mapped_sequence, scrambler_register, mcs, index):
        """Save unpadded bit sequence, mappend sequence (including zero padding), and initial scrambler register."""
        path = os.path.join(self.storage, f'{mcs}', f'{index:04d}')
        np.savez( path,
            unpadded_bit_sequence=raw_bit_sequence,
            mapped_sequence=mapped_sequence,
            scrambler_register=scrambler_register
        )

    def read(self, mcs, index):
        path = os.path.join(self.storage, f'{mcs}', f'{index:04d}.npz')
        if not os.path.exists(path): raise ReferenceError (f'Requested non-existent file at {path}')
        data = np.load(path)
        return data['unpadded_bit_sequence'], data['mapped_sequence'], data['scrambler_register']