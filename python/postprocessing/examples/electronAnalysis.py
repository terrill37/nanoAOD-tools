#!/usr/bin/env python
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from importlib import import_module
import os
import sys
import ROOT
from optparse import OptionParser

ROOT.PyConfig.IgnoreCommandLineOptions = True

parser = OptionParser()
parser.add_option("-i", "--input", dest="input_file", 
                  help= "input file name")

parser.add_option("-o", "--output", dest="output",
                  help= "output file name")

(o, a) = parser.parse_args()

class ElectronAnalysis(Module):
    def __init__(self):
        self.writeHistFile = True

        # helper function
        f = lambda p: (abs(p.pdgId) in [11,13] # lepton
                       and p.statusFlags & (1<<13) # last copy
                       and ((p.statusFlags & (1<<10)) # tau OR
                            or ((p.statusFlags & (1<<0)) and (p.statusFlags & (1<<8))))) # prompt+ hard proc
        self.genLeptonSelector = f

    # quick add a TH1
    def bookTH1(self, hist_name, hist_title, nbins, xlo, xhi):
        h = ROOT.TH1F(hist_name, hist_title, nbins, xlo, xhi)
        setattr(self, hist_name, h)
        self.addObject( getattr(self, hist_name) )
    
    # quick add a generic object
    def bookObject(self, obj_name, obj):
        setattr(self, obj_name, obj)
        self.addObject( getattr(self, obj_name) )

    def MakeRatio(self, ratio_name, num, den):
        r=ROOT.TGraphAsymmErrors()
        r.Divide(num, den, "b(1,1)mode")
        r.SetName(ratio_name)
        r.GetXaxis().SetTitle( num.GetXaxis().GetTitle() )
        r.GetYaxis().SetTitle( "Efficiency" )
        self.bookObject(ratio_name, r)
        
    def beginJob(self, histFile=None, histDirName=None):
        Module.beginJob(self, histFile, histDirName)

        # reco electrons
        self.bookTH1("h_ele_pt",";Reco electron p_{T} [GeV];entries",20,0,10)
        self.bookObject("h_ele_pt_eta", ROOT.TH2F("h_ele_pt_eta",";Reco electron p_{T} [GeV];Reco electron #eta", 20,0,10, 10,-2.7,2.7))

        # reco electrons matching truth
        self.bookTH1("h_ele_pt_match",";Reco electron p_{T} [GeV];entries",20,0,10)

        # truth electrons
        self.bookTH1("h_gen_ele_pt",";Gen electron p_{T} [GeV];entries",20,0,10)

        # truth electrons matching reco
        self.bookTH1("h_gen_ele_pt_match",";Gen electron p_{T} [GeV];entries",20,0,10)

        #reco muons
        self.bookTH1("h_mu_pt", ";Reco muon p_{T} [GeV];entries",20,0,10)
        self.bookObject("h_mu_pt_eta", ROOT.TH2F("h_mu_pt_eta",
                                                  ";Reco muon p_{T} [GeV];Reco muon #eta",
                                                  20,0,10, 10,-2.7,2.7))
        
        # reco muons matching truth
        self.bookTH1("h_mu_pt_match",";Reco muon p_{T} [GeV];entries",20,0,10)

        # truth muons
        self.bookTH1("h_gen_mu_pt",";Gen muon p_{T} [GeV];entries",20,0,10)

        # truth muons matching reco
        self.bookTH1("h_gen_mu_pt_match",";Gen muon p_{T} [GeV];entries",20,0,10)

    def endJob(self):
        self.MakeRatio("gen_ele_efficiency", self.h_gen_ele_pt_match, self.h_gen_ele_pt )
        self.MakeRatio("gen_mu_efficiency", self.h_gen_mu_pt_match, self.h_gen_mu_pt )

        Module.endJob(self)
        
    def analyze(self, event):
        # all reco leptons
        all_leptons = Collection(event, "LepAll")
        electrons = filter( lambda lep: abs(lep.pdgId)==11, all_leptons)
        muons = filter( lambda lep: abs(lep.pdgId)==13, all_leptons)

        # truth / generator-level leptons
        gen_particles = Collection(event, "GenPart")
        for ip, p in enumerate(gen_particles): p.idx = ip
        gen_leptons = filter(self.genLeptonSelector, gen_particles)
        gen_electrons = filter( lambda lep: abs(lep.pdgId)==11, gen_leptons)
        gen_muons = filter( lambda lep: abs(lep.pdgId)==13, gen_leptons)

        # record truth_to_reco mapping
        truth_to_reco_ele = dict()
        truth_to_reco_mu  = dict()
        
        # reco electron loop
        for ele_idx, ele in enumerate(electrons):
            self.h_ele_pt.Fill( ele.pt )
            self.h_ele_pt_eta.Fill( ele.pt, ele.eta )
            isTruthMatch = (ele.genPartIdx >= 0 and ele.genPartFlav==1)
            if isTruthMatch:
                truth_to_reco_ele[ele.genPartIdx] = ele_idx
                self.h_ele_pt_match.Fill( ele.pt )
            
        # gen electron loop
        for gen_ele in gen_electrons:
            self.h_gen_ele_pt.Fill( gen_ele.pt )
            isRecoMatch = (gen_ele.idx in truth_to_reco_ele)
            if isRecoMatch:
                self.h_gen_ele_pt_match.Fill( gen_ele.pt )
            
        # reco muon loop
        for mu_idx, mu in enumerate(muons):
            self.h_mu_pt.Fill( mu.pt )
            self.h_mu_pt_eta.Fill( mu.pt, mu.eta )
            isTruthMatch = (mu.genPartIdx >= 0 and mu.genPartFlav==1)
            if isTruthMatch:
                truth_to_reco_mu[mu.genPartIdx] = mu_idx
                self.h_mu_pt_match.Fill( mu.pt )

        # gen electron loop
        for gen_mu in gen_muons:
            self.h_gen_mu_pt.Fill( gen_mu.pt )
            isRecoMatch = (gen_mu.idx in truth_to_reco_mu)
            if isRecoMatch:
                self.h_gen_mu_pt_match.Fill( gen_mu.pt )

        # return True to keep the event if we're saving another tree
        return True


preselection = "GenMET_pt>50"
files = ["file:"+o.input_file]
p = PostProcessor(".", files, cut=preselection, branchsel=None, modules=[
                  ElectronAnalysis()], noOut=True, histFileName=o.output, histDirName="plots1")

p.run()
