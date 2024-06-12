import numpy as np
import tensorly as tl
from tensorly.decomposition import non_negative_parafac_hals
import pandas as pd
import argparse
import os
import seaborn as sns
import matplotlib.pyplot as plt
import icd10
import re
from sklearn.preprocessing import MinMaxScaler
import pickle

CASE = 'CASE'
ID = 'ID'

def get_args():
    '''
    Arguments.
    '''
    parser = argparse.ArgumentParser(description='Phenotype data with CP decomposition.')
    parser.add_argument('-i', '--input_dir', help='Directory of input data', type=str, required=False, default='.')
    parser.add_argument('-r', '--rank', help='Rank of decomposition (number of phenotypes)', type=int, required=False, default=3)
    parser.add_argument('-n', '--max_iter', help='Max number of iterations', type=float, required=False, default=200)
    parser.add_argument('-t', '--tol', help='error tolerance when fitting', type=float, required=False, default=1e-6)
    parser.add_argument('-e', '--name', help='Name of output data', type=str, required=False, default='')
    parser.add_argument('-l', '--labs_vitals', help='Use only labs and vitals', action='store_true', required=False, default=False)
    args = parser.parse_args()
    return args

def preprocess(df, features=None, labs_vitals=False, bins=None):

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
                    df[col] = pd.cut(df[col], bins=bins[col], duplicates='drop', include_lowest=True)
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

        # drop therapeutic class columns
        thera_class_cols = [col for col in df.columns.tolist() if col.startswith('rx_') and all(c.isupper() or c.isspace() or c == '/' for c in col[3:])]
        df = df.drop(thera_class_cols, axis=1)
        rx_cols = [col for col in df.columns.tolist() if col.startswith('rx_')] # update

        if features:
            df = df[features]
            # update dx_cols
            dx_cols = [col for col in df.columns.tolist() if col.startswith('dx_')]
        else:
            # remove features in less than 2% of patients
            freq = df.groupby(ID).max().mean()
            cols = freq[freq > 0.0].index.tolist()
            df = df[cols]
            dx_cols = [col for col in df.columns.tolist() if col.startswith('dx_')]
        
        # imputation
        df = df.fillna(0)

        return df, None

def make_sparse_tensor(df, scaler, test=False):
    # get tensor dimensions, features, and format data

    if not test:
        x = pd.DataFrame(scaler.fit_transform(df), index=df.index, columns=df.columns)
    else:
        x = pd.DataFrame(scaler.transform(df), index=df.index, columns=df.columns)
    
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

    return tensor, mask, features, pids, scaler

def learn_phenotypes(tensor_train, rank, tol, n_iter_max):
    # factorize
    cp_tensor, errors = non_negative_parafac_hals(
        tensor=tensor_train,
        rank=rank,
        init='random',
        verbose=False,
        n_iter_max=n_iter_max,
        tol=tol,
        return_errors=True,
        random_state=0,
        exact=True
    )

    # print error
    print('Error: ', errors[-1])

    # extract normalized factors
    weights, factors = cp_tensor
    f_features, f_time, f_patients = factors
    return f_features, f_time, f_patients, errors, cp_tensor

def project_phenotypes(tensor_test, rank, tol, n_iter_max, cp_tensor):
    # random init test set phenotype membership
    rando_cp = tl.random.random_cp(tl.shape(tensor_test), rank, **tl.context(tensor_test))
    init_decomposition_train = cp_tensor.cp_copy()
    init_decomposition_train.factors[-1] = rando_cp.factors[-1]

    # test set fixed decomposition
    cp_tensor_test, errors_test = non_negative_parafac_hals(
        tensor=tensor_test,
        rank=rank,
        init=init_decomposition_train, # initialize the train decoposition but random patient membership
        n_iter_max=n_iter_max,
        tol=tol,
        return_errors=True,
        fixed_modes=[0, 1],
        random_state=0,
        exact=True
    )

    weights_test, factors_test = cp_tensor_test
    f_features_test, f_time_test, f_patients_test = factors_test
    print('Test error: ', errors_test[-1])

    return f_features_test, f_time_test, f_patients_test, errors_test, cp_tensor_test

def plot_error(errors, out_dir, file_name):
    # plot reconstruction errors
    plt.clf()
    sns.set(rc={'figure.figsize':(8,5)})
    sns.set_theme(style="white")
    sns.lineplot(x=range(len(errors)), y=errors, marker='o')
    plt.xlabel('Iteration')
    plt.ylabel('Reconstruction error (scaled by tensor norm)')
    plt.title('Reconstruction errors over iterations')
    plt.savefig(f'{out_dir}/{file_name}.png')

def summarize_phenotypes(f_features, features_train, out_dir, labs_vitals):

    # get phenotype descriptions
    factors_df = pd.DataFrame(f_features, index=features_train)
    factors_df = factors_df.reset_index(names=['feature'])
    if not labs_vitals:
        factors_df['feature'] = factors_df['feature'].apply(lambda x: icd10.find(x[3:]).description + ' (' +  icd10.find(x[3:]).code + ')' if icd10.find(x[3:]) else x)
    factors_df = factors_df.set_index('feature')
    factors_df = pd.melt(factors_df.reset_index(), id_vars='feature', var_name='factor', value_name='weight')

    with open(f'{out_dir}/phenotypes_summaries.txt', 'w') as f:
        for i in factors_df['factor'].unique():
            print(factors_df[factors_df['factor'] == i].sort_values(by='weight', ascending=False).head(5), file=f)
            print('\n', file=f)

    return factors_df

