#!/usr/bin/env python3

"""
Calculate sequence tolerance with or without the score function term accounting 
for buried unsatisfied H-bonds.

Usage:
    ./analysis.py <sfxn> [options]

Arguments:
    <sfxn>
        One of the score functions tested in the benchmark.  Valid options are: 
        'ref' and 'ref_buns'.

Options:
    -v --verbose
        Print out debugging information.
"""

import os
import docopt
from pathlib import Path
from attr import attrs, attrib
import matplotlib.pyplot as plt
from math import *
from statistics import *
from color_me import ucsf

BENCHMARK = Path('park2016')

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


def parse_logs(sfxn):
    scores = {}
    logs = BENCHMARK / 'logs' / sfxn

    for log in logs.glob('seq_recov.sh.o*'):
        scores.update(parse_log(log))

    return probs_from_scores(scores)

def parse_log(log):
    with log.open() as file:
        lines = file.readlines()

    scores = {}
    wildtypes = {}

    for line in lines:

        # Figure out which PDB this file is for.

        if line.startswith('protocols.jd2.PDBJobInputter: pushed'):
            pdb_path = Path(line.split()[2])
            pdb = pdb_path.stem

        # Figure out what the wildtype residues were.

        if line.startswith('protocols.protein_interface_design.filters.FilterScanFilter: Mutating residue'):
            code = line.split()[3]
            resi = int(code[3:])
            resn = aa_table[code[:3]]
            wildtypes[resi] = resn

        # Get the data

        if line.startswith('ResidueScan:'):
            tokens = line.split()
            resi=int(tokens[2])
            resn=tokens[3]
            score=float(tokens[4])

            pos = Position(
                    pdb=pdb,
                    resi=resi,
                    wt=wildtypes[resi],
            )
            if pos not in scores:
                scores[pos] = {}
            scores[pos][resn] = score

    return scores

def parse_pssms():
    counts = {}
    paths = BENCHMARK / 'pssm'

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


def compare(results, expected):
    overlaps = []
    for pos in results:
        overlap = dot_product(results[pos], expected[pos])
        overlaps.append(overlap)
        #print(f"{pos.pdb} {pos.wt}{pos.resi}: {overlap:.3f}")

    print(median(overlaps))

def plot(sfxn, results, expected):
    xs = {
            'positive': [],
            'negative': [],
            'polar': [],
            'nonpolar': [],
            'aromatic': [],
            'special': [],
    }
    ys = {
            'positive': [],
            'negative': [],
            'polar': [],
            'nonpolar': [],
            'aromatic': [],
            'special': [],
    }
    cs = {
            'positive': ucsf.blue[0],
            'negative': ucsf.red[0],
            'polar': ucsf.purple[0],
            'nonpolar': ucsf.dark_grey[0],
            'aromatic': ucsf.black[1],
            'special': ucsf.orange[0],
    }
    titles = {
            'ref': 'ref2015',
            'ref_buns': 'ref2015 + buried_unsatisfied_penalty (weight=1.0)',
    }

    for pos in results:
        for mut in results[pos]:
            type = aa_types[mut]
            xs[type].append(expected[pos][mut])
            ys[type].append(results[pos][mut])

    fig, axes = plt.subplots(2, 3, sharex='all', sharey='all')
    fig.suptitle(titles.get(sfxn, sfxn))

    for ax, type in zip(axes.flat, xs):
        ax.set_title(type)
        ax.plot(xs[type], ys[type], 'o', color=cs[type], markersize=0.5)
    for i in range(2):
        axes[i,0].set_ylabel('Rosetta frequency')
    for j in range(3):
        axes[-1,j].set_xlabel('PSI-BLAST frequency')

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(f'{sfxn}.svg')
    plt.savefig(f'{sfxn}.png', dpi=600)
    plt.show()

args = docopt.docopt(__doc__)
sfxn = args['<sfxn>']
verbose = args['--verbose']

results = parse_logs(sfxn)
expected = parse_pssms()

compare(results, expected)

if os.fork() == 0:
    plot(sfxn, results, expected)

#print(compare(results, pssm[150]))

