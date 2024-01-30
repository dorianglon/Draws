import pandas as pd


def write_df(df, file):
    """
    write dataframe to file
    :param df: dataframe
    :param file: file for df
    """

    df.to_csv(file, index=False)


def read_df(file):
    """
    Read dataframe from csv
    :param file: path to csv
    :return: dataframe
    """

    return pd.read_csv(file, encoding='windows-1254')
