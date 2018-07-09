#!/usr/bin/env bash
set -eo pipefail
source helpers.sh

if [ $# != 2 ]; then
    echo "Usage: SFXN=<sfxn> ./show_mutants.sh <pdb> <resi>"
    exit 1
fi

PDB=$1
RESI=$2

gnumeric \
    $OUTPUTS/$SFXN/score/$PDB.scores \
    &> /dev/null &

pymol -qx \
    $INPUTS/pdb/orig/$PDB.pdb \
    $OUTPUTS/$SFXN/pdb/$PDB.???$RESI???.pdb \
    -d "set cartoon_side_chain_helper, off" \
    -d "select mut, resi $RESI" \
    -d "select env, byres all within 8 of mut" \
    -d "show sticks, env" \
    -d "hide everything, hydro" \
    -d "zoom env" \
    -d "select none" \
    &> /dev/null &
