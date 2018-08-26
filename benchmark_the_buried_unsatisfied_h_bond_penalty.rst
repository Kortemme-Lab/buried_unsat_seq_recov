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

Methods
=======

Benchmark set
-------------
Tanja recommended that I consider using the protein/proeint interface sequence 
recovery benchmark from the ref2015 paper [Park2016]_.  In turn, they used a 
subset of the ZDOCK 4 benchmark [Hwang2010]_.  There is now a ZDOCK 5 benchmark 
available [Vreven2015]_, although I'm not using it here.  The ZDOCK benchmarks 
are based on interfaces for which both bound and unbound (for at least one of 
the partners) structures are available.  The idea is that proteins change 
conformation upon binding, so it's not enough to simply find bound complexes.  
This consideration isn't important for us (I don't think; maybe is would be 
interesting to do the benchmark on the unbound structures...), but it's 
probably still best to stick to the established set.

It wasn't clear to me how [Park2016]_ chose which residues to design, so I 
emailed Hahnbeom and get him to send me all the input files.  He didn't send me 
any analysis scripts, so I wrote those from scratch based on what was described 
in the paper.

- Relax in rosetta?

- Define interface residues?

Picking a weight
----------------
If N is the number of buried unsatisfied H-bonds, the buried unsatisfied 
penalty in master is (5×N)².  This seems arbitrary to me, but I'm curious 
enough to ask Vikram about the rationale here.  My thought is that 5×N would've 
made more sense, since the energy of desolvating an amide H-bond from vacuum is 
about 6 kcal/mol [Baldwin2003]_, and the rosetta score function is nearly in 
kcal/mol.  Take into account that the energy of desolvating an H-bond depends 
on its charge, and the van der Waals interactions in a protein would be more 
stabilizing than a vacuum, and maybe you get 5 as a reasonable coefficient.


Results
=======
.. figure:: native_recovery.svg

Case studies
============
I wanted to look at a couple of specific cases to get a more intuitive feel for 
the benchmakr, and why the buried unsat penalty isn't helping as much as I 
think it should.  Is the code broken, is there some confounding factor, what?

1AK4 P240
---------
This position stood out to me because the native residue (Pro) scores a lot 
worse than any other residue, even with just ref2015.  When I looked at the 
structure, it seemed clear to me that anything other than Pro would in fact 
create a buried unsatisfied backbone amide H-bond at that position.  


The buried unsat penalty does correctly identify this, but is not stong enough 
to make proline the preferred amino acide:

=== === === =========== =========== ==========
#   Wt  Mut ref2015     ref_buns_10  Δ + 330
=== === === =========== =========== ==========
240	P	A	-363.852699	-33.852383	-0.0003160
240	P	C	-362.475716	-32.449308	-0.0264080
240	P	D	-364.117705	-34.126733	 0.0090280
240	P	E	-364.615257	-34.590181	-0.0250760
240	P	F	-360.960073	-30.929833	-0.0302400
240	P	G	-361.693290	-31.691957	-0.0013330
240	P	H	-362.685125	-32.694122	 0.0089970
240	P	I	-362.313195	-32.312959	-0.0002360
240	P	K	-364.672997	-34.680188	 0.0071910
240	P	L	-365.245612	-35.244684	-0.0009280
240	P	M	-364.108912	-34.117267	 0.0083550
240	P	N	-364.296828	-34.268200	-0.0286280
240	P	P	-350.690779	-15.671559	-5.0192200
240	P	Q	-364.099368	-34.106122	 0.0067540
240	P	R	-364.044313	-34.013912	-0.0304010
240	P	S	-363.697364	-33.695779	-0.0015850
240	P	T	-361.565784	-31.575691	 0.0099070
240	P	V	-362.056089	-32.054118	-0.0019710
240	P	W	-360.587982	-30.587108	-0.0008740
240	P	Y	-361.654416	-31.653135	-0.0012810
=== === === =========== =========== ==========

Why is P240 so bad?  I compared the per-residue scores for P240 and P240A:

- fa_atr: 0.9 REU 
- fa_rep: 1.5 REU
- pro_close: 1.0 REU
- p_aa_pp: -0.9 REU
- ref: -2.9 REU
- total: -1.6 REU

What?  The proline scores almost 2 REU better alanine?  What's scoring so 
badly, then?

- I57 score 6.3 REU worse
- P58 scores 1.6 REU worse
- F60 scores 5.9 REU worse
- A239 scores 1.5 REU worse
- P240 scores 2.4 REU better

