#!/bin/bash
#SBATCH --mail-user=
#SBATCH --mail-type=BEGIN,FAIL,END
#SBATCH --job-name=pick_rank_lv
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=3GB
#SBATCH --time=12:00:00
#SBATCH --account=
#SBATCH --partition=standard

module load python3.9
source env/bin/activate
python pick_rank.py -i $1 -a $2 -z $3 -s $4 -n $5 --lv