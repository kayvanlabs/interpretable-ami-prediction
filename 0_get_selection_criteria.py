#!/usr/bin/env python
# coding: utf-8

import pandas as pd


# misc columns
ICD_CODE = 'ICD_CODE'
END_DSB = 'END_DSB'
QUAL_DX_DSB = 'QUALIFYING_DX_DSB'
VISIT_ID = 'VISIT_ID'
VISIT_ADMIT_DSB = 'VISIT_ADMIT_DSB'
DX_DESC = 'DX_DESC'
DX_CATEGORY = 'DX_CATEGORY'
PID = 'PATIENT_ID'
DTE = 'DAYS_TO_END'
CASE = 'CASE'
DX = 'DIAGNOSIS_CODE'

pd.options.mode.chained_assignment = None  # default='warn'

def psl_filter(df, end_dsb):
    df = pd.merge(case_psl, end_dsb, on=PID)
    rm_df = df[((df['DIAGNOSIS_CODE'].str.contains('414')) & (df['ENTRY_DSB'] < df[END_DSB])) | ((df['DIAGNOSIS_CODE'].str.contains('410')) & (df['ENTRY_DSB'] < df[END_DSB]))]
    return rm_df[PID].unique().tolist()

def get_case_end_dsb(qual_dx, dx_icd_regex):
    qual_dx = qual_dx.sort_values(QUAL_DX_DSB)
    idx = qual_dx.index.where(qual_dx[ICD_CODE].str.contains(dx_icd_regex, regex=True)).dropna().unique()
    qual_dx = qual_dx.loc[idx, :]

    # Get time of first diagnosis
    qual_dx.reset_index(inplace=True, drop=True)
    qual_dx.sort_values([PID, QUAL_DX_DSB], inplace=True)
    cases_end_dsb = qual_dx.groupby(PID).first().drop(columns=[VISIT_ID, DX_DESC, DX_CATEGORY, ICD_CODE]) # index is patient id
    cases_end_dsb = cases_end_dsb.rename(columns={QUAL_DX_DSB: END_DSB})
    cases_end_dsb = cases_end_dsb.reset_index()
    return cases_end_dsb


def filter_by_pid(df, end_dsb):
    df = pd.merge(df, end_dsb, on=PID, how='inner')
    df.reset_index(drop=True, inplace=True)
    return df


def filter_by_date(df, end_dsb, time_col, is_rx=False, pred_window=0):
    df = pd.merge(df, end_dsb, on=PID, how='inner')
    df = df[df[time_col] <= (df[END_DSB] - pred_window)]
    df[DTE] = df[END_DSB] - df[time_col]
    df = df.reset_index(drop=True)
    return df


def get_demographics(demographics, end_dsb):
    demographics = filter_by_pid(demographics, end_dsb)
    demographics = demographics.fillna('Unknown')
    demographics = pd.get_dummies(demographics[[PID,'SEX']], columns=['SEX'])
    demographics = demographics[demographics['SEX_Unknown'] == 0]
    demographics = demographics.drop(['SEX_Male','SEX_Unknown'], axis=1)
    return demographics


def get_hfrs(dx, encs, end_dsb, scores, crosswalk, pred_window, days_b4_end=1826):
    # get visit time
    dx = pd.merge(
        encs[[VISIT_ID, PID, VISIT_ADMIT_DSB]], 
        dx[[VISIT_ID, PID, DX]], 
        on=[PID, VISIT_ID], 
        how='inner'
    )
    dx = dx.drop_duplicates()
    dx = filter_by_date(dx, end_dsb, 'VISIT_ADMIT_DSB', False, pred_window)

    # get ICD10 codes
    dx = pd.merge(dx, crosswalk, how='left', left_on='DIAGNOSIS_CODE', right_index=True)
    dx = dx[~dx.index.duplicated(keep='first')]
    dx['ICD10'] = dx['ICD10'].fillna(dx['DIAGNOSIS_CODE'])
    dx['ICD10'] = dx['ICD10'].str[:3] # get just the first 3 

    # filter to look at only 5 years before the prediction window
    dx = dx[(dx[VISIT_ADMIT_DSB] >= dx[END_DSB] - days_b4_end + pred_window) & (dx[VISIT_ADMIT_DSB] < dx[END_DSB] - pred_window)]

    # compute HFRS scores
    x = pd.merge(dx, scores, how='inner', left_on='ICD10', right_on='ICD-10 Code')
    x = x.pivot_table(index='PATIENT_ID', columns='ICD10', aggfunc='max', values='Score')
    hfrs = x.sum(axis=1)
    hfrs.name = 'HFRS'

    return hfrs


############################################################################################################################################
# PARAMETERS
############################################################################################################################################

dx_icd_regex = '410.*|I21.*' # ICD 9 and 10 codes for cases diagnosis (acute myocardial infarction)
data_path = 'raw_data'
helper_files_dir = 'helper_files'

############################################################################################################################################
# GET COHORT
############################################################################################################################################

# Get cases end time
qual_dx = pd.read_csv(f'{data_path}/Cases_QualifyingDx_DEID_v2.csv')
cases_end_dsb = get_case_end_dsb(qual_dx, dx_icd_regex)
cases_end_dsb[CASE] = 1
del qual_dx

# remove cases that actually have a cardiac disease before qualifying dx shows
case_psl = pd.read_csv(f'{data_path}/Cases_PSL_DEID.csv')
rm_pids = psl_filter(case_psl, cases_end_dsb)
cases_end_dsb = cases_end_dsb[~cases_end_dsb[PID].isin(rm_pids)]

# get control pids
control_encs = pd.read_csv(f'{data_path}/Controls_Encs_DEID.csv')
case_encs = pd.read_csv(f'{data_path}/Cases_Encs_DEID.csv')
encs = pd.concat([control_encs, case_encs], axis=0, ignore_index=True)
del control_encs, case_encs
control_encs = encs[~encs[PID].isin(cases_end_dsb[PID])] # filter out acute MI patients

# get controls last encounter
controls_end_dsb = pd.DataFrame(control_encs.groupby(PID)[VISIT_ADMIT_DSB].max())
controls_end_dsb = controls_end_dsb.rename(columns={VISIT_ADMIT_DSB: END_DSB})
controls_end_dsb[CASE] = 0
controls_end_dsb = controls_end_dsb.reset_index()

# combine cases and controls end times
end_dsb = pd.concat([cases_end_dsb, controls_end_dsb], axis=0, ignore_index=True)

# Extract demographics
case_demographics = pd.read_csv(f'{data_path}/Cases_Demographics_DEID.csv')
controls_demographics = pd.read_csv(f'{data_path}/Controls_Demographics_DEID.csv')
demographics = pd.concat([case_demographics, controls_demographics])
del case_demographics, controls_demographics
demographics = get_demographics(demographics, end_dsb)

# create dataframe to store data used to match cases and controls
selection_criteria = pd.DataFrame(columns=[PID, CASE, END_DSB])
selection_criteria = pd.concat([cases_end_dsb, controls_end_dsb], axis=0, ignore_index=True)

# get patients' sex
selection_criteria = pd.merge(selection_criteria, demographics[[PID,'SEX_Female']], on=PID, how='left')

# get hospital frailty risk score of all patients
# icd 9 to 10 conversion file from https://github.com/bhanratt/ICD9CMtoICD10CM
# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5946808/ and https://github.com/CogStack/risk-score-builder/blob/master/input_files/hfrs_definition.csv
scores = pd.read_csv(f'{helper_files_dir}/HFRS_scores.csv')

crosswalk = pd.read_csv(f'{helper_files_dir}/icd9to10dictionary.txt', sep='|', header=None, names=['ICD9', 'ICD10', 'Description'], index_col=0)
crosswalk.index = crosswalk.index.str.replace('\'','')
crosswalk['ICD10'] = crosswalk['ICD10'].str.replace('\'','')

case_dx = pd.read_csv(f'{data_path}/Cases_Dx_DEID.csv')
control_dx = pd.read_csv(f'{data_path}/Controls_Dx_DEID.csv')
dx = pd.concat([case_dx, control_dx])
hfrs_table = get_hfrs(dx, encs, end_dsb, scores, crosswalk, 0)
selection_criteria = pd.merge(selection_criteria, hfrs_table, on=PID, how='left')
selection_criteria['HFRS'] = selection_criteria['HFRS'].fillna(0)
selection_criteria.to_csv(f'{helper_files_dir}/selection_criteria.csv', index=False)


# print number of cases and controls
print(selection_criteria[CASE].value_counts())