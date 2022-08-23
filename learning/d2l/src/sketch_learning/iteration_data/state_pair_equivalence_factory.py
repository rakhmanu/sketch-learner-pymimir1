import dlplan

from collections import defaultdict
from dataclasses import dataclass
from typing import List

from .state_pair_equivalence import RuleEquivalences, StatePairEquivalence
from .domain_feature_data import DomainFeatureData
from .instance_feature_data import InstanceFeatureData
from .state_pair import StatePair


@dataclass
class StatePairEquivalenceStatistics:
    num_equivalences: int = 0

    def increase_num_equivalences(self, num: int):
        self.num_equivalences += num

    def print(self):
        print("Num equivalences:", self.num_equivalences)


class StatePairEquivalenceFactory:
    def __init__(self):
        self.statistics = StatePairEquivalenceStatistics()

    def make_state_pair_equivalences(self, domain_feature_data: DomainFeatureData, state_pairs_by_subproblem: List[List[StatePair]], instance_feature_datas_by_subproblem: List[InstanceFeatureData]):
        policy_builder = dlplan.PolicyBuilder()
        policy_boolean_features = [policy_builder.add_boolean_feature(b) for b in domain_feature_data.boolean_features]
        policy_numerical_features = [policy_builder.add_numerical_feature(n) for n in domain_feature_data.numerical_features]
        rules = []
        rule_repr_to_idx = dict()
        state_pair_equivalences = []
        for state_pairs, instance_feature_data in zip(state_pairs_by_subproblem, instance_feature_datas_by_subproblem):
            r_idx_to_state_pairs = defaultdict(list)
            state_pair_to_r_idx = dict()
            for state_pair in state_pairs:
                source_idx = state_pair.source_idx
                target_idx = state_pair.target_idx
                # add conditions
                conditions = self._make_conditions(policy_builder, source_idx, policy_boolean_features, policy_numerical_features, instance_feature_data)
                # add effects
                effects = self._make_effects(policy_builder, source_idx, target_idx, policy_boolean_features, policy_numerical_features, instance_feature_data)
                # add rule
                rule = policy_builder.add_rule(conditions, effects)
                rule_repr = rule.compute_repr()
                if rule_repr in rule_repr_to_idx:
                    r_idx = rule_repr_to_idx[rule_repr]
                else:
                    r_idx = len(rules)
                    rule_repr_to_idx[rule_repr] = r_idx
                    rules.append(rule)
                state_pair = (source_idx, target_idx)
                r_idx_to_state_pairs[r_idx].append(state_pair)
                state_pair_to_r_idx[state_pair] = r_idx
            state_pair_equivalences.append(StatePairEquivalence(r_idx_to_state_pairs, state_pair_to_r_idx))
        self.statistics.increase_num_equivalences(len(rules))
        return RuleEquivalences(rules), state_pair_equivalences

    def _make_conditions(self, policy_builder: dlplan.PolicyBuilder, source_idx: int, policy_boolean_features, policy_numerical_features, instance_feature_data):
        """ Create conditions over all features that are satisfied in source_idx """
        conditions = []
        numerical_feature_valuations = instance_feature_data.numerical_feature_valuations
        boolean_feature_valuations = instance_feature_data.boolean_feature_valuations
        for n_idx in range(len(policy_numerical_features)):
            if numerical_feature_valuations[source_idx][n_idx] > 0:
                conditions.append(policy_builder.add_gt_condition(policy_numerical_features[n_idx]))
            else:
                conditions.append(policy_builder.add_eq_condition(policy_numerical_features[n_idx]))
        for b_idx in range(len(policy_boolean_features)):
            if boolean_feature_valuations[source_idx][b_idx]:
                conditions.append(policy_builder.add_pos_condition(policy_boolean_features[b_idx]))
            else:
                conditions.append(policy_builder.add_neg_condition(policy_boolean_features[b_idx]))
        return conditions

    def _make_effects(self, policy_builder: dlplan.PolicyBuilder, source_idx: int, target_idx: int, policy_boolean_features, policy_numerical_features, instance_feature_data):
        """ Create effects over all features that are satisfied in (source_idx,target_idx) """
        effects = []
        numerical_feature_valuations = instance_feature_data.numerical_feature_valuations
        boolean_feature_valuations = instance_feature_data.boolean_feature_valuations
        for n_idx in range(len(policy_numerical_features)):
            if instance_feature_data.numerical_feature_valuations[source_idx][n_idx] > numerical_feature_valuations[target_idx][n_idx]:
                effects.append(policy_builder.add_dec_effect(policy_numerical_features[n_idx]))
            elif numerical_feature_valuations[source_idx][n_idx] < numerical_feature_valuations[target_idx][n_idx]:
                effects.append(policy_builder.add_inc_effect(policy_numerical_features[n_idx]))
            else:
                effects.append(policy_builder.add_bot_effect(policy_numerical_features[n_idx]))
        for b_idx in range(len(policy_boolean_features)):
            if boolean_feature_valuations[source_idx][b_idx] and not boolean_feature_valuations[target_idx][b_idx]:
                effects.append(policy_builder.add_neg_effect(policy_boolean_features[b_idx]))
            elif not boolean_feature_valuations[source_idx][b_idx] and boolean_feature_valuations[target_idx][b_idx]:
                effects.append(policy_builder.add_pos_effect(policy_boolean_features[b_idx]))
            else:
                effects.append(policy_builder.add_bot_effect(policy_boolean_features[b_idx]))
        return effects
