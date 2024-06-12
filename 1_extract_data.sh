#!/bin/bash
#SBATCH --mail-user=
#SBATCH --mail-type=START,FAIL,END
#SBATCH --job-name=1_extract_data
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=60GB
#SBATCH --time=6:00:00
#SBATCH --account=
#SBATCH --partition=standard

module load python3.9
source env/bin/activate
python 1_extract_data.py