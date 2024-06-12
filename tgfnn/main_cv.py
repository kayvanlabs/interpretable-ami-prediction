# -*- coding: utf-8 -*-
"""
Performing nested cross-validation on the dataset with machine learning techniques.
The inner cross-validation is used for hyper-parameter tuning.
The outer cross-validation is used to better evaluate the performance of the machine learning techniques.
"""
import numpy as np
import pandas as pd
import pickle
import sklearn
from sklearn.model_selection import StratifiedShuffleSplit, RandomizedSearchCV
from sklearn.svm import SVC  
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression 
from sklearn.naive_bayes import GaussianNB
import sys
import os
import pickle
import load_dataset
import utils
from generalized_fuzzy_net import GeneralizedFuzzyClassifier
from mlxtend.classifier import EnsembleVoteClassifier
import xgboost
from imblearn.under_sampling import RandomUnderSampler


def multiclass_roc_auc_score(truth, pred, average="macro"):
    lb = sklearn.preprocessing.LabelBinarizer()
    lb.fit(truth)
    truth = lb.transform(truth)
    pred = lb.transform(pred)            
    return sklearn.metrics.roc_auc_score(truth, pred, average=average)

def nested_cross_validation(X, y, num_classes, category_info, feature_names, rule_data, model_name, 
                            n_folds, n_folds_hyper_tuning, search_iters, max_steps, split_method, 
                            random_state):
    """
    Nested cross-validation.

    Parameters
    ---------- 
    X : np.ndarray. A np.array of features with a shape (the number of samples, the number of features)
    y : np.dnarray. A np.ndarray of labels with a shape (the number of samples,)
    num_classes : Int. The number of classes
    category_info : A np.array with a shape (the number of features).  entry category_info[i] = 0 means the i-th variable 
        is a continous variable. entry category_info[i] > 0 means the i-th variable is a categorical variable, and 
        the value is the number of levels. This information is only used in the proposed machine learning technique.
    feature_names : A list of feature names.
    rule_data : A list of existing rules
    model_name : Str. A string of model name. Options: 'RF', 'XGB', 'SVM', 'EBM', 'GFN_cv', 'DT', 'LR', 'NB', 'FLN', 'GFN'
    n_folds : Int. The number of folds in the outer cross-validation.
    n_folds_hyper_tuning : Int. The number of folds in the inner cross-validation.
    search_iters : Int. The number of search interations in the hyper-parameter tuning.
    max_steps : Int. The maximal steps in optimizing GFN algorithm.
    split_method : Str. It indicates how the train/val/test data split should be performed.
        Options include 'patient_wise', and 'sample_wise'. 'sample_wise' is the regular split. 
        For 'patient_wise', data samples from the same patient should be put into the same data set.
    random_state : Int. Random state.
    
    Returns
    -------
    fold_classifiers : A list of trained classifier objects from the outer cross-validation.
    eval_series : A pd.Series contains evaluation metrics from the outer cross-validation.
    roc_values : A dictionary with keys: 'fpr_test', 'tpr_test', 'auc_test' from the outer cross-validation. 
        It can help draw the ROC curve and its confidence interval from the outer cross-validation.

    """
    fold_classifiers = []
    cv_network = ['RF', 'XGB', 'SVM', 'EBM', 'GFN', 'DT', 'TNET'] # models that require hyperparameter tuning
    
    # downsample the majority class for EBM
    if model_name in ['EBM','TNET']:
        rus = RandomUnderSampler(random_state=0)
        X, y = rus.fit_resample(X, y)
        print(np.unique(y, return_counts=True))

    # compute class weights on train set
    classes, counts = np.unique(y, return_counts=True)
    weights = counts.sum() / (len(classes) * counts)
    weights_dict = dict(zip(classes, weights))

    for index in range(n_folds):

        # Standardize input data for non-GFN models 
        if not model_name.startswith('GFN'):
            scaler = sklearn.preprocessing.StandardScaler().fit(X)
            X = scaler.transform(X)
            # X_val = scaler.transform(X_val)
        
        # Instantiate model
        if model_name == 'SVM':
            base = SVC(probability=True, random_state=random_state)
            grid = utils.create_SVM_grid()

        elif model_name == 'RF': # random forest
            base = RandomForestClassifier(
                class_weight=weights_dict,
                random_state=random_state
                )
            grid = utils.create_RF_grid()

        elif model_name == 'XGB': # XGBoost
            scaling_factor = (len(y_train) - np.sum(y_train)) / np.sum(y_train)
            base = xgboost.XGBClassifier(scale_pos_weight=scaling_factor)
            grid = utils.create_XGBoost_grid()

        elif model_name == 'LR': # Logistic regression
            classifier = LogisticRegression(
                solver='lbfgs',
                class_weight=weights_dict,
                random_state=random_state,
                max_iter=10000
                )
            
        elif model_name == 'NB': # Naive bayes
            classifier = GaussianNB()

        elif model_name == 'EBM': # Explainable bossting machine
            from interpret.glassbox import ExplainableBoostingClassifier
            base = ExplainableBoostingClassifier(
                random_state=random_state
                )
            grid = utils.create_EBM_grid(num_classes==2)

        elif model_name == 'TNET': # T-NET
            from pytorch_tabnet.tab_model import TabNetClassifier
            base = TabNetClassifier(
                verbose=0
            )
            grid = utils.create_TNET_grid()

        elif model_name == 'DT':
            base = sklearn.tree.DecisionTreeClassifier(
                class_weight=weights_dict
            )
            grid = utils.create_DT_grid()

        elif model_name == 'GFN': # Generalized fuzzy network
            base = GeneralizedFuzzyClassifier(
             n_classes=num_classes,
             max_steps=max_steps, #100000
             category_info=category_info,
            #  batch_size = 50,
             report_freq = 50, # 50
             patience_step = 5000, # 500
             random_state=random_state,
             epsilon_training=True,
             binary_pos_only=True,
             weighted_loss=weights,
             split_method=split_method,
             verbose=0,
             init_rule_index = None,
             rule_data = rule_data
             ) 
            grid = utils.create_GFN_grid()


        # Hyper-parameter tuning
        if model_name in cv_network:
            import platform
            if platform.system() == 'Windows':
                n_jobs = 1
            else:
                n_jobs = -1
            
            # Inner cross-validation
            classifier = RandomizedSearchCV(estimator=base, param_distributions=grid, 
                                           n_iter=search_iters, cv=n_folds_hyper_tuning, 
                                           verbose=1, random_state=random_state,
                                           n_jobs=n_jobs, scoring='f1') #sklearn.metrics.make_scorer(multiclass_roc_auc_score))
  
        classifier.fit(X, y)
        
        if model_name in cv_network: 
            best_classifier = classifier.best_estimator_
            cv_results = pd.DataFrame(classifier.cv_results_)
            cv_results.to_csv(os.path.join(exp_save_path, f'cv_results_{model_name}.csv'))
        else:
            best_classifier = classifier
        
        fold_classifiers.append(best_classifier) # Save best classifier from each outer fold

    return fold_classifiers
    

