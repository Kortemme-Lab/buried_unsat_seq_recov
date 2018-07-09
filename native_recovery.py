#!/usr/bin/env python3

"""
Calculate native recovery (i.e. how often Rosetta picks the native residue in 
fixbb simulations where only the residue in question is allowed to design) with 
or without the score function term accounting for buried unsatisfied H-bonds.

Usage:
    ./native_recovery.py 
"""

import os
import docopt
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
from attr import attrs, attrib
from math import *
from statistics import *
from color_me import ucsf

BENCHMARK = Path('park2016')
INPUTS = Path('park2016') / 'inputs'
OUTPUTS = Path('park2016') / 'outputs'

aa_table = {
        'ALA': 'A',
        'CYS': 'C',
        'ASP': 'D',
        'GLU': 'E',
        'GLY': 'G',
        'HIS': 'H',
        'ILE': 'I',
        'LYS': 'K',
        'LEU': 'L',
        'MET': 'M',
        'ASN': 'N',
        'PHE': 'F',
        'PRO': 'P',
        'GLN': 'Q',
        'ARG': 'R',
        'SER': 'S',
        'THR': 'T',
        'VAL': 'V',
        'TRP': 'W',
        'TYR': 'Y',
}
aa_types = {
        'D': 'positive',
        'E': 'positive',

        'K': 'negative',
        'R': 'negative',
        'H': 'negative',

        'N': 'polar',
        'Q': 'polar',
        'S': 'polar',
        'T': 'polar',

        'A': 'nonpolar',
        'C': 'nonpolar',
        'I': 'nonpolar',
        'L': 'nonpolar',
        'M': 'nonpolar',
        'V': 'nonpolar',

        'F': 'aromatic',
        'W': 'aromatic',
        'Y': 'aromatic',

        'G': 'special',
        'P': 'special',
}

@attrs(frozen=True)
class Position:
    pdb = attrib()
    resi = attrib()
    wt = attrib()

@attrs
class Mutation:
    resi = attrib()
    mut = attrib()
    score = attrib()


def parse_score_files(sfxn):
    scores = {}
    paths = OUTPUTS / sfxn / 'score'

    for path in paths.glob('*.scores'):
        scores.update(parse_score_file(path))

    return probs_from_scores(scores)

def parse_score_file(path):
    scores = {}
    pdb = path.stem

    with path.open() as file:
        lines = file.readlines()

    for line in lines:
        tokens = line.split()
        resi = int(tokens[0])
        wt = tokens[1]
        mut = tokens[2]
        score = float(tokens[3])

        pos = Position(pdb, resi, wt)
        if pos not in scores:
            scores[pos] = {}
        scores[pos][mut] = score

    return scores

def parse_pssms():
    counts = {}
    paths = INPUTS / 'pssm'

    for path in paths.glob('*.pssm'):
        counts.update(parse_pssm(path))

    return probs_from_counts(counts)

def parse_pssm(path):
    with path.open() as file:
        lines = file.readlines()

    pdb = path.stem
    header = lines[0].split()[2:]
    pssm = {}

    for row in lines[1:]:
        expected = {}
        resi, wt, *counts = row.split()
        resi = int(resi)
        counts = map(int, counts)

        pos = Position(
                pdb=pdb,
                resi=resi,
                wt=wt,
        )
        pssm[pos] = {}

        for mut, count in zip(header, counts):
            pssm[pos][mut] = count

    return pssm
    
def probs_from_scores(scores):
    probs = {}

    # The rosetta score function is approximately in units of kcal/mol.
    RT = 1.9872036e-3 * 293

    for key in scores:
        min_score = min(scores[key].values())
        boltzmann_weights = {
                resn: exp(-(scores[key][resn] - min_score) / RT)
                for resn in scores[key]
        }
        probs[key] = normalize(boltzmann_weights)

    return probs

def probs_from_counts(expected):
    probs = {}
    for key in expected:
        probs[key] = normalize(expected[key])
    return probs


def normalize(x):
    Z = sum(x.values())
    if Z == 0: Z = 1
    return {k: x[k] / Z for k in x}

def dot_product(p1, p2):
    return sum(
            p1[k] * p2[k]
            for k in p1)


args = docopt.docopt(__doc__)

recoveries = {}
sfxns = [
        'ref',
        'ref_buns_02',
        'ref_buns_04',
        'ref_buns_06',
        'ref_buns_08',
        'ref_buns_10',
]
types = [
        'positive',
        'negative',
        'polar',
        'nonpolar',
        'aromatic',
        'special',
]
colors = {
        'positive': ucsf.blue[0],
        'negative': ucsf.red[0],
        'polar': ucsf.purple[0],
        'nonpolar': ucsf.black[1],
        'aromatic': ucsf.black[0],
        'special': ucsf.orange[0],
}


for sfxn in sfxns:
    probs = parse_score_files(sfxn)
    recoveries[sfxn] = {
            'positive': [],
            'negative': [],
            'polar': [],
            'nonpolar': [],
            'aromatic': [],
            'special': [],
    }
    recoveries[sfxn] = {
            k: []
            for k in aa_types
    }
    for i, pos in enumerate(probs):
        type = aa_types[pos.wt]
        recovery = probs[pos][pos.wt]
        #recoveries[sfxn][type].append(recovery)
        recoveries[sfxn][pos.wt].append(recovery)

if os.fork():
    raise SystemExit

fig, axes = plt.subplots(4, 5, sharex='all', sharey='all', figsize=(11,8.5))

for ax, type in zip(axes.flat, aa_types):
    xs = [recoveries[x][type] for x in sfxns]
    ii = range(len(xs))
    color = colors[aa_types[type]]

    ax.set_title(type)
    ax.set_xticks(ii)
    ax.set_xticklabels(sfxns, rotation='vertical')
    ax.set_title(f"{type} (N={len(xs[0])})")

    ax.axhline(
            mean(recoveries['ref'][type]),
            color=color, linestyle='--', alpha=0.5)

    artists = ax.violinplot(xs, ii, showmeans=True)

    for i in ii:
        artists['bodies'][i].set_facecolor(color)
    artists['cbars'].set_visible(False)
    artists['cmins'].set_visible(False)
    artists['cmaxes'].set_visible(False)
    artists['cmeans'].set_edgecolor(color)


for i in range(4):
    axes[i,0].set_ylabel('Native frequency')

fig.tight_layout()
plt.savefig('native_recovery.svg')
plt.show()

