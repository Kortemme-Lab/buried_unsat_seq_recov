#!/usr/bin/env python3

"""\
Print out detailed information about the predictions for the given 
position.

Usage:
    describe_position.py <pdb> <resi>
"""

import docopt
import math, statistics
from analysis_helpers import *
from attr import attrs, attrib
from nonstdlib import title
from more_itertools import one

ref = normalize_scores(parse_score_files('ref', probs=False))
ref_buns = normalize_scores(parse_score_files('ref_buns_10', probs=False))

ref_probs = probs_from_scores(ref, log=True)
ref_buns_probs = probs_from_scores(ref_buns, log=True)

args = docopt.docopt(__doc__)
pdb = args['<pdb>']
resi = int(args['<resi>'])

pos = one(x for x in ref if x.pdb == pdb and x.resi == resi)

print(pos)
print()

print('ref / ref_buns')
print(ref_probs[pos][pos.wt] - ref_buns_probs[pos][pos.wt])
print()

print('ref scores')
print_ranked_list(ref[pos])
print()

print('ref probs')
print_ranked_list(ref_probs[pos])
print()

print('ref_buns scores')
print_ranked_list(ref_buns[pos])
print()

print('ref_buns probs')
print_ranked_list(ref_buns_probs[pos])
print()

