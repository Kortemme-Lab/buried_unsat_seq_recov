#!/usr/bin/env bash
set -euo pipefail

rsync \
    park2016 \
    seq_recov.* \
    relax.* \
    shared_defs.xml \
    helpers.sh \
    chef:ksi/notebook/20180604_benchmark_the_buried_unsatisfied_h_bond_penalty \
    --archive \
    --recursive \
    --verbose \
    --exclude 'out' \
    --exclude 'logs' \
