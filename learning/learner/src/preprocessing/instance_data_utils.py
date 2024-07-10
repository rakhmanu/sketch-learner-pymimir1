import logging
from typing import List, Tuple, Dict, Union
from pathlib import Path
from collections import defaultdict

import pymimir as mm
import dlplan.core as dlplan_core
import dlplan.state_space as dlplan_statespace

from .instance_data import InstanceData
from .domain_data import DomainData
from .domain_data_utils import compute_domain_data

from ..util import change_dir, write_file

def create_vocabulary_info(domain: mm.Domain) -> dlplan_core.VocabularyInfo:
    vocabulary_info = dlplan_core.VocabularyInfo()
    for predicate in sorted(domain.get_static_predicates(), key=lambda x: x.get_name()):
    #for predicate in domain.get_static_predicates():
        print("Static predicate")
        print(f"Predicate name: {predicate.get_name()}")
        if predicate.get_name() != "=":
            vocabulary_info.add_predicate(predicate.get_name(), len(predicate.get_parameters()), True)
            vocabulary_info.add_predicate(predicate.get_name() + "_g", len(predicate.get_parameters()), True)
    for predicate in sorted(domain.get_fluent_predicates(), key=lambda x: x.get_name()):
    #for predicate in domain.get_static_predicates():
        print("Fluent predicate")
        print(f"Predicate name: {predicate.get_name()}")
        vocabulary_info.add_predicate(predicate.get_name(), len(predicate.get_parameters()), False)
        vocabulary_info.add_predicate(predicate.get_name() + "_g", len(predicate.get_parameters()), False)
    for predicate in sorted(domain.get_derived_predicates(), key=lambda x: x.get_name()):
    #for predicate in domain.get_derived_predicates():
        print("Derived predicate")
        print(f"Predicate name: {predicate.get_name()}")
        vocabulary_info.add_predicate(predicate.get_name(), len(predicate.get_parameters()), False)
        vocabulary_info.add_predicate(predicate.get_name() + "_g", len(predicate.get_parameters()), False)
    for obj in domain.get_constants():
        vocabulary_info.add_constant(obj.get_name())
    #assert False
    return vocabulary_info

def create_instance_info(
        vocabulary_info: dlplan_core.VocabularyInfo,
        instance_id: int,
        mimir_state_space: mm.StateSpace
) -> Tuple[dlplan_core.InstanceInfo, Dict[Union[mm.FluentGroundAtom, mm.DerivedGroundAtom], dlplan_core.Atom]]:
    instance_info = dlplan_core.InstanceInfo(instance_id, vocabulary_info)
    pddl_factories = mimir_state_space.get_aag().get_pddl_factories()
    problem = mimir_state_space.get_aag().get_problem()
    # Static initial literals
    for literal in problem.get_static_initial_literals():
        if literal.get_atom().get_predicate().get_name() != "=":
            assert not literal.is_negated()
            instance_info.add_static_atom(literal.get_atom().get_predicate().get_name(), [obj.get_name() for obj in literal.get_atom().get_objects()])
    # Reached atoms
    atom_to_dlplan_atom = dict()
    for atom in pddl_factories.get_fluent_ground_atoms_from_ids(mimir_state_space.get_ssg().get_reached_fluent_ground_atoms()):
        atom_to_dlplan_atom[atom] = instance_info.add_atom(atom.get_predicate().get_name(), [obj.get_name() for obj in atom.get_objects()])
    for atom in pddl_factories.get_derived_ground_atoms_from_ids(mimir_state_space.get_ssg().get_reached_derived_ground_atoms()):
        atom_to_dlplan_atom[atom] = instance_info.add_atom(atom.get_predicate().get_name(), [obj.get_name() for obj in atom.get_objects()])
    # Goal literals
    for literal in problem.get_static_goal_condition():
        assert not literal.is_negated()
        instance_info.add_static_atom(literal.get_atom().get_predicate().get_name() + "_g", [obj.get_name() for obj in literal.get_atom().get_objects()])
    for literal in problem.get_fluent_goal_condition():
        assert not literal.is_negated()
        instance_info.add_static_atom(literal.get_atom().get_predicate().get_name() + "_g", [obj.get_name() for obj in literal.get_atom().get_objects()])
    for literal in problem.get_derived_goal_condition():
        assert not literal.is_negated()
        instance_info.add_static_atom(literal.get_atom().get_predicate().get_name() + "_g", [obj.get_name() for obj in literal.get_atom().get_objects()])
    return instance_info, atom_to_dlplan_atom


