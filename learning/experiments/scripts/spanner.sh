#!/bin/bash

DOMAIN="${PWD}/../../benchmarks/spanner/domain.pddl"
TASK_DIR="${PWD}/../../benchmarks/spanner/instances"
WIDTH=$1
CONCEPT_COMPLEXITY=9
ROLE_COMPLEXITY=9
BOOLEAN_COMPLEXITY=9
COUNT_NUMERICAL_COMPLEXITY=9
DISTANCE_NUMERICAL_COMPLEXITY=9
WORKSPACE="${PWD}/workspace/spanner_${WIDTH}_${CONCEPT_COMPLEXITY}_${ROLE_COMPLEXITY}_${BOOLEAN_COMPLEXITY}_${COUNT_NUMERICAL_COMPLEXITY}_${DISTANCE_NUMERICAL_COMPLEXITY}"
RUN_ERR="${WORKSPACE}/run.err"
RUN_LOG="${WORKSPACE}/run.log"

# Run a single task in the foreground.
rm -rf ${WORKSPACE}
mkdir -p ${WORKSPACE}
./../../learner/main.py --domain ${DOMAIN} --task_dir ${TASK_DIR} --workspace ${WORKSPACE} -w ${WIDTH} -cc ${CONCEPT_COMPLEXITY} -rc ${ROLE_COMPLEXITY} -bc ${BOOLEAN_COMPLEXITY} -ncc ${COUNT_NUMERICAL_COMPLEXITY} -ndc ${DISTANCE_NUMERICAL_COMPLEXITY} --exp_id spanner:sketch 2> ${RUN_ERR} 1> ${RUN_LOG}
