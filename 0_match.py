import pandas as pd
from scipy.spatial.distance import cdist

selection_criteria = pd.read_csv('helper_files/selection_criteria.csv')

selection_criteria['AGE'] = (selection_criteria['END_DSB'] - 180) / 365.25
selection_criteria = selection_criteria[selection_criteria['SEX_Female'].notna()]
selection_criteria['SEX_Female'] = selection_criteria['SEX_Female'].astype(int)
selection_criteria = selection_criteria.set_index('PATIENT_ID')

def match(u, v):
    age_diff = abs(u[0] - v[0])
    sex_diff = u[1] - v[1]
    hfrs_diff = abs(u[2] - v[2])
    if age_diff <= 2 and sex_diff == 0 and hfrs_diff <= 2:
        return 1
    return 0

cases = selection_criteria[selection_criteria['CASE'] == 1][['AGE', 'SEX_Female', 'HFRS']]
controls = selection_criteria[selection_criteria['CASE'] == 0][['AGE', 'SEX_Female', 'HFRS']]

match_mat = pd.DataFrame(cdist(controls, cases, metric=match), columns=cases.index, index=controls.index)

# drop controls without any matches
a = match_mat.sum(axis=1)
no_match_pids = a[a == 0].index
match_mat = match_mat.drop(no_match_pids)

# drop cases without any matches
a = match_mat.sum(axis=0)
no_match_pids = a[a == 0].index
match_mat = match_mat.drop(columns=no_match_pids)

match_mat.to_csv('helper_files/match_mat_stringent.csv')