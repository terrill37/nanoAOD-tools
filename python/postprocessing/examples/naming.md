<!-- Plot Naming Conventions -->
## Plot Naming Conventions
This lists the naming conventions along with a short description for what they are defined to be. They are created by leptonInternal.py and electron_lepRecl.py. Each convention can be used with almost any other within reason.

### leptons
1. h_ele_*
   histogram from electrons
2. h_mu_*
   histogram from muons

### lepton pt
1. *_lower_*
    leptons with pt below 5 GeV
2. *_upper_*
    leptons with pt above 5 GeV

### matching
1. *_match_*
    gen Leptons matched to reco leptons
2. *_unmatch_*
    reco electrons not matched to gen leptons

### region
1. *_barrel_*
    leptons in the barrel region (eta <= 1.47)
2. *_endcap_*
    leptons in the endcap region (1.47<eta<2.5, 2.5 for electrons and 2.4 for muons)
3. *_outer_*
    leptons outside the detector (eta>2.5 for electrons, 2.4 for muons)
    used for book keeping purposes
4. *_inner_*
    leptons inside the detector (eta < 2.5 or 2.4 for muons)

## Matching Convention
The standard electrons are matched slightly differently to those of the newer low pt collection. Here is the procedures used for the low pt objects:

### low pt leptons
helper matching function used
    <br/>
    ```sh
    f = lambda p: (abs(p.pdgId) in [11, 13] #lepton
                   and p.statusFlags & (1<<13) # last copy
                   and ((p.statusFlags & (1<<10) #tau or
                        or ((p.statusFlags & (1<<0)) and (p.statusFlags & (1<<8))))) # prompt + hard proc
    ```

look for nearest gen electron to reco electron in a given event
    <br/>
    ```sh
    def truthMatch(self, reco, gen_lep_col):
        best_dR=9e9
        isMatch=False
        for gen_lep in gen_lep_col:
            dr = gen_lep.p4().DeltaR(reco.p4())
            if dr<0.1 and dr<best_dR:
                best_dR = dr
                reco.genPartIdx = gen_lep.idx
                isMatch = True
        return isMatch
    ```

