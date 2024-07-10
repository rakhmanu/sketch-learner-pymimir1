import logging

from pathlib import Path
from termcolor import colored
from typing import List, MutableSet, Dict
import clingo
import pymimir as mm
from dlplan.policy import PolicyMinimizer
from collections import defaultdict
from .src.exit_codes import ExitCode
from .src.iteration import EncodingType, ASPFactory, ClingoExitCode, IterationData, LearningStatistics, Sketch, D2sepDlplanPolicyFactory, ExplicitDlplanPolicyFactory, compute_feature_pool, compute_per_state_feature_valuations, compute_state_pair_equivalences, compute_tuple_graph_equivalences, minimize_tuple_graph_equivalences
from .src.util import Timer, create_experiment_workspace, change_working_directory, write_file, change_dir, memory_usage, add_console_handler, print_separation_line
from .src.preprocessing import InstanceData, PreprocessingData, StateFinder, compute_instance_datas, compute_tuple_graphs


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
    # Initialize variables and setup
    if additional_booleans is None:
        additional_booleans = []
    if additional_numericals is None:
        additional_numericals = []
    instance_filepaths = list(problems_directory.iterdir())
    add_console_handler(logging.getLogger(), logging.INFO)
    create_experiment_workspace(workspace)
    change_working_directory(workspace)

    total_timer = Timer()
    preprocessing_timer = Timer()
    asp_timer = Timer(stopped=True)
    verification_timer = Timer(stopped=True)
    iteration_data = IterationData()

    # Generate data
    with change_dir("input"):
        logging.info(colored("Constructing InstanceDatas...", "blue", "on_grey"))
        domain_data, instance_datas, gfa_states_by_id = compute_instance_datas(domain_filepath, instance_filepaths, disable_closed_Q, max_num_states_per_instance, max_time_per_instance, enable_dump_files)
        logging.info(colored("..done", "blue", "on_grey"))
        if instance_datas is None:
            raise Exception("Failed to create InstanceDatas.")

        state_finder = StateFinder(domain_data, instance_datas)

        logging.info(colored("Initializing TupleGraphs...", "blue", "on_grey"))
        gfa_state_id_to_tuple_graph: Dict[int, mm.TupleGraph] = compute_tuple_graphs(domain_data, instance_datas, state_finder, width, enable_dump_files)
        logging.info(colored("..done", "blue", "on_grey"))

    preprocessing_data = PreprocessingData(domain_data, instance_datas, state_finder, gfa_states_by_id, gfa_state_id_to_tuple_graph)
    preprocessing_timer.stop()

    # Learn sketch
    if encoding_type == EncodingType.EXPLICIT:
        create_experiment_workspace(workspace)
        preprocessing_timer.resume()
        sketches = set()
        unsolvable_states = set()
        sketch_count_per_state = {}
        sketches_per_state = defaultdict(set)
        total_sketch_count = 0
        
        # Ensure instance_datas is not empty before iterating
        if preprocessing_data.instance_datas:
            for instance_data in preprocessing_data.instance_datas:
                iteration_data = IterationData()
                iteration_data.instance_datas = [instance_data]
                write_file(f"{instance_data.idx}.dot", instance_data.dlplan_ss.to_dot(1))
                print("     ", end="")
                print("id:", instance_data.idx,
                      "problem_filepath:", instance_data.mimir_ss.get_pddl_parser().get_problem_filepath(),
                      "num_states:", instance_data.mimir_ss.get_num_states(),
                      "num_state_equivalences:", instance_data.gfa.get_num_states())

                logging.info(colored("Initialize global faithful abstract states...", "blue", "on_grey"))
                gfa_states: MutableSet[mm.GlobalFaithfulAbstractState] = set()
                for instance_data in iteration_data.instance_datas:
                    gfa_states.update(instance_data.gfa.get_states())
                iteration_data.gfa_states = list(gfa_states)
                logging.info(colored("..done", "blue", "on_grey"))

                logging.info(colored("Initializing DomainFeatureData...", "blue", "on_grey"))
                iteration_data.feature_pool = compute_feature_pool(
                    preprocessing_data,
                    iteration_data,
                    gfa_state_id_to_tuple_graph,
                    state_finder,
                    disable_feature_generation,
                    concept_complexity_limit,
                    role_complexity_limit,
                    boolean_complexity_limit,
                    count_numerical_complexity_limit,
                    distance_numerical_complexity_limit,
                    feature_limit,
                    additional_booleans,
                    additional_numericals
                )
                
                logging.info(colored("Constructing PerStateFeatureValuations...", "blue", "on_grey"))
                iteration_data.gfa_state_id_to_feature_evaluations = compute_per_state_feature_valuations(preprocessing_data, iteration_data)
                logging.info(colored("..done", "blue", "on_grey"))

                logging.info(colored("Constructing StatePairEquivalenceDatas...", "blue", "on_grey"))
                iteration_data.state_pair_equivalences, iteration_data.gfa_state_id_to_state_pair_equivalence = compute_state_pair_equivalences(preprocessing_data, iteration_data)
                logging.info(colored("..done", "blue", "on_grey"))

                logging.info(colored("Constructing TupleGraphEquivalences...", "blue", "on_grey"))
                iteration_data.gfa_state_id_to_tuple_graph_equivalence = compute_tuple_graph_equivalences(preprocessing_data, iteration_data)
                logging.info(colored("..done", "blue", "on_grey"))

                logging.info(colored("Minimizing TupleGraphEquivalences...", "blue", "on_grey"))
                minimize_tuple_graph_equivalences(preprocessing_data, iteration_data)
                logging.info(colored("..done", "blue", "on_grey"))
                preprocessing_timer.stop()
                asp_timer.resume()

                for gfa_state in iteration_data.gfa_states:
                    gfa_state_idx = preprocessing_data.state_finder.get_gfa_state_idx_from_gfa_state(instance_data.idx, gfa_state)
                    instance_data.initial_gfa_state_idxs = [gfa_state_idx]
                    asp_factory = ASPFactory(encoding_type, enable_goal_separating_features, max_num_rules)
                    facts = asp_factory.make_facts(preprocessing_data, iteration_data)
                    logging.info(colored("Grounding Logic Program...", "blue", "on_grey"))
                    asp_factory.ground(facts)
                    logging.info(colored("..done", "blue", "on_grey"))
                    logging.info(colored("Solving Logic Program...", "blue", "on_grey"))
                    solutions = [asp_factory.solve()]
                    #solutions = list(asp_factory.solve_all())
                    asp_factory.print_statistics()

                    valid_solutions = [symbols for symbols, status in solutions if symbols is not None]
                    if len(valid_solutions) == 0:
                        print(colored("UNSAT problem for selected instances", "red", "on_grey"))
                        exit(ExitCode.UNSOLVABLE)
                    elif len(valid_solutions) == 1:
                        print(colored("ASP solving returns a unique solution", "red", "on_grey"))
                    else:
                        print(colored(f"ASP solving returns {len(valid_solutions)}", "red", "on_grey"))

                    for idx, symbols in enumerate(valid_solutions):
                        print(f"Solution {idx + 1}:")
                        dlplan_policy = ExplicitDlplanPolicyFactory().make_dlplan_policy_from_answer_set(symbols, preprocessing_data, iteration_data)
                        sketch = Sketch(dlplan_policy, width)
                        for gfa_state in gfa_states:
                            state_idx = preprocessing_data.state_finder.get_gfa_state_idx_from_gfa_state(instance_data.idx, gfa_state)
                            if state_idx not in sketches_per_state:
                                sketches_per_state[state_idx] = set()
                            if state_idx in sketch_count_per_state:
                                sketch_count_per_state[state_idx] += 1
                            else:
                                sketch_count_per_state[state_idx] = 1
                            if sketch not in sketches_per_state[gfa_state_idx] and str(sketch.dlplan_policy):
                                if len(valid_solutions) > 1:
                                    sketches_per_state[gfa_state_idx].add(sketch)
                                    sketches.add(sketch)
                                    total_sketch_count += 1
                                    for idx, sketch in enumerate(sketches):
                                        print(f"Sketch {idx + 1}:")
                                        print(str(sketch.dlplan_policy))
                                        print()
                                    for state_id in unsolvable_states_from_solution(symbols):
                                        unsolvable_states.add(state_id)

        else:
            print("No instance datas found in preprocessing_data. Skipping feature pool printing.")

    else:
        raise Exception("No implementation for the given encoding type.")

    # Output the result
    with change_dir("output"):
        print_separation_line()
        logging.info(colored("Summary:", "green", "on_grey"))

        learning_statistics = LearningStatistics(
            num_training_instances=len(instance_datas),
            num_selected_training_instances=len(iteration_data.instance_datas),
            num_states_in_selected_training_instances=sum(instance_data.gfa.get_num_states() for instance_data in iteration_data.instance_datas),
            num_states_in_complete_selected_training_instances=sum(instance_data.mimir_ss.get_num_states() for instance_data in iteration_data.instance_datas),
            num_features_in_pool=len(iteration_data.feature_pool))

        learning_statistics.print()
        print_separation_line()

        print(f"Preprocessing time: {int(preprocessing_timer.get_elapsed_sec()) + 1} seconds.")
        print(f"ASP time: {int(asp_timer.get_elapsed_sec()) + 1} seconds.")
        print(f"Verification time: {int(verification_timer.get_elapsed_sec()) + 1} seconds.")
        print(f"Total time: {int(total_timer.get_elapsed_sec()) + 1} seconds.")
        print(f"Total memory: {int(memory_usage() / 1024)} GiB.")
        print(f"Total sketches across all instances: {total_sketch_count}")

        for idx, sketch in enumerate(sketches):
            file_name = f"sketch_{width}_{idx}.txt"
            with open(file_name, "w") as file:
                file.write(str(sketch.dlplan_policy))
                #print(f"Successfully wrote {file_name}")

        print(f"Number of states in training data:", len(preprocessing_data.gfa_states_by_id))
        if unsolvable_states:
            print("Total num of unsolved states:", len(unsolvable_states))
            for state_id in unsolvable_states:
                print(f"Unsolvable state: {state_id}")

        sketches = {sketch for sketches in sketches_per_state.values() for sketch in sketches}

        for state_idx in sketches_per_state:
            for idx, sketch in enumerate(sketches_per_state[state_idx]):
                try:
                    file_name = f"sketch_{width}_{idx}_{state_idx}.txt"
                    with open(file_name, "w") as file:
                        file.write(str(sketch.dlplan_policy))
                    #print(f"Successfully wrote {file_name}")
                except Exception as e:
                    print(f"Failed to write sketch for state_idx {state_idx} and sketch index {idx}: {e}")

        print("Feature Pool: ")
        for f in iteration_data.feature_pool:
            print(str(f.dlplan_feature))
        sorted_features = sorted(iteration_data.feature_pool, key=lambda x: str(x.dlplan_feature))
        for feature in sorted_features:
            print(feature)

