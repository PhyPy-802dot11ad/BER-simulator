"""
Populate Sequence directory with subdirs associated with subdirs.
"""

import os

import pandas as pd

mcs_df = pd.read_csv('MCS_table.csv', index_col=0)
mcs_list = mcs_df.index.values

for mcs in mcs_list:
    os.mkdir(f'Sequence/{mcs}')
    with open(f'Sequence/{mcs}/.gitignore', 'w') as f:
        f.write( '*\n' )
        f.write( '!.gitignore\n' )
