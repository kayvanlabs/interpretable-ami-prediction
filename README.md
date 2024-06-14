# interpretable-ami-prediction
Code and results repository for study to evaluate interpretable models' ability to predict acute myocardial infarctions in patients without pre-existing cardiac conditions using outpatient data.

## Workflow
![workflow](workflow.png)

## Dx/Rx Phenotypes

| Phenotype 0                                                  |   Weight |
|:-------------------------------------------------------------|---------:|
| LISINOPRIL 10 mg tablet                                      |   0.0171 |
| ATORVASTATIN 10 mg tablet                                    |   0.0018 |
| metFORMIN (GLUCOPHAGE) 1,000 mg tablet                       |   0.0015 |
| FUROSEMIDE 20 mg tablet                                      |   0.0008 |
| HYDROCHLOROTHIAZIDE 25 mg tablet                             |   0.0007 |
| insulin glargine (LANTUS SOLOSTAR) 100 unit/mL injection pen |   0.0006 |
| pravastatin (PRAVACHOL) 40 mg tablet                         |   0.0006 |
| spironolactone (ALDACTONE) 25 mg tablet                      |   0.0005 |
| simvastatin (ZOCOR) 20 mg tablet                             |   0.0005 |
| ibuprofen (MOTRIN) 800 mg tablet                             |   0.0005 |


| Phenotype 1                                                |   Weight |
|:-----------------------------------------------------------|---------:|
| Age-related cataract (H25)                                 |   0.0184 |
| Age-related nuclear cataract, bilateral (H2513)            |   0.0106 |
| Disorders of vitreous body (H43)                           |   0.0063 |
| Age-related nuclear cataract, unspecified eye (H2510)      |   0.0034 |
| Vitreous degeneration, bilateral (H43813)                  |   0.0033 |
| Combined forms of age-related cataract, bilateral (H25813) |   0.0021 |
| Unspecified disorder of refraction (H527)                  |   0.0018 |
| Unspecified age-related cataract (H259)                    |   0.0014 |
| Vitreous degeneration, right eye (H43811)                  |   0.0012 |
| Age-related nuclear cataract, left eye (H2512)             |   0.0012 |


| Phenotype 2                                                    |   Weight |
|:---------------------------------------------------------------|---------:|
| Type 2 diabetes mellitus (E11)                                 |   0.0174 |
| Type 2 diabetes mellitus without complications (E119)          |   0.0149 |
| metFORMIN (GLUCOPHAGE) 1,000 mg tablet                         |   0.0038 |
| Type 2 diabetes mellitus with hyperglycemia (E1165)            |   0.0026 |
| insulin glargine (LANTUS SOLOSTAR) 100 unit/mL injection pen   |   0.0018 |
| blood sugar diagnostic (GLUCOSE BLOOD) Strip                   |   0.0017 |
| Type 2 diabetes mellitus with diabetic polyneuropathy (E1142)  |   0.0016 |
| Essential (primary) hypertension (I10)                         |   0.0016 |
| metFORMIN (GLUCOPHAGE XR) 500 mg 24 hr tablet                  |   0.0014 |
| Type 2 diabetes mellitus with unspecified complications (E118) |   0.0014 |


| Phenotype 3                                                               |   Weight |
|:--------------------------------------------------------------------------|---------:|
| Abdominal and pelvic pain (R10)                                           |   0.0185 |
| Nausea and vomiting (R11)                                                 |   0.0094 |
| Unspecified abdominal pain (R109)                                         |   0.0081 |
| Other symptoms and signs involving the digestive system and abdomen (R19) |   0.0057 |
| Other functional intestinal disorders (K59)                               |   0.0055 |
| Constipation, unspecified (K5900)                                         |   0.005  |
| Nausea with vomiting, unspecified (R112)                                  |   0.005  |
| Nausea (R110)                                                             |   0.005  |
| Malaise and fatigue (R53)                                                 |   0.0049 |
| Diarrhea, unspecified (R197)                                              |   0.0046 |


| Phenotype 4                                         |   Weight |
|:----------------------------------------------------|---------:|
| FLUTICASONE 50 MCG/ACTUATION NASAL SPRAY,SUSPENSION |   0.031  |
| loratadine (CLARITIN) 10 mg tablet                  |   0.0056 |
| MONTELUKAST 10 mg tablet                            |   0.0041 |
| Vasomotor and allergic rhinitis (J30)               |   0.004  |
| CETIRIZINE 10 mg tablet                             |   0.0025 |
| Other seasonal allergic rhinitis (J302)             |   0.0013 |
| Cough (R05)                                         |   0.0012 |
| cholecalciferol (VITAMIN D3) 2,000 unit capsule     |   0.001  |
| Other allergic rhinitis (J3089)                     |   0.001  |
| FUROSEMIDE 20 mg tablet                             |   0.001  |


| Phenotype 5                                                    |   Weight |
|:---------------------------------------------------------------|---------:|
| Essential (primary) hypertension (I10)                         |   0.033  |
| Disorders of lipoprotein metabolism and other lipidemias (E78) |   0.033  |
| Hyperlipidemia, unspecified (E785)                             |   0.0264 |
| Pure hypercholesterolemia, unspecified (E7800)                 |   0.0032 |
| Mixed hyperlipidemia (E782)                                    |   0.0028 |
| Elevated blood glucose level (R73)                             |   0.0025 |
| Sleep disorders (G47)                                          |   0.0024 |
| ACETAMINOPHEN 325 mg tablet                                    |   0.0022 |
| DOCUSATE SODIUM 100 mg CAPSULE                                 |   0.0022 |
| Chronic obstructive pulmonary disease, unspecified (J449)      |   0.0022 |