Ok.  What's happening is that P240 pushes F60 into a rotamer that clashes with 
I57, and also a little bit with (probably) the backbone carbonyl of P58.

Interestingly, even for P240 rosetta actually gets the wrong rotamer F240, 

The input structure has a score of -358.29, which is markedly better than P240.  
I'm not including native rotamers, and I shouldn't, since that would bias me 
towards the answer I want to get.  But maybe the right Phe rotamer isn't in the 
set.  I should use -exaro.

More specifically, I had the LimitAromaChi2 setting on, which is really just 
for design::

    <LimitAromaChi2 name="aro" include_trp="yes"/>

It just eliminates some less common aromatic rotamers.  But I'll 
bet it's getting rid of the rotamer I need here.

I also added ``ex1aro="yes" ex2aro="yes"`` to  ExtraRotamersGeneric for good 
measure.

2OT3 T303
---------
2OT3 is the PDB with the biggest difference in native recovery prediction 
accuracy, averaged across all positions, between ref and ref_buns_10.  It is 
2.1Å with R-free = .243, and has slightly above average clashes and rama 
outliers.  T303 is the position with the second biggest difference in accuracy 
in this PDB.  The position with the biggest difference (C222) I'm putting aside 
for now, because it's a cysteine, and I suspect there's something broken about 
cysteines specifically, aside from anything else.  Threonine, in contrast, 
seems likely to be interesting::
   
   $ ./describe_position.py 2OT3 303
   Position(pdb='2OT3', resi=303, wt='T')

   ref / ref_buns
   22.584717205879137

   ref scores
   Y 0.0
   F 0.21778199999994285
   T 6.937962999999968
   W 7.522968999999989
   C 7.979802999999947
   A 9.369907000000012
   V 10.014802999999915
   S 10.379777999999988
   N 13.650672999999983
   D 14.492207000000008
   G 14.57633199999998
   R 15.634731999999985
   K 16.632700999999997
   Q 18.770547999999962
   H 21.979691000000003
   E 23.54226899999992
   M 23.975516999999968
   I 24.50425999999993
   L 38.85974299999998
   P 206.07224299999996

   ref probs
   P -153.9344258994053
   L -29.21242609299569
   I -18.50482619498015
   M -18.11044249553402
   E -17.787287486356274
   H -16.62177741376308
   Q -14.228112271355988
   K -12.63351525785443
   R -11.889140947173088
   G -11.099691805541303
   D -11.036943875609564
   N -10.409252743755845
   S -7.969527450749725
   V -7.6972965357203265
   A -7.21627556667111
   C -6.179411989971416
   W -5.838664437847286
   T -5.402314773684911
   F -0.3898042653135817
   Y -0.22736302101765657

   ref_buns scores
   H 0.0
   F 12.725914
   Y 14.405113999999998
   V 35.627251
   W 37.022813
   R 37.107245999999996
   T 37.521701
   G 39.833653999999996
   A 40.233581
   S 41.207181999999996
   C 43.940846
   N 45.062219999999996
   D 46.693365
   K 48.286155
   M 48.915396
   I 50.725616
   Q 53.647114
   E 58.752374
   L 66.496936
   P 217.068571

   ref_buns probs
   P -161.90910530172272
   L -49.599347171673934
   E -43.82276192676265
   Q -40.01480356999105
   I -37.83568972987488
   M -36.485466161125174
   K -36.016122087684586
   D -34.828077210228344
   N -33.61142375205849
   C -32.775002983210996
   S -30.735992497279685
   A -30.00979401490833
   G -29.711492780152682
   T -27.987031979564048
   R -27.677894466341254
   W -27.614916802532303
   V -26.573982162515364
   Y -10.744619125627574
   F -9.492121961390911
   H -1.4766920076784994e-10

The reason for the dramatic prediction error seems to be that rosetta just 
really likes histidine (ΔREU=37).  Comparing T303H with T303T, I found that 
this score difference breaks down as follows:

- 25 REU: buried unsat term
- 1 REU: D71, fa_elec, hbond_sc; doesn't move, score changes due to R208 
  moving.
- 5 REU: R208, fa_dun; very far from T303, shouldn't have been repacked.
- 1 REU: T219, fa_elec; no discernable difference in electronic environment.
- 1 REU: N220, fa_dun; seems like both amide N and O are buried unsats, 
  although pymol thinks the N is H-bonding with the backbone of an α-helix.  I 
  assumed this couldn't happen, but if this structure is right, maybe it does?  
  I should look into that.  Quick search just reveals some discussion of helix 
  caps.
