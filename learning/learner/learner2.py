import logging

from pathlib import Path
from termcolor import colored
from typing import List

from dlplan.policy import PolicyMinimizer

from .exit_codes import ExitCode
from .src.asp.encoding_type import EncodingType
from .src.asp.asp_factory import ASPFactory
from .src.asp.returncodes import ClingoExitCode
from .src.util.command import create_experiment_workspace, change_working_directory, write_file, change_dir
from .src.util.performance import memory_usage
from .src.util.timer import Timer
from .src.util.console import add_console_handler, print_separation_line
from .src.instance_data.instance_data import InstanceData
from .src.instance_data.instance_data_utils import compute_instance_datas
from .src.instance_data.tuple_graph_utils import compute_tuple_graphs
from .src.iteration_data.learning_statistics import LearningStatistics
from .src.iteration_data.feature_pool_utils import compute_feature_pool
from .src.iteration_data.feature_valuations_utils import compute_per_state_feature_valuations
from .src.iteration_data.dlplan_policy_factory import D2sepDlplanPolicyFactory, ExplicitDlplanPolicyFactory
from .src.iteration_data.sketch import Sketch
from .src.iteration_data.state_pair_equivalence_utils import compute_state_pair_equivalences
from .src.iteration_data.tuple_graph_equivalence_utils import compute_tuple_graph_equivalences, minimize_tuple_graph_equivalences
from collections import defaultdict

def compute_smallest_unsolved_instance(sketch: Sketch,
                                       instance_datas: List[InstanceData],
                                       enable_goal_separating_features: bool):
    for instance_data in instance_datas:
        if not sketch.solves(instance_data, enable_goal_separating_features):
            return instance_data
    return None

from collections import defaultdict

def count_sketches_per_state(sketch, instance_datas):
    sketches_per_state = defaultdict(int)
    for instance_data in instance_datas:
        for s_idx in instance_data.state_space.get_states().keys():
            sketches_per_state[s_idx] += 1
    return sketches_per_state

def sum_sketches_per_state(sketch, instance_datas):
    total_sketches_per_state = defaultdict(int)
    for instance_data in instance_datas:
        sketches_per_state = count_sketches_per_state(sketch, [instance_data])
        for state, num_sketches in sketches_per_state.items():
            total_sketches_per_state[state] += num_sketches
    return total_sketches_per_state