| Phenotype 6                                                  |   Weight |
|:-------------------------------------------------------------|---------:|
| ATORVASTATIN 40 mg tablet                                    |   0.0214 |
| AMLODIPINE 10 mg tablet                                      |   0.0095 |
| CLOPIDOGREL 75 mg tablet                                     |   0.005  |
| lisinopril (ZESTRIL) 40 mg tablet                            |   0.0025 |
| METOPROLOL SUCCINATE ER 25 mg tablet,EXTENDED RELEASE 24 HR  |   0.0016 |
| insulin glargine (LANTUS SOLOSTAR) 100 unit/mL injection pen |   0.0014 |
| LOSARTAN 50 mg tablet                                        |   0.0009 |
| METOPROLOL TARTRATE 25 mg tablet                             |   0.0009 |
| ASPIRIN 325 mg tablet                                        |   0.0009 |
| hydrochlorothiazide 12.5 mg tablet                           |   0.0008 |


| Phenotype 7                                     |   Weight |
|:------------------------------------------------|---------:|
| Disorders of refraction and accommodation (H52) |   0.0121 |
| Unspecified cataract (H269)                     |   0.0064 |
| Other cataract (H26)                            |   0.0064 |
| Presbyopia (H524)                               |   0.0062 |
| Myopia, bilateral (H5213)                       |   0.0057 |
| Unspecified astigmatism, bilateral (H52203)     |   0.0036 |
| Hypermetropia, bilateral (H5203)                |   0.0033 |
| Disorders of vitreous body (H43)                |   0.0029 |
| Disorders of lacrimal system (H04)              |   0.0018 |
| Glaucoma (H40)                                  |   0.0014 |


| Phenotype 8                                                    |   Weight |
|:---------------------------------------------------------------|---------:|
| Disorders of lipoprotein metabolism and other lipidemias (E78) |   0.027  |
| Hyperlipidemia, unspecified (E785)                             |   0.0216 |
| Mixed hyperlipidemia (E782)                                    |   0.0027 |
| Benign neoplasm of colon, rectum, anus and anal canal (D12)    |   0.0018 |
| Benign neoplasm of colon, unspecified (D126)                   |   0.0015 |
| SIMVASTATIN 40 mg tablet                                       |   0.0015 |
| ATORVASTATIN 10 mg tablet                                      |   0.0015 |
| Male erectile dysfunction, unspecified (N529)                  |   0.0013 |
| Male erectile dysfunction (N52)                                |   0.0013 |
| Pure hypercholesterolemia, unspecified (E7800)                 |   0.0013 |


| Phenotype 9                                                            |   Weight |
|:-----------------------------------------------------------------------|---------:|
| Type 2 diabetes mellitus (E11)                                         |   0.1577 |
| Type 2 diabetes mellitus without complications (E119)                  |   0.1381 |
| Type 2 diabetes mellitus with hyperglycemia (E1165)                    |   0.0213 |
| metFORMIN (GLUCOPHAGE) 1,000 mg tablet                                 |   0.0195 |
| Type 2 diabetes mellitus with unspecified complications (E118)         |   0.0168 |
| insulin glargine (LANTUS SOLOSTAR) 100 unit/mL injection pen           |   0.0128 |
| metFORMIN (GLUCOPHAGE XR) 500 mg 24 hr tablet                          |   0.0118 |
| Type 2 diabetes mellitus with diabetic neuropathy, unspecified (E1140) |   0.0104 |
| Type 2 diabetes mellitus with diabetic polyneuropathy (E1142)          |   0.0102 |
| blood sugar diagnostic (GLUCOSE BLOOD) Strip                           |   0.01   |


| Phenotype 10                                                |   Weight |
|:------------------------------------------------------------|---------:|
| Gastro-esophageal reflux disease (K21)                      |   0.018  |
| Gastro-esophageal reflux disease without esophagitis (K219) |   0.0174 |
| omeprazole (PRILOSEC) 40 mg delayed release capsule         |   0.0031 |
| RANITIDINE 150 mg tablet                                    |   0.0022 |
| Asthma (J45)                                                |   0.0021 |
| Aphagia and dysphagia (R13)                                 |   0.0016 |
| Diaphragmatic hernia without obstruction or gangrene (K449) |   0.0016 |
| Diaphragmatic hernia (K44)                                  |   0.0016 |
| Dysphagia, unspecified (R1310)                              |   0.0015 |
| Vasomotor and allergic rhinitis (J30)                       |   0.0014 |


| Phenotype 11                                         |   Weight |
|:-----------------------------------------------------|---------:|
| Hypothyroidism, unspecified (E039)                   |   0.12   |
| Other hypothyroidism (E03)                           |   0.12   |
| LEVOTHYROXINE 50 MCG tablet                          |   0.0126 |
| LEVOTHYROXINE 75 MCG tablet                          |   0.0123 |
| LEVOTHYROXINE 100 MCG tablet                         |   0.012  |
| Other disorders of urinary system (N39)              |   0.0104 |
| levothyroxine (SYNTHROID) 125 mcg tablet             |   0.0099 |
| Malaise and fatigue (R53)                            |   0.0098 |
| Other and unspecified osteoarthritis (M19)           |   0.0085 |
| Unspecified osteoarthritis, unspecified site (M1990) |   0.0085 |


