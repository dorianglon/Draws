import numpy as np
import pandas as pd
import os
from sklearn.pipeline import Pipeline
from Resources.resources import *
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import seaborn as sns
import scipy.stats as stats
import time
from sklearn.model_selection import train_test_split
from sklearn.linear_model import BayesianRidge
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.impute import KNNImputer
from feature_engine.encoding import CountFrequencyEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsRegressor
from feature_engine.encoding import OneHotEncoder
from feature_engine.encoding import OrdinalEncoder
from sklearn.compose import ColumnTransformer
import warnings
warnings.filterwarnings("ignore")


def missing_data_per_feature(df):
    print(df.isnull().sum())


def check_categorical_cardinality(df):
    print(df['Home Team'].nunique())


def frequency_of_categories(df):
    label_freq = df['Home Team'].value_counts() / len(df)
    print(label_freq)


def histogram_of_features(df):
    for column in df:
        if column != 'Home Team' and column != 'Away Team' and column != 'Game Number':
            sns.distplot(df[column], bins=30)
            plt.show()
            time.sleep(0.25)


def qq_plots(df):
    for column in df:
        if column != 'Home Team' and column != 'Away Team' and column != 'Game Number':
            stats.probplot(df[column], dist="norm", plot=plt)
            plt.title(column)
            plt.show()
            time.sleep(0.25)


def find_IQR_boundaries(df, column, distance):
    IQR = df[column].quantile(0.75) - df[column].quantile(0.25)
    lower_boundary = df[column].quantile(0.25) - (IQR * distance)
    upper_boundary = df[column].quantile(0.75) + (IQR * distance)
    return upper_boundary, lower_boundary


def get_outliers(df):
    for column in df:
        if column != 'Home Team' and column != 'Away Team' and column != 'Game Number' and column != 'FTR':
            print(column)
            upper_boundary, lower_boundary = find_IQR_boundaries(df, column, 3)
            outliers = np.where(df[column] > upper_boundary, True,
            np.where(df[column] < lower_boundary, True, False))
            outliers_df = df.loc[outliers, column]
            print(outliers_df)
            print(80*'-')


def compare_feature_magnitude(df):
    for column in df:
        if column != 'Id' and column != 'EJ' and column != 'Class':
            # print(df.describe())
            print(df[column].max() - df[column].min())


def check_linearity_between_features(df, observe):
    x = df[observe].tolist()
    for column in df:
        if column != 'Game Number' and column != observe:
            y = df[column].tolist()
            plt.scatter(x, y)
            plt.title(column)
            plt.show()
            time.sleep(2)


def multivariate_imputation_linear_regression(train, test, categorical_columns):
    indices_train = []
    for i in range(len(categorical_columns)):
        col, col_index, name = train[categorical_columns[i]].tolist(), train.columns.get_loc(categorical_columns[i])\
            , categorical_columns[i]
        indices_train.append([col, col_index, name])
        train = train.drop(categorical_columns[i], axis=1)

    columns = []
    for column in train:
        columns.append(column)

    lr = LinearRegression()
    imp = IterativeImputer(estimator=lr, missing_values=np.nan, max_iter=10, verbose=0, imputation_order='roman',
                           random_state=0)

    imp.fit(train)
    train = imp.transform(train)
    train = pd.DataFrame(train, columns=columns)

    for col in indices_train:
        train.insert(col[1], col[2], col[0])

    indices_test = []
    for i in range(len(categorical_columns)):
        col, col_index, name = test[categorical_columns[i]].tolist(), test.columns.get_loc(categorical_columns[i])\
            , categorical_columns[i]
        indices_test.append([col, col_index, name])
        test = test.drop(categorical_columns[i], axis=1)

    columns = []
    for column in test:
        columns.append(column)

    test = imp.transform(test)
    test = pd.DataFrame(test, columns=columns)

    for col in indices_test:
        test.insert(col[1], col[2], col[0])

    return train, test


def multivariate_imputation_knn(train, test):
    ej_train, ej_index_train = train['EJ'].tolist(), train.columns.get_loc('EJ')
    train = train.drop('EJ', axis=1)
    columns = []
    for column in train:
        columns.append(column)

    imp = IterativeImputer(estimator=KNeighborsRegressor(n_neighbors=7), max_iter=10, random_state=0, verbose=0)
    imp.fit(train)
    train = imp.transform(train)
    train = pd.DataFrame(train, columns=columns)
    train.insert(ej_index_train, 'EJ', ej_train)

    ej_test, ej_index_test = test['EJ'].tolist(), test.columns.get_loc('EJ')
    test = test.drop('EJ', axis=1)
    columns = []
    for column in test:
        columns.append(column)

    test = imp.transform(test)
    test = pd.DataFrame(test, columns=columns)
    test.insert(ej_index_test, 'EJ', ej_test)

    return train, test


def cat_frequency_encode(train, test):
    count_enc = CountFrequencyEncoder(encoding_method='frequency', variables='EJ')
    count_enc.fit(train)
    train = count_enc.transform(train)
    test = count_enc.transform(test)
    return train, test


def one_hot_encode(train, test, columns_to_encode):
    ohe_enc = OneHotEncoder(variables=columns_to_encode, drop_last=False)
    ohe_enc.fit(train)
    X_train_enc = ohe_enc.transform(train)
    X_test_enc = ohe_enc.transform(test)
    return X_train_enc, X_test_enc


def ordinal_encoding(train, test):
    ordinal_enc = OrdinalEncoder(encoding_method='arbitrary', variables='EJ')
    ordinal_enc.fit(train)
    train = ordinal_enc.transform(train)
    test = ordinal_enc.transform(test)
    return train, test


def standardize_features(train, test):
    scaler = StandardScaler()
    scaler.fit(train)
    train_scaled = scaler.transform(train)
    test_scaled = scaler.transform(test)
    final_train = pd.DataFrame(train_scaled, columns=train.columns)
    final_test = pd.DataFrame(test_scaled, columns=test.columns)
    return final_train, final_test


def standardize_only_certain_columns(train, test, numerical_columns):
    scaler = StandardScaler()
    scaler.fit(train[numerical_columns])
    train[numerical_columns] = scaler.transform(train[numerical_columns])
    test[numerical_columns] = scaler.transform(test[numerical_columns])
    return train, test


if __name__ == '__main__':
    df = pd.read_csv(EPL + 'dataset.csv')
    del df['Season']
    # check_categorical_cardinality(df)
    # frequency_of_categories(df)
    # histogram_of_features(df)
    # qq_plots(df)
    # get_outliers(df)
    # check_linearity_between_features(df, 'P(Home) 1')