def fit_and_eval(model, i, X_train, y_train, X_test, y_test, num_classes, model_name):

    if model_name == 'TNET':
        model.fit(X_train, y_train, eval_set=[(X_train, y_train)], patience=10)
    else:
        model.fit(X_train, y_train)
    params = str(model.get_params())

    # evaluate
    _, train_metrics, metrics_name, _, _, fpr_train, tpr_train = utils.cal_acc(model, X_train, y_train, num_classes>2)
    _, test_metrics, _, _, _, fpr_test, tpr_test = utils.cal_acc(model, X_test, y_test, num_classes>2)
    
    # compile metrics
    roc_values = {'fpr_test': fpr_test, 'tpr_test': tpr_test, 'auc_test': test_metrics[5],
                    'fpr_train': fpr_train, 'tpr_train': tpr_train, 'auc_train': train_metrics[5]}

    
    metrics = pd.DataFrame([train_metrics, test_metrics], 
                            columns=metrics_name, 
                            index=['Train', 'Test'])
    metrics = metrics.reset_index(names='Set')
    metrics['i'] = i
    metrics['Parameters'] = params
    metrics['Model'] = model_name
    
    return model, metrics, roc_values, metrics_name

################################################################################################################
# Experiment confgurations
################################################################################################################

# Parameters
out_root = './cv_results'
input_file = sys.argv[1] # dir
name_id = sys.argv[2]
n_folds = int(sys.argv[3])
search_iters = int(sys.argv[4])
n_folds_hyper_tuning = int(sys.argv[5])
unique_id = f'{name_id}'
random_state = 0

model_set = ['DT', 'LR', 'RF', 'EBM', 'XGB', 'TNET']
debug = False # Set to True if only want to debug the code.

# Create output folders
exp_save_path = os.path.join(out_root, unique_id)
if not os.path.isdir(out_root):
    os.mkdir(out_root)
if not os.path.isdir(exp_save_path):
    os.mkdir(exp_save_path)