| Phenotype 12                                                             |   Weight |
|:-------------------------------------------------------------------------|---------:|
| TAMSULOSIN ER 0.4 mg CAPSULE,EXTENDED RELEASE 24 HR                      |   0.0901 |
| Benign prostatic hyperplasia (N40)                                       |   0.0307 |
| Malignant neoplasm of prostate (C61)                                     |   0.0252 |
| Benign prostatic hyperplasia with lower urinary tract symptoms (N401)    |   0.0201 |
| Benign prostatic hyperplasia without lower urinary tract symptoms (N400) |   0.0149 |
| FINASTERIDE 5 mg tablet                                                  |   0.0149 |
| Abnormal tumor markers (R97)                                             |   0.0136 |
| Polyuria (R35)                                                           |   0.0117 |
| Retention of urine (R33)                                                 |   0.0112 |
| Retention of urine, unspecified (R339)                                   |   0.0112 |


| Phenotype 13                                        |   Weight |
|:----------------------------------------------------|---------:|
| HYDROCODONE 5 mg-ACETAMINOPHEN 325 mg tablet        |   0.1814 |
| IBUPROFEN 600 mg tablet                             |   0.0379 |
| ibuprofen (MOTRIN) 800 mg tablet                    |   0.0228 |
| ERGOCALCIFEROL (VITAMIN D2) (VITAMIN D ORAL)        |   0.0153 |
| DOCUSATE SODIUM 100 mg CAPSULE                      |   0.0131 |
| CYCLOBENZAPRINE 10 mg tablet                        |   0.0112 |
| CYCLOBENZAPRINE 5 mg tablet                         |   0.0111 |
| ONDANSETRON 4 mg DISINTEGRATING tablet              |   0.0103 |
| SULFAMETHOXAZOLE 800 mg-TRIMETHOPRIM 160 mg tablet  |   0.0059 |
| polyethylene glycol 3350 (MIRALAX) 17 g/dose powder |   0.0058 |


| Phenotype 14                                           |   Weight |
|:-------------------------------------------------------|---------:|
| Overweight and obesity (E66)                           |   0.0349 |
| Obesity, unspecified (E669)                            |   0.0235 |
| Morbid (severe) obesity due to excess calories (E6601) |   0.0126 |
| Essential (primary) hypertension (I10)                 |   0.0053 |
| Elevated blood glucose level (R73)                     |   0.0044 |
| OXYCODONE 5 mg tablet                                  |   0.0035 |
| Prediabetes (R7303)                                    |   0.0031 |
| Obstructive sleep apnea (adult) (pediatric) (G4733)    |   0.003  |
| Sleep disorders (G47)                                  |   0.003  |
| Other disorders of urinary system (N39)                |   0.0027 |


| Phenotype 15                                                  |   Weight |
|:--------------------------------------------------------------|---------:|
| Major depressive disorder, single episode, unspecified (F329) |   0.0192 |
| Major depressive disorder, single episode (F32)               |   0.0192 |
| SERTRALINE 100 mg tablet                                      |   0.0033 |
| buPROPion (WELLBUTRIN XL) 300 mg 24 hr tablet                 |   0.0025 |
| TRAZODONE 50 mg tablet                                        |   0.0024 |
| BUPROPION HCL XL 150 mg 24 HR tablet, EXTENDED RELEASE        |   0.002  |
| DULOXETINE 60 mg CAPSULE,DELAYED RELEASE                      |   0.0019 |
| TRAZODONE 100 mg tablet                                       |   0.0014 |
| FLUOXETINE 20 mg CAPSULE                                      |   0.0014 |
| CITALOPRAM 20 mg tablet                                       |   0.0013 |


| Phenotype 16                                           |   Weight |
|:-------------------------------------------------------|---------:|
| Overweight and obesity (E66)                           |   0.0509 |
| Obesity, unspecified (E669)                            |   0.0292 |
| Morbid (severe) obesity due to excess calories (E6601) |   0.0218 |
| Elevated blood glucose level (R73)                     |   0.0095 |
| Prediabetes (R7303)                                    |   0.0068 |
| Vitamin D deficiency, unspecified (E559)               |   0.0042 |
| Vitamin D deficiency (E55)                             |   0.0042 |
| Overweight (E663)                                      |   0.0032 |
| ibuprofen (MOTRIN) 800 mg tablet                       |   0.0031 |
| Other obesity due to excess calories (E6609)           |   0.0025 |


| Phenotype 17                                                                              |   Weight |
|:------------------------------------------------------------------------------------------|---------:|
| peg 3350-electrolytes (TRILYTE WITH FLAVOR PACKETS) 420 gram solution                     |   0.0376 |
| Benign neoplasm of colon, rectum, anus and anal canal (D12)                               |   0.0111 |
| Benign neoplasm of colon, unspecified (D126)                                              |   0.0055 |
| Elevated blood glucose level (R73)                                                        |   0.0033 |
| Other diseases of intestine (K63)                                                         |   0.0032 |
| Polyp of colon (K635)                                                                     |   0.0028 |
| Prediabetes (R7303)                                                                       |   0.0027 |
| Benign neoplasm of transverse colon (D123)                                                |   0.0027 |
| Diverticular disease of intestine (K57)                                                   |   0.0026 |
| Diverticulosis of large intestine without perforation or abscess without bleeding (K5730) |   0.0026 |


| Phenotype 18                                                  |   Weight |
|:--------------------------------------------------------------|---------:|
| ASPIRIN 81 mg CHEWABLE tablet                                 |   0.0678 |
| ATORVASTATIN 10 mg tablet                                     |   0.0035 |
| LATANOPROST 0.005 % EYE DROPS                                 |   0.003  |
| SIMVASTATIN 40 mg tablet                                      |   0.003  |
| CETIRIZINE 10 mg tablet                                       |   0.0029 |
| CLOPIDOGREL 75 mg tablet                                      |   0.0029 |
| HYDROCHLOROTHIAZIDE 25 mg tablet                              |   0.0028 |
| METOPROLOL TARTRATE 25 mg tablet                              |   0.0028 |
| lisinopril-hydrochlorothiazide (ZESTORETIC) 20-12.5 mg tablet |   0.0027 |
| omeprazole (PRILOSEC) 40 mg delayed release capsule           |   0.0026 |


