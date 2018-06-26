***********************************************
Benchmark the buried unsatisfied H-bond penalty
***********************************************

I've come to believe that the number of buried unsatisfied H-bonds is an 
important metrics for loop design projects.  Buried unsatisfied H-bonds are 
very unfavorable, and it can be difficult to design backbones that satisfy all 
their H-bonds.  Unlike sidechains, the backbone unavoidably contains a lot of 
polar atoms.  Consequently, 68% of H-bonds in proteins involve the backbone 
[Sticke1992]_.  Movements to the backbone (e.g.  to satisfy one H-bond) also 
propagate and may cause other H-bonds to become buried.  Most 

We've been using the BuriedUnsatHbonds filter to count the number of buried 
unsatisfied H-bonds in a design, and to move forward accordingly.  However, 
since Rosetta itself doesn't make much of an effort to avoid burying polar 
residues, almost all of our designs have some buried unsats.

We think we'd get better designs if rosetta was aware of buried unsats dring 
the design process.  Fortunately, Vikram recently added a 
non-pairwise-decomposable "design-centric" score term to do just this: 
`buried_unsatsified_penalty`.  This term and others are outlined here:

https://www.rosettacommons.org/docs/latest/rosetta_basics/scoring/design-guidance-terms

Although this sounds like a promising term, I'd like to have some idea how well 
it works before using it.  To my knowledge, Vikram has not published any 
benchmarking results.  It's also not clear what the weight of the score term 
should be.  The documentation suggests a weight between 0.1 and 1.0, but warns 
that this should be optimized for each system. 

The plan is to perform a sequence recovery benchmark using FastDesign on a set 
of polar, dry interfaces.

Notes
=====
2018/06/23:

- It's not really appropriate to use this score term for design, since it's not 
  accounted for in the reference term and (as it can only be a penalty) is 
  clearly biased towards residues that can't make H-bonds.

  That said, I guess you just don't want rotamers that make buried unsats.

- I'm coming to think that sequence recovery isn't the right benchmark.  What's 
  important to us is getting backbone H-bonds right, 

2018/06/24:

- I don't think [Park2016]_ describes how the data in the protein-protein 
  interaction row of Table 1 was aggregated, e.g. mean, median, etc.  But I 
  think it's a mean, because that gives better agreement with the data I 
  collected (median: 0.146, mean: 0.300, paper: 0.316).  The difference could 
  be attributable to the fact that I enabled extra rotamers.

  It should be said that I think it's completely inappropriate to be averaging 
  probabilities like this.  First, it just doesn't make sense to average 
  probabilities; probabilities are multiplied.  Second, I haven't plotted it 
  yet, but the difference between the mean and the median makes it clear that 
  the majority of the positions have very low overlaps and that the average is 
  being inflated by a long tail.  Third, I would bet that the positions which 
  scored well (and are thus driving the average) are basically just the easiest 
  and most conserved.
  
  The median is probably a better metric than the mean, but the best thing 
  would be to make plots.

2018/06/25:

- I plotted the frequency of each mutation according to PSI-BLAST against the 
  frequency of each mutation that you would derive from considering the Rosetta 
  scores.  I'm struck by the total lack of correlation.  I didn't think 
  sequence recovery was such a hard task; I'm worried that I'm doing something 
  totally wrong.  I'm also worried that overlapping points may be playing a 
  significant role, maybe I should try making a 2D histogram.

  .. figure:: ref.svg
  
  At the same time, though, I can see that predicting amino acid frequencies 
  could be a lot harder than figuring out which amino acids fit best.  I think 
  I should try coming up with some easier metrics.  Tanja might have some good 
  advice, here.

- I need to look into corner cases better.  I know from debugging the analysis 
  script that there are some mutations with very high scores (e.g. ΔREU≈400), 
  even with just ref2015.  I need to figure out what's going on with that.


Methods
=======

Benchmark set
-------------
Tanja recommended that I consider using the protein/proeint interface sequence 
recovery benchmark from the ref2015 paper [Park2016]_.  In turn, they used a 
subset of the ZDOCK 4 benchmark [Hwang2010]_.  There is now a ZDOCK 5 benchmark 
available [Vreven2015]_.  The ZDOCK benchmarks are based on interfaces for 
which both bound and unbound (for at least one of the partners) structures are 
available.  The idea is that proteins change conformation upon binding, so it's 
not enough to simply find bound complexes.  This consideration isn't important 
for us (I don't think; maybe is would be interesting to do the benchmark on the 
unbound structures...), but it's probably still best to stick to the 
established set.

It's not clear to me how the structures were picked.

It's also not clear how [Park2016]_ chose which residues to design.

- Relax in rosetta?

- Define interface residues?

Picking a weight
----------------
If N is the number of buried unsatisfied H-bonds, the buried unsatisfied 
penalty is (5×N)².  This seems arbitrary to me, but I'm curious enough to ask 
Vikram about the rationale here.  My thought is that 5×N would've made more 
sense, since the energy of desolvating an amide H-bond from vacuum is about 6 
kcal/mol [Baldwin2003]_, and the rosetta score function is nearly in kcal/mol.  
Take into account that the energy of desolvating an H-bond depends on its 
charge, and the van der Waals interactions in a protein would be more 
stabilizing than a vacuum, and maybe you get 5 as a reasonable coefficient.


References
==========
_ Sticke1992: :pubmed:`10.1016/0022-2836(92)91058-W`
_ Baldwin2003: :pubmed:`10.1074/jbc.X200009200`
_ Park2016: :pubmed:`10.1021/acs.jctc.6b00819`
_ Hwang2010: :pubmed:`10.1002/prot.22830`
_ Vreven2015: :pubmed:`10.1016/j.jmb.2015.07.016`
