#!/bin/bash
#SBATCH --mail-user=
#SBATCH --mail-type=BEGIN,FAIL,END
#SBATCH --job-name=phenotype_lv_hals
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=5GB
#SBATCH --time=1:30:00
#SBATCH --account=
#SBATCH --partition=standard

module load python3.9
source env/bin/activate
python phenotype_hals_notsparse.py -i $1 -r $2 -e $3 --labs_vitals