#!/usr/bin/env bash
set -euo pipefail

#SRC=ksi/notebook/20180604_benchmark_the_buried_unsatisfied_h_bond_penalty
SRC=ksi/20180219_res16_loop12_lhkic_del1
rsync \
    chef:$SRC/park2016/outputs/ \
    park2016/outputs/ \
    --archive \
    --recursive \
    --verbose \