if debug:
    n_folds = 1 # The number of folds in the outer cross-validation.
    search_iters = 1 # The number of search interations in the hyper-parameter tuning.
    n_folds_hyper_tuning = 2 # The number of folds in the inner cross-validation.
    max_steps = 100 # Maximal training steps for the proposed GFN model.
else:
    n_folds = n_folds
    search_iters = search_iters
    n_folds_hyper_tuning = n_folds_hyper_tuning
    max_steps = 10000

print('######################################')
print('Experiment ID:', unique_id)
print('n_folds:', n_folds)
print('search_iters:', search_iters)
print('n_folds_hyper_tuning:', n_folds_hyper_tuning)
print('max_steps:', max_steps)
print('######################################')

################################################################################################################
# Load data
################################################################################################################

if input_file.endswith('.pkl'):
    dataset = pickle.load(open(input_file, 'rb'))
else:
    dataset = load_dataset.load_data(input_file)
    pickle.dump(dataset, open(os.path.join(exp_save_path, 'dataset.pkl'), 'wb'))

row_name_list = []
row_list = []

################################################################################################################
# Run experiment for each model type
################################################################################################################

all_model_metrics = pd.DataFrame()

for model_name in model_set:

    ################################################################################################################
    # Prepare data and parameters for experiment
    ################################################################################################################

    print(model_name)
    split_method = dataset['split_method'] if 'split_method' in dataset else 'sample_wise'

    if 'X_train' in dataset.keys():
        X_train = dataset['X_train']
        y_train = dataset['y_train']
        X_test = dataset['X_test']
        y_test = dataset['y_test']
        
    else:
        data = np.array(dataset['variables'])
        labels = np.array(dataset['response'])
        ss_train_test = StratifiedShuffleSplit(n_splits=1, test_size=0.30, random_state=random_state)
        X_train, y_train, X_test, y_test = utils.split_dataset(ss_train_test, data, labels, split_method, index=0)

    category_info = dataset['category_info']
    num_classes = dataset['num_classes']
    rule_data = dataset.get('rule_data') 
    feature_names = dataset.get('feature_names')

    ################################################################################################################
    # Identify optimal hyperparameters via nested cross-validation on the training set
    ################################################################################################################

    fold_classifiers = nested_cross_validation(
        X_train, y_train, num_classes, category_info, feature_names, 
        rule_data, model_name, n_folds, n_folds_hyper_tuning, 
        search_iters, max_steps, split_method, random_state)

    ################################################################################################################
    # Retrain models on the whole training set and evaluate
    ################################################################################################################

    fitted_fold_classifiers = []
    all_metrics = []
    all_roc_values = {'fpr_test': [], 'tpr_test': [], 'auc_test': [],
                    'fpr_train': [], 'tpr_train': [], 'auc_train': []}

    for i in range(len(fold_classifiers)):
        model = fold_classifiers[i]
        fitted_model, metrics, roc_values, metrics_name = fit_and_eval(model, i, X_train, y_train, X_test, y_test, num_classes, model_name)
        all_metrics.append(metrics)
        fitted_fold_classifiers.append(fitted_model)

        # compile roc values for plotting
        for key in all_roc_values.keys():
            all_roc_values[key].append(roc_values[key])

    ################################################################################################################
    # Save model evaluation results
    ################################################################################################################

    # Save the models
    pickle.dump(fitted_fold_classifiers, open(os.path.join(exp_save_path, f'saved_fitted_cv_models_{model_name}.mdl'), 'wb'))

    # compile and save performance metrics
    metrics = pd.concat(all_metrics, axis=0, ignore_index=True)
    all_model_metrics = pd.concat([all_model_metrics, metrics], axis=0, ignore_index=True)

    # print best model metrics
    idx = metrics[metrics['Set'] == 'Test']['f1'].idxmax()
    i = metrics.iloc[idx,:]['i']
    print('BEST MODEL PERFORMANCE')
    print(metrics[metrics['i'] == i][metrics_name])

    # Draw the ROC curve and the confidence intervals (if multiple outer folds requested).
    utils.draw_ROC_curves(all_roc_values['tpr_train'], all_roc_values['fpr_train'], all_roc_values['auc_train'],
                          model_name, os.path.join(exp_save_path, f'ROC_train_{model_name}.png'))
    utils.draw_ROC_curves(all_roc_values['tpr_test'], all_roc_values['fpr_test'], all_roc_values['auc_test'],
                          model_name, os.path.join(exp_save_path, f'ROC_test_{model_name}.png'))
    

# Save the metrics
metrics_file_name = os.path.join(exp_save_path, f'results.csv')
all_model_metrics.to_csv(metrics_file_name, index=False)
print(f'All model performance metrics saved to {metrics_file_name}')