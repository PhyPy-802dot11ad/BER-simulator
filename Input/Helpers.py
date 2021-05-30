import pandas as pd

def get_MCS_list():
    """Get list of all MCSs available for simulation.

    :return: MCSs that can be simulated.
    :rtype: list
    """
    mcs_df = pd.read_csv('MCS_table.csv', index_col=0)
    mcs_df = mcs_df[mcs_df['Repetition'] == 1][mcs_df['Code_rate'] != 0.875]
    return mcs_df.index

def get_Rm_and_Rc_from_MCS(MCS):
    """Get the modulation- and coder rate for an individual MCS.

    :param MCS: Target MCS
    :type MCS: float
    :return: Modulation- and code rate
    :rtype: tuple
    """
    df = pd.read_csv('MCS_table.csv', index_col='MCS')
    try:
        Rm = df.loc[MCS]['Modulation_rate']
        Rc = df.loc[MCS]['Code_rate']
        return (Rm, Rc)
    except:
        raise ValueError(f"Unknonw MCS {MCS}.")