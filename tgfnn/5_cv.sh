#!/bin/bash
#SBATCH --mail-user=
#SBATCH --mail-type=FAIL,END
#SBATCH --job-name=6_cv_old_tgfnn
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=5GB
#SBATCH --time=6:00:00
#SBATCH --account=
#SBATCH --partition=standard

module load python3.9
source env/bin/activate
python 5_cv.py