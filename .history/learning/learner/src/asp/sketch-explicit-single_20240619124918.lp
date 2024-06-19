% Optimization for fewest number of rules, then smallest sum over feature complexities
#minimize { C@2,complexity(F, C) : complexity(F, C), feature(F), select(F) }.

%%%%%%%%%% C1 %%%%%%%%%%
% Generate selected features
{ select(F) } :- feature(F).
% Generate rules
rule(1).

% Generate feature conditions and effects
{ c_n_eq(R, F); c_n_gt(R, F); c_n_unk(R, F) } = 1 :- rule(R), numerical(F).
{ c_b_pos(R, F); c_b_neg(R, F); c_b_unk(R, F) } = 1 :- rule(R), boolean(F).
{ e_n_dec(R, F); e_n_inc(R, F); e_n_unk(R, F); e_n_bot(R, F) } = 1 :- rule(R), numerical(F).
{ e_b_pos(R, F); e_b_neg(R, F); e_b_unk(R, F); e_b_bot(R, F) } = 1 :- rule(R), boolean(F).


% Define equivalence class C and rule R have same feature condition on F
c_satisfied(R, F, C) :- c_n_eq(R, F), feature_condition(C, F, "c_n_eq"), numerical(F), rule(R), state_pair_class(C).
c_satisfied(R, F, C) :- c_n_gt(R, F), feature_condition(C, F, "c_n_gt"), numerical(F), rule(R), state_pair_class(C).
c_satisfied(R, F, C) :- c_b_pos(R, F), feature_condition(C, F, "c_b_pos"), boolean(F), rule(R), state_pair_class(C).
c_satisfied(R, F, C) :- c_b_neg(R, F), feature_condition(C, F, "c_b_neg"), boolean(F), rule(R), state_pair_class(C).
c_satisfied(R, F, C) :- c_n_unk(R, F), numerical(F), rule(R), state_pair_class(C).
c_satisfied(R, F, C) :- c_b_unk(R, F), boolean(F), rule(R), state_pair_class(C).

e_satisfied(R, F, C) :- e_n_dec(R, F), feature_effect(C, F, "e_n_dec"), numerical(F), rule(R), state_pair_class(C).
e_satisfied(R, F, C) :- e_n_inc(R, F), feature_effect(C, F, "e_n_inc"), numerical(F), rule(R), state_pair_class(C).
e_satisfied(R, F, C) :- e_b_pos(R, F), feature_effect(C, F, "e_b_pos"), boolean(F), rule(R), state_pair_class(C).
e_satisfied(R, F, C) :- e_b_neg(R, F), feature_effect(C, F, "e_b_neg"), boolean(F), rule(R), state_pair_class(C).
e_satisfied(R, F, C) :- e_b_bot(R, F), feature_effect(C, F, "e_b_bot"), boolean(F), rule(R), state_pair_class(C).
e_satisfied(R, F, C) :- e_n_bot(R, F), feature_effect(C, F, "e_n_bot"), numerical(F), rule(R), state_pair_class(C).
e_satisfied(R, F, C) :- e_b_pos(R, F), feature_effect(C, F, "e_b_bot"), feature_condition(C, F, "c_b_pos"), boolean(F), rule(R), state_pair_class(C).
e_satisfied(R, F, C) :- e_b_neg(R, F), feature_effect(C, F, "e_b_bot"), feature_condition(C, F, "c_b_neg"), boolean(F), rule(R), state_pair_class(C).
e_satisfied(R, F, C) :- e_n_unk(R, F), numerical(F), rule(R), state_pair_class(C).
e_satisfied(R, F, C) :- e_b_unk(R, F), boolean(F), rule(R), state_pair_class(C).

{ alive_selected(I, S) } = 1 :- alive(I, S), nongoal(I, S).

%%%%%%%%%% C2.1 %%%%%%%%%%
{ subgoal_distance(I, S, D, R) : t_distance(I, S, _, D), D > 0 } != 0 :- sat_cond(I, S, R), alive_selected(I, S), nongoal(I, S).

%%%%%%%%%% C3.1 %%%%%%%%%%
{ subgoal(I, S, T, R) : t_distance(I, S, T, D) } != 0 :- subgoal_distance(I, S, D, R).

%%%%%%%%%% C4.1 %%%%%%%%%%
% Require that all equivalence classes C underlying a tuple T of subproblem P[S] are good, effectively bounding the width of P[S]
:- not sat_rule(R, C), subgoal(I, S, T, R), contain(I, S, T, C).

%%% TODO: Unsolvable states can be addressed with d_distance
:- D <= D', subgoal_distance(I, S', D, R), d_distance(I, S, R, D'), alive(I, S), nongoal(I, S), sat_pair(I, S, S', R),    


%%%%%%%%%% C6.1 %%%%%%%%%%
% (Optimal-width): Require solvable states S' closer than subgoal to not be assigned to any rule.
:- D < D', r_distance(I, S, C, D), sat_rule(R, C), subgoal_distance(I, S, D', R), nongoal(I, S).

%%%%%%%%%% C7.1 %%%%%%%%%%
% Define state pair equivalences that are compatible with rules.
sat_rule(R, C) :- { feature(F) : not c_satisfied(R, F, C), select(F);
     feature(F) : not e_satisfied(R, F, C), select(F) } = 0, rule(R), state_pair_class(C).
% Define state pairs that are compatible with rules.
sat_pair(I, S, S', R) :- sat_rule(R, C), cover(I, S, S', C), nongoal(I, S).

%%%%%%%%%% C7.2 %%%%%%%%%%
sat_cond(I, S, R) :- { feature(F) : not c_satisfied(R, F, C), select(F) } = 0, rule(R), state_pair_class(C), cover(I, S, _, C), nongoal(I, S).


% Display
#show r_distance/4.
#show sat_rule/2.
#show subgoal_distance/4.
#show rule/1.
#show select/1.

#show c_n_eq/2.
#show c_n_gt/2.
#show c_n_unk/2.

#show e_n_dec/2.
#show e_n_inc/2.
#show e_n_bot/2.
#show e_n_unk/2.

#show c_b_pos/2.
#show c_b_neg/2.
#show c_b_unk/2.

#show e_b_pos/2.
#show e_b_neg/2.
#show e_b_bot/2.
#show e_b_unk/2.