def learn_sketch_for_problem_class(
    domain_filepath: Path,
    problems_directory: Path,
    workspace: Path,
    width: int,
    disable_closed_Q: bool = True,
    max_num_states_per_instance: int = 2000,
    max_time_per_instance: int = 10,
    encoding_type: EncodingType = EncodingType.EXPLICIT,
    max_num_rules: int = 1,
    enable_goal_separating_features: bool = True,
    disable_feature_generation: bool = True,
    concept_complexity_limit: int = 9,
    role_complexity_limit: int = 9,
    boolean_complexity_limit: int = 9,
    count_numerical_complexity_limit: int = 9,
    distance_numerical_complexity_limit: int = 9,
    feature_limit: int = 1000000,
    additional_booleans: List[str] = None,
    additional_numericals: List[str] = None,
    enable_dump_files: bool = False,
):
    # Setup arguments and workspace
    if additional_booleans is None:
        additional_booleans = []
    if additional_numericals is None:
        additional_numericals = []
    instance_filepaths = list(problems_directory.iterdir())
    add_console_handler(logging.getLogger(), logging.INFO)
    create_experiment_workspace(workspace)
    change_working_directory(workspace)

    # Keep track of time
    total_timer = Timer()
    preprocessing_timer = Timer()
    asp_timer = Timer(stopped=True)
    verification_timer = Timer(stopped=True)

    # Generate data
    with change_dir("input"):
        logging.info(colored("Constructing InstanceDatas...", "blue", "on_grey"))
        instance_datas, domain_data, num_states, num_partitions = compute_instance_datas(domain_filepath, instance_filepaths, disable_closed_Q, max_num_states_per_instance, max_time_per_instance, enable_dump_files)
        logging.info(colored("..done", "blue", "on_grey"))

        logging.info(colored("Initializing TupleGraphs...", "blue", "on_grey"))
        compute_tuple_graphs(width, instance_datas, enable_dump_files)
        logging.info(colored("..done", "blue", "on_grey"))

        total_states = 0

        # Print all states generated and sum of the states
        for instance_data in instance_datas:
            instance_states = len(instance_data.state_space.get_states())
            total_states += instance_states
            # Print individual states here if needed
            for state_id, state in instance_data.state_space.get_states().items():
                print(f"State {state_id}: {state}")
                
        print(f"Total states: {total_states}")


    preprocessing_timer.stop()

    max_iterations = 50
    # Learn sketch
    with change_dir("iterations"):
        for iteration in range(max_iterations):
            logging.info(colored(f"Iteration: {iteration}", "red", "on_grey"))
            preprocessing_timer.resume()
            create_experiment_workspace(workspace)
            name = instance_data.instance_filepath.stem
            write_file(f"{name}.dot", instance_data.state_space.to_dot(1))
            print("     ", end="")
            print("id:", instance_data.id,
                    "name:", name,
                    "num_states:", len(instance_data.complete_state_space.get_states()),
                    "num_state_equivalences:", len(instance_data.state_space.get_states()))

            logging.info(colored("Initializing DomainFeatureData...", "blue", "on_grey"))
            domain_data.feature_pool = compute_feature_pool(
                domain_data,
                instance_datas,
                disable_feature_generation,
                concept_complexity_limit,
                role_complexity_limit,
                boolean_complexity_limit,
                count_numerical_complexity_limit,
                distance_numerical_complexity_limit,
                feature_limit,
                additional_booleans,
                additional_numericals)
            logging.info(colored("..done", "blue", "on_grey"))

            logging.info(colored("Constructing PerStateFeatureValuations...", "blue", "on_grey"))
            compute_per_state_feature_valuations(instance_datas, domain_data)
            logging.info(colored("..done", "blue", "on_grey"))

            logging.info(colored("Constructing StatePairEquivalenceDatas...", "blue", "on_grey"))
            compute_state_pair_equivalences(domain_data, instance_datas)
            logging.info(colored("..done", "blue", "on_grey"))

            logging.info(colored("Constructing TupleGraphEquivalences...", "blue", "on_grey"))
            compute_tuple_graph_equivalences(instance_datas)
            logging.info(colored("..done", "blue", "on_grey"))

            logging.info(colored("Minimizing TupleGraphEquivalences...", "blue", "on_grey"))
            minimize_tuple_graph_equivalences(instance_datas)
            logging.info(colored("..done", "blue", "on_grey"))
            preprocessing_timer.stop()

            asp_timer.resume()
            
               
            asp_factory = ASPFactory(encoding_type, enable_goal_separating_features, max_num_rules)
            facts = asp_factory.make_facts(domain_data, instance_datas)

            logging.info(colored("Grounding Logic Program...", "blue", "on_grey"))
            asp_factory.ground(facts)
            logging.info(colored("..done", "blue", "on_grey"))
            logging.info(colored("Solving Logic Program...", "blue", "on_grey"))
            asp_factory.print_solve_all_output()
            symbols, returncode = asp_factory.solve()
            print("Symbols:", symbols)
            print("Return code:", returncode)
            logging.info(colored("..done", "blue", "on_grey"))

            if returncode == ClingoExitCode.UNSATISFIABLE:
                print("UNSAT")
                return None, None, None
                    
            asp_factory.print_statistics()
                    
            dlplan_policy = ExplicitDlplanPolicyFactory().make_dlplan_policy_from_answer_set(symbols, domain_data)
            sketch = Sketch(dlplan_policy, width)
            logging.info("Learned the following sketch:")
            sketch.print()
        

            asp_timer.stop()

            verification_timer.resume()
            logging.info(colored("Verifying learned sketch...", "blue", "on_grey"))
            #assert compute_smallest_unsolved_instance(sketch, selected_instance_datas, enable_goal_separating_features) is None
            smallest_unsolved_instance = compute_smallest_unsolved_instance(sketch, instance_datas, enable_goal_separating_features)
            logging.info(colored("..done", "blue", "on_grey"))
            verification_timer.stop()

            if not smallest_unsolved_instance:
                print(colored("Sketch solves all instances!", "red", "on_grey"))
                break
        
            

                
             # Check for new instances being added
             #   new_instance_idx = smallest_unsolved_instance.id
             #   if new_instance_idx not in selected_instance_idxs:
             #       selected_instance_idxs.append(new_instance_idx)
             #       selected_instance_idxs = sorted(set(selected_instance_idxs))  
             #   else:
             #       print("No new instances to add. Terminating to avoid infinite loop.")
             #       break  # Terminate if no new instances are added
             #   i += 1  
             #   if len(selected_instance_idxs) == len(instance_datas):
             #       print("All instances are selected but the sketch is not solving all. Terminating to avoid infinite loop.")
             #       break  # Terminate if all instances are selected but the problem persists
    total_timer.stop()
    sketches_per_state = count_sketches_per_state(sketch, instance_datas)
    total_sketches_per_state = sum_sketches_per_state(sketch, instance_datas)

    # Print all sketches
    print("Sketches per state:")
    for state, total_sketches in total_sketches_per_state.items():
        print(f"State {state}: {total_sketches} sketches")
        
    for state, total_sketches in total_sketches_per_state.items():
        print(f"State {state}:")
        for _ in range(total_sketches):
            sketch.print()
    
    print("Total sketches per state:")
    for state, total_sketches in total_sketches_per_state.items():
        print(f"State {state}: {total_sketches} sketches")
    total_sketches = sum(total_sketches for total_sketches in total_sketches_per_state.values())
    print("Total sketches:", total_sketches)
    print(total_sketches_per_state.values())
    # Output the result
    with change_dir("output"):
        print_separation_line()
        logging.info(colored("Summary:", "green", "on_grey"))

        learning_statistics = LearningStatistics(
            num_training_instances=len(instance_datas),
            num_states_in_selected_training_instances=sum(len(instance_data.state_space.get_states()) for instance_data in instance_datas),
            num_states_in_complete_selected_training_instances=sum(len(instance_data.complete_state_space.get_states()) for instance_data in instance_datas),
            num_features_in_pool=len(domain_data.feature_pool.features))
        learning_statistics.print()
        print_separation_line()

        print("Resulting sketch:")
        sketch.print()
        print_separation_line()

        print("Resulting minimized sketch:")
        sketch_minimized = Sketch(PolicyMinimizer().minimize(sketch.dlplan_policy, domain_data.policy_builder), sketch.width)
        sketch_minimized.print()
        print_separation_line()

        create_experiment_workspace(workspace / "output")
        write_file(f"sketch_{width}.txt", str(sketch.dlplan_policy))
        write_file(f"sketch_minimized_{width}.txt", str(sketch_minimized.dlplan_policy))
        # Count sketches per state
        print("Sketches per state:", sketches_per_state)
        print_separation_line()
        print(f"Preprocessing time: {int(preprocessing_timer.get_elapsed_sec()) + 1} seconds.")
        print(f"ASP time: {int(asp_timer.get_elapsed_sec()) + 1} seconds.")
        print(f"Verification time: {int(verification_timer.get_elapsed_sec()) + 1} seconds.")
        print(f"Total time: {int(total_timer.get_elapsed_sec()) + 1} seconds.")
        print(f"Total memory: {int(memory_usage() / 1024)} GiB.")
        print("Num states in training data before symmetry pruning:", num_states)
        print("Num states in training data after symmetry pruning:", num_partitions)
        print_separation_line()

        print(flush=True)