def plot_time(rank, f_time, out_dir):
    plt.clf()
    sns.set(rc={'figure.figsize':(10,5)})
    sns.set_theme(style="white")

    # plot factors over time
    for i in range(rank):
        sns.lineplot(x=range(-10,0), y=np.flip(f_time[:,i]), label='Factor {}'.format(i))

    # set x label
    plt.xlabel('Number of 6-month obs. windows before acute MI')
    plt.title('Phenotype time mode')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
    plt.tight_layout()
    plt.savefig(f'{out_dir}/time_factor.png')

def remove_px(df):
    df = df.drop([c for c in df.columns if 'px_' in c], axis=1)
    return df

if __name__ == '__main__':
    print('start')
    args = get_args()
    data_dir = args.input_dir

    # make output dir
    out_dir = f'{data_dir}/phenotypes_{args.rank}_{args.name}'
    os.makedirs(out_dir, exist_ok=True)

    print(f'dir: {data_dir}')

    # load data
    X_train = pd.read_csv(f'{data_dir}/X_train.csv', index_col=[0,1])
    X_test = pd.read_csv(f'{data_dir}/X_test.csv', index_col=[0,1])
    cohort = pd.read_csv(f'{data_dir}/cohort.csv')

    print('data loaded.')

    # remove px
    X_train = remove_px(X_train)
    X_test = remove_px(X_test)

    # make sure both train and test have same features
    columns = list(set(X_train.columns.tolist()) & set(X_test.columns.tolist()))
    X_train = X_train[columns]
    X_test = X_test[columns]

    # preprocess
    X_train, train_bins = preprocess(X_train, labs_vitals=args.labs_vitals)
    X_test, _ = preprocess(X_test, labs_vitals=args.labs_vitals, bins=train_bins)
    
    print(X_train.shape)
    print(X_test.shape)

    print('data preprocessed.')

    # make sparse patient x time x feature tensor
    scaler = MinMaxScaler()
    tensor_train, mask_train, features_train, pids_train, scaler = make_sparse_tensor(X_train, scaler)
    tensor_test, mask_test, features_test, pids_test, scaler = make_sparse_tensor(X_test, scaler, test=True)

    # save data tensors and features and pids
    np.save(f'{out_dir}/tensor_train.npy', tensor_train)
    np.save(f'{out_dir}/tensor_test.npy', tensor_test)
    pickle.dump(features_train, open(f'{out_dir}/features_train.pkl', 'wb'))
    pickle.dump(features_test, open(f'{out_dir}/features_test.pkl', 'wb'))
    pickle.dump(pids_train, open(f'{out_dir}/pids_train.pkl', 'wb'))
    pickle.dump(pids_test, open(f'{out_dir}/pids_test.pkl', 'wb'))

    print('tensor created.')
    print(tensor_train.shape)
    print(tensor_test.shape)

    # hyperparameters
    rank = args.rank
    n_iter_max = int(args.max_iter)
    tol = args.tol

    # factor
    f_features, f_time, f_patients, errors, cp_tensor = learn_phenotypes(tensor_train, rank, tol, n_iter_max)
    print('successfully factored train tensor')

    # project onto test set
    f_features_test, f_time_test, f_patients_test, errors_test, cp_tensor_test = project_phenotypes(tensor_test, rank, 1e-30, 50, cp_tensor)
    print('successfully projected factors onto test set')

    # plot
    plot_error(errors, out_dir, 'train_error')
    plot_error(errors_test, out_dir, 'test_error')
    plot_time(rank, f_time, out_dir)
    factors_df = summarize_phenotypes(f_features, features_train, out_dir, labs_vitals=args.labs_vitals)

    print('plotted')

    # save patient membership values for machine learning
    # get patient IDs
    pheno_train = pd.DataFrame(f_patients, index=pids_train)
    pheno_test = pd.DataFrame(f_patients_test, index=pids_test)

    # standardize
    scaler = MinMaxScaler()
    pheno_train = pd.DataFrame(scaler.fit_transform(pheno_train), index=pids_train)
    pheno_test = pd.DataFrame(scaler.transform(pheno_test), index=pids_test)

    # get labels
    y_train = pd.merge(pheno_train, cohort, left_index=True, right_on=ID)[CASE]
    y_test = pd.merge(pheno_test, cohort, left_index=True, right_on=ID)[CASE]

    # reset index
    pheno_train = pheno_train.reset_index(names=[ID])
    pheno_test = pheno_test.reset_index(names=[ID])

    # save
    pd.DataFrame(errors).to_csv(f'{out_dir}/train_errors.csv')
    pd.DataFrame(errors_test).to_csv(f'{out_dir}/test_errors.csv')
    pd.DataFrame(f_time).to_csv(f'{out_dir}/time_factors.csv')
    factors_df.to_csv(f'{out_dir}/phenotypes.csv', index=False)
    pheno_train.to_csv(f'{out_dir}/pheno_patient_membership_train.csv', index=False)
    pheno_test.to_csv(f'{out_dir}/pheno_patient_membership_test.csv', index=False)
    y_train.to_csv(f'{out_dir}/y_train.csv')
    y_test.to_csv(f'{out_dir}/y_test.csv')
    pickle.dump(cp_tensor, open(f'{out_dir}/cp_tensor.pkl', 'wb'))
    pickle.dump(cp_tensor_test, open(f'{out_dir}/cp_tensor_test.pkl', 'wb'))

    print('saved')