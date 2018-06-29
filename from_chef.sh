#!/usr/bin/env bash
set -euo pipefail

SRC=ksi/notebook/20180604_benchmark_the_buried_unsatisfied_h_bond_penalty
rsync \
    chef:$SRC/park2016/outputs/ \
    park2016/outputs/ \
    --archive \
    --recursive \
    --verbose \
    --exclude 'pdb/' \

