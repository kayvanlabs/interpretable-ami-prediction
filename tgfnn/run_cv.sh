#!/bin/bash
#SBATCH --mail-user=
#SBATCH --mail-type=FAIL,END
#SBATCH --job-name=ami_old_tgfnn_cv
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=15GB
#SBATCH --time=8:00:00
#SBATCH --account=
#SBATCH --partition=standard

module load python3.9
source env/bin/activate
python -W ignore main_cv.py $1 $2 $3 $4 $5