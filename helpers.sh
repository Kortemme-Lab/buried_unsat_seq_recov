BENCHMARK=park2016
INPUTS=$BENCHMARK/inputs
OUTPUTS=$BENCHMARK/outputs
BIN=$ROSETTA/source/bin
PDBS=($INPUTS/pdb/orig/????.pdb)
NUM_PDBS=${#PDBS[*]}

if [ "$SGE_TASK_ID" != "" ]; then
    PDB=$(basename ${PDBS[((SGE_TASK_ID+1))]})
    PDB=${PDB%.pdb}
    DUMP_PDB="no"
else
    DUMP_PDB="yes"
fi

if [ "$SFXN" = "" ]; then
    echo "Usage: SFXN=... $0"
    echo "No score function specified.  Valid options are:"
    echo "  'ref'"
    echo "  'ref_buns_02'"
    echo "  'ref_buns_04'"
    echo "  'ref_buns_06'"
    echo "  'ref_buns_08'"
    echo "  'ref_buns_10'"
    exit 1
fi


