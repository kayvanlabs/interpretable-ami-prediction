import pandas as pd
import numpy as np
import tensorly as tl
from tensorly.decomposition import non_negative_parafac_hals
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, f1_score, average_precision_score, accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os
from sklearn.preprocessing import MinMaxScaler
from sklearn.utils.class_weight import compute_class_weight

ID = 'ID'
CASE = 'CASE'

def get_args():
    '''
    Arguments.
    '''
    parser = argparse.ArgumentParser(description='Phenotype data with CP decomposition.')
    parser.add_argument('-i', '--input_dir', help='Directory of input data', type=str, required=False, default='.')
    parser.add_argument('-n', '--name', help='Name of experiment', type=str, required=False, default='test_run')
    parser.add_argument('-a', '--start', help='start rank', type=int, required=False, default=1)
    parser.add_argument('-z', '--stop', help='stop rank', type=int, required=False, default=10)
    parser.add_argument('-s', '--step', help='step rank', type=int, required=False, default=1)
    parser.add_argument('--lv', help='phenotype labs/vitals', action='store_true')

    args = parser.parse_args()
    return args

def preprocess(df, features=False, labs_vitals=False, bins=None):

    if labs_vitals:
        # drop all columns not labs/vitals
        dx_cols = [col for col in df.columns.tolist() if col.startswith('dx_')]
        rx_cols = [col for col in df.columns.tolist() if col.startswith('rx_')]
        other_cols = [
            'AGE',
            'OZ_PER_WEEK',
            'PACKS_PER_DAY',
            'QUIT_DSB',
            'SMOKING_YEARS',
            'ALCOHOL_USE_STATUS_No',
            'ALCOHOL_USE_STATUS_Not Asked',
            'ALCOHOL_USE_STATUS_Not Currently',
            'ALCOHOL_USE_STATUS_Yes',
            'ILLICIT_DRUG_USE_No',
            'ILLICIT_DRUG_USE_Not Asked',
            'ILLICIT_DRUG_USE_Not Currently',
            'ILLICIT_DRUG_USE_Yes',
            'SMOKING_STATUS_Current',
            'SMOKING_STATUS_Former',
            'SMOKING_STATUS_Never',
            'SMOKING_STATUS_Unknown'
        ]
        df = df.drop(dx_cols + rx_cols + other_cols, axis=1)

        def discretize(df, bins=None):
            if bins is None:
                col_bins = {}
                for col in df.columns:
                    df[col], bins = pd.qcut(df[col], 5, retbins=True, duplicates='drop')
                    col_bins[col] = bins
                return df, col_bins
            else:
                for col in df.columns:
                    df[col] = pd.cut(df[col], bins=bins[col], duplicates='drop')
                return df, None
            
        # discretize
        df, bins = discretize(df, bins)
        df = pd.get_dummies(df)
        df = df * 1.0
        return df, bins

    else:

        # remove ICD codes for encounters
        Z_icd_cols = [col for col in df.columns.tolist() if col.startswith('dx_Z')]
        df = df.drop(Z_icd_cols, axis=1)

        # filter to only diagnosis and medication features
        dx_cols = [col for col in df.columns.tolist() if col.startswith('dx_')]
        rx_cols = [col for col in df.columns.tolist() if col.startswith('rx_')]
        df = df[dx_cols + rx_cols]

        # # drop therapeutic class columns
        thera_class_cols = [col for col in df.columns.tolist() if col.startswith('rx_') and all(c.isupper() or c.isspace() or c == '/' for c in col[3:])]
        df = df.drop(thera_class_cols, axis=1)
        rx_cols = [col for col in df.columns.tolist() if col.startswith('rx_')] # update

        if features:
            df = df[features]
            # update dx_cols
            dx_cols = [col for col in df.columns.tolist() if col.startswith('dx_')]
            rx_cols = [col for col in df.columns.tolist() if col.startswith('rx_')]
        else:
            # remove features in less than 2% of patients
            freq = df.groupby(ID).max().mean()
            cols = freq[freq > 0.0].index.tolist()
            df = df[cols]
            dx_cols = [col for col in df.columns.tolist() if col.startswith('dx_')]
            rx_cols = [col for col in df.columns.tolist() if col.startswith('rx_')]
        
        # imputation
        df = df.fillna(0)

        return df, None

def make_sparse_tensor(df):
    # get tensor dimensions, features, and format data
    x = df.apply(lambda x: (x - x.min()) / (x.max() - x.min())) # min max scale
    features = x.columns.tolist()
    n_features = x.shape[1]
    x = x.unstack(level=1)
    pids = x.index.values.tolist()
    n_patients = x.shape[0]
    n_time_bins = x[features[0]].shape[1]

    # make tensor
    tensor = np.full((n_features, n_time_bins, n_patients), np.nan)
    for i in range(tensor.shape[0]):
            tensor[i, :, :] = x[features[i]].T.values

    # get mask
    mask = ~np.isnan(tensor)
    tensor = np.nan_to_num(tensor)

    # set all nonzero values to 1
    tensor = np.where(tensor != 0, 1, tensor) 

    return tensor, mask, features, pids