| Phenotype 19                                         |   Weight |
|:-----------------------------------------------------|---------:|
| Dorsalgia (M54)                                      |   0.0092 |
| Pain, not elsewhere classified (G89)                 |   0.0079 |
| Other chronic pain (G8929)                           |   0.0076 |
| Low back pain (M545)                                 |   0.0056 |
| Cervicalgia (M542)                                   |   0.0018 |
| CYCLOBENZAPRINE 10 mg tablet                         |   0.0016 |
| Other joint disorder, not elsewhere classified (M25) |   0.0014 |
| Lumbago with sciatica, right side (M5441)            |   0.0012 |
| Dorsalgia, unspecified (M549)                        |   0.0011 |
| Spondylosis (M47)                                    |   0.001  |


| Phenotype 20                                                                   |   Weight |
|:-------------------------------------------------------------------------------|---------:|
| FOLIC ACID 1 mg tablet                                                         |   0.013  |
| PREDNISONE 5 mg tablet                                                         |   0.0103 |
| Other disorders involving the immune mechanism, not elsewhere classified (D89) |   0.0094 |
| Disorder involving the immune mechanism, unspecified (D899)                    |   0.0094 |
| hydroxychloroquine (PLAQUENIL) 200 mg tablet                                   |   0.0077 |
| methotrexate 2.5 mg tablet                                                     |   0.0075 |
| Rheumatoid arthritis, unspecified (M069)                                       |   0.0069 |
| Other rheumatoid arthritis (M06)                                               |   0.0069 |
| ATORVASTATIN 10 mg tablet                                                      |   0.0055 |
| PREDNISONE 10 mg tablet                                                        |   0.0043 |


| Phenotype 21                                                   |   Weight |
|:---------------------------------------------------------------|---------:|
| Disorders of lipoprotein metabolism and other lipidemias (E78) |   0.0297 |
| Essential (primary) hypertension (I10)                         |   0.0293 |
| Hyperlipidemia, unspecified (E785)                             |   0.0237 |
| Gastro-esophageal reflux disease (K21)                         |   0.0106 |
| Gastro-esophageal reflux disease without esophagitis (K219)    |   0.0102 |
| Overweight and obesity (E66)                                   |   0.0085 |
| Type 2 diabetes mellitus (E11)                                 |   0.0076 |
| Sleep disorders (G47)                                          |   0.0064 |
| Obesity, unspecified (E669)                                    |   0.006  |
| Pain, not elsewhere classified (G89)                           |   0.0056 |


| Phenotype 22                                                                |   Weight |
|:----------------------------------------------------------------------------|---------:|
| GABAPENTIN 300 mg CAPSULE                                                   |   0.0109 |
| TRAMADOL 50 mg tablet                                                       |   0.0045 |
| TRAZODONE 50 mg tablet                                                      |   0.0011 |
| CYCLOBENZAPRINE 10 mg tablet                                                |   0.0009 |
| HYDROCODONE 10 mg-ACETAMINOPHEN 325 mg tablet                               |   0.0008 |
| Other and unspecified soft tissue disorders, not elsewhere classified (M79) |   0.0008 |
| gabapentin (NEURONTIN) 600 mg tablet                                        |   0.0007 |
| HYDROcodone-acetaminophen (NORCO) 7.5-325 mg tablet                         |   0.0005 |
| Neuralgia and neuritis, unspecified (M792)                                  |   0.0005 |
| triamcinolone 0.1 % cream                                                   |   0.0005 |


| Phenotype 23                                                |   Weight |
|:------------------------------------------------------------|---------:|
| Essential (primary) hypertension (I10)                      |   0.0591 |
| HYDROCHLOROTHIAZIDE 25 mg tablet                            |   0.0061 |
| AMLODIPINE 10 mg tablet                                     |   0.0056 |
| LOSARTAN 50 mg tablet                                       |   0.0031 |
| lisinopril (ZESTRIL) 40 mg tablet                           |   0.003  |
| Elevated blood glucose level (R73)                          |   0.0027 |
| lisinopril-hydrochlorothiazide (ZESTORETIC) 20-25 mg tablet |   0.0015 |
| sildenafil (VIAGRA) 100 mg tablet                           |   0.0014 |
| Benign prostatic hyperplasia (N40)                          |   0.0014 |
| Other abnormal glucose (R7309)                              |   0.0011 |


| Phenotype 24                                    |   Weight |
|:------------------------------------------------|---------:|
| Disorders of refraction and accommodation (H52) |   0.0197 |
| Presbyopia (H524)                               |   0.011  |
| Age-related cataract (H25)                      |   0.0101 |
| Myopia, bilateral (H5213)                       |   0.0099 |
| Unspecified cataract (H269)                     |   0.0099 |
| Other cataract (H26)                            |   0.0099 |
| Unspecified astigmatism, bilateral (H52203)     |   0.0064 |
| Disorders of vitreous body (H43)                |   0.006  |
| Age-related nuclear cataract, bilateral (H2513) |   0.0049 |
| Hypermetropia, bilateral (H5203)                |   0.0046 |


