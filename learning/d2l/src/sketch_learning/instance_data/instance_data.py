import dlplan
from dataclasses import dataclass
from typing import List

from ..domain_data.domain_data import DomainData
from ..iteration_data.feature_valuations import FeatureValuation
from ..iteration_data.state_equivalence import InstanceStateEquivalence
from ..iteration_data.state_pair_equivalence import InstanceStatePairEquivalence
from ..iteration_data.tuple_graph_equivalence import TupleGraphEquivalence
from ..driver import Bunch


@dataclass
class InstanceData:
    """ """
    id: int
    instance_information: Bunch
    domain_data: DomainData
    state_space: dlplan.StateSpace
    goal_distance_information: dlplan.GoalDistanceInformation = None
    state_information: dlplan.StateInformation = None
    denotations_caches: dlplan.DenotationsCaches = None
    novelty_base: dlplan.NoveltyBase = None
    tuple_graphs: List[dlplan.TupleGraph] = None
    feature_valuations: List[FeatureValuation] = None
    state_equivalence: InstanceStateEquivalence = None
    state_pair_equivalence: InstanceStatePairEquivalence = None
    tuple_graph_equivalences: List[TupleGraphEquivalence] = None

    def print_statistics(self):
        pass
