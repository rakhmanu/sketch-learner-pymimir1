#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --gpus-per-node=1
#SBATCH --mem-per-cpu=64g
#SBATCH --partition=rleap_gpu_24gb
#SBATCH --output=/work/rleap1/ulzhalgas.rakhman/%A.txt



python3 ~/sketch-learner/learning/main.py --domain_filepath ~/sketch-learner/learning/benchmarks/blocks_4_on/domain.pddl --problems_directory ~/sketch-learner/learning/benchmarks/blocks_4_on/instances --width 1 --workspace workspace
