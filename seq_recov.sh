#!/usr/bin/env bash
source helpers.sh

#$ -S /bin/bash
#$ -cwd                            #-- tell the job that it should start in your working directory
#$ -j y                            #-- tell the system that the STDERR and STDOUT should be joined
#$ -l mem_free=1G                  #-- submits on nodes with enough free memory (required)
#$ -l arch=linux-x64               #-- SGE resources (CPU type)
#$ -l netapp=1G,scratch=1G         #-- SGE resources (home and scratch disks)
#$ -l h_rt=24:00:00                #-- runtime limit (see above; this requests 24 hours)

if [ "$PDB" = "" ]; then
    echo "Usage: PDB=... $0"
    echo "No PDB ID specified."
    exit 1
fi

# Using the unrelaxed structures, because relaxing seems to move the structures 
# a lot, and may make the native recovery benchmark too easy.

$BIN/buried_unsats.$ROSETTA_BUILD                                             \
    -in:file:s $INPUTS/pdb/orig/$PDB.pdb                                      \
    -packing:resfile $INPUTS/resfile/$PDB.resfile                             \
    -app:resis 303 \
    -app:sfxn $SFXN                                                           \
    -app:out:scores $OUTPUTS/$SFXN/score/$PDB.scores                          \
    -app:out:pdbs $OUTPUTS/$SFXN/pdb/${PDB}_                                  \
    -app:out:save_pdbs $DUMP_PDB                                              \
    