def create_dlplan_statespace(
        instance_info: dlplan_core.InstanceInfo,
        mimir_state_space: mm.StateSpace,
        atom_to_dlplan_atom: Dict[Union[mm.FluentGroundAtom, mm.DerivedGroundAtom], dlplan_core.Atom]
) -> dlplan_statespace.StateSpace:
    pddl_factories = mimir_state_space.get_aag().get_pddl_factories()
    dlplan_states: Dict[int, dlplan_core.State] = dict()
    forward_successors = defaultdict(set)
    for ss_state_idx, ss_state in enumerate(mimir_state_space.get_states()):
        dlplan_state_atoms = []
        for atom in pddl_factories.get_fluent_ground_atoms_from_ids(ss_state.get_fluent_atoms()):
            dlplan_state_atoms.append(atom_to_dlplan_atom[atom])
        for atom in pddl_factories.get_derived_ground_atoms_from_ids(ss_state.get_derived_atoms()):
            dlplan_state_atoms.append(atom_to_dlplan_atom[atom])
        dlplan_states[ss_state_idx] = dlplan_core.State(ss_state_idx, instance_info, dlplan_state_atoms)
        for transition in mimir_state_space.get_forward_transitions()[ss_state_idx]:
            forward_successors[ss_state_idx].add(transition.get_successor_state())
    dlplan_state_space = dlplan_statespace.StateSpace(instance_info, dlplan_states, mimir_state_space.get_initial_state(), forward_successors, mimir_state_space.get_goal_states())
    return dlplan_state_space

def compute_instance_datas(domain_filepath: Path,
                           instance_filepaths: List[Path],
                           disable_closed_Q: bool,
                           max_num_states_per_instance: int,
                           max_time_per_instance: int,
                           enable_dump_files: bool) -> Tuple[List[InstanceData], DomainData]:
    instance_datas: List[InstanceData] = []

    with change_dir("state_spaces", enable=enable_dump_files):
        # 1. Create mimir StateSpace and GlobalFaithfulAbstraction
        logging.info("Constructing GlobalFaithfulAbstractions...")
        logging.debug(f"domain_filepath: {domain_filepath}, type: {type(domain_filepath)}")
        logging.debug(f"instance_filepaths: {instance_filepaths}, type: {type(instance_filepaths)}")
        logging.debug(f"max_num_states_per_instance: {max_num_states_per_instance}, type: {type(max_num_states_per_instance)}")
        logging.debug(f"max_time_per_instance: {max_time_per_instance}, type: {type(max_time_per_instance)}")

        abstractions = mm.GlobalFaithfulAbstraction.create(str(domain_filepath), [str(p) for p in instance_filepaths], False, True, True, True, max_num_states_per_instance, max_time_per_instance)
        logging.info("...done")
        if len(abstractions) == 0:
            return None * 3

        logging.info("Constructing StateSpaces...")
        memories = []
        fas = abstractions[0].get_abstractions()
        for gfa in fas:
            memories.append([gfa.get_pddl_parser(), gfa.get_aag(), gfa.get_ssg()])
        # We must not sort state spaces to match the sorting of gfas
        state_spaces = mm.StateSpace.create(memories, True, True, sort_ascending_by_num_states=False)
        logging.info("...done")

        # 2. Create DomainData
        vocabulary_info = create_vocabulary_info(state_spaces[0].get_aag().get_problem().get_domain())
        domain_data = compute_domain_data(str(domain_filepath), vocabulary_info)

        # 3. Create InstanceData
        instance_idx = 0
        for mimir_ss, gfa in zip(state_spaces, abstractions):
            # Ensure that unsolvable instances were removed
            assert(mimir_ss.get_num_goal_states())

            # 3.1. Create dlplan instance info
            instance_info, atom_to_dlplan_atom = create_instance_info(vocabulary_info, instance_idx, mimir_ss)

            # 3.2 Create dlplan state space
            dlplan_ss = create_dlplan_statespace(instance_info, mimir_ss, atom_to_dlplan_atom)

            # 3.3 Create mapping from concrete states to global faithful abstract states
            ss_state_idx_to_gfa_state_idx = dict()
            for ss_state_idx, sp_state in enumerate(mimir_ss.get_states()):
                ss_state_idx_to_gfa_state_idx[ss_state_idx] = gfa.get_abstract_state_index(sp_state)

            if enable_dump_files:
                write_file(f"{instance_idx}.dot", dlplan_ss.to_dot(1))

            if disable_closed_Q:
                initial_gfa_state_idxs = [gfa.get_initial_state(),]
            else:
                initial_gfa_state_idxs = [state_idx for state_idx in range(gfa.get_num_states()) if gfa.is_alive_state(state_idx)]

            logging.info(f"Created InstanceData with num concrete states: {mimir_ss.get_num_states()} and num abstract states: {gfa.get_num_states()}")
            instance_data = InstanceData(instance_idx, dlplan_core.DenotationsCaches(), mimir_ss.get_pddl_parser().get_problem_filepath(), gfa, mimir_ss, dlplan_ss, ss_state_idx_to_gfa_state_idx, initial_gfa_state_idxs)
            instance_datas.append(instance_data)
            instance_idx += 1

    gfa_states_by_id: Dict[int, mm.GlobalFaithfulAbstractState] = dict()
    for instance_data in instance_datas:
        for gfa_state in instance_data.gfa.get_states():
            gfa_states_by_id[gfa_state.get_id()] = gfa_state

    return domain_data, instance_datas, gfa_states_by_id