| Phenotype 25                                                                |   Weight |
|:----------------------------------------------------------------------------|---------:|
| Other joint disorder, not elsewhere classified (M25)                        |   0.0218 |
| Osteoarthritis of knee (M17)                                                |   0.0102 |
| Pain in right knee (M25561)                                                 |   0.0049 |
| Pain in unspecified knee (M25569)                                           |   0.0048 |
| Other and unspecified osteoarthritis (M19)                                  |   0.0047 |
| Unspecified osteoarthritis, unspecified site (M1990)                        |   0.0047 |
| Other and unspecified soft tissue disorders, not elsewhere classified (M79) |   0.0043 |
| Pain in left knee (M25562)                                                  |   0.0043 |
| Bilateral primary osteoarthritis of knee (M170)                             |   0.0037 |
| Unilateral primary osteoarthritis, right knee (M1711)                       |   0.0029 |


| Phenotype 26                                                              |   Weight |
|:--------------------------------------------------------------------------|---------:|
| Nausea and vomiting (R11)                                                 |   0.0277 |
| Abnormalities of breathing (R06)                                          |   0.027  |
| Malaise and fatigue (R53)                                                 |   0.0267 |
| Anemia, unspecified (D649)                                                |   0.0262 |
| Other anemias (D64)                                                       |   0.0262 |
| Abdominal and pelvic pain (R10)                                           |   0.0227 |
| Other symptoms and signs involving the digestive system and abdomen (R19) |   0.0203 |
| Other disorders of fluid, electrolyte and acid-base balance (E87)         |   0.0182 |
| PROCHLORPERAZINE MALEATE 10 mg tablet                                     |   0.0172 |
| Diarrhea, unspecified (R197)                                              |   0.017  |


| Phenotype 27                                                                      |   Weight |
|:----------------------------------------------------------------------------------|---------:|
| CHOLECALCIFEROL (VITAMIN D3) 1,000 UNIT tablet                                    |   0.0185 |
| SIMVASTATIN 40 mg tablet                                                          |   0.002  |
| cyanocobalamin (VITAMIN B-12) 1,000 mcg tablet                                    |   0.0018 |
| ascorbic acid (VITAMIN C) 500 mg Tablet                                           |   0.0016 |
| Malignant neoplasm of bladder (C67)                                               |   0.0014 |
| Malignant neoplasm of bladder, unspecified (C679)                                 |   0.0014 |
| Other and unspecified symptoms and signs involving the genitourinary system (R39) |   0.0013 |
| omega-3 fatty acids-fish oil 300-1,000 mg Capsule                                 |   0.0011 |
| Other disorders of urinary system (N39)                                           |   0.001  |
| Other symptoms and signs involving the genitourinary system (R3989)               |   0.0009 |


| Phenotype 28                                                   |   Weight |
|:---------------------------------------------------------------|---------:|
| Disorders of lipoprotein metabolism and other lipidemias (E78) |   0.0705 |
| Hyperlipidemia, unspecified (E785)                             |   0.0564 |
| Essential (primary) hypertension (I10)                         |   0.0535 |
| Overweight and obesity (E66)                                   |   0.0175 |
| Obesity, unspecified (E669)                                    |   0.0134 |
| Type 2 diabetes mellitus (E11)                                 |   0.0117 |
| Type 2 diabetes mellitus without complications (E119)          |   0.0104 |
| Gastro-esophageal reflux disease (K21)                         |   0.0089 |
| Gastro-esophageal reflux disease without esophagitis (K219)    |   0.0087 |
| Major depressive disorder, single episode, unspecified (F329)  |   0.0072 |


| Phenotype 29                                                                |   Weight |
|:----------------------------------------------------------------------------|---------:|
| Pain, not elsewhere classified (G89)                                        |   0.0655 |
| Other chronic pain (G8929)                                                  |   0.0588 |
| Dorsalgia (M54)                                                             |   0.0567 |
| Low back pain (M545)                                                        |   0.0332 |
| Other joint disorder, not elsewhere classified (M25)                        |   0.0248 |
| Cervicalgia (M542)                                                          |   0.0144 |
| Other and unspecified soft tissue disorders, not elsewhere classified (M79) |   0.0109 |
| Pain, unspecified (R52)                                                     |   0.0099 |
| Pain in left knee (M25562)                                                  |   0.0086 |
| Lumbago with sciatica, right side (M5441)                                   |   0.0085 |


| Phenotype 30                                                |   Weight |
|:------------------------------------------------------------|---------:|
| Sleep disorders (G47)                                       |   0.1222 |
| Obstructive sleep apnea (adult) (pediatric) (G4733)         |   0.1101 |
| Insomnia, unspecified (G4700)                               |   0.012  |
| Sleep apnea, unspecified (G4730)                            |   0.0101 |
| Morbid (severe) obesity due to excess calories (E6601)      |   0.0067 |
| Abnormalities of breathing (R06)                            |   0.0062 |
| EPINEPHRINE 0.3 mg/0.3 ML (1:1,000) INJECTION,AUTO-INJECTOR |   0.0061 |
| Other extrapyramidal and movement disorders (G25)           |   0.0044 |
| Restless legs syndrome (G2581)                              |   0.0044 |
| loratadine (CLARITIN) 10 mg tablet                          |   0.0038 |


