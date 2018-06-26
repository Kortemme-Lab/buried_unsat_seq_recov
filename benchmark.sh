#!/usr/bin/env bash
set -eo pipefail

BIN=$ROSETTA/source/bin
BENCHMARK=$(dirname $0)/park2016
ROSETTA_BUILD=linuxclangrelease

[ "$J" = "" ] && J=1

if [ "$SFXN" = "" ]; then
    echo "Usage: SFXN=... ./benchmark.sh"
    echo "No score function specified.  Valid options are 'ref' and 'ref_buns'."
    exit 1
fi

mkdir -p $BENCHMARK/out/$SFXN

function sequence_recovery() {
    PDB=$1
    stdbuf -oL $ROSETTA/source/bin/rosetta_scripts.$ROSETTA_BUILD           \
        -in:file:s $BENCHMARK/pdb/orig/$PDB.pdb                             \
        -out:prefix $BENCHMARK/out/$SFXN/                                   \
        -out:no_nstruct_label                                               \
        -out:overwrite                                                      \
        -parser:protocol park2016/scan.xml                                  \
        -parser:script_vars                                                 \
            sfxn=$SFXN                                                      \
            resfile=$BENCHMARK/resfile/$PDB.resfile                         \
        |& tee $BENCHMARK/out/$SFXN/$PDB.log
}

i=0
for GLOB in $BENCHMARK/pdb/orig/*.pdb; do
    PDB=$(basename $GLOB)
    PDB=${PDB%.pdb}

    sequence_recovery $PDB &
    (( ++i % J == 0 )) && wait
done
wait

