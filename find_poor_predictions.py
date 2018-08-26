#!/usr/bin/env python3

# Basically, my goal is to identify poor predictions where the buried unsat 
# term should help, but doesn't.  Specific examples might include:
# 
# - An non-native amino acid creates a buried unsatisfied H-bond, but is not 
#   penalized for it.
# - A native amino acid is penalized for a buried unsatisfied H-bond that 
#   doesn't really exist.
#
# I can't really know which residues actually have buried unsatisfied H-bonds, 
# since the whole premise is that I don't really trust Rosetta, so I don't 
# really have a way to directly identify the poor predictions described above.
#
# Another proxy for interesting predictions are those that differ significantly 
# with and without the buried unsat score term, for any mutation (i.e. not just 
# looking at the native)

import math, statistics
from analysis_helpers import *
from attr import attrs, attrib
from nonstdlib import title

ref = normalize_scores(parse_score_files('ref', probs=False))
ref_buns = normalize_scores(parse_score_files('ref_buns_10', probs=False))

ref_probs = probs_from_scores(ref)
ref_buns_probs = probs_from_scores(ref_buns)

def compare_scores(a, b):
    score_diffs = {}

    for pos in a:
        score_diffs[pos] = {}
        for mut in a[pos]:
            score_diffs[pos][mut] = b[pos][mut] - a[pos][mut]

    return score_diffs

positions = list(ref.keys())

# Rank by native recovery probability.
# >1: better without buried_unsat term.
prob_ranks = {}
for pos in positions:
    prob_ranks[pos] = math.log10(
            ref_probs[pos][pos.wt] / ref_buns_probs[pos][pos.wt])

# Average rank (by amino acid)
pdb_ranks = {}
for i, pos in enumerate(positions):
    pdb_ranks.setdefault(pos.pdb, []).append(prob_ranks[pos])

# Average rank (by input pdb)
wt_ranks = {}
wt_ranks_i = {}
for i, pos in enumerate(positions):
    wt_ranks.setdefault(pos.wt, []).append(prob_ranks[pos])
    wt_ranks_i.setdefault(pos.wt, []).append(i)

def print_ranked_list(ranking, reduce=lambda x: x, reverse=False, limit=None):
    sorted_items = sorted(
            ranking.keys(),
            key=lambda x: reduce(ranking[x]),
            reverse=reverse,
    )
    for i, item in enumerate(sorted_items):
        if i and i == limit: break
        print(item, reduce(ranking[item]))

title("Ranked by native recovery")
print_ranked_list(prob_ranks)
print()

title("Ranked by input PDB")
print_ranked_list(pdb_ranks, statistics.mean)
print()

title("Ranked by wt residue")
print_ranked_list(wt_ranks, statistics.mean)
print()
print_ranked_list(wt_ranks_i, statistics.mean)


# These diffs will often be in steps of 5 REU.
#
# Really, this is just telling me where 
#
# Diffs for non-polar residues could be interesting.
#
# Negative diff: scores better with buried unsat term
#
# I should look first at p
#
# For any mutation I'm interested in, I'll have to rerun the simulations to get 
# the structures.  I'll also need to hack rosetta to show me the buried unsats.  
# So I definitely need to prioritize here.
#
# Input: wt residue
#
# First: find positions with that wt residue that are better predicted with ref 
# buns.
#
# Second: 

#score_diffs = compare_scores(ref, ref_buns_10)
#pprint(score_diffs[k])

