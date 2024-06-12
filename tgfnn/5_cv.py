import pandas as pd
import numpy as np
from sklearn.model_selection import cross_validate
from sklearn import metrics
import pickle
import seaborn as sns
import matplotlib.pyplot as plt
import os

from interpret.glassbox import ExplainableBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from generalized_fuzzy_net import GeneralizedFuzzyClassifier as TGFNN
from pytorch_tabnet.tab_model import TabNetClassifier
from sklearn.tree import DecisionTreeClassifier


def score(y_pred, y_pred_proba, y_label):
    auc = metrics.roc_auc_score(y_label, y_pred_proba)
    auprc = metrics.average_precision_score(y_label, y_pred_proba)
    f1 = metrics.f1_score(y_label, y_pred)
    acc = metrics.accuracy_score(y_label, y_pred)
    precision = metrics.precision_score(y_label, y_pred)
    recall = metrics.recall_score(y_label, y_pred)
    results = [auc, auprc, f1, precision, recall]
    conf_mat = metrics.confusion_matrix(y_label, y_pred)

    return results, conf_mat

def get_results(scoring_metrics, scores, X_test, y_test):
    # get cv results
    cv_results = {}
    for set in ['train', 'test']:
        cv_results[set] = {}
        for metric in scoring_metrics:
            cv_results[set][metric] = scores[f'{set}_{metric}'].tolist()

    # make df
    all_res = []
    for set in ['train','test']:
        res = pd.DataFrame(cv_results[set])
        res['set'] = set
        all_res.append(res)
    cv_res = pd.concat(all_res)
    cv_res['set'] = cv_res['set'].replace('test','valid')
    cv_res = cv_res.sort_values('set')
    cv_res = cv_res.rename(columns = {'average_precision':'auprc'})

    # eval on test set
    all_results = []
    for cv_model in scores['estimator']:
        y_pred_test = cv_model.predict(X_test)
        y_pred_proba_test = cv_model.predict_proba(X_test)[:,1]
        results, _ = score(y_pred_test, y_pred_proba_test, y_test)
        all_results.append(results)

    test_res = pd.DataFrame(all_results, columns=['roc_auc', 'auprc', 'f1', 'precision', 'recall'])
    test_res['set'] = 'test'

    # combine dfs
    res = pd.concat([cv_res, test_res])

    return res

if __name__ == '__main__':
    results_path = 'cv_results'
    exp = 'experiment'

    dataset_names = [
        # '30_phenotypes',
        # '30_aggregate',
        # '20_latest+demo',
        # '30_latest+demo+phenotypes',
        # '20_latest+demo+aggregate',
        '60_all'
    ]

    model_names = [
        # 'RF',
        # 'LR',
        'GFN',
        # 'XGB',
        # 'TNET',
        # 'EBM',
        # 'DT'
    ]

    out_dir = 'cv_output'
    os.makedirs(out_dir, exist_ok=True)

    all_res = []

    for d in dataset_names:

        print(d)

        # load data
        data_dir = f'{results_path}/{exp}'
        dataset = pickle.load(open(f'{data_dir}/dataset.pkl', 'rb'))
        X_train = dataset['X_train']
        y_train = dataset['y_train']
        X_test = dataset['X_test']
        y_test = dataset['y_test']

        for m in model_names:

            print(m)

            if not os.path.exists(f'{data_dir}/saved_fitted_cv_models_{m}.mdl'):
                continue

            # load model params
            params = pickle.load(open(f'{data_dir}/saved_fitted_cv_models_{m}.mdl', 'rb'))[0].get_params()

            # initialize model
            if m == 'DT':
                model = DecisionTreeClassifier(**params)
            if m == 'EBM':
                model = ExplainableBoostingClassifier(**params)
            elif m == 'RF':
                model = RandomForestClassifier(**params)
            elif m == 'LR':
                model = LogisticRegression(**params)
            elif m == 'XGB':
                model = XGBClassifier(**params)
            elif m == 'GFN':
                model = TGFNN(**params)
            elif m == 'TNET':
                model = TabNetClassifier(**params)

            # cross validate
            scoring_metrics = ['roc_auc', 'average_precision', 'f1', 'precision', 'recall']
            scores = cross_validate(
                model,
                X_train, y_train.ravel(),
                cv=5,
                scoring=scoring_metrics,
                return_train_score=True,
                n_jobs=-1,
                return_estimator=True
            )

            # save models
            pickle.dump(scores['estimator'], open(f'{out_dir}/{exp}_{d}_{m}_cv_models.pkl', 'wb'))

            # compile results
            res = get_results(scoring_metrics, scores, X_test, y_test)
            res['dataset'] = d
            res['model'] = m
            all_res.append(res)

    # save
    res = pd.concat(all_res)
    res.to_csv(f'{out_dir}/{exp}_cv_results.csv', index=False)

    # plot
    sns.set(style='whitegrid')
    g = sns.barplot(data=res[res['set']=='test'], x='model', y='roc_auc', hue='dataset', errorbar='sd')
    sns.move_legend(g, "upper left", bbox_to_anchor=(1, 1))
    g.set_title('Test set ROC-AUC (mean +/- sd)')
    plt.savefig(f'{out_dir}/{exp}_cv_roc_auc.png', bbox_inches='tight')