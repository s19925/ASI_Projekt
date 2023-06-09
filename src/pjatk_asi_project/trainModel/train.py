import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from typing import Any, Dict

from sklearn.preprocessing import MinMaxScaler
import wandb
import joblib
import logging

def prepare_data_for_modeling(data):
    #_rows = primary_param["n_rows"]
    '''Prepare data for modeling

    Inputs:
    data: a pandas dataframe with customers data

    Outputs:
    data: a pandas dataframe with customers data ready for modeling
        X: a pandas dataframe with customer features
        y: a pandas series with customer labels, encoded as integers (0 = low revenue, 1 = high revenue)

    '''
    # Suppress "a copy of slice from a DataFrame is being made" warning
    pd.options.mode.chained_assignment = None

    # prepare dataset for classification
    features = data.columns[1:-1]
    X = data[features]
    y = data['HeartDisease']

    # identify numeric features in X
    numeric_features = X.select_dtypes(include=[np.number]).columns
    # identify categorical features in X
    categorical_features = X.select_dtypes(exclude=[np.number]).columns

    # Normalize numeric features with MinMaxScaler
    scaler = MinMaxScaler()
    X[numeric_features] = scaler.fit_transform(X[numeric_features])

    # One-hot encode categorical features
    X = pd.get_dummies(X, columns=categorical_features)

    # transform bool in y to 0/1
    y = y.astype(int)

    # create a dataframe with the features and the labels
    data_prepared = pd.concat([X, y], axis=1)
    return data_prepared


def split_data(data):
    """Splits data into features and targets training and test sets.

    Inputs:
        data: Data containing features and target.

    Output:
        Split data.
    """
    # split dataset into train and test

    features = data.columns[:-1]
    X = data[features]
    y = data['HeartDisease']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    return X_train, X_test, y_train, y_test

def experiment_tracking():
    wandb.init(project="pjatk_asi_project")
    n_estimators = wandb.config.n_estimators
    max_depth = wandb.config.max_depth
    return n_estimators, max_depth


def train_model(X_train, y_train, n_estimators, max_depth):

    # Suppress "a copy of slice from a DataFrame is being made" warning
    pd.options.mode.chained_assignment = None
    model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=0)

    '''
    model = LogisticRegression(C=0.056, class_weight={}, dual=False, fit_intercept=True,
                intercept_scaling=1, l1_ratio=None, max_iter=1000,
                multi_class='auto', n_jobs=None, penalty='l2',
                random_state=123, solver='lbfgs', tol=0.0001, verbose=0,
                warm_start=False)
    '''

    model.fit(X_train, y_train)

    # save the model
    joblib.dump(model, 'data/07_model_output/model.pkl')

    return model


def evaluate_model(model, X_test, y_test):
    '''Evaluate a model predicting high-revenue customers from features and labels

    Inputs:
    model: a trained model
    X_test: a pandas dataframe with customers features


    Outputs:
    None

    '''

    labels = y_test.unique()
    y_pred = model.predict(X_test)
    y_probas = model.predict_proba(X_test)[:, 1]

    # evaluate the model
    accuracy = accuracy_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_probas)
    print('ROC AUC: %.3f' % roc_auc)
    print('Accuracy: %.3f' % accuracy)

    # printout the results
    logger = logging.getLogger(__name__)
    logger.info("Model has an accuracy of %.3f on test data.", accuracy)
    logger.info("Model has an ROC AUC of %.3f on test data.", roc_auc)



# Read customers_labeled dataset

def main():
    data = pd.read_csv('data/01_raw/heart.csv')

    data_prepared = prepare_data_for_modeling(data)
    X_train, X_test, y_train, y_test = split_data(data_prepared)

    model = train_model(X_train, y_train, experiment_tracking())
    accuracy, roc_auc = evaluate_model(model, X_test, y_test)

    wandb.log({"n_estimators and max_depth": experiment_tracking()})
    wandb.log({"accuracy": accuracy})
    wandb.log({"roc_auc": roc_auc})

    print("accuracy: ", accuracy)
    print("roc_auc: ", roc_auc)

sweep_configuration = {
    'method': 'bayes',
    'name': 'sweep',
    'metric': {'goal': 'maximize', 'name': 'roc_auc'},
    'parameters':
        {
            'n_estimators': {'min': 25, 'max': 200},
            'max_depth': {'min': 3, 'max': 10}
        }
}

sweep_id = wandb.sweep(sweep=sweep_configuration, project='my-pjatk-asi-project-sweep')
wandb.agent(sweep_id, function=main, count=4)