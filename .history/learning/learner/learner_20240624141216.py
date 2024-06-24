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
import clingo

def unsolvable_states_from_solution(symbols):
    unsolvable_states = set()
    for symbol in symbols:
        if isinstance(symbol, clingo.Symbol) and symbol.name == "unsolvable":
            if len(symbol.arguments) >= 2:
                state_id = int(symbol.arguments[0].number)  
                instance_id = int(symbol.arguments[1].number)  
                unsolvable_states.add((state_id, instance_id))
    return unsolvable_states

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
        instance_datas, domain_data, num_states, num_partitions = compute_instance_datas(
            domain_filepath, instance_filepaths, disable_closed_Q, max_num_states_per_instance, max_time_per_instance, enable_dump_files)
        logging.info(colored("..done", "blue", "on_grey"))

        logging.info(colored("Initializing TupleGraphs...", "blue", "on_grey"))
        compute_tuple_graphs(width, instance_datas, enable_dump_files)
        logging.info(colored("..done", "blue", "on_grey"))
 
    preprocessing_timer.stop()
   
    # Learn sketch
    if encoding_type == EncodingType.EXPLICIT:
        create_experiment_workspace(workspace)
        preprocessing_timer.resume()

        #################################################################################
        sketches = set()
        unsolvable_states = set() 
        for instance_data in instance_datas:
            name = instance_data.instance_filepath.stem
            write_file(f"{name}.dot", instance_data.state_space.to_dot(1))
            print("     ", end="")
            print("id:", instance_data.id, "name:", name, "num_states:", len(instance_data.complete_state_space.get_states()), "num_state_equivalences:", len(instance_data.state_space.get_states()))

            logging.info(colored("Initializing DomainFeatureData...", "blue", "on_grey"))
            domain_data.feature_pool = compute_feature_pool(
                domain_data,
                [instance_data],
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
            compute_per_state_feature_valuations( [instance_data], domain_data)
            logging.info(colored("..done", "blue", "on_grey"))

            logging.info(colored("Constructing StatePairEquivalenceDatas...", "blue", "on_grey"))
            compute_state_pair_equivalences(domain_data,  [instance_data])
            logging.info(colored("..done", "blue", "on_grey"))

            logging.info(colored("Constructing TupleGraphEquivalences...", "blue", "on_grey"))
            compute_tuple_graph_equivalences( [instance_data])
            logging.info(colored("..done", "blue", "on_grey"))

            logging.info(colored("Minimizing TupleGraphEquivalences...", "blue", "on_grey"))
            minimize_tuple_graph_equivalences( [instance_data])
            logging.info(colored("..done", "blue", "on_grey"))
            preprocessing_timer.stop()
            asp_timer.resume()
            for state_idx in instance_data.state_space.get_states().keys():
                instance_data.initial_s_idxs = {state_idx}
                asp_factory = ASPFactory(encoding_type, enable_goal_separating_features, max_num_rules)
                facts = asp_factory.make_facts(domain_data,  [instance_data])
                #for fact in facts:
                #    print(fact)
                logging.info(colored("Grounding Logic Program...", "blue", "on_grey"))
                asp_factory.ground(facts)
                logging.info(colored("..done", "blue", "on_grey"))
                logging.info(colored("Solving Logic Program...", "blue", "on_grey"))
                # Collect all solutions
                solutions = list(asp_factory.solve_all())
                asp_factory.print_statistics()

                # Filter out None solutions
                valid_solutions = [symbols for symbols, status in solutions if symbols is not None]

                if len(valid_solutions) == 0:
                    print(colored("UNSAT problem for selected instances", "red", "on_grey"))
                    exit(ExitCode.UNSOLVABLE)
                elif len(valid_solutions) == 1:
                    print(colored("ASP solving returns a unique solution", "red", "on_grey"))
                else:
                    print(colored(f"ASP solving returns {len(valid_solutions)}", "red", "on_grey"))
                #print("all solutions:", valid_solutions)

                for idx, symbols in enumerate(valid_solutions):
                    # print(symbols)
                    print(f"solution {idx + 1}:")

                    dlplan_policy = ExplicitDlplanPolicyFactory().make_dlplan_policy_from_answer_set(symbols, domain_data)
                    sketch = Sketch(dlplan_policy, width)
                    print(str(sketch.dlplan_policy))
                    sketches.add(sketch)  
                    for state_id in unsolvable_states_from_solution(symbols):
                        unsolvable_states.add(state_id)
    else:
        raise Exception("No implementation for the given encoding type.")

    # Output the result
    with change_dir("output"):
        print_separation_line()
        logging.info(colored("Summary:", "green", "on_grey"))

        learning_statistics = LearningStatistics(
            num_training_instances=len(instance_datas),
            num_selected_training_instances=len(instance_datas),
            num_states_in_selected_training_instances=sum(len(instance_data.state_space.get_states()) for instance_data in instance_datas),
            num_states_in_complete_selected_training_instances=sum(len(instance_data.complete_state_space.get_states()) for instance_data in instance_datas),
            num_features_in_pool=len(domain_data.feature_pool.features))
        learning_statistics.print()
        
        print_separation_line()

        print(f"Preprocessing time: {int(preprocessing_timer.get_elapsed_sec()) + 1} seconds.")
        print(f"ASP time: {int(asp_timer.get_elapsed_sec()) + 1} seconds.")
        print(f"Verification time: {int(verification_timer.get_elapsed_sec()) + 1} seconds.")
        print(f"Total time: {int(total_timer.get_elapsed_sec()) + 1} seconds.")
        print(f"Total memory: {int(memory_usage() / 1024)} GiB.")
        print("Num states in training data before symmetry pruning:", num_states)
        print("Num states in training data after symmetry pruning:", num_partitions)
        print("Total number of sketches:", len(sketches))
        if unsolvable_states:
            print("Unsolvable states found:", unsolvable_states)
            print("Total number of unsolved states:", len(unsolvable_states))
        else:
            print("No unsolvable states found.")
        for idx, sketch in enumerate(sketches):
            with open(f"sketch_{width}_{idx}_{state_idx}.txt", "w") as file:
                file.write(str(sketch.dlplan_policy))
 

