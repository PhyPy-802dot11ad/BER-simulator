"""
Data storage definitions.

"""

import os
import pickle


class LogBase():

    def __init__(self, parent_dir_path, sub_dir_name):
        self.parent_dir_path = parent_dir_path
        self.sub_dir_name = sub_dir_name
        # self.set_sub_dir_name()

    def set_sub_dir_name(self):
        dirs = os.listdir(self.parent_dir_path)
        try:
            new_dir_idx = int(dirs[-1]) + 1
        except:
            new_dir_idx = 0
        self.sub_dir_name = f'{new_dir_idx:04d}'


class Log(LogBase):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_proc_dir_name(self, process_id):
        self.proc_dir_name = f'{process_id:04d}'
        self.dirpath = os.path.join( self.parent_dir_path, self.sub_dir_name, self.proc_dir_name )
        if not os.path.exists(self.dirpath): os.makedirs(self.dirpath)

    def save_data(self, bit_errors, packet_errors, transmitted_bits, decoder_iterations ):
        """Save data as CSV."""

        data = [bit_errors, packet_errors, transmitted_bits, decoder_iterations]
        name = ['bit_errors', 'packet_errors', 'transmitted_bits', 'decoder_iterations']

        for d, n in zip(data, name):
            full_path = os.path.join( self.dirpath, f'{n}.csv' )
            d.to_csv(full_path)

    def save_metadata(self, **kwargs):
        """Save meta as pickle"""

        data = {}

        for key in kwargs:
            data[f'{key}'] = kwargs[key]

        full_path = os.path.join( self.dirpath, 'metadata.pkl' )
        with open(full_path, 'wb') as f: pickle.dump(data, f)


class LogIndividualMCSAndEbNo(LogBase):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dirpath = os.path.join( self.parent_dir_path, self.sub_dir_name )
        if not os.path.exists(self.dirpath): os.makedirs(self.dirpath)

    def set_filepath(self, MCS, Eb_N0, demapping_algorithm, decoding_algorithm, max_decoder_iterations, allow_early_exit):
        name_root = f'{MCS}_{Eb_N0}db_{demapping_algorithm}_{decoding_algorithm}_{max_decoder_iterations}_{allow_early_exit}'
        # self.path_csv = os.path.join( self.dirpath, f'{name_root}.csv' )
        # self.path_metadata = os.path.join( self.dirpath, f'{name_root}_metadata.pkl' )
        self.path_universal = os.path.join( self.dirpath, name_root )
        self.path_csv = f'{self.path_universal}.csv'
        self.path_metadata = f'{self.path_universal}_metadata.pkl'

    def get_universal_filepath(self):
        """Return the process-specific log filepath, without a file extension."""
        return self.path_universal

    def save_data(self, df, MCS, Eb_N0 ):
        """Save data as CSV."""
        df.to_csv(self.path_csv)

    def save_metadata(self, **kwargs):
        """Save meta as pickle"""

        data = {}

        for key in kwargs:
            data[f'{key}'] = kwargs[key]

        with open(self.path_metadata, 'wb') as f: pickle.dump(data, f)
