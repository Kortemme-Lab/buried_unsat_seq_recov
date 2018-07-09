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

import os, docopt
from analysis_helpers import *

def plot(sfxn, results, expected, native_only=True):
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

    xs = {k: [] for k in aa_types}
    ys = {k: [] for k in aa_types}

    for pos in results:
        for mut in results[pos]:
            if native_only and mut != pos.wt:
                continue
            #type = aa_types[mut]
            type = mut
            xs[type].append(expected[pos][mut])
            ys[type].append(results[pos][mut])

    fig, axes = plt.subplots(4, 5, sharex='all', sharey='all', figsize=(11,8.5))
    fig.suptitle(sfxn_titles.get(sfxn, sfxn))

    for ax, type in zip(axes.flat, xs):
        ax.set_title(f"{type} (N={len(xs[type])})")
        ax.plot(xs[type], ys[type], 'o', color=type_colors[aa_types[type]], markersize=0.5)
    for i in range(4):
        axes[i,0].set_ylabel('Rosetta\nfrequency')
    for j in range(5):
        axes[-1,j].set_xlabel('PSI-BLAST\nfrequency')

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    #plt.savefig(f'{sfxn}_wt.svg')
    #plt.savefig(f'{sfxn}_wt.png', dpi=600)
    plt.show()


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    sfxn = args['<sfxn>']

    results = parse_score_files(sfxn)
    expected = parse_pssms()

    if os.fork() == 0:
        plot(sfxn, results, expected)