def score(y_pred, y_pred_proba, y_label):
    auc = roc_auc_score(y_label, y_pred_proba)
    auprc = average_precision_score(y_label, y_pred_proba)
    f1 = f1_score(y_label, y_pred)
    acc = accuracy_score(y_label, y_pred)
    precision = precision_score(y_label, y_pred)
    recall = recall_score(y_label, y_pred)
    results = [auc, auprc, f1, acc, precision, recall]

    return results

def eval(model, rank, error, n_estimators, max_depth, X_train, y_train, X_test, y_test):
    y_pred_train = model.predict(X_train)
    y_pred_proba_train = model.predict_proba(X_train)[:,1]
    y_pred_test = model.predict(X_test)
    y_pred_proba_test = model.predict_proba(X_test)[:,1]

    results_train = score(y_pred_train, y_pred_proba_train, y_train)
    results_test = score(y_pred_test, y_pred_proba_test, y_test)

    eval_results = pd.DataFrame(
        [results_train, results_test], 
        columns=['auc', 'auprc', 'f1', 'acc', 'precision', 'recall'],
        index=['train', 'test']
    )

    eval_results['rank'] = rank
    eval_results['error'] = error
    eval_results['n_estimators'] = n_estimators
    eval_results['max_depth'] = max_depth
    eval_results = eval_results.reset_index().rename(columns={'index': 'set'})
        
    return eval_results

if __name__ == '__main__':
    args = get_args()
    out_dir = f'{args.input_dir}/{args.name}'
    os.makedirs(out_dir, exist_ok=True)
     
    # load data
    print('loading data')
    data_dir = args.input_dir
    X_train = pd.read_csv(f'{data_dir}/X_train.csv', index_col=[0,1])
    cohort = pd.read_csv(f'{data_dir}/cohort.csv')

    # preprocess
    print('preprocessing data')
    X_train, _ = preprocess(X_train, labs_vitals=args.lv)

    # make sparse patient x time x feature tensor
    tensor_train, mask_train, features_train, pids_train = make_sparse_tensor(X_train)

    n_iter_max = 50
    tol = 1e-6
    all_eval = []
    all_errors = []

    print('running decompositions')
    for rank in range(args.start, args.stop, args.step):
        for i in range(3): # repeat random init

            # run decomposition
            decomposition, errors = non_negative_parafac_hals(
                tensor=tensor_train, 
                rank=rank, 
                init='random',
                verbose=False,
                return_errors=True,
                tol=tol,
                n_iter_max=n_iter_max)

            decomposition.normalize()
            weights, factors = decomposition
            f_features, f_time, f_patients = factors
            error = errors[-1]
            all_errors.append([rank, i, error])
            print(rank, i, error)

            # get patient phenotype membership values
            pheno_train = pd.DataFrame(f_patients, index=pids_train) #.todense()
            scaler = MinMaxScaler()
            pheno_train = pd.DataFrame(scaler.fit_transform(pheno_train), index=pheno_train.index, columns=pheno_train.columns)
            y_train = pd.merge(pheno_train, cohort, left_index=True, right_on=ID)[CASE].values
            
            # train test split
            pheno_train, pheno_test, y_train, y_test = train_test_split(pheno_train, y_train, test_size=0.3, random_state=0)

            # compute class weights
            class_weights = compute_class_weight(class_weight='balanced', classes=np.unique(y_train), y=y_train.reshape(-1))
            class_weights = dict(zip(np.unique(np.unique(y_train)), class_weights))

            # assess predictive power
            clf = RandomForestClassifier(n_estimators=500, max_depth=5, random_state=0, class_weight=class_weights)
            clf.fit(pheno_train, y_train)
            all_eval.append(eval(clf, rank, error, 500, 5, pheno_train, y_train, pheno_test, y_test))
    
    # plot errors
    all_errors = pd.DataFrame(all_errors, columns=['rank', 'replicate', 'error'])
    all_errors.to_csv(f'{out_dir}/{args.start}_{args.stop}_{args.step}_pick_rank_errors.csv', index=False)
    sns.lineplot(data=all_errors[['rank','error']], x='rank', y='error')
    plt.savefig(f'{out_dir}/{args.start}_{args.stop}_{args.step}_pick_rank_errors.png')
    
    # save eval results
    all_eval = pd.concat(all_eval, axis=0).reset_index(drop=True)
    all_eval.to_csv(f'{out_dir}/rf_rank_eval.csv', index=False)

    import seaborn as sns
    import matplotlib.pyplot as plt

    sns.set_theme(style="whitegrid")
    plt.clf()
    sns.lineplot(data=all_eval, x='rank', y='auc', hue='set')
    plt.savefig(f'{out_dir}/rf_rank_auc.png')

    plt.clf()
    sns.lineplot(data=all_eval, x='rank', y='auprc', hue='set')
    plt.savefig(f'{out_dir}/rf_rank_auprc.png')

    plt.clf()
    sns.lineplot(data=all_eval, x='rank', y='f1', hue='set')
    plt.savefig(f'{out_dir}/rf_rank_f1.png')