- 2 REU: C223, fa_rep; Almost identical conformation, ΔREU is probably due to 
  Y316 being slightly closer.
- -5 REU: T303
- 3 REU: Y316, fa_rep; Yup, probably this has to do with C223.

There must be 5 buried unsatisfied H-bonds in the T303T structure, but I can't 
find them.  In fact, T303 looks satisfied (nicely using a sidechain H-bond to 
finish off a strand), while H303 looks to introduce at least 1, probably 2 
buried unsatisfied H-bonds.

I need to get rosetta to tell me where these buried unsats are.  But my guess 
in this case is that they're far from the interaction in question, seeing as 
how residues as far away as R208 are being repacked (disadvantageously).  In 
fact, I worry that the repacking step isn't doing what I think it is, because 
R208 (in the T303 prediction but not the H303 one) is in a conformation that 
costs 6 REU, with nothing seeming to preclude the penalty-free conformation.  I 
wonder if the H303 (penalty-free) conformation is really available to T303, and 
if so, if rotamer trials could've found it.

This is a case where I can definitely use clash-based repack shell, since we're 
not doing any relaxing.  It might be appropriate to write my own pilot app 
(wish I could use pyrosetta, but it would take too long to set up.  I need my 
custom changes to the buried_unsat score term)::

   - Determine clash-based repack shell for position.
   - For each mutation:
      - repack
      - rotamer trials (just to be sure nothing stupid was missed).

Notes
=====
2018/06/23:

- It's not really appropriate to use this score term for design, since it's not 
  accounted for in the reference term and (as it can only be a penalty) is 
  clearly biased towards residues that can't make H-bonds.

  That said, I guess you just don't want rotamers that make buried unsats.

- I'm coming to think that sequence recovery isn't the right benchmark.  What's 
  important to us is getting backbone H-bonds right, and that would be better 
  tested by the loop modeling benchmark.

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

2018/06/26:

- On Tanja's suggestion, I plotted the results for just the wildtype amino 
  acid, e.g. "native recovery".  These were a lot better.

  .. figure:: ref_wt.svg
  
  I plotted the results for just native recovery

  Relaxing did move the starting structures a lot, and may have made the native 
  recovery case too easy.  

2018/07/08:

- The buried unsat penalty uses the method of "sidechain neighbor cones" to 
  determine burial.  This method is implemented by 
  ``core::select::util::determine_whether_point_is_buried()``, which is defined 
  in ``core/select/util/burial_utilities.cc``.  In pseduocode, the algorithm 
  works like this:

  - Iterate through each residue in the pose.
  - Define a fuzzy cone from the Cα-Cβ vector for that residue.
  - Add up the degree to which that cone overlaps the given coordinate.
  - Return true if the number of overlaps exceeds a certain threshold.

  Note that the size of the cone does not depend on the identity of the residue 
  in question.

2018/07/09:

- The sidechain neighbor cone method described above is not very accurate.  I 
  modified ``FilterScan`` to call the ``PolarGroupBurialPyMolStringMetric``, 
  which prints pymol commands to highlight the polar groups that the 
  ``buried_unsat_penalty`` considers to be either buried (orange) or exposed 
  (teal).  For example, consider the 1AK4 structure from the interface 
  benchmark:

  :download:`buried_vs_exposed.pse`

  It's hard for me to confidently say what's buried and what isn't, but it's 
  pretty easy to find examples that don't look right.  For example, N35 looks 
  clearly wrong in the above pymol session.  W119 is also questionable, and 
  it's one of the residues involved in the benchmark interface.

  One takeaway is that when I try to incorporate buried unsats into the loop 
  modeling protocol, I should just use the ``BuriedUnsatHbonds``.  It 
  determines burial by computing "VSASA".  I'm not sure exactly what that is, 
  but I think it's based on querying discrete points around each atom/rotamer 
  to see which are buried.  [LeaverFay2007]_ may be relevant.  If I want to dig 
  deeper, the relevant code is in ``protocols/vardist_solaccess``.

References
==========
.. [Sticke1992] :doi:`10.1016/0022-2836(92)91058-W`
.. [Baldwin2003] :doi:`10.1074/jbc.X200009200`
.. [Park2016] :doi:`10.1021/acs.jctc.6b00819`
.. [Hwang2010] :doi:`10.1002/prot.22830`
.. [Vreven2015] :doi:`10.1016/j.jmb.2015.07.016`
.. [LeaverFay2007] :doi:`10.1002/jcc.20626`
