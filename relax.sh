#!/usr/bin/env bash
source helpers.sh

#$ -S /bin/bash
#$ -cwd                            #-- tell the job that it should start in your working directory
#$ -j y                            #-- tell the system that the STDERR and STDOUT should be joined
#$ -l mem_free=1G                  #-- submits on nodes with enough free memory (required)
#$ -l arch=linux-x64               #-- SGE resources (CPU type)
#$ -l netapp=1G,scratch=1G         #-- SGE resources (home and scratch disks)
#$ -l h_rt=24:00:00                #-- runtime limit (see above; this requests 24 hours)

$BIN/rosetta_scripts.$ROSETTA_BUILD                                         \
    -in:file:s $INPUTS/pdb/orig/$PDB.pdb                                    \
    -out:prefix $INPUTS/pdb/$SFXN/                                          \
    -out:no_nstruct_label                                                   \
    -out:overwrite                                                          \
    -relax:constrain_relax_to_start_coords                                  \
    -relax:coord_constrain_sidechains                                       \
    -relax:ramp_constraints false                                           \
    -parser:protocol relax.xml                                              \
    -parser:script_vars                                                     \
        sfxn=$SFXN                                                          \