| Phenotype 31                                                    |   Weight |
|:----------------------------------------------------------------|---------:|
| ASPIRIN 81 mg tablet,DELAYED RELEASE                            |   0.0789 |
| METOPROLOL TARTRATE 25 mg tablet                                |   0.0051 |
| atorvastatin (LIPITOR) 80 mg tablet                             |   0.0031 |
| LATANOPROST 0.005 % EYE DROPS                                   |   0.0028 |
| budesonide-formoterol (SYMBICORT) 160-4.5 mcg/actuation inhaler |   0.0027 |
| CLOPIDOGREL 75 mg tablet                                        |   0.0026 |
| ALLOPURINOL 100 mg tablet                                       |   0.0026 |
| METOPROLOL SUCCINATE ER 50 mg tablet,EXTENDED RELEASE 24 HR     |   0.0026 |
| pravastatin (PRAVACHOL) 40 mg tablet                            |   0.0024 |
| ACETAMINOPHEN 325 mg tablet                                     |   0.002  |


| Phenotype 32                                         |   Weight |
|:-----------------------------------------------------|---------:|
| ELECT/CALORIC/H2O                                    |   0.0313 |
| ferrous sulfate 325 mg (65 mg iron) Tablet           |   0.0189 |
| MAGNESIUM OXIDE 400 mg tablet                        |   0.0125 |
| FUROSEMIDE 40 mg tablet                              |   0.0022 |
| FUROSEMIDE 20 mg tablet                              |   0.0021 |
| cholecalciferol (VITAMIN D3) 2,000 unit capsule      |   0.002  |
| meclizine (ANTIVERT) 25 mg tablet                    |   0.0019 |
| ATORVASTATIN 10 mg tablet                            |   0.0016 |
| Iron deficiency anemia (D50)                         |   0.0016 |
| pantoprazole (PROTONIX) 40 mg delayed release tablet |   0.0013 |


| Phenotype 33                                  |   Weight |
|:----------------------------------------------|---------:|
| LISINOPRIL 20 mg tablet                       |   0.0231 |
| metFORMIN (GLUCOPHAGE) 1,000 mg tablet        |   0.0078 |
| simvastatin (ZOCOR) 20 mg tablet              |   0.0035 |
| ASPIRIN 325 mg tablet                         |   0.0021 |
| METOPROLOL TARTRATE 25 mg tablet              |   0.0014 |
| LATANOPROST 0.005 % EYE DROPS                 |   0.0014 |
| SIMVASTATIN 40 mg tablet                      |   0.0013 |
| HYDROCHLOROTHIAZIDE 25 mg tablet              |   0.0013 |
| PREDNISOLONE ACETATE 1 % EYE DROPS,SUSPENSION |   0.0012 |
| CLOPIDOGREL 75 mg tablet                      |   0.0011 |


| Phenotype 34                                                    |   Weight |
|:----------------------------------------------------------------|---------:|
| ALBUTEROL SULFATE HFA 90 MCG/ACTUATION AEROSOL INHALER          |   0.1497 |
| Asthma (J45)                                                    |   0.0324 |
| MONTELUKAST 10 mg tablet                                        |   0.0257 |
| Chronic obstructive pulmonary disease, unspecified (J449)       |   0.0199 |
| Other chronic obstructive pulmonary disease (J44)               |   0.0199 |
| Unspecified asthma, uncomplicated (J45909)                      |   0.019  |
| Cough (R05)                                                     |   0.0157 |
| Mild intermittent asthma, uncomplicated (J4520)                 |   0.0157 |
| TIOTROPIUM BROMIDE 18 MCG CAPSULE WITH INHALATION DEVICE        |   0.0144 |
| budesonide-formoterol (SYMBICORT) 160-4.5 mcg/actuation inhaler |   0.0118 |


| Phenotype 35                                        |   Weight |
|:----------------------------------------------------|---------:|
| ACETAMINOPHEN 500 mg tablet                         |   0.0743 |
| DOCUSATE SODIUM 100 mg CAPSULE                      |   0.0489 |
| OXYCODONE 5 mg tablet                               |   0.0228 |
| POLYETHYLENE GLYCOL 3350 17 GRAM ORAL POWDER PACKET |   0.0219 |
| TRAMADOL 50 mg tablet                               |   0.0098 |
| ACETAMINOPHEN 325 mg tablet                         |   0.008  |
| senna (SENOKOT) 8.6 mg tablet                       |   0.008  |
| IBUPROFEN 200 mg tablet                             |   0.0056 |
| cholecalciferol (VITAMIN D3) 2,000 unit capsule     |   0.0044 |
| omega-3 fatty acids-fish oil 300-1,000 mg Capsule   |   0.0036 |


| Phenotype 36                                                   |   Weight |
|:---------------------------------------------------------------|---------:|
| Type 2 diabetes mellitus (E11)                                 |   0.0463 |
| Type 2 diabetes mellitus without complications (E119)          |   0.0413 |
| Essential (primary) hypertension (I10)                         |   0.0113 |
| Type 2 diabetes mellitus with hyperglycemia (E1165)            |   0.0076 |
| Disorders of lipoprotein metabolism and other lipidemias (E78) |   0.0064 |
| Hyperlipidemia, unspecified (E785)                             |   0.0062 |
| metFORMIN (GLUCOPHAGE) 1,000 mg tablet                         |   0.0051 |
| METFORMIN 500 mg tablet                                        |   0.0046 |
| metFORMIN (GLUCOPHAGE XR) 500 mg 24 hr tablet                  |   0.0034 |
| insulin glargine (LANTUS SOLOSTAR) 100 unit/mL injection pen   |   0.0033 |


| Phenotype 37                                          |   Weight |
|:------------------------------------------------------|---------:|
| Other anxiety disorders (F41)                         |   0.0347 |
| Anxiety disorder, unspecified (F419)                  |   0.0285 |
| Generalized anxiety disorder (F411)                   |   0.0068 |
| LORAZEPAM 0.5 mg tablet                               |   0.0035 |
| Other specified anxiety disorders (F418)              |   0.0034 |
| ALPRAZOLAM 0.25 mg tablet                             |   0.003  |
| ALPRAZOLAM 0.5 mg tablet                              |   0.0029 |
| Major depressive disorder, recurrent (F33)            |   0.0024 |
| Major depressive disorder, recurrent, moderate (F331) |   0.0024 |
| CLONAZEPAM 0.5 mg tablet                              |   0.0023 |


