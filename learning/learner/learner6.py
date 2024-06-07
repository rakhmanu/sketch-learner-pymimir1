import logging
from pathlib import Path
from termcolor import colored
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
from typing import Dict, List

def compute_smallest_unsolved_instance(sketch: Sketch, instance_datas: List[InstanceData], enable_goal_separating_features: bool):
    for instance_data in instance_datas:
        print(instance_data.id)
        print(instance_data)
        print(sketch)
        if not sketch.solves(instance_data, enable_goal_separating_features):
            print("instance not solved")
            return instance_data
    return None

def count_sketches_per_state(sketch, instance_datas):
    sketches_per_state = defaultdict(list)  # Initialize as defaultdict of lists
    for instance_data in instance_datas:
        for state_idx in instance_data.state_space.get_states().keys():
            # Append sketch to the list for the corresponding state
            sketches_per_state[state_idx].append(sketch)
    return sketches_per_state


def sum_sketches_per_state(sketch, instance_datas):
    total_sketches_per_state = defaultdict(int)  # Initialize as defaultdict of integers
    for instance_data in instance_datas:
        sketches_per_state = count_sketches_per_state(sketch, [instance_data])
        for state, num_sketches in sketches_per_state.items():
            # Ensure that num_sketches is a list of sketches for each state
            total_sketches_per_state[state] += len(num_sketches)
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
    # Learn sketch
    with change_dir("iterations"):
        i = 0
        with change_dir(str(i), enable=enable_dump_files):
            #selected_instance_idxs = list(range(len(instance_datas)))

            selected_instance_idxs = [0]

            # Iterate over the indices of instance_datas
            #for index in range(len(instance_datas)):
                # Add the index to the list of selected instances
                #selected_instance_idxs.append(index)
            create_experiment_workspace(workspace)
            sketches_per_state = defaultdict(list)
            while True:
                logging.info(colored(f"Iteration: {i}", "red", "on_grey"))

                preprocessing_timer.resume()
                selected_instance_datas: List[InstanceData] = [instance_datas[subproblem_idx] for subproblem_idx in selected_instance_idxs]
                print("Selected instance datas", selected_instance_datas)
                for instance_data in selected_instance_datas:
                    name = instance_data.instance_filepath.stem
                    write_file(f"{name}.dot", instance_data.state_space.to_dot(1))
                    print("     ", end="")
                    print("id:", instance_data.id, "name:", name, "num_states:", len(instance_data.complete_state_space.get_states()), "num_state_equivalences:", len(instance_data.state_space.get_states()))

                logging.info(colored("Initializing DomainFeatureData...", "blue", "on_grey"))
                domain_data.feature_pool = compute_feature_pool(
                    domain_data,
                    selected_instance_datas,
                    disable_feature_generation,
                    concept_complexity_limit,
                    role_complexity_limit,
                    boolean_complexity_limit,
                    count_numerical_complexity_limit,
                    distance_numerical_complexity_limit,
                    feature_limit,
                    additional_booleans,
                    additional_numericals)
                
                if not domain_data.feature_pool.features:
                    raise RuntimeError("Feature pool is empty. Check the feature generation process")
                logging.info(colored("..done", "blue", "on_grey"))

                logging.info(colored("Constructing PerStateFeatureValuations...", "blue", "on_grey"))
                compute_per_state_feature_valuations(selected_instance_datas, domain_data)
                logging.info(colored("..done", "blue", "on_grey"))

                logging.info(colored("Constructing StatePairEquivalenceDatas...", "blue", "on_grey"))
                compute_state_pair_equivalences(domain_data, selected_instance_datas)
                logging.info(colored("..done", "blue", "on_grey"))

                logging.info(colored("Constructing TupleGraphEquivalences...", "blue", "on_grey"))
                compute_tuple_graph_equivalences(selected_instance_datas)
                logging.info(colored("..done", "blue", "on_grey"))

                logging.info(colored("Minimizing TupleGraphEquivalences...", "blue", "on_grey"))
                minimize_tuple_graph_equivalences(selected_instance_datas)
                logging.info(colored("..done", "blue", "on_grey"))
                preprocessing_timer.stop()

                asp_timer.resume()
                if encoding_type == EncodingType.D2:
                    d2_facts = set()
                    symbols = None
                    j = 0
                    while True:
                        asp_factory = ASPFactory(encoding_type, enable_goal_separating_features, max_num_rules)
                        facts = asp_factory.make_facts(domain_data, selected_instance_datas)
                        if j == 0:
                            d2_facts.update(asp_factory.make_initial_d2_facts(selected_instance_datas))
                            print("Number of initial D2 facts:", len(d2_facts))
                        elif j > 0:
                            unsatisfied_d2_facts = asp_factory.make_unsatisfied_d2_facts(domain_data, symbols)
                            d2_facts.update(unsatisfied_d2_facts)
                            print("Number of unsatisfied D2 facts:", len(unsatisfied_d2_facts))
                        print("Number of D2 facts:", len(d2_facts), "of", len(domain_data.domain_state_pair_equivalence.rules) ** 2)
                        facts.extend(list(d2_facts))

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
                            print(colored("UNSAT problem due to current D2-separation constraints for selected instances!", "red", "on_grey"))
                            exit(ExitCode.UNSOLVABLE)
                        elif returncode == ClingoExitCode.UNKNOWN:
                            print(colored("ASP solving throws unknown error!", "red", "on_grey"))
                            exit(ExitCode.UNKNOWN)
                        elif returncode == ClingoExitCode.INTERRUPTED:
                            print(colored("ASP solving interrupted!", "red", "on_grey"))
                            exit(ExitCode.INTERRUPTED)

                        asp_factory.print_statistics()
                        dlplan_policy = D2sepDlplanPolicyFactory().make_dlplan_policy_from_answer_set(symbols, domain_data)
                        sketch = Sketch(dlplan_policy, width)
                        logging.info("Learned the following sketch:")
                        sketch.print()
                        
                        # Store the sketch for each state
                        for state in instance_data.state_space.get_states():
                            sketches_per_state[state].append(Sketch(dlplan_policy, width))
                        
                        if compute_smallest_unsolved_instance(sketch, selected_instance_datas, enable_goal_separating_features) is None:
                            # Stop adding D2-separation constraints if sketch solves all training instances
                            break
                        j += 1
                elif encoding_type == EncodingType.EXPLICIT:
                    asp_factory = ASPFactory(encoding_type, enable_goal_separating_features, max_num_rules)
                    facts = asp_factory.make_facts(domain_data, selected_instance_datas)
                    for fact in facts:
                        print(fact)
                    logging.info(colored("Grounding Logic Program...", "blue", "on_grey"))
                    asp_factory.ground(facts)
                    logging.info(colored("..done", "blue", "on_grey"))
                    logging.info(colored("Solving Logic Program...", "blue", "on_grey"))
                    asp_factory.print_solve_all_output()
                    # Collect all solutions
                    solutions = list(asp_factory.solve_all())
                    
                    # Filter out None solutions
                    valid_solutions = [symbols for symbols, status in solutions if symbols is not None]

                    if not valid_solutions:
                        raise ValueError("No valid solutions found.")

                    for symbols in valid_solutions:
                        dlplan_policy = ExplicitDlplanPolicyFactory().make_dlplan_policy_from_answer_set(symbols, domain_data)
                    asp_factory.print_statistics()

                    dlplan_policy = ExplicitDlplanPolicyFactory().make_dlplan_policy_from_answer_set(symbols, domain_data)
                    sketch = Sketch(dlplan_policy, width)
                    logging.info("Learned the following sketch:")
                    sketch.print()

                    # Store a new sketch for each state
                    for state in instance_data.state_space.get_states():
                        new_sketch = Sketch(dlplan_policy, width)  # Create a new sketch for each state
                        sketches_per_state[state].append(new_sketch)

                else:
                    raise RuntimeError("Unknown encoding type:", encoding_type)

                asp_timer.stop()

                verification_timer.resume()
                logging.info(colored("Verifying learned sketch...", "blue", "on_grey"))

                #assert compute_smallest_unsolved_instance(sketch, selected_instance_datas, enable_goal_separating_features) is None
                smallest_unsolved_instance = compute_smallest_unsolved_instance(sketch, instance_datas, enable_goal_separating_features)
                logging.info(colored("..done", "blue", "on_grey"))
                verification_timer.stop()

                if smallest_unsolved_instance is None:
                    print(colored("Sketch solves all instances!", "red", "on_grey"))
                    break
                else:
                    if smallest_unsolved_instance.id > max(selected_instance_idxs):
                        selected_instance_idxs = [smallest_unsolved_instance.id]
                    else:
                        selected_instance_idxs.append(smallest_unsolved_instance.id)
                    print("Smallest unsolved instance:", smallest_unsolved_instance.id)
                    print("Selected instances:", selected_instance_idxs)


                
                # Check if all instances have been added
                if len(selected_instance_idxs) >= len(instance_datas):
                    print(len(selected_instance_idxs))
                    print(len(instance_datas))
                    print("All instances have been added. Terminating loop.")
                    break  # Terminate the loop if all instances have been added

                i += 1
                
    total_timer.stop()
    sketches_per_state = count_sketches_per_state(sketch, instance_datas)
    total_sketches_per_state = sum_sketches_per_state(sketch, instance_datas)
   
    for feature in domain_data.feature_pool.features:
        logging.info(f"Feature: {feature}")

    for instance_data in instance_datas:
        logging.info(f"Instance {instance_data.id} states:") 
        for state_id, state in instance_data.state_space.get_states().items():
            logging.info(f"state {state_id}: {state}")   
    # Output sketches per state
    print("Sketches per state:")
    for state, state_sketches in sketches_per_state.items():
        print(f"State {state}:")
        for s in state_sketches:
            s.print()
    print_separation_line()

    #empty_sketches = asp_factory.has_empty_sketches(symbols)
    #if empty_sketches:
    #    print("There are empty sketches")
    #else:
    #    print("No empty sketches found")

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
            num_selected_training_instances=len(selected_instance_datas),
            num_states_in_selected_training_instances=sum(len(instance_data.state_space.get_states()) for instance_data in selected_instance_datas),
            num_states_in_complete_selected_training_instances=sum(len(instance_data.complete_state_space.get_states()) for instance_data in selected_instance_datas),
            num_features_in_pool=len(domain_data.feature_pool.features))
        learning_statistics.print()
        print_separation_line()

        print("Resulting sketch:")
        sketch.print()
        print_separation_line()

        print("Resulting minimized sketch:")
        sketch_minimized = Sketch(PolicyMinimizer().minimize(sketch.dlplan_policy, domain_data.policy_builder), sketch.width)
        sketch_minimized.print()

        # Print all sketches per state
        for state, num_sketches in sketches_per_state.items():
            with open(f"sketch_1_state{state}.txt", "w") as file:
                file.write(f"Sketches for State {state}:\n")
                for idx, sketch in enumerate(num_sketches, start=1):
                    file.write(f"Sketch {idx}:\n")
                    file.write(str(sketch.dlplan_policy))
                    file.write("\n\n")


        print_separation_line()

        create_experiment_workspace(workspace / "output")
        write_file(f"sketch_{width}.txt", str(sketch.dlplan_policy))
        write_file(f"sketch_minimized_{width}.txt", str(sketch_minimized.dlplan_policy))
        # Count sketches per state
        #print("Sketches per state:", sketches_per_state)
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