#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --gpus-per-node=1
#SBATCH --mem-per-cpu=16g
#SBATCH --partition=rleap_gpu_24gb
#SBATCH --output=/work/rleap1/ulzhalgas.rakhman/%A.txt

python3 ~/sketch-learner/learning/main.py --domain_filepath ~/sketch-learner/learning/benchmarks/gripper/domain.pddl --problems_directory ~/sketch-learner/learning/benchmarks/gripper/instances --width 1 --workspace workspace
python3 ~/sketch-learner/learning/main.py --domain_filepath ~/sketch-learner/learning/benchmarks/delivery/domain.pddl --problems_directory ~/sketch-learner/learning/benchmarks/delivery/instances --width 1 --workspace workspace
python3 ~/sketch-learner/learning/main.py --domain_filepath ~/sketch-learner/learning/benchmarks/barman/domain.pddl --problems_directory ~/sketch-learner/learning/benchmarks/barman/instances --width 1 --workspace workspace
python3 ~/sketch-learner/learning/main.py --domain_filepath ~/sketch-learner/learning/benchmarks/block_3/domain.pddl --problems_directory ~/sketch-learner/learning/benchmarks/block_3/instances --width 1 --workspace workspace
python3 ~/sketch-learner/learning/main.py --domain_filepath ~/sketch-learner/learning/benchmarks/block_4/domain.pddl --problems_directory ~/sketch-learner/learning/benchmarks/block_4/instances --width 1 --workspace workspace
python3 ~/sketch-learner/learning/main.py --domain_filepath ~/sketch-learner/learning/benchmarks/block_4_clear/domain.pddl --problems_directory ~/sketch-learner/learning/benchmarks/block_4_clear/instances --width 1 --workspace workspace
python3 ~/sketch-learner/learning/main.py --domain_filepath ~/sketch-learner/learning/benchmarks/block_4_on/domain.pddl --problems_directory ~/sketch-learner/learning/benchmarks/block_4_on/instances --width 1 --workspace workspace
python3 ~/sketch-learner/learning/main.py --domain_filepath ~/sketch-learner/learning/benchmarks/childsnack/domain.pddl --problems_directory ~/sketch-learner/learning/benchmarks/childsnack/instances --width 1 --workspace workspace
python3 ~/sketch-learner/learning/main.py --domain_filepath ~/sketch-learner/learning/benchmarks/driverlog/domain.pddl --problems_directory ~/sketch-learner/learning/benchmarks/driverlog/instances --width 1 --workspace workspace
python3 ~/sketch-learner/learning/main.py --domain_filepath ~/sketch-learner/learning/benchmarks/example/domain.pddl --problems_directory ~/sketch-learner/learning/benchmarks/example/instances --width 1 --workspace workspace
python3 ~/sketch-learner/learning/main.py --domain_filepath ~/sketch-learner/learning/benchmarks/example2/domain.pddl --problems_directory ~/sketch-learner/learning/benchmarks/example2/instances --width 1 --workspace workspace
python3 ~/sketch-learner/learning/main.py --domain_filepath ~/sketch-learner/learning/benchmarks/ferry/domain.pddl --problems_directory ~/sketch-learner/learning/benchmarks/ferry/instances --width 1 --workspace workspace
python3 ~/sketch-learner/learning/main.py --domain_filepath ~/sketch-learner/learning/benchmarks/grid/domain.pddl --problems_directory ~/sketch-learner/learning/benchmarks/grid/instances --width 1 --workspace workspace
python3 ~/sketch-learner/learning/main.py --domain_filepath ~/sketch-learner/learning/benchmarks/hiking/domain.pddl --problems_directory ~/sketch-learner/learning/benchmarks/hiking/instances --width 1 --workspace workspace
python3 ~/sketch-learner/learning/main.py --domain_filepath ~/sketch-learner/learning/benchmarks/logistics/domain.pddl --problems_directory ~/sketch-learner/learning/benchmarks/logistics/instances --width 1 --workspace workspace
python3 ~/sketch-learner/learning/main.py --domain_filepath ~/sketch-learner/learning/benchmarks/miconic/domain.pddl --problems_directory ~/sketch-learner/learning/benchmarks/miconic/instances --width 1 --workspace workspace
python3 ~/sketch-learner/learning/main.py --domain_filepath ~/sketch-learner/learning/benchmarks/reward/domain.pddl --problems_directory ~/sketch-learner/learning/benchmarks/reward/instances --width 1 --workspace workspace
python3 ~/sketch-learner/learning/main.py --domain_filepath ~/sketch-learner/learning/benchmarks/rovers/domain.pddl --problems_directory ~/sketch-learner/learning/benchmarks/rovers/instances --width 1 --workspace workspace
python3 ~/sketch-learner/learning/main.py --domain_filepath ~/sketch-learner/learning/benchmarks/satellite/domain.pddl --problems_directory ~/sketch-learner/learning/benchmarks/satellite/instances --width 1 --workspace workspace
python3 ~/sketch-learner/learning/main.py --domain_filepath ~/sketch-learner/learning/benchmarks/spanner/domain.pddl --problems_directory ~/sketch-learner/learning/benchmarks/spanner/instances --width 1 --workspace workspace
python3 ~/sketch-learner/learning/main.py --domain_filepath ~/sketch-learner/learning/benchmarks/visitall/domain.pddl --problems_directory ~/sketch-learner/learning/benchmarks/visitall/instances --width 1 --workspace workspace



