% Optimization for fewest number of rules, then smallest sum over feature complexities
#minimize { C@2,complexity(F, C) : complexity(F, C), feature(F), select(F) }.

%%%%%%%%%% C1 %%%%%%%%%%
% Generate selected features
{ select(F) } :- feature(F).
% Generate rules
rule(1).

% Generate feature conditions and effects
{ c_n_eq(R, F); c_n_gt(R, F) } = 1 :- rule(R), numerical(F).
{ c_b_pos(R, F); c_b_neg(R, F) } = 1 :- rule(R), boolean(F).
{ e_n_dec(R, F); e_n_inc(R, F); e_n_bot(R, F) } = 1 :- rule(R), numerical(F).
{ e_b_pos(R, F); e_b_neg(R, F); e_b_bot(R, F) } = 1 :- rule(R), boolean(F).


% Define equivalence class C and rule R have same feature condition on F
c_satisfied(R, F, C) :- c_n_eq(R, F), feature_condition(C, F, "c_n_eq"), numerical(F), rule(R), state_pair_class(C).
c_satisfied(R, F, C) :- c_n_gt(R, F), feature_condition(C, F, "c_n_gt"), numerical(F), rule(R), state_pair_class(C).
c_satisfied(R, F, C) :- c_b_pos(R, F), feature_condition(C, F, "c_b_pos"), boolean(F), rule(R), state_pair_class(C).
c_satisfied(R, F, C) :- c_b_neg(R, F), feature_condition(C, F, "c_b_neg"), boolean(F), rule(R), state_pair_class(C).

e_satisfied(R, F, C) :- e_n_dec(R, F), feature_effect(C, F, "e_n_dec"), numerical(F), rule(R), state_pair_class(C).
e_satisfied(R, F, C) :- e_n_inc(R, F), feature_effect(C, F, "e_n_inc"), numerical(F), rule(R), state_pair_class(C).
e_satisfied(R, F, C) :- e_b_pos(R, F), feature_effect(C, F, "e_b_pos"), boolean(F), rule(R), state_pair_class(C).
e_satisfied(R, F, C) :- e_b_neg(R, F), feature_effect(C, F, "e_b_neg"), boolean(F), rule(R), state_pair_class(C).
e_satisfied(R, F, C) :- e_b_bot(R, F), feature_effect(C, F, "e_b_bot"), boolean(F), rule(R), state_pair_class(C).
e_satisfied(R, F, C) :- e_n_bot(R, F), feature_effect(C, F, "e_n_bot"), numerical(F), rule(R), state_pair_class(C).
e_satisfied(R, F, C) :- e_b_pos(R, F), feature_effect(C, F, "e_b_bot"), feature_condition(C, F, "c_b_pos"), boolean(F), rule(R), state_pair_class(C).
e_satisfied(R, F, C) :- e_b_neg(R, F), feature_effect(C, F, "e_b_bot"), feature_condition(C, F, "c_b_neg"), boolean(F), rule(R), state_pair_class(C).

%change
%%%%%{alive_selected(S)} = 1 :- alive(S), nongoal(S).
%{alive_selected(S) : alive(S), nongoal(S)} = 1.

%%%%%%%%%% C2.1 %%%%%%%%%%
%change
%{ subgoal_distance(S, D, R) : t_distance(S, _, D), D > 0 } != 0 :- sat_cond(S, R), alive_selected(S), nongoal(S).
{ subgoal_distance(S, D, R) : t_distance(S, _, D), D > 0 } != 0 :- sat_cond(S, R), initial(S), nongoal(S).
% why does this work?
% subgoal_distance(0,1,1).
%%%%%%%%%% C3.1 %%%%%%%%%%
{ subgoal(S, T, R) : t_distance(S, T, D) } != 0 :- subgoal_distance(S, D, R).

%%%%%%%%%% C4.1 %%%%%%%%%%
% Require that all equivalence classes C underlying a tuple T of subproblem P[S] are good, effectively bounding the width of P[S]
:- not sat_rule(R, C), subgoal(S, T, R), contain(S, T, C).

%%% Unsolvable states can be addressed with d_distance
%change
:- D <= D',  subgoal_distance(S, D, R), sat_rule(R, C), d_distance(S, C, D'), initial(S), unsolvable(S), nongoal(S).     

%%%%%%%%%% C6.2 %%%%%%%%%%
%change
%:- D < D', t_distance(S, T, D), sat_pair(S, S', R), subgoal_distance(S, D', R), nongoal(S).

%%%%%%%%%% C6.1 %%%%%%%%%%
% (Optimal-width): Require solvable states S' closer than subgoal to not be assigned to any rule.
:- D < D', r_distance(S, C, D), sat_rule(R, C), subgoal_distance(S, D', R), nongoal(S).

%%%%%%%%%% C7.1 %%%%%%%%%%
% Define state pair equivalences that are compatible with rules.
sat_rule(R, C) :- { feature(F) : not c_satisfied(R, F, C), select(F);
     feature(F) : not e_satisfied(R, F, C), select(F) } = 0, rule(R), state_pair_class(C).
% Define state pairs that are compatible with rules.
sat_pair(S, S', R) :- sat_rule(R, C), cover(S, S', C), nongoal(S).

%%%%%%%%%% C7.2 %%%%%%%%%%
sat_cond(S, R) :- { feature(F) : not c_satisfied(R, F, C), select(F) } = 0, rule(R), state_pair_class(C), cover(S, _, C), nongoal(S).

% python3 learning/main.py --domain_filepath learning/benchmarks/gripper/domain.pddl --problems_directory learning/benchmarks/gripper/instances_debug --width 1 --workspace workspace --additional_numericals "n_count(r_primitive(carry,0,1))" "n_count(r_diff(r_primitive(at_g,0,1), r_primitive(at,0,1)))" --disable_feature_generation


% Display
#show rule/1.
#show select/1.

#show c_n_eq/2.
#show c_n_gt/2.

#show e_n_dec/2.
#show e_n_inc/2.
#show e_n_bot/2.

#show c_b_pos/2.
#show c_b_neg/2.

#show e_b_pos/2.
#show e_b_neg/2.
#show e_b_bot/2.