import math

from collections import deque, defaultdict

from .instance_data import InstanceData
from .state_pair import StatePair
from .state_pair_classifier import StatePairClassification, StatePairClassifier


class StatePairClassifierFactory:
    def __init__(self, delta=1.0):
        assert delta >= 1
        self.delta = delta

    def make_state_pair_classifier(self, config, instance_data: InstanceData):
        """
        Classifies state pairs induced by tuples graphs into one of four classes:
            (1) DELTA_OPTIMAL, i.e., delta * h^*(source) >= h^*(target) + distance(source, target) where
              - left side of equation is upper bound on worst case cost for source, and
              - right side of equation is best case goal distance of source over target.
            (2) NOT_DELTA_OPTIMAL, i.e, delta * h^*(source) < h^*(target) + distance(source, target)
            (3) SELF_LOOP, i.e., state pair induces loop
            (4) DEADEND, i.e., state pair leads to deadend
        Afterwards restricts to relevant state pairs.
        """
        # 1. Classify any state pair.
        state_space = instance_data.state_space
        goal_distance_information = instance_data.goal_distance_information
        goal_distances = goal_distance_information.get_goal_distances()
        state_pair_to_classification = dict()
        expanded_state_indices = set()
        generated_state_indices = set()
        source_idx_to_state_pairs = defaultdict(set)
        for source_idx in state_space.get_state_indices():
            if not goal_distance_information.is_alive(source_idx):
                continue
            tuple_graph = instance_data.tuple_graphs[source_idx]
            expanded_state_indices.add(source_idx)
            generated_state_indices.add(source_idx)
            source_cost = goal_distances.get(source_idx, math.inf)
            assert source_cost != math.inf
            for distance, target_idxs in enumerate(tuple_graph.s_idxs_by_distance):
                for target_idx in target_idxs:
                    target_cost = goal_distances.get(target_idx, math.inf)
                    state_pair = StatePair(source_idx, target_idx)
                    if source_idx == target_idx or \
                        self.delta * source_cost < target_cost + distance:
                        state_pair_to_classification[state_pair] = StatePairClassification.NOT_DELTA_OPTIMAL
                        generated_state_indices.add(target_idx)
                        source_idx_to_state_pairs[source_idx].add(state_pair)
                    else:
                        state_pair_to_classification[state_pair] = StatePairClassification.DELTA_OPTIMAL
                        generated_state_indices.add(target_idx)
                        source_idx_to_state_pairs[source_idx].add(state_pair)

        # 2. Select relevant state pairs
        state_pair_to_classification_2 = dict()
        expanded_state_indices_2 = set()
        generated_state_indices_2 = set()
        source_idx_to_state_pairs_2 = defaultdict(set)
        queue = deque()
        visited = set()
        initial_state_index = state_space.get_initial_state_index()
        queue.append(initial_state_index)
        visited.add(initial_state_index)
        while queue:
            source_idx = queue.popleft()
            if not goal_distance_information.is_alive(source_idx):
                continue
            has_delta_optimal_successor = not all([state_pair_to_classification[state_pair] != StatePairClassification.DELTA_OPTIMAL for state_pair in source_idx_to_state_pairs.get(source_idx, [])])
            if not has_delta_optimal_successor:
                continue
            expanded_state_indices_2.add(source_idx)
            for state_pair in source_idx_to_state_pairs.get(source_idx, []):
                state_pair_to_classification_2[state_pair] = state_pair_to_classification[state_pair]
                source_idx_to_state_pairs_2[source_idx].add(state_pair)
                generated_state_indices_2.add(state_pair.target_idx)
                if state_pair_to_classification[state_pair] == StatePairClassification.DELTA_OPTIMAL:
                    if state_pair.target_idx not in visited:
                        visited.add(state_pair.target_idx)
                        queue.append(state_pair.target_idx)
        state_pair_to_classification = state_pair_to_classification_2
        expanded_state_indices = expanded_state_indices_2
        generated_state_indices = generated_state_indices_2
        source_idx_to_state_pairs = source_idx_to_state_pairs_2
        state_pair_classifier = StatePairClassifier(self.delta, state_pair_to_classification, source_idx_to_state_pairs, expanded_state_indices, generated_state_indices)
        return state_pair_classifier
