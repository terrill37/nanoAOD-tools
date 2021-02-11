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

parser.add_option("-c", "--collection", dest="collect",
                  default = "LepAll", help= "collection name")

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
        self.bookTH1("h_ele_pt_match",        ";Reco electron p_{T} [GeV];entries",20,0,10)
        self.bookTH1("h_ele_pt_match_barrel", ";Reco electron barrel p_{T} [GeV];entries",20,0,10)
        self.bookTH1("h_ele_pt_match_endcap", ";Reco electron endcap p_{T} [GeV];entries",20,0,10)
        self.bookTH1("h_ele_pt_match_out", ";Reco electron endcap p_{T} [GeV];entries",20,0,10)
    
        # truth electrons
        self.bookTH1("h_gen_ele_pt",        ";Gen electron p_{T} [GeV];entries",20,0,10)
        self.bookTH1("h_gen_ele_pt_barrel", ";Gen electron barrel p_{T} [GeV];entries",20,0,10)
        self.bookTH1("h_gen_ele_pt_endcap", ";Gen electron endcap p_{T} [GeV];entries",20,0,10)
        self.bookTH1("h_gen_ele_pt_out",    ";Gen electron out p_{T} [GeV];entries",20,0,10)
        self.bookTH1("h_gen_ele_pt_inner",  ";Gen electron inner p_{T} [GeV];entries",20,0,10)

        # truth electrons matching reco
        self.bookTH1("h_gen_ele_pt_match",        ";Gen electron p_{T} [GeV];entries",20,0,10)
        self.bookTH1("h_gen_ele_pt_match_barrel", ";Gen electron barrel p_{T} [GeV];entries",20,0,10)
        self.bookTH1("h_gen_ele_pt_match_endcap", ";Gen electron endcap p_{T} [GeV];entries",20,0,10)
        self.bookTH1("h_gen_ele_pt_match_out",    ";Gen electron outside p_{T} [GeV];entries",20,0,10)
        self.bookTH1("h_gen_ele_pt_match_inner",  ";Gen electron inside p_{T} [GeV];entries",20,0,10)

        # truth electrons not matched to reco
        self.bookTH1("h_ele_pt_unmatch",        ";Unmatched electron p_{T} [GeV];entries",20,0,10)
        self.bookTH1("h_ele_pt_unmatch_barrel", ";Unmatched electron barrel p_{T} [GeV];entries",20,0,10)
        self.bookTH1("h_ele_pt_unmatch_endcap", ";Unmatched electron endcap p_{T} [GeV];entries",20,0,10)
        self.bookTH1("h_ele_pt_unmatch_out",    ";Unmatched electron out p_{T} [GeV];entries",20,0,10)

        ###
        ### add pt of electrons not matched to gen-level
        ### lepAll_genPartIdx=-1 is fake
        ### Electron_genPartFlav!=1 is fake
        ### 
        ###

    def endJob(self):
        self.MakeRatio("gen_ele_efficiency",        self.h_gen_ele_pt_match,        self.h_gen_ele_pt )
        self.MakeRatio("gen_ele_efficiency_barrel", self.h_gen_ele_pt_match_barrel, self.h_gen_ele_pt_barrel)
        self.MakeRatio("gen_ele_efficiency_endcap", self.h_gen_ele_pt_match_endcap, self.h_gen_ele_pt_endcap)
        self.MakeRatio("gen_ele_efficiency_out",    self.h_gen_ele_pt_match_out,    self.h_gen_ele_pt_out)
        self.MakeRatio("gen_ele_efficiency_inner",  self.h_gen_ele_pt_match_inner,  self.h_gen_ele_pt_inner)
        #self.MakeRatio("gen_mu_efficiency", self.h_gen_mu_pt_match, self.h_gen_mu_pt )

        Module.endJob(self)
        
    def analyze(self, event):
        # all reco leptons
        leptons = Collection(event, o.collect)

        electrons = filter( lambda lep: abs(lep.pdgId)==11, leptons)
        muons = filter( lambda lep: abs(lep.pdgId)==13, leptons)

        # truth / generator-level leptons
        gen_particles = Collection(event, "GenPart")
        for ip, p in enumerate(gen_particles): 
            p.idx = ip
        
        gen_leptons          = filter(self.genLeptonSelector, gen_particles)
        gen_electrons        = filter(lambda lep: abs(lep.pdgId)==11, gen_leptons)
        
        #FIXME might remove
        gen_electrons_barrel = filter(lambda lep: abs(lep.eta)<=1.47, gen_electrons)
        gen_electrons_endcap = filter(lambda lep: 2.5>abs(lep.eta)>1.47, gen_electrons)
        gen_electrons_out    = filter(lambda lep: 2.5<=abs(lep.eta), gen_electrons)

        gen_muons = filter( lambda lep: abs(lep.pdgId)==13, gen_leptons)

        # record truth_to_reco mapping
        truth_to_reco_ele = dict()
        truth_to_reco_ele_barrel = dict()
        truth_to_reco_ele_endcap = dict()

        truth_to_reco_mu  = dict()
        truth_to_reco_unmatchedEle=dict()

        # reco electron loop
        for ele_idx, ele in enumerate(electrons):
            self.h_ele_pt.Fill( ele.pt )
            self.h_ele_pt_eta.Fill( ele.pt, ele.eta )
            isTruthMatch = (ele.genPartIdx >= 0 and ele.genPartFlav==1)
            barrel_eta = (abs(ele.eta)<=1.47)
            endcap_eta = (2.5>abs(ele.eta)>1.47)
            out_eta    = (2.5<=abs(ele.eta))
            if isTruthMatch:
                truth_to_reco_ele[ele.genPartIdx] = ele_idx
                self.h_ele_pt_match.Fill( ele.pt )
                if barrel_eta: 
                    self.h_ele_pt_match_barrel.Fill( ele.pt )
                if endcap_eta:
                    self.h_ele_pt_match_endcap.Fill( ele.pt )
                if out_eta:
                    self.h_ele_pt_match_out.Fill( ele.pt )
            
            if not isTruthMatch:
                truth_to_reco_unmatchedEle[ele.genPartIdx] = ele_idx
                self.h_ele_pt_unmatch.Fill( ele.pt )
                if barrel_eta:
                    self.h_ele_pt_unmatch_barrel.Fill( ele.pt )
                if endcap_eta:
                    self.h_ele_pt_unmatch_endcap.Fill( ele.pt )
                
                #for book keeping
                if out_eta:
                    self.h_ele_pt_unmatch_out.Fill( ele.pt )

        # gen electron loop
        for gen_ele in gen_electrons:
            self.h_gen_ele_pt.Fill( gen_ele.pt )
            
            isRecoMatch = (gen_ele.idx in truth_to_reco_ele)
            
            barrel_eta = (abs(gen_ele.eta) <= 1.47)
            endcap_eta = (1.47 < abs(gen_ele.eta) < 2.5)
            out_eta    = (2.5 <= abs(gen_ele.eta))
            
            if barrel_eta:
                self.h_gen_ele_pt_barrel.Fill( gen_ele.pt )

            if endcap_eta:
                self.h_gen_ele_pt_endcap.Fill( gen_ele.pt )

            if out_eta:
                self.h_gen_ele_pt_out.Fill( gen_ele.pt )
            
            if not out_eta:
                self.h_gen_ele_pt_inner.Fill( gen_ele.pt )

            if isRecoMatch:
                self.h_gen_ele_pt_match.Fill( gen_ele.pt )
                
                if barrel_eta:
                    self.h_gen_ele_pt_match_barrel.Fill( gen_ele.pt )

                if endcap_eta:
                    self.h_gen_ele_pt_match_endcap.Fill( gen_ele.pt )

                if out_eta:
                    self.h_gen_ele_pt_match_out.Fill( gen_ele.pt )

                if not out_eta:
                    self.h_gen_ele_pt_match_inner.Fill( gen_ele.pt )
        

        # return True to keep the event if we're saving another tree
        return True


preselection = "GenMET_pt>50"
files = ["file:"+o.input_file]
p = PostProcessor(".", files, cut=preselection, branchsel=None, modules=[
                  ElectronAnalysis()], noOut=True, histFileName=o.output, histDirName="plots1")

p.run()
