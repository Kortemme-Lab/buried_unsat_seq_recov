if [ "$SFXN" = "" ]; then
    SFXN="ref_buns_10"
fi

function compare_models() {
    PDB=$1
    pymol -qx \
        -d "load orig/$PDB.pdb, orig_$PDB" \
        -d "load $SFXN/$PDB.pdb, ${SFXN}_$PDB" 
}

for PDB in orig/*; do
    PDB=$(basename $PDB)
    PDB=${PDB%.pdb}

    echo -n "Compare models for $PDB? "
    read
    compare_models $PDB
done