| Phenotype 38                                                   |   Weight |
|:---------------------------------------------------------------|---------:|
| ATORVASTATIN 20 mg tablet                                      |   0.0737 |
| AMLODIPINE 10 mg tablet                                        |   0.0063 |
| lisinopril (ZESTRIL) 40 mg tablet                              |   0.0041 |
| insulin glargine (LANTUS SOLOSTAR) 100 unit/mL injection pen   |   0.0039 |
| Pure hypercholesterolemia, unspecified (E7800)                 |   0.0034 |
| Other peripheral vascular diseases (I73)                       |   0.003  |
| Peripheral vascular disease, unspecified (I739)                |   0.003  |
| DULoxetine (CYMBALTA) 30 mg delayed release capsule            |   0.003  |
| ALLOPURINOL 100 mg tablet                                      |   0.0024 |
| Disorders of lipoprotein metabolism and other lipidemias (E78) |   0.0023 |


| Phenotype 39                                    |   Weight |
|:------------------------------------------------|---------:|
| Disorders of refraction and accommodation (H52) |   0.0389 |
| Age-related cataract (H25)                      |   0.0343 |
| Unspecified cataract (H269)                     |   0.0324 |
| Other cataract (H26)                            |   0.0324 |
| Presbyopia (H524)                               |   0.0239 |
| PREDNISOLONE ACETATE 1 % EYE DROPS,SUSPENSION   |   0.0216 |
| Age-related nuclear cataract, bilateral (H2513) |   0.0176 |
| Myopia, bilateral (H5213)                       |   0.0175 |
| Unspecified astigmatism, bilateral (H52203)     |   0.0155 |
| Disorders of vitreous body (H43)                |   0.0152 |


| Phenotype 40                                             |   Weight |
|:---------------------------------------------------------|---------:|
| METFORMIN 500 mg tablet                                  |   0.0634 |
| simvastatin (ZOCOR) 20 mg tablet                         |   0.0097 |
| ALPRAZOLAM 0.25 mg tablet                                |   0.0067 |
| omeprazole (PRILOSEC) 40 mg delayed release capsule      |   0.0062 |
| CYCLOBENZAPRINE 10 mg tablet                             |   0.0051 |
| naproxen (NAPROSYN) 500 mg tablet                        |   0.0043 |
| ATORVASTATIN 10 mg tablet                                |   0.0035 |
| TIOTROPIUM BROMIDE 18 MCG CAPSULE WITH INHALATION DEVICE |   0.0033 |
| SERTRALINE 50 mg tablet                                  |   0.0029 |
| aspirin, buffered (BUFFERIN LOW DOSE) 81 mg Tablet       |   0.0029 |


| Phenotype 41                                        |   Weight |
|:----------------------------------------------------|---------:|
| Hypothyroidism, unspecified (E039)                  |   0.0269 |
| Other hypothyroidism (E03)                          |   0.0269 |
| LEVOTHYROXINE 100 MCG tablet                        |   0.0051 |
| LEVOTHYROXINE 50 MCG tablet                         |   0.0032 |
| levothyroxine (SYNTHROID) 125 mcg tablet            |   0.0027 |
| LEVOTHYROXINE 75 MCG tablet                         |   0.0022 |
| LEVOTHYROXINE 112 MCG tablet                        |   0.0016 |
| LEVOTHYROXINE 25 MCG tablet                         |   0.0014 |
| Menopausal and other perimenopausal disorders (N95) |   0.0012 |
| ACETAMINOPHEN 325 mg tablet                         |   0.0011 |


| Phenotype 42                                            |   Weight |
|:--------------------------------------------------------|---------:|
| Disorders of lacrimal system (H04)                      |   0.0613 |
| Dry eye syndrome of bilateral lacrimal glands (H04123)  |   0.0451 |
| LATANOPROST 0.005 % EYE DROPS                           |   0.021  |
| Dry eye syndrome of unspecified lacrimal gland (H04129) |   0.0178 |
| PREDNISOLONE ACETATE 1 % EYE DROPS,SUSPENSION           |   0.0154 |
| Glaucoma (H40)                                          |   0.0142 |
| TIMOLOL MALEATE 0.5 % EYE DROPS                         |   0.0095 |
| cycloSPORINE (RESTASIS) 0.05 % ophthalmic dropperette   |   0.0084 |
| Unspecified glaucoma (H409)                             |   0.0079 |
| Other inflammation of eyelid (H01)                      |   0.0076 |


| Phenotype 43                                                                 |   Weight |
|:-----------------------------------------------------------------------------|---------:|
| Osteoporosis without current pathological fracture (M81)                     |   0.019  |
| Age-related osteoporosis without current pathological fracture (M810)        |   0.019  |
| alendronate (FOSAMAX) 70 mg tablet                                           |   0.005  |
| Malignant neoplasm of unspecified site of unspecified female breast (C50919) |   0.0037 |
| Malignant neoplasm of breast (C50)                                           |   0.0037 |
| Vitamin D deficiency, unspecified (E559)                                     |   0.0037 |
| Vitamin D deficiency (E55)                                                   |   0.0037 |
| polyethylene glycol 3350 (MIRALAX) 17 g/dose powder                          |   0.0031 |
| Dermatophytosis (B35)                                                        |   0.0031 |
| Tinea unguium (B351)                                                         |   0.003  |


