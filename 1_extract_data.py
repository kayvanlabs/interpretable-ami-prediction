import pandas as pd
import numpy as np
import os

# output data columns
ID = 'ID'
TIME = 't'
VAR = 'variable_name'
VAL = 'variable_value'

# used in load_cohort
CASE = 'CASE'
PID = 'PATIENT_ID'
VISIT_ADMIT_DSB = 'VISIT_ADMIT_DSB'
END_DSB = 'END_DSB'
QUAL_DX_DSB = 'QUALIFYING_DX_DSB'
ICD_CODE = 'ICD_CODE'
VISIT_ID = 'VISIT_ID'
DX_DESC = 'DX_DESC'
DX_CATEGORY = 'DX_CATEGORY'

# params
out_dir = 'data'
dx_icd_regex = '410.*|I21.*'

# change step variable in prep_rx to be less than bin size in next script

def load_cohort(dx_icd_regex, data_root):

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

    # get cases
    qual_dx = pd.read_csv(f'{data_root}/Cases_QualifyingDx_DEID_v2.csv')
    cases_end_dsb = get_case_end_dsb(qual_dx, dx_icd_regex)
    cases_end_dsb[CASE] = 1

    # get control pids
    control_encs = pd.read_csv(f'{data_root}/Controls_Encs_DEID.csv')
    case_encs = pd.read_csv(f'{data_root}/Cases_Encs_DEID.csv')
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

    return end_dsb
    
def filter_by_end_dsb(df, cohort):
    df = pd.merge(df, cohort[[PID,END_DSB]], left_on=[ID], right_on=[PID], how='inner').drop(PID, axis=1)
    df = df[df[TIME] < df[END_DSB]]
    df = df.drop(END_DSB, axis=1)
    return df

def to_float(df, col):
    '''
    Remove all values with alphabetic characters and convert the rest to floats, anything else is NaN.
    '''
    df.reset_index(drop=True, inplace=True)
    x = df[col].str.contains('[a-zA-Z]', regex=True)
    df = df.iloc[(x[x == False]).index]
    df[col] = df[col].str.strip()
    df[col] = pd.to_numeric(df[col], errors='coerce')
    return df[col]

def prep_labs(labs, cohort):
    labs = labs.rename(columns={'RESULT_NAME':VAR,'VALUE':VAL,'COLLECTION_DSB':TIME,PID:ID})
    labs[VAR] = labs[VAR].str.replace(' EX', '')
    labs[VAR] = labs[VAR].str.replace(' LEVEL', '')
    labs[VAR] = labs[VAR].str.title()
    labs = labs[[ID,TIME,VAR,VAL]]
    labs = filter_by_end_dsb(labs, cohort)
    labs[VAL] = to_float(labs, VAL)
    return labs

def prep_vitals(vitals, cohort):
    vitals_variables = ['WEIGHT_KG','HEIGHT_CM','BMI','TEMP','PULSE','BP_SYS','BP_DIA']
    vitals = vitals.rename(columns={PID:ID,'VISIT_ADMIT_DSB':TIME})

    vitals['TEMP'] = vitals['TEMP'].apply(lambda x: x * 9/5 + 32 if x < 50 else x) # convert celsius to fahrenheit
    vitals = vitals[vitals['BMI'] < 200] # remove BMI outliers

    vitals = pd.melt(vitals, id_vars=[ID,TIME], value_vars=vitals_variables, var_name=VAR, value_name=VAL)
    vitals = filter_by_end_dsb(vitals, cohort)
    return vitals

def prep_dx(dx, encs, cohort):
    dx = pd.merge(dx[['VISIT_ID',PID,'DIAGNOSIS_CODE']], encs[['VISIT_ID','VISIT_ADMIT_DSB']], on='VISIT_ID')
    dx = dx.rename(columns={PID:ID,'VISIT_ADMIT_DSB':TIME,'DIAGNOSIS_CODE':VAL})
    dx[VAR] = 'ICD9_CODE'
    dx = dx[[ID,TIME,VAR,VAL]]
    dx = dx.drop_duplicates()

    assert dx[VAL].isnull().sum() == 0, 'There are null values in the ICD9_CODE column.' 

    # convert ICD9 to ICD10
    df_icd_mapping = pd.read_csv('https://raw.githubusercontent.com/bhanratt/ICD9CMtoICD10CM/master/icd9to10dictionary.txt', sep='|', header=None, names=['ICD9', 'ICD10', 'Description'])
    icd_mapping_9_to_10 = dict(df_icd_mapping[['ICD9', 'ICD10']].values)
    dx[VAL] = dx[VAL].replace(icd_mapping_9_to_10)

    # find ICD10 codes
    icd10 = '[A-TV-Z][0-9][0-9AB]\.?[0-9A-TV-Z]{0,4}' # https://www.johndcook.com/blog/2019/05/05/regex_icd_codes/
    dx.loc[dx[VAL].str.contains(icd10, regex=True, na=False),VAR] = 'ICD10_CODE'

    # remove ' characters from variable values
    dx[VAL] = dx[VAL].str.replace("'", '')

    dx = filter_by_end_dsb(dx, cohort)
    return dx

