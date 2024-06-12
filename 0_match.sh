#!/bin/bash
#SBATCH --mail-user=
#SBATCH --mail-type=BEGIN,FAIL,END
#SBATCH --job-name=0_match
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=50GB
#SBATCH --time=1:00:00
#SBATCH --account=
#SBATCH --partition=standard

module load python3.9
source env/bin/activate
python 0_match.py