| Phenotype 44                                                             |   Weight |
|:-------------------------------------------------------------------------|---------:|
| Gastro-esophageal reflux disease (K21)                                   |   0.0639 |
| Gastro-esophageal reflux disease without esophagitis (K219)              |   0.0629 |
| Abdominal and pelvic pain (R10)                                          |   0.0081 |
| omeprazole (PRILOSEC) 40 mg delayed release capsule                      |   0.0059 |
| Benign neoplasm of other and ill-defined parts of digestive system (D13) |   0.0056 |
| OMEPRAZOLE 20 mg CAPSULE,DELAYED RELEASE                                 |   0.005  |
| Benign neoplasm of colon, rectum, anus and anal canal (D12)              |   0.0049 |
| Aphagia and dysphagia (R13)                                              |   0.0047 |
| Dysphagia, unspecified (R1310)                                           |   0.0045 |
| Asthma (J45)                                                             |   0.0044 |


| Phenotype 45                                                |   Weight |
|:------------------------------------------------------------|---------:|
| OMEPRAZOLE 20 mg CAPSULE,DELAYED RELEASE                    |   0.0659 |
| simvastatin (ZOCOR) 20 mg tablet                            |   0.0021 |
| SIMVASTATIN 40 mg tablet                                    |   0.0017 |
| TRAMADOL 50 mg tablet                                       |   0.0017 |
| aspirin, buffered (BUFFERIN LOW DOSE) 81 mg Tablet          |   0.0015 |
| ALLOPURINOL 100 mg tablet                                   |   0.0015 |
| loratadine (CLARITIN) 10 mg tablet                          |   0.0015 |
| LEVOTHYROXINE 100 MCG tablet                                |   0.0015 |
| alendronate (FOSAMAX) 70 mg tablet                          |   0.0013 |
| METOPROLOL SUCCINATE ER 25 mg tablet,EXTENDED RELEASE 24 HR |   0.0012 |


| Phenotype 46                                                                    |   Weight |
|:--------------------------------------------------------------------------------|---------:|
| Skin changes due to chronic exposure to nonionizing radiation (L57)             |   0.0174 |
| Actinic keratosis (L570)                                                        |   0.0127 |
| Seborrheic keratosis (L82)                                                      |   0.0113 |
| Other disorders of skin and subcutaneous tissue, not elsewhere classified (L98) |   0.0111 |
| Other skin changes due to chronic exposure to nonionizing radiation (L578)      |   0.0097 |
| Other seborrheic keratosis (L821)                                               |   0.0094 |
| Disorder of the skin and subcutaneous tissue, unspecified (L989)                |   0.0078 |
| triamcinolone 0.1 % cream                                                       |   0.0053 |
| Other benign neoplasms of skin (D23)                                            |   0.0052 |
| Melanocytic nevi (D22)                                                          |   0.0051 |


| Phenotype 47                                                                |   Weight |
|:----------------------------------------------------------------------------|---------:|
| Dorsalgia (M54)                                                             |   0.0252 |
| Low back pain (M545)                                                        |   0.0148 |
| Other joint disorder, not elsewhere classified (M25)                        |   0.0118 |
| Pain, not elsewhere classified (G89)                                        |   0.0111 |
| Other chronic pain (G8929)                                                  |   0.0097 |
| Other and unspecified soft tissue disorders, not elsewhere classified (M79) |   0.0091 |
| Sleep disorders (G47)                                                       |   0.007  |
| Other anxiety disorders (F41)                                               |   0.0065 |
| HYDROCODONE 5 mg-ACETAMINOPHEN 325 mg tablet                                |   0.0064 |
| Overweight and obesity (E66)                                                |   0.0064 |


| Phenotype 48                                      |   Weight |
|:--------------------------------------------------|---------:|
| amLODIPine (NORVASC) 5 mg tablet                  |   0.078  |
| losartan (COZAAR) 100 mg tablet                   |   0.0114 |
| LOSARTAN 50 mg tablet                             |   0.0075 |
| DOCOSAHEXANOIC ACID/EPA (FISH OIL ORAL)           |   0.0036 |
| TRAMADOL 50 mg tablet                             |   0.0034 |
| ATORVASTATIN 10 mg tablet                         |   0.0033 |
| cholecalciferol (VITAMIN D3) 2,000 unit capsule   |   0.0029 |
| Essential (primary) hypertension (I10)            |   0.0024 |
| ascorbic acid (VITAMIN C) 500 mg Tablet           |   0.0023 |
| omega-3 fatty acids-fish oil 300-1,000 mg Capsule |   0.0022 |


| Phenotype 49                                                                   |   Weight |
|:-------------------------------------------------------------------------------|---------:|
| Chronic kidney disease (CKD) (N18)                                             |   0.0107 |
| Other disorders of kidney and ureter, not elsewhere classified (N28)           |   0.0096 |
| Chronic kidney disease, stage 3 (moderate) (N183)                              |   0.0082 |
| Disorder of kidney and ureter, unspecified (N289)                              |   0.0073 |
| Chronic kidney disease, unspecified (N189)                                     |   0.0043 |
| Other specified disorders of kidney and ureter (N2889)                         |   0.0031 |
| insulin glargine (LANTUS SOLOSTAR) 100 unit/mL injection pen                   |   0.0025 |
| Vitamin D deficiency, unspecified (E559)                                       |   0.0024 |
| Vitamin D deficiency (E55)                                                     |   0.0024 |
| Other disorders involving the immune mechanism, not elsewhere classified (D89) |   0.0021 |