def prep_rx(rx, cohort):
    rx[VAL] = rx['THERA_CLASS'] + ';' + rx['MEDICATION_NAME']
    rx = rx.rename(columns={PID:ID,'ORDERING_DSB':'time_start','ORDER_STOP_DSB':'time_stop'})
    rx[VAR] = 'MEDICATION'
    rx = rx[[ID,'time_start','time_stop',VAR,VAL]]

    # replace NaN stop times with end time
    rx = pd.merge(rx, cohort[[PID,END_DSB]], left_on=[ID], right_on=[PID], how='inner').drop(PID, axis=1)
    rx['time_stop'] = rx['time_stop'].fillna(rx[END_DSB]).astype(int)
    rx = rx.drop(END_DSB, axis=1)

    def create_rows(row):
        step = 30
        if row['time_stop'] - row['time_start'] < step:
            time_range = [row['time_start']]
        else:
            time_range = range(row['time_start'], row['time_stop'], step)  # +1 to include the stop time
        x = pd.DataFrame({ID: row[ID], TIME: time_range, VAR: row[VAR], VAL: row[VAL]})
        return x

    # create a new row for every time step drug was taken
    rx = pd.concat(rx.apply(create_rows, axis=1).tolist(), ignore_index=True)
    rx = filter_by_end_dsb(rx, cohort)

    return rx

def prep_social_hx(social_hx, cohort):
    social_hx = pd.merge(social_hx, encs[[VISIT_ID,VISIT_ADMIT_DSB]], on=VISIT_ID).drop(VISIT_ID, axis=1)

    # convert alcohol consumption to floats (not the root beer kind)
    def format_weekly_oz(x):
        if not isinstance(x, str):
            x = float(x)
            if np.isnan(x):
                return x
        elif '-' in x:
            x = x.replace(' ','')
            x = x.split('-')
            x = (float(x[0]) + float(x[1])) / 2
        return float(x)

    social_hx['OZ_PER_WEEK'] = social_hx['OZ_PER_WEEK'].apply(lambda x: format_weekly_oz(x))
    social_hx['AGE'] = social_hx[VISIT_ADMIT_DSB] // 365.25
    social_hx = pd.melt(social_hx, id_vars=[PID,VISIT_ADMIT_DSB])
    social_hx = social_hx.rename(columns={PID:ID,VISIT_ADMIT_DSB:TIME,'variable':VAR,'value':VAL})
    social_hx = filter_by_end_dsb(social_hx, cohort)
    social_hx = social_hx[social_hx[VAL] != VISIT_ID]
    return social_hx

def get_demographics(demographics):
        '''
        Get demographic data for cohort (first race group, sex, marital status).

        Input:
            demographics: demographics table
            end_dsb: table with patient ids and end dates
            group: CASES or CONTROLS

        Output:
            demographics: demographics table
        '''
        # demographics = demographics.fillna('Unknown')
        demographics['FIRST_RACE_GROUP'] = demographics['RACE'].str.split(',', expand=True)[0]

        demographics['FIRST_RACE_GROUP'] = demographics['FIRST_RACE_GROUP'].replace({
            'Chinese' : 'Asian',
            'Asian Indian' : 'Asian',
            'Filipino' : 'Asian',
            'Japanese' : 'Asian',
            'Korean' : 'Asian',
            'Vietnamese' : 'Asian',
            'Other Asian' : 'Asian',
            'American Indian and Alaska Native' : 'American Indian or Alaska Native',
            'Native Hawaiian and Other Pacific Islander' : 'Native Hawaiian or Other Pacific Islander',
            'Native Hawaiian' : 'Native Hawaiian or Other Pacific Islander',
            'Other Pacific Islander' : 'Native Hawaiian or Other Pacific Islander',
            'Guamanian or Chamorro' : 'Native Hawaiian or Other Pacific Islander',
            'Samoan' : 'Native Hawaiian or Other Pacific Islander',
            'Patient Refused' : np.nan, # 'Unknown',
            'Choose not to disclose' : np.nan, #'Unknown',
            'Middle Eastern/North African' : 'Other'})

        demographics['MARITAL_STATUS'] = demographics['MARITAL_STATUS'].replace({
            'Married' : 1,
            'M': 1})
        demographics.loc[demographics['MARITAL_STATUS'] != 1, 'MARITAL_STATUS'] = 0
        demographics = demographics[[PID,'SEX','MARITAL_STATUS','FIRST_RACE_GROUP']]
        return demographics

def prep_demographics(demographics):
    demographics = get_demographics(demographics)
    demographics = pd.melt(demographics, id_vars=[PID])
    demographics = demographics.rename(columns={PID:ID,'variable':VAR,'value':VAL})
    demographics[TIME] = np.nan
    demographics = demographics[[ID,TIME,VAR,VAL]]
    demographics = demographics * 1
    return demographics

def get_family_hx(family_hx):
    '''
    Filter family history so they are for cohort and in the list of relevant diseases.
    Create a single boolean column for present in family history or not.

    Input:
        family_hx: family history table
        group: CASES or CONTROLS

    Output:
        family_hx: family history table with boolean column for disease presence in family history
    '''
    SEVERE_CARDIAC_HX = [
        'Heart disease', 
        'Heart attack', 
        'Coronary art dis', 
        'Heart failure', 
        'Heart Dis. <45yo', 
        'Congestive Heart Failure', 
        'Heart defect', 
        'Sudden cardiac death', 
        'Aortic disease', 
        'Congenital heart disease/defect', 
        'Cardiomyopathy', 
        'Cardiovascular disease', 
        'Rheumatic heart disease'
    ]

    cardiac_hx = family_hx[family_hx['MedicalHX'].isin(SEVERE_CARDIAC_HX)] # filter to only severe cardiac diseases
    cardiac_hx = cardiac_hx[cardiac_hx['Relation'] != 'Neg Hx'] # remove rows where disease is marked as not present in family history

    # create boolean column indicating if patient has any family history of severe cardiac disease
    cardiac_hx = pd.DataFrame(cardiac_hx.groupby(PID)['MedicalHX'].nunique()) 
    cardiac_hx.rename(columns={'MedicalHX': 'FAMILY_CARDIAC_HX'}, inplace=True)
    cardiac_hx['FAMILY_CARDIAC_HX'] = 1
    cardiac_hx = pd.merge(family_hx, cardiac_hx, on=PID, how='left').drop_duplicates(PID)[[PID, 'FAMILY_CARDIAC_HX']].fillna(0)

    return cardiac_hx

def prep_family_hx(family_hx):
    family_hx = get_family_hx(family_hx)
    family_hx = pd.melt(family_hx, id_vars=[PID])
    family_hx = family_hx.rename(columns={PID:ID,'variable':VAR,'value':VAL})
    family_hx[TIME] = np.nan
    family_hx = family_hx[[ID,TIME,VAR,VAL]]
    return family_hx

def prep_procs(px, cohort):
    px = px[[PID,'PROCEDURE_DSB','PROCEDURE_CODE_TYPE','PROCEDURE_CODE']]
    px = px.drop_duplicates()
    px = px.rename(columns={PID:ID,'PROCEDURE_DSB':TIME,'PROCEDURE_CODE_TYPE':VAR,'PROCEDURE_CODE':VAL})
    px = filter_by_end_dsb(px, cohort)
    return px

if __name__ == '__main__':

    print('loading data...')
    data_root = 'raw_data'

    # make output dir
    os.makedirs(out_dir, exist_ok=True)

    # load cohort
    cohort = load_cohort(dx_icd_regex, data_root)
    cohort.to_csv(f'{out_dir}/cohort.csv', index=False)

    # load cases
    vitals_cases = pd.read_csv(f'{data_root}/Cases_Encs_Vitals_DEID.csv')
    labs_cases = pd.read_csv(f'{data_root}/Cases_Labs_DEID.csv')
    rx_cases = pd.read_csv(f'{data_root}/Cases_MedOrders_DEID.csv')
    dx_cases = pd.read_csv(f'{data_root}/Cases_Dx_DEID.csv')
    encs_cases = pd.read_csv(f'{data_root}/Cases_Encs_DEID.csv')
    social_hx_cases = pd.read_csv(f'{data_root}/Cases_SocialHx_DEID.csv')
    demographics_cases = pd.read_csv(f'{data_root}/Cases_Demographics_DEID.csv')
    family_hx_cases = pd.read_csv(f'{data_root}/Cases_FamilyHx_DEID.csv')
    px_cases = pd.read_csv(f'{data_root}/Cases_Procs_DEID.csv')

    # filter cases
    vitals_cases = vitals_cases[vitals_cases[PID].isin(cohort[PID])]
    labs_cases = labs_cases[labs_cases[PID].isin(cohort[PID])]
    rx_cases = rx_cases[rx_cases[PID].isin(cohort[PID])]
    dx_cases = dx_cases[dx_cases[PID].isin(cohort[PID])]
    encs_cases = encs_cases[encs_cases[PID].isin(cohort[PID])]
    social_hx_cases = social_hx_cases[social_hx_cases[PID].isin(cohort[PID])]
    demographics_cases = demographics_cases[demographics_cases[PID].isin(cohort[PID])]
    family_hx_cases = family_hx_cases[family_hx_cases[PID].isin(cohort[PID])]
    px_cases = px_cases[px_cases[PID].isin(cohort[PID])]

    # load controls
    vitals_controls = pd.read_csv(f'{data_root}/Controls_Encs_Vitals_DEID.csv')
    labs_controls = pd.read_csv(f'{data_root}/Controls_Labs_DEID.csv')
    rx_controls = pd.read_csv(f'{data_root}/Controls_MedOrders_DEID.csv')
    dx_controls = pd.read_csv(f'{data_root}/Controls_Dx_DEID.csv')
    encs_controls = pd.read_csv(f'{data_root}/Controls_Encs_DEID.csv')
    social_hx_controls = pd.read_csv(f'{data_root}/Controls_SocialHx_DEID.csv')
    demographics_controls = pd.read_csv(f'{data_root}/Controls_Demographics_DEID.csv')
    family_hx_controls = pd.read_csv(f'{data_root}/Controls_FamilyHx_DEID.csv')
    px_controls = pd.read_csv(f'{data_root}/Controls_Procs_DEID.csv')

    # filter controls
    vitals_controls = vitals_controls[vitals_controls[PID].isin(cohort[PID])]
    labs_controls = labs_controls[labs_controls[PID].isin(cohort[PID])]
    rx_controls = rx_controls[rx_controls[PID].isin(cohort[PID])]
    dx_controls = dx_controls[dx_controls[PID].isin(cohort[PID])]
    encs_controls = encs_controls[encs_controls[PID].isin(cohort[PID])]
    social_hx_controls = social_hx_controls[social_hx_controls[PID].isin(cohort[PID])]
    demographics_controls = demographics_controls[demographics_controls[PID].isin(cohort[PID])]
    family_hx_controls = family_hx_controls[family_hx_controls[PID].isin(cohort[PID])]
    px_controls = px_controls[px_controls[PID].isin(cohort[PID])]

    # combine cases and controls
    vitals = pd.concat([vitals_cases, vitals_controls])
    labs = pd.concat([labs_cases, labs_controls])
    rx = pd.concat([rx_cases, rx_controls])
    dx = pd.concat([dx_cases, dx_controls])
    encs = pd.concat([encs_cases, encs_controls])
    social_hx = pd.concat([social_hx_cases, social_hx_controls])
    demographics = pd.concat([demographics_cases, demographics_controls])
    family_hx = pd.concat([family_hx_cases, family_hx_controls])
    px = pd.concat([px_cases, px_controls])

    # delete unused variables
    del vitals_cases, labs_cases, rx_cases, dx_cases, encs_cases, social_hx_cases, demographics_cases, family_hx_cases, px_cases
    del vitals_controls, labs_controls, rx_controls, dx_controls, encs_controls, social_hx_controls, demographics_controls, family_hx_controls, px_controls

    print('prepping data...')

    # prep data
    vitals = prep_vitals(vitals, cohort)
    vitals.to_csv(f'{out_dir}/vitals.csv')
    print('vitals done')

    labs = prep_labs(labs, cohort)
    labs.to_csv(f'{out_dir}/labs.csv')
    print('labs done')

    rx = prep_rx(rx, cohort)
    rx.to_csv(f'{out_dir}/rx.csv')
    print('rx done')

    dx = prep_dx(dx, encs, cohort)
    dx.to_csv(f'{out_dir}/dx.csv')
    print('dx done')

    social_hx = prep_social_hx(social_hx, cohort)
    social_hx.to_csv(f'{out_dir}/social_hx.csv')
    print('social hx done')

    demographics = prep_demographics(demographics)
    demographics.to_csv(f'{out_dir}/demographics.csv')
    print('demographics done')

    family_hx = prep_family_hx(family_hx)
    family_hx.to_csv(f'{out_dir}/family_hx.csv')
    print('family hx done')

    px = prep_procs(px)
    px.to_csv(f'{out_dir}/px.csv')
    print('px done')

    print('combining, post-processing, and saving data...')
    # combine data
    data = pd.concat([vitals, labs, dx, rx, social_hx, demographics, family_hx, px])
    data = data.dropna(subset=[VAL])

    # make sure all events are within 5 years from end time
    data = pd.merge(data, cohort[[PID,END_DSB]], left_on=[ID], right_on=[PID], how='inner').drop(PID, axis=1)
    data[TIME] = data[END_DSB] - data[TIME]
    data = data[((data[TIME] > 0) & (data[TIME] < 5*365.25)) | (data[TIME].isnull())]
    data = data.drop([END_DSB], axis=1)

    data = data.sort_values([ID,TIME]) # sort
    data = data.drop_duplicates() # remove duplicates
    
    # save data
    data.to_csv(f'{out_dir}/data.csv', index=False)

    print('done')