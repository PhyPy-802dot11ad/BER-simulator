import pandas as pd


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