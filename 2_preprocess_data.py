import pandas as pd
import numpy as np
import sparse
import os
import icd10
import sys
import re


TIME = 't'
ID = 'ID'
VAR = 'variable_name'
VAL = 'variable_value'
CASE = 'CASE'
TRAIN = 'train'

RX = 'MEDICATION'
ICD9 = 'ICD9_CODE'
ICD10 = 'ICD10_CODE'
CPT4 = 'CPT4'
HCPCS = 'HCPCS'
ICD10_PX = 'ICD10'

categorical_variables = ['SEX','FIRST_RACE_GROUP','ALCOHOL_USE_STATUS','SMOKING_STATUS','ILLICIT_DRUG_USE']

T = int(365.25 * 5) # max time before end
dt = 180 # bin size in days
control_ratio = 2
match = True

input_dir = 'data'
output_dir = input_dir

if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    
def get_time_bins(T, dt):
    return np.arange(0, dt*(np.floor(T/dt)+1), dt)

def get_time_bins_index(T, dt):
    return pd.cut([], get_time_bins(T, dt), right=False).categories

def expand_icd(s):
    code = icd10.find(s)
    try:
        full_code = code.code
    except:
        full_code = s
    
    return [full_code[:3], full_code]

def process_hierarchical(df):
    df = df.drop(columns=[VAR, VAL, 'VISIT_ID', 'END_DSB'], axis=1)
    df = df.melt(id_vars=[ID, TIME], value_name=VAR, var_name=VAL)
    df[VAL] = 1.0
    # df.groupby(['newidx', 'Code'])['val'].max().unstack() # potential alternative to pivot_table that is more memory efficient
    df = df.pivot_table(index=[ID, TIME], columns=VAR, aggfunc=lambda x: x.count() if x.count() > 0 else np.nan)
    df.columns = df.columns.droplevel(0)
    return df

def filter_by_case_freq(df, col, threshold):
    freqs = pd.DataFrame(df.groupby([CASE,col])[ID].nunique() / df.groupby([CASE])[ID].nunique())
    freqs = freqs.reset_index()
    freqs = freqs.rename(columns={ID : 'freq'})
    freqs = freqs.pivot_table(index=col, columns=CASE, values='freq')
    freqs = freqs.fillna(0)
    freqs = freqs.reset_index()
    freq_variables = freqs[(freqs[0] >= threshold) & (freqs[1] >= threshold)][col].values
    return freq_variables

def get_stats(df):
    df = df.groupby([ID,VAR])[VAL].agg(['mean','std','min','max'])
    df['std'] = df['std'].fillna(0)
    df = df.pivot_table(index='ID', columns=VAR, values=['mean','std','min','max'])
    df = df.reset_index()
    df.columns = df.columns.map('_'.join).str.strip('_')
    return df

def get_latest(X):
    # get latest data
    X.loc[:, X.columns] = X.loc[:, X.columns].groupby(X.index.get_level_values(0)).bfill() # carry forward imputation
    X = X.loc[(slice(None), pd.Interval(0, dt, closed='left')), :] # get latest data
    X = X.droplevel(1) # drop time bin index
    X.columns = ['latest_' + col for col in X.columns]
    X = X.reset_index()

    return X


def preprocess_dx_rx_proc(df):

    # filter to only diagnosis and medication and procedure features
    dx_cols = [col for col in df.columns.tolist() if col.startswith('dx_')]
    rx_cols = [col for col in df.columns.tolist() if col.startswith('rx_')]
    df = df[dx_cols + rx_cols]

    # imputation
    df = df.apply(lambda row: row.fillna(0) if row.count() > 0 else row, axis=1) # if visit present in bin, fill nan with 0
    df.loc[:, dx_cols] = df.loc[:, dx_cols].groupby(df.index.get_level_values(0)).bfill() # carry forward imputation of diagnoses

    return df

def preprocess(data, T, dt):
    data = data[data[VAR] != 'VISIT_ID'] # remove error

    # split static and time series
    S = data[data[TIME].isna()]
    X = data[data[TIME].notna()]

    # process static data
    S = S.pivot_table(index=ID, columns=VAR, values=VAL, aggfunc='last')
    cols = [col for col in S.columns if col in categorical_variables]
    S = pd.get_dummies(S, columns=cols)
    S = S.fillna(0)
    S = S.astype(float)

    # process time series data

    # split by type
    X_rx = X[X[VAR] == RX]
    X_dx = X[X[VAR].isin([ICD9, ICD10])]
    X_cat = X[X[VAR].isin(categorical_variables)]
    cont_vars = set(X[VAR].values) - set(categorical_variables) - set([RX, ICD9, ICD10, CPT4, HCPCS, ICD10_PX])
    X_cont = X[X[VAR].isin(cont_vars)]
    X_cont[VAL] = X_cont[VAL].apply(lambda val: val.replace('+', '')) # remove '+' from values (SMOKING_YEARS)
    X_cont = X_cont.astype({VAL: float})

    # process categorical variables
    X_cat[TIME] = pd.cut(X_cat[TIME], get_time_bins(T, dt), right=False)
    X_cat = X_cat.pivot_table(index=[ID, TIME], columns=VAR, values=VAL, aggfunc='last')
    X_cat = pd.get_dummies(X_cat)
    X_cat = X_cat.astype(float)
    cat_vars = X_cat.columns.tolist()

    # process continuous variables
    X_cont[TIME] = pd.cut(X_cont[TIME], get_time_bins(T, dt), right=False)
    X_cont_stats = get_stats(X_cont)
    X_cont = X_cont.pivot_table(index=[ID, TIME], columns=VAR, values=VAL, aggfunc='last')

    # process rx variables
    X_rx[TIME] = pd.cut(X_rx[TIME], get_time_bins(T, dt), right=False)
    X_rx = X_rx.drop_duplicates() # now that I have the time bins, I can remove those extra rows I artificially added
    X_rx = pd.concat([X_rx, X_rx[VAL].str.split(';', expand=True)], axis=1) # create a variable for both drug name and class
    X_rx = process_hierarchical(X_rx)
    X_rx.columns = ['rx_' + col for col in X_rx.columns] # add rx_ to variable names
    rx_vars = X_rx.columns.tolist()

    # process dx variables
    X_dx[TIME] = pd.cut(X_dx[TIME], get_time_bins(T, dt), right=False)
    X_dx = X_dx.drop_duplicates() # if i don't drop duplicates here than i could get some severity information but should be normalized by # visits in time bin
    X_dx = pd.concat([X_dx, X_dx.apply(lambda x: expand_icd(x[VAL]), axis=1).apply(pd.Series)], axis=1)
    X_dx = process_hierarchical(X_dx)
    X_dx.columns = ['dx_' + col for col in X_dx.columns] # add dx_ to variable names
    dx_vars = X_dx.columns.tolist()

    # combine all data
    X = pd.merge(X_dx, X_rx, on=[ID, TIME], how='outer')
    X = pd.merge(X, X_cont, on=[ID, TIME], how='outer')
    X = pd.merge(X, X_cat, on=[ID, TIME], how='outer')
    X = X.unstack(TIME).stack(TIME, dropna=False)

    # get latest data only (not Dx nor Rx)
    X_latest = pd.merge(X_cat, X_cont, on=[ID, TIME], how='outer')
    X_latest = get_latest(X_latest)

    # get latest and history of Dx and Rx and Px
    df = preprocess_dx_rx_proc(X)
    X_dx_rx_latest = df.loc[(slice(None), pd.Interval(0, dt, closed='left')), :].droplevel(1) # get latest
    X_dx_rx_latest.columns = ['latest_' + col for col in X_dx_rx_latest.columns]
    X_dx_rx_history = df.groupby(df.index.get_level_values(0)).max() # get max (e.g. if ever in EHR)
    X_dx_rx_history = X_dx_rx_history.apply(lambda x: x.apply(lambda y: 1 if y > 1 else y)) # replace max with 1 if >1. makes this boolean
    X_dx_rx_history.columns = ['history_' + col for col in X_dx_rx_history.columns]

    # combine latest tables
    X_latest = pd.merge(X_latest, X_dx_rx_latest, on=ID, how='outer')

    def make_bool(df):
        cols = [c for c in df.columns if 'dx_' in c or 'rx_' in c]
        df[cols] = df[cols].fillna(0)
        df[cols] = df[cols].apply(lambda x: x.apply(lambda y: 1 if y > 1 else y))
        return df

    # impute dx, rx variables with 0, replace values >1 with 1.
    X = make_bool(X)
    X_latest = make_bool(X_latest)
    X_dx_rx_history = make_bool(X_dx_rx_history)
    
    return S, X, X_cont_stats, X_latest, X_dx_rx_history


if __name__ == '__main__':
    # load data
    data = pd.read_csv(f'{input_dir}/data.csv')
    pop = pd.read_csv(f'{input_dir}/cohort.csv')
    pop = pop.rename(columns={'PATIENT_ID':ID})

    controls = pop[pop[CASE] == 0]
    cases = pop[pop[CASE] == 1]

    if match:
        match_mat = pd.read_csv('helper_files/match_mat_stringent.csv', index_col=0)
        match_mat = match_mat.rename(columns={'PATIENT_ID':ID})

        # get matches for each case
        matched_controls = set()
        for pid in cases[ID]:
            if pid not in match_mat.columns:
                print(f'{pid} not in match_mat_stringent.csv columns')
            else:
                matches = match_mat[pid][match_mat[pid] == 1]
                if matches.shape[0] > control_ratio+1:
                    matches = matches.sample(n=control_ratio+1, random_state=0).index
                else:
                    matches = matches.index
                matched_controls.update(matches)

        # remove cases without matches
        cases = match_mat.columns.tolist()

        print(f'Cases with matches: {len(cases)}')
        print(f'Controls with matches: {len(matched_controls)}')
        
        # downsample matches to ratio
        controls = controls[controls[ID].isin(matched_controls)]
        controls = controls.sample(n=len(cases)*control_ratio, random_state=0)
        cases = pop[pop[ID].isin(cases)]

    else:
        controls = controls.sample(n=cases.shape[0]*control_ratio, random_state=0) # randomly sample controls

    cohort = pd.concat([cases, controls])

    # split by train/test and filter
    # a better way would be to use a stratified split, and split by positive patents, then ensure their negative matches are in the same set
    cohort[TRAIN] = np.random.choice([0, 1], cohort.shape[0], p=[0.3, 0.7])
    data = pd.merge(data, cohort, on=ID, how='inner')
    data_train = data[data[TRAIN] == 1]
    print(f'Patients in cohort: {cohort[ID].nunique()}')
    print(cohort.groupby([TRAIN,CASE])[ID].nunique())

    # filter out variables in less than threshold % of each class on training set
    # filter by variable name
    freq_variable_names = filter_by_case_freq(data_train, VAR, 0.01)
    data_train = data_train[data_train[VAR].isin(freq_variable_names)]

    # filter hierchical variables by value
    data_train_hier = data_train[data_train[VAR].isin([RX,ICD9,ICD10,CPT4,HCPCS,ICD10_PX])]
    freq_hier_variable_values = filter_by_case_freq(data_train_hier, VAL, 0.01)
    data_train = data_train[~((data_train[VAR].isin([RX,ICD9,ICD10,CPT4,HCPCS,ICD10_PX])) & (~data_train[VAL].isin(freq_hier_variable_values)))]
    data_train = data_train.drop(columns=[CASE,TRAIN])
    data_train = data_train.reset_index(drop=True)

    # filter out of test set
    data_test = data[data[TRAIN] == 0]
    data_test = data_test[data_test[VAR].isin(freq_variable_names)]
    data_test = data_test[~((data_test[VAR].isin([RX,ICD9,ICD10,CPT4,HCPCS,ICD10_PX])) & (~data_test[VAL].isin(freq_hier_variable_values)))]
    data_test = data_test.drop(columns=[CASE,TRAIN])
    data_test = data_test.reset_index(drop=True)

    # preprocess
    S_train, X_train, X_cont_stats_train, X_latest_train, X_dx_rx_history_train = preprocess(data_train, T, dt)
    S_test, X_test, X_cont_stats_test, X_latest_test, X_dx_rx_history_test = preprocess(data_test, T, dt)

    # save
    cohort.to_csv(f'{output_dir}/cohort.csv', index=False)
    S_train.to_csv(f'{output_dir}/S_train.csv')
    S_test.to_csv(f'{output_dir}/S_test.csv')
    X_train.to_csv(f'{output_dir}/X_train.csv')
    X_test.to_csv(f'{output_dir}/X_test.csv')
    X_cont_stats_train.to_csv(f'{output_dir}/X_cont_stats_train.csv', index=False)
    X_cont_stats_test.to_csv(f'{output_dir}/X_cont_stats_test.csv', index=False)
    X_latest_train.to_csv(f'{output_dir}/X_latest_train.csv', index=False)
    X_latest_test.to_csv(f'{output_dir}/X_latest_test.csv', index=False)
    X_dx_rx_history_train.to_csv(f'{output_dir}/X_dx_rx_history_train.csv')
    X_dx_rx_history_test.to_csv(f'{output_dir}/X_dx_rx_history_test.csv')