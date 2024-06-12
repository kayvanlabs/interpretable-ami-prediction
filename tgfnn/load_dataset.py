# -*- coding: utf-8 -*-
"""
Load public datasets and synthetic datasets for classification.

The data loading functions will return a dictionary with the following keys:
variables: A np.ndarray of features with a shape (the number of samples, the number of features)
response: A np.ndarray of labels with a shape (the number of samples,)
num_classes: Int. The number of classes
category_info: A np.array with a shape (the number of features).  entry category_info[i] = 0 means the i-th variable 
        is a continuous variable. entry category_info[i] > 0 means the i-th variable is a categorical variable, and 
        the value is the number of levels. This information is only used in the proposed machine learning technique.
"""

import pandas as pd
import numpy as np

def load_data(dir):

    X_train = pd.read_csv(f'{dir}/X_train.csv', index_col=0)
    y_train = pd.read_csv(f'{dir}/y_train.csv', index_col=0)
    X_test = pd.read_csv(f'{dir}/X_test.csv', index_col=0)
    y_test = pd.read_csv(f'{dir}/y_test.csv', index_col=0)

    feature_names = X_train.columns.tolist()

    X_train = X_train.values
    X_test = X_test.values
    y_train = y_train.values.squeeze()
    y_test = y_test.values.squeeze()

    # determine each features' category
    category_info = np.zeros(X_train.shape[1]).astype(int) # initialize to zeros
    for i in range(X_train.shape[1]):
        if list(np.unique(X_train[:,i])) == [0,1]:
            category_info[i] = 2

    # compute class weights
    classes, counts = np.unique(y_train, return_counts=True)
    weights = counts.sum() / (len(np.unique(y_train)) * counts)
    weights_dict = dict(zip(classes, weights))

    dataset = {
        'X_train': X_train,
        'y_train': y_train,
        'X_test': X_test,
        'y_test': y_test,
        'num_classes': 2,
        'category_info': category_info,
        'feature_names': feature_names,
        'weights': weights_dict
    }

    return dataset