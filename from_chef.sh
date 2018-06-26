#!/usr/bin/env bash
set -euo pipefail

SRC=ksi/notebook/20180604_benchmark_the_buried_unsatisfied_h_bond_penalty
rsync \
    chef:$SRC/ \
    . \
    --archive \
    --recursive \
    --verbose \

