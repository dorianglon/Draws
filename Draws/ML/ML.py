from collections import Counter
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from imblearn.over_sampling import SMOTE
from FeatureEngineering.feature_engineering import *
from FeatureEngineering.feature_engineering import one_hot_encode
from Resources.resources import *
from numpy import mean
from numpy import std
from sklearn.datasets import make_classification
from sklearn.model_selection import cross_val_score, GridSearchCV, RandomizedSearchCV, train_test_split
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import GradientBoostingClassifier
import math


def get_precision_matrix(definitions, y_test, y_pred):
    reverse_factor = dict(zip(range(2), definitions))
    y_test = np.vectorize(reverse_factor.get)(y_test)
    y_pred = np.vectorize(reverse_factor.get)(y_pred)
    print(pd.crosstab(y_test, y_pred, rownames=['Actual Class'], colnames=['Predicted Class']))


def KNN(X_train, y_train, X_test, y_test):
    neighbors = list(range(1, 21, 1))
    weights = ['uniform', 'distance']
    algorithms = ['auto', 'ball_tree', 'kd_tree', 'brute']
    ps = [1, 2]

    for neighbor in neighbors:
        for weight in weights:
            for algorithm in algorithms:
                for p in ps:
                    print(neighbor, ' : ', weight, ' : ', algorithm, ' : ', p)
                    knn = KNeighborsClassifier(n_neighbors=neighbor, weights=weight, algorithm=algorithm, p=p)
                    knn.fit(X_train, y_train)
                    y_pred = knn.predict(X_test.to_numpy())
                    get_precision_matrix([0, 1], y_test, y_pred)
                    print(80 * '-')


def SVM(X_train, y_train, X_test, y_test):
    Cs = [0.00001, 0.00005, 0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 10]
    kernels = ['linear', 'poly', 'rbf', 'sigmoid']
    for C in Cs:
        for kernel in kernels:
            print(C, ' : ', kernel)
            svm = SVC(C=C, kernel=kernel, class_weight={0: 1, 1: 3})
            svm.fit(X_train, y_train)
            y_pred = svm.predict(X_test)
            get_precision_matrix([0, 1], y_test, y_pred)
            print(80 * '-')


def xgboost(X_train, y_train, X_test, y_test):
    losses = ['log_loss', 'exponential']
    rates = [0.0001, 0.001, 0.01, 0.1, 1, 10]
    ns = [50, 100, 300, 500]
    criterias = ['friedman_mse', 'squared_error']
    for loss in losses:
        for rate in rates:
            for n in ns:
                for crit in criterias:
                    print(loss, ' : ', rate, ' : ', n, ' : ', crit)
                    xgb = GradientBoostingClassifier(loss=loss, learning_rate=rate, n_estimators=n, criterion=crit)
                    xgb.fit(X_train, y_train)
                    y_pred = xgb.predict(X_test)
                    get_precision_matrix([0, 1], y_test, y_pred)
                    print(80*'-')


def change_to_week_num(df):
    weeks = []
    for index, row in df.iterrows():
        game_num = row['Game Number']
        game_num = 10 * math.ceil(game_num / 10)
        weeks.append(str(game_num / 10))
    df['Week Number'] = weeks
    return df


def predict_draw():
    df = pd.read_csv(EPL + 'dataset.csv')
    del df['Season']

    df = change_to_week_num(df)
    del df['Game Number']

    ftr_col = df['FTR'].tolist()
    ftrs = []
    for ftr in ftr_col:
        if ftr == 'D':
            ftrs.append(1)
        else:
            ftrs.append(0)

    del df['FTR']
    df['FTR'] = ftrs

    X_train, X_test, y_train, y_test = train_test_split(
        df.drop('FTR', axis=1), df['FTR'], test_size=0.2,
        random_state=37)

    X_train, X_test = one_hot_encode(X_train, X_test, ['Home Team', 'Away Team', 'Week Number'])

    smote = SMOTE()
    X_train, y_train = smote.fit_resample(X_train, y_train)

    numerical_columns = ['P(Home) 1', 'P(Away) 1', 'P(Draw) 1', 'P(Home) 2', 'P(Away) 2', 'P(Draw) 2'
        , 'P(Home) 3', 'P(Away) 3', 'P(Draw) 3', 'Home Win odds', 'Away Win odds', 'Draw odds']

    # X_train, X_test = standardize_features(X_train, X_test)
    X_train, X_test = standardize_only_certain_columns(X_train, X_test, numerical_columns)

    # KNN(X_train, y_train, X_test, y_test)
    # SVM(X_train, y_train, X_test, y_test)
    xgboost(X_train, y_train, X_test, y_test)


if __name__ == '__main__':
    predict_draw()
