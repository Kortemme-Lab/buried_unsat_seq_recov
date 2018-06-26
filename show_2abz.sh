#!/usr/bin/env bash
set -euo pipefail

pymol \
    -d 'set cartoon_side_chain_helper, off' \
    -d 'load park2016/pdb/orig/2ABZ.pdb, orig' \
    -d 'load park2016/out/ref/2ABZ.pdb, ref' \
    -d 'load park2016/out/ref_buns/2ABZ.pdb, ref_buns' \
    -d 'select scene, byres all within 8 of resi 150' \
    -d 'select none' \
    -d 'show sticks, scene' \
    -d 'hide everything, hydro' \
    -d 'zoom scene' \
