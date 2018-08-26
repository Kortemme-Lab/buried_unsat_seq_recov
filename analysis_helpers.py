#!/usr/bin/env python3

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
        'V': 'nonpolar',
        'I': 'nonpolar',
        'L': 'nonpolar',
        'C': 'nonpolar',
        'M': 'nonpolar',

        'F': 'aromatic',
        'Y': 'aromatic',
        'W': 'aromatic',

        'G': 'special',
        'P': 'special',
}
type_colors = {
        'positive': ucsf.blue[0],
        'negative': ucsf.red[0],
        'polar': ucsf.purple[0],
        'nonpolar': ucsf.black[1],
        'aromatic': ucsf.black[0],
        'special': ucsf.orange[0],
}
sfxn_titles = {
        'ref': 'ref2015',
        'ref_buns_02': 'ref2015 + buried_unsatisfied_penalty (weight=0.2)',
        'ref_buns_04': 'ref2015 + buried_unsatisfied_penalty (weight=0.4)',
        'ref_buns_06': 'ref2015 + buried_unsatisfied_penalty (weight=0.6)',
        'ref_buns_08': 'ref2015 + buried_unsatisfied_penalty (weight=0.8)',
        'ref_buns_10': 'ref2015 + buried_unsatisfied_penalty (weight=1.0)',
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

def parse_score_files(sfxn, probs=True):
    scores = {}
    paths = OUTPUTS / sfxn / 'score'

    for path in paths.glob('*.scores'):
        scores.update(parse_score_file(path))

    return probs_from_scores(scores) if probs else scores

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
    
def normalize_scores(scores):
    normed = {}

    for key in scores:
        min_score = min(scores[key].values())
        normed[key] = {
                k: v - min_score
                for k, v in scores[key].items()
        }

    return normed

def probs_from_scores(scores, log=False):
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
        if log:
            probs[key] = {k: np.log10(v) for k, v in probs[key].items()}

    return probs

def probs_from_counts(expected):
    probs = {}
    for key in expected:
        probs[key] = normalize(expected[key])
    return probs

def print_ranked_list(ranking, reduce=lambda x: x, reverse=False, limit=None):
    sorted_items = sorted(
            ranking.keys(),
            key=lambda x: reduce(ranking[x]),
            reverse=reverse,
    )
    for i, item in enumerate(sorted_items):
        if i and i == limit: break
        print(item, reduce(ranking[item]))


def normalize(x):
    Z = sum(x.values())
    if Z == 0: Z = 1
    return {k: x[k] / Z for k in x}

def dot_product(p1, p2):
    return sum(
            p1[k] * p2[k]
            for k in p1)


if __name__ == '__main__':
    # The PSSM looks right in this spot-check.
    #pssm = parse_pssm(INPUTS / 'pssm/1A2K.pssm')
    #pprint(pssm)

    # The scores look right in this spot check.
    #scores = parse_score_file(OUTPUTS / 'ref/score/1AK4.scores')
    #pprint(scores)

    scores = parse_score_files('ref')
    pos = Position('1AK4', 240, 'P')
    print(pos)
    pprint(scores[pos])
