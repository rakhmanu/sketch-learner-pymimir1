import math

from collections import defaultdict, deque
from termcolor import colored
from typing import Dict, List, Deque, MutableSet

import pymimir as mm
import dlplan.core as dlplan_core
import dlplan.policy as dlplan_policy

from .iteration_data import IterationData

from ..preprocessing import PreprocessingData, InstanceData
from learner.src.iteration.asp.asp_factory import ASPFactory

class Sketch:
    def __init__(self, dlplan_policy: dlplan_policy.Policy, width: int):
        self.dlplan_policy = dlplan_policy
        self.width = width

    def __eq__(self, other):
        if isinstance(other, Sketch):
            return str(self.dlplan_policy) == str(other.dlplan_policy)
        return False
    
    def __hash__(self):
        return hash((str(self.dlplan_policy), self.width))
    
    def _verify_bounded_width(self,
                              preprocessing_data: PreprocessingData,
                              iteration_data: IterationData,
                              instance_data: InstanceData,
                              require_optimal_width=False):
        """
        Performs forward search over R-reachable states.
        Initially, the R-reachable states are all initial states.
        For each R-reachable state there must be a satisfied subgoal tuple.
        If optimal width is required, we do not allow R-compatible states
        that are closer than the closest satisfied subgoal tuple.
        """
        queue: Deque[mm.GlobalFaithfulAbstractState] = deque()
        visited: MutableSet[mm.GlobalFaithfulAbstractState] = set()
        for gfa_state_idx in instance_data.initial_gfa_state_idxs:
            gfa_state = instance_data.gfa.get_states()[gfa_state_idx]
            queue.append(gfa_state)
            visited.add(gfa_state)
        # byproduct for acyclicity check
        subgoal_states_per_r_reachable_state = defaultdict(set)
        while queue:
            gfa_root = queue.pop()
            gfa_root_id = gfa_root.get_id()
            instance_idx = gfa_root.get_abstraction_index()
            instance_data = preprocessing_data.instance_datas[instance_idx]
            gfa_root_idx = instance_data.gfa.get_state_index(gfa_root)

            if instance_data.gfa.is_deadend_state(gfa_root_idx):
                print("Deadend state is r_reachable")
                print("State:", gfa_root_idx)
                return False, []
            if instance_data.gfa.is_goal_state(gfa_root_idx):
                continue

            tuple_graph = preprocessing_data.gfa_state_id_to_tuple_graph[gfa_root_id]

            dlplan_ss_root = preprocessing_data.state_finder.get_dlplan_ss_state(gfa_root)

            ḧas_bounded_width = False
            min_compatible_distance = math.inf
            for s_distance, tuple_vertex_idxs in enumerate(tuple_graph.get_vertex_indices_by_distances()):
                for mimir_ss_state_prime in tuple_graph.get_states_by_distance()[s_distance]:
                    gfa_state_prime = preprocessing_data.state_finder.get_gfa_state_from_ss_state_idx(instance_idx, instance_data.mimir_ss.get_state_index(mimir_ss_state_prime))
                    gfa_state_prime_id = gfa_state_prime.get_id()
                    dlplan_ss_state_prime = preprocessing_data.state_finder.get_dlplan_ss_state(gfa_state_prime)

                    if self.dlplan_policy.evaluate(dlplan_ss_root, dlplan_ss_state_prime, instance_data.denotations_caches) is not None:
                        min_compatible_distance = min(min_compatible_distance, s_distance)
                        subgoal_states_per_r_reachable_state[gfa_root_id].add(gfa_state_prime_id)
                        if gfa_state_prime not in visited:
                            visited.add(gfa_state_prime)
                            queue.append(gfa_state_prime)

                # Check whether there exists a subgoal tuple for which all underlying states are subgoal states
                found_subgoal_tuple = False
                for tuple_vertex_idx in tuple_vertex_idxs:
                    tuple_vertex = tuple_graph.get_vertices()[tuple_vertex_idx]
                    is_subgoal_tuple = True
                    for mimir_ss_state_prime in tuple_vertex.get_states():
                        gfa_state_prime = preprocessing_data.state_finder.get_gfa_state_from_ss_state_idx(instance_idx, instance_data.mimir_ss.get_state_index(mimir_ss_state_prime))
                        gfa_state_prime_id = gfa_state_prime.get_id()
                        dlplan_ss_state_prime = preprocessing_data.state_finder.get_dlplan_ss_state(gfa_state_prime)

                        if self.dlplan_policy.evaluate(dlplan_ss_root, dlplan_ss_state_prime, instance_data.denotations_caches) is not None:
                            min_compatible_distance = min(min_compatible_distance, s_distance)
                            subgoal_states_per_r_reachable_state[gfa_root_id].add(gfa_state_prime_id)
                        else:
                            is_subgoal_tuple = False
                    if is_subgoal_tuple:
                        found_subgoal_tuple = True
                        break

                # Decide whether width is bounded or not
                if found_subgoal_tuple:
                    if require_optimal_width and min_compatible_distance < s_distance:
                        print(colored("Optimal width disproven.", "red", "on_grey"))
                        print("Min compatible distance:", min_compatible_distance)
                        print("Subgoal tuple distance:", s_distance)
                        return False, []
                    else:
                        ḧas_bounded_width = True
                        break

            if not ḧas_bounded_width:
                print(colored("Sketch fails to bound width of a state", "red", "on_grey"))
                print("Instance:", instance_data.idx)
                print("Source_state:", gfa_root_id)
                return False, []

        return True, subgoal_states_per_r_reachable_state

    def query_subgoal_distances(self, asp_factory: ASPFactory, instance_id: int, state_id: int) -> List[int]:
        """
        Query subgoal distances from the ASP program.
        Returns a list of subgoal distances for the given instance_id and state_id.
        """
        query = f"subgoal_distance({instance_id}, {state_id}, D, R)."
        solutions = list(asp_factory.solve_all(query))
        subgoal_distances = []
        for solution in solutions:
            _, _, subgoal_distance, _ = solution.arguments
            subgoal_distances.append(int(subgoal_distance.number))
            print(subgoal_distances)
        return subgoal_distances

    def query_d_distances(self, asp_factory: ASPFactory, instance_id: int, state_id: int) -> List[int]:
        """
        Query d distances from the ASP program.
        Returns a list of d distances for the given instance_id and state_id.
        """
        query = f"d_distance({instance_id}, {state_id}, C, D')."
        solutions = list(asp_factory.solve_all(query))
        d_distances = []
        for solution in solutions:
            _, _, _, d_distance = solution.arguments
            d_distances.append(int(d_distance.number))
            print(d_distances)
        return d_distances

    def verify_unsolvable_states_removed(self, instance_data: InstanceData, asp_factory: ASPFactory) -> bool:
        """
        Verifies that unsolvable states are removed from the solution.
        Returns True if all unsolvable states are removed, False otherwise.
        """
        unsolvable_states = set()
        for s_idx, state in instance_data.state_space.get_states().items():
            if instance_data.is_deadend(s_idx) and not instance_data.is_goal(s_idx):
                unsolvable_states.add(s_idx)
        
        queue = deque(instance_data.initial_s_idxs)
        visited = set(queue)
        while queue:
            current_idx = queue.popleft()
            if current_idx in unsolvable_states:
                print(colored(f"Unsolvable state found during search: {current_idx}", "yellow"))
                return False
            current_state = instance_data.state_space.get_states()[current_idx]
            successors = instance_data.get_successors(current_idx)
            for successor_idx in successors:
                if successor_idx not in visited:
                    visited.add(successor_idx)
                    queue.append(successor_idx)
                    subgoal_distances = self.query_subgoal_distances(asp_factory, instance_data.id, successor_idx)
                    if not subgoal_distances:
                        print(colored(f"No subgoal_distance found for state ({instance_data.id}, {successor_idx}).", "red"))
                        return False
                    d_distances = self.query_d_distances(asp_factory, instance_data.id, successor_idx)
                    if not d_distances:
                        print(colored(f"No d_distance found for state ({instance_data.id}, {successor_idx}).", "red"))
                        return False
                    for subgoal_dist in subgoal_distances:
                        for d_dist in d_distances:
                            if subgoal_dist <= d_dist:
                                print(f"Unsolvable state ({instance_data.id}, {successor_idx}) verified.")
                                break
                        else:
                            print(f"Unsatisfactory d_distance for state ({instance_data.id}, {successor_idx}).")
                    else:
                        print(f"No subgoal_distance found for state ({instance_data.id}, {successor_idx}).")

        return True

    def _verify_acyclicity(self, instance_data: InstanceData, r_compatible_successors: Dict[int, int]):
        """
        Returns True iff sketch is acyclic, i.e., no infinite trajectories s1,s2,... are possible.
        """
        for s_idx, successors in r_compatible_successors.items():
            # The depth-first search is the iterative version where the current path is explicit in the stack.
            # https://en.wikipedia.org/wiki/Depth-first_search
            stack = [(s_idx, iter(successors))]
            s_idxs_on_path = {s_idx,}
            frontier = set()  # the generated states, to ensure that they are only added once to the stack
            while stack:
                source_idx, iterator = stack[-1]
                s_idxs_on_path.add(source_idx)
                try:
                    gfa_target_idx = next(iterator)
                    if instance_data.gfa.is_goal_state(gfa_target_idx):
                        continue
                    if gfa_target_idx in s_idxs_on_path:
                        print(colored("Sketch cycles", "red", "on_grey"))
                        print("Instance:", instance_data.idx)
                        for s_idx in s_idxs_on_path:
                            print(f"{s_idx}")
                        print(f"{gfa_target_idx}")
                        return False
                    if gfa_target_idx not in frontier:
                        frontier.add(gfa_target_idx)
                        stack.append((gfa_target_idx, iter(r_compatible_successors.get(gfa_target_idx, []))))
                except StopIteration:
                    s_idxs_on_path.discard(source_idx)
                    stack.pop(-1)
        return True

    def _compute_state_b_values(self, booleans: List[dlplan_policy.NamedBoolean], numericals: List[dlplan_policy.NamedNumerical], state: dlplan_core.State, denotations_caches: dlplan_core.DenotationsCaches):
        return tuple([boolean.get_element().evaluate(state, denotations_caches) for boolean in booleans] + [numerical.get_element().evaluate(state, denotations_caches) > 0 for numerical in numericals])

    def _verify_goal_separating_features(self,
                                         preprocessing_data: PreprocessingData,
                                         iteration_data: IterationData,
                                         instance_data: InstanceData):
        """
        Returns True iff sketch features separate goal from nongoal states.
        """
        goal_b_values = set()
        nongoal_b_values = set()
        booleans = self.dlplan_policy.get_booleans()
        numericals = self.dlplan_policy.get_numericals()
        for gfa_state_idx, gfa_state in enumerate(instance_data.gfa.get_states()):
            new_instance_idx = gfa_state.get_abstraction_index()
            new_instance_data = preprocessing_data.instance_datas[new_instance_idx]
            dlplan_ss_state = preprocessing_data.state_finder.get_dlplan_ss_state(gfa_state)
            b_values = self._compute_state_b_values(booleans, numericals, dlplan_ss_state, new_instance_data.denotations_caches)
            separating = True
            if instance_data.gfa.is_goal_state(gfa_state_idx):
                goal_b_values.add(b_values)
                if b_values in nongoal_b_values:
                    separating = False
            else:
                nongoal_b_values.add(b_values)
                if b_values in goal_b_values:
                    separating = False
            if not separating:
                print("Features do not separate goals from non goals")
                print("Booleans:")
                print("State:", str(dlplan_ss_state))
                print("b_values:", b_values)
                return False
        return True

    def solves(self,
               preprocessing_data: PreprocessingData,
               asp_factory: ASPFactory,
               iteration_data: IterationData,
               instance_data: InstanceData,
               enable_goal_separating_features: bool):
        """
        Returns True iff the sketch solves the instance, i.e.,
            (1) subproblems have bounded width,
            (2) sketch only classifies delta optimal state pairs as good,
            (3) sketch is acyclic, and
            (4) sketch features separate goals from nongoal states. """
        bounded, subgoal_states_per_r_reachable_state = self._verify_bounded_width(preprocessing_data, iteration_data, instance_data)
        if not bounded:
            return False
        if enable_goal_separating_features:
            if not self._verify_goal_separating_features(preprocessing_data, iteration_data, instance_data):
                return False
        if not self._verify_acyclicity(instance_data, subgoal_states_per_r_reachable_state):
            return False
        if not self.verify_unsolvable_states_removed(instance_data, asp_factory):
            return False
        return True

    def print(self, instance_data: InstanceData, asp_factory: ASPFactory):
        print(str(self.dlplan_policy))
        print("Number of sketch rules:", len(self.dlplan_policy.get_rules()))
        print("Number of selected features:", len(self.dlplan_policy.get_booleans()) + len(self.dlplan_policy.get_numericals()))
        print("Maximum complexity of selected feature:", max(
            [0] + [boolean.get_element().compute_complexity() for boolean in self.dlplan_policy.get_booleans()] +
            [numerical.get_element().compute_complexity() for numerical in self.dlplan_policy.get_numericals()]))

        if self.verify_unsolvable_states_removed(instance_data, asp_factory):
            print("Deadend states are removed")
        else:
            print("Failed to remove deadend states")
