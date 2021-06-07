#!/usr/bin/env python
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from PhysicsTools.NanoAODTools.postprocessing.examples.leptonInternal import LeptonAnalysis_steps
from importlib import import_module
import os
import sys
import ROOT
from optparse import OptionParser

#python/CMGTools/TTHAnalysis/tools/nanoAOD/susySOS_modules
#from .CMGTools.TTHAnalysis.tools.nanoAOD.susySOS_modules import * 

from CMGTools.TTHAnalysis.tools.nanoAOD.susySOS_modules import *


ROOT.PyConfig.IgnoreCommandLineOptions = True

parser = OptionParser()
parser.add_option("-i", "--input", dest="input_file", 
                  help= "input file name")

parser.add_option("-o", "--output", dest="output",
                  help= "output file name")

parser.add_option("-p", "--output2", dest="output2",
                  help= "output file 2 name")

parser.add_option("-c", "--collection", dest="collect",
                  default = "LepGood", help= "collection name")

parser.add_option("--pfRelIso03_all", dest="pfRelIso03_all",
                  default = False, action="store_true", help="turn on pfRelIso03_all cut")

parser.add_option("--pfRelIso03_allxPT", dest="pfRelIso03_allxPT",
                  default = False, action="store_true", help="turn on pfRelIso03_all*pT cut")

parser.add_option("--ip3d", dest="ip3d",
                  default = False, action="store_true", help="turn on ip3d cut")

parser.add_option("--sip3d", dest="sip3d",
                  default = False, action="store_true", help="turn on sip3d cut")

parser.add_option("--deepCSV", dest="BTagDeepCSV",
                  default = False, action="store_true", help="turn on deepCSV cut")

parser.add_option("--lostHits", dest="lostHits",
                  default = False, action="store_true", help="turn on lostHits cut")

parser.add_option("--VLooseFOEleID", dest="VLooseFOEleID",
                  default=False, action="store_true", help="turn on VLooseFOEleID")

parser.add_option("--convVeto", dest="convVeto",
                  default=False, action="store_true", help="turn on convVeto")

parser.add_option("--tightEleID", dest="tightEleID", 
                  default=False, action="store_true", help="turn on tightEleID")

parser.add_option("--miniPFRelIso_cut", dest="miniPFRelIso_cut",
                  default=0.5, help="sets selection upper bound on miniPFRelIso")

parser.add_option("--miniPFRelIsoxPT_cut", dest="miniPFRelIsoxPT_cut",
                  default=5.0, help="sets selection upper bound on miniPFRelIsoxPT")

parser.add_option("--softId", dest="softId",
                  default=False, action="store_true", help="turn on softId for muons")

parser.add_option("-l", "--lepton", dest="lepton",
                  default='electron', help="sets lepton to muon or electron in analysis")

(o, a) = parser.parse_args()           

class ElectronAnalysis(Module):
    def __init__(self, pfRelIso03_all, pfRelIso03_allxPT, ip3d, sip3d, BTagDeepCSV, lostHits_on, 
                 VLooseFOEleID_on, tightEleID_on, convVeto, softId, miniPF_cut, miniPFxPT_cut, 
                 lepton='electron'):
        self.writeHistFile = True

        self.pfRelIso03_all    = pfRelIso03_all
        self.pfRelIso03_allxPT = pfRelIso03_allxPT
        self.VLooseFOEleID     = VLooseFOEleID_on
        self.ip3d              = ip3d  
        self.sip3d             = sip3d
        self.BTagDeepCSV       = BTagDeepCSV
        self.lostHits          = lostHits_on
        self.tightEleID        = tightEleID_on
        self.convVeto          = convVeto
        self.softId            = softId
        
        self.miniPF_cut        = miniPF_cut
        self.miniPFxPT_cut     = miniPFxPT_cut
        
        self.lepton            = lepton

        # helper function
        f = lambda p: (abs(p.pdgId) in [11,13] # lepton
                       and p.statusFlags & (1<<13) # last copy
                       and ((p.statusFlags & (1<<10)) # tau OR
                            or ((p.statusFlags & (1<<0)) and (p.statusFlags & (1<<8))))) # prompt+ hard proc
        self.genLeptonSelector = f
    
    def Recleaner(self, lepton):
        #returns whether lepton passed from specified cuts
        
        #list of cut parameters
        pfRelIso_cut    = 0.5   #unitless
        pfRelIsoxPT_cut = 5.0   #GeV
        ip3d_cut        = 0.01  #cm 
        sip3d_cut       = 2     #unitless (in sigma)
        DeepCSV_cut     = 0.1241   #unitless
        
        if self.pfRelIso03_allxPT:
            if self.lepton=="softElectron" and lepton.ID>1:
                if not lepton.trkRelIso * lepton.pt< pfRelIsoxPT_cut:
                    return False

            elif (self.lepton== "Electron" or self.lepton=="Electron") and abs(lepton.pdgId)==11 and lepton.pt<5:
                if not lepton.miniPFRelIso_all * lepton.pt< self.miniPFxPT_cut:
                    return False
            
            else:
                if not lepton.pfRelIso03_all * lepton.pt< pfRelIsoxPT_cut:
                    return False

        if self.pfRelIso03_all:
            #print("pfRelIso03_all")
            if self.lepton=="softElectron" and lepton.ID>1:
                if not lepton.trkRelIso < pfRelIso_cut:
                    return False
            
            elif (self.lepton== "Electron" or self.lepton=="Electron") and abs(lepton.pdgId)==11 and lepton.pt<5:
                if not lepton.miniPFRelIso_all < self.miniPF_cut:
                    return False
            else: 
                if not lepton.pfRelIso03_all < pfRelIso_cut:
                    return False
    
        if self.VLooseFOEleID: 
            if not VLooseFOEleID(lepton, 2018):
                #print(VLooseFOEleID(lepton,2018))
                return VLooseFOEleID(lepton, 2018)

        if self.tightEleID:
            if self.lepton=="softElectron" and lepton.ID>1:
                if not softEleID(lepton, 2018):
                    return softEleID(lepton, 2018)
            else:
                if not tightEleID(lepton, 2018):
                    return tightEleID(lepton, 2018)

        if self.convVeto:
            if not lepton.convVeto:
                return False
    
        if self.ip3d:
            if not abs(lepton.ip3d) < ip3d_cut:
                return False
    
        if self.sip3d:
            if not lepton.sip3d < sip3d_cut:
                return False
        
        if self.BTagDeepCSV:
            if not lepton.jetBTagDeepCSV < DeepCSV_cut:
                return False
        
        if self.lostHits:
            #print(lepton.lostHits)
            if lepton.lostHits != 0:
             #   print("lostHits failed")
        #        print("lostHits: ", lepton.lostHits)
                return False

        if self.softId:
            if not lepton.softId==True:
                return False

        else:
            return True

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
        self.bookTH1("h_ele_pt_match_out",    ";Reco electron endcap p_{T} [GeV];entries",20,0,10)
        
        
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
        
        
    def endJob(self):
        self.MakeRatio("gen_ele_efficiency",        self.h_gen_ele_pt_match,        self.h_gen_ele_pt )
        self.MakeRatio("gen_ele_efficiency_barrel", self.h_gen_ele_pt_match_barrel, self.h_gen_ele_pt_barrel)
        self.MakeRatio("gen_ele_efficiency_endcap", self.h_gen_ele_pt_match_endcap, self.h_gen_ele_pt_endcap)
        self.MakeRatio("gen_ele_efficiency_out",    self.h_gen_ele_pt_match_out,    self.h_gen_ele_pt_out)
        self.MakeRatio("gen_ele_efficiency_inner",  self.h_gen_ele_pt_match_inner,  self.h_gen_ele_pt_inner)
        
        #self.MakeRatio("gen_mu_efficiency", self.h_gen_mu_pt_match, self.h_gen_mu_pt )
        
        Module.endJob(self)
        
    def truthMatch(self, reco, gen_lep_col):
        best_dR=9e9
        isMatch=False
        for gen_lep in gen_lep_col:
            dr = gen_lep.p4().DeltaR(reco.p4())
            #print dr
            if dr<0.1 and dr<best_dR:
                best_dR = dr
                reco.genPartIdx = gen_lep.idx
                isMatch = True
                #print dr
        return isMatch

    def analyze(self, event):
        # all reco leptons
        if o.collect=="LepRecl":
            leptons = Collection(event, 'LepGood')

        else:
            leptons = Collection(event, o.collect)
        
        gen_particles        = Collection(event, "GenPart")
        gen_leptons          = filter(self.genLeptonSelector, gen_particles)
        
        # truth / generator-level leptons
        for ip, p in enumerate(gen_particles): 
            p.idx = ip

        #print(self.lepton)
        if (self.lepton=='electron') or (self.lepton=='Electron'):
            lepton_use     = filter( lambda lep: abs(lep.pdgId)==11, leptons )
            gen_lepton_use = filter( lambda lep: abs(lep.pdgId)==11, gen_leptons )
        
        elif (self.lepton=='softElectron'):
            #print self.lepton
            lepton_use     = filter( lambda lep: lep.ID>1 and abs(lep.pdgId)==11, leptons )
            gen_lepton_use = filter( lambda lep: abs(lep.pdgId)==11, gen_leptons )
        
        elif (self.lepton=='muon') or (self.lepton=='Muon'):
            lepton_use     = filter( lambda lep: abs(lep.pdgId)==13, leptons )
            gen_lepton_use = filter( lambda lep: abs(lep.pdgId)==13, gen_leptons )

        # record truth_to_reco mapping
        truth_to_reco_ele = dict()
        truth_to_reco_ele_recl = dict()
        truth_to_reco_ele_barrel = dict()
        truth_to_reco_ele_endcap = dict()

        truth_to_reco_mu  = dict()
        truth_to_reco_unmatchedEle=dict()

        # reco electron loop
        for ele_idx, ele in enumerate(lepton_use):
            #print 'loop'
            match=False
            #print self.lepton
            if self.lepton=='softElectron':
                match=self.truthMatch(ele, gen_lepton_use)
                #print(ele.genPartIdx, match)

            self.h_ele_pt.Fill( ele.pt )
            self.h_ele_pt_eta.Fill( ele.pt, ele.eta ) 
                                                     #prompt electron      electron from prompt tau
            isTruthMatch = (ele.genPartIdx >= 0 and (ele.genPartFlav==1 or ele.genPartFlav==15)) #FIXME
            isRecl = self.Recleaner(ele)
            barrel_eta = (abs(ele.eta)<=1.47)
            endcap_eta = (2.5>abs(ele.eta)>1.47)
            out_eta    = (2.5<=abs(ele.eta))

            if o.collect=="LepRecl":
                isRecl_full=ele.isLepTight_Recl
            else:
                isRecl_full=True #always true unless LepRecl specified
            
            if (isTruthMatch or match) and isRecl and isRecl_full:
                #if o.collect=='LepGood':
                #    print('pass truth match')
                truth_to_reco_ele[ele.genPartIdx] = ele_idx
                self.h_ele_pt_match.Fill( ele.pt )

                if barrel_eta: 
                    self.h_ele_pt_match_barrel.Fill( ele.pt )
                if endcap_eta:
                    self.h_ele_pt_match_endcap.Fill( ele.pt )
                if out_eta:
                    self.h_ele_pt_match_out.Fill( ele.pt )
            
               
            if not (isTruthMatch or match) and isRecl and isRecl_full:
            #is not matched to gen part and passes recleaning steps
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
        for gen_ele in gen_lepton_use:
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
            
           # if isRecoMatch_recl:
           #     self.h_gen_ele_recl_pt_match.Fill( gen_ele.pt )
           #     
           #     if barrel_eta:
           #         self.h_gen_ele_recl_pt_match_barrel.Fill( gen_ele.pt )

           #     if endcap_eta:
           #         self.h_gen_ele_recl_pt_match_endcap.Fill( gen_ele.pt )

           #     if out_eta:
           #         self.h_gen_ele_recl_pt_match_out.Fill( gen_ele.pt )

           #     if not out_eta:
           #         self.h_gen_ele_recl_pt_match_inner.Fill( gen_ele.pt )

            
        # return True to keep the event if we're saving another tree
        return True


preselection = "GenMET_pt>50"
files = ["file:"+o.input_file+
         ",file:/eos/user/w/wterrill/softlepton_root/ch_outdir_dec18_ULtest_qcd_vtest/reclean/Higgsino_N2N1_testing_Chunk0_Friend.root"]

#friend=["file:/eos/user/w/wterrill/softlepton_root/ch_outdir_dec18_ULtest_qcd/reclean/Higgsino_N2N1_Chunk0_Friend.root"]
p = PostProcessor(".", files, cut=preselection, branchsel=None, modules=[
                  ElectronAnalysis(pfRelIso03_all=o.pfRelIso03_all,
                                       pfRelIso03_allxPT=o.pfRelIso03_allxPT,
                                       ip3d=o.ip3d,
                                       sip3d=o.sip3d,
                                       BTagDeepCSV=o.BTagDeepCSV, 
                                       lostHits_on=o.lostHits,
                                       VLooseFOEleID_on=o.VLooseFOEleID,
                                       tightEleID_on=o.tightEleID,
                                       convVeto=o.convVeto,
                                       softId=o.softId,
                                       miniPF_cut=o.miniPFRelIso_cut,
                                       miniPFxPT_cut=o.miniPFRelIsoxPT_cut,
                                       lepton=o.lepton)], 
                  noOut=True, histFileName=o.output, histDirName="plots1")

p2= PostProcessor(".", files, cut=preselection, branchsel=None, modules=[
                  LeptonAnalysis_steps(pfRelIso03_all=o.pfRelIso03_all,
                                       pfRelIso03_allxPT=o.pfRelIso03_allxPT,
                                       ip3d=o.ip3d,
                                       sip3d=o.sip3d,
                                       BTagDeepCSV=o.BTagDeepCSV,
                                       lostHits_on=o.lostHits,
                                       VLooseFOEleID_on=o.VLooseFOEleID,
                                       tightEleID_on=o.tightEleID,
                                       convVeto=o.convVeto,
                                       softId=o.softId,
                                       collect=o.collect,
                                       miniPF_cut=o.miniPFRelIso_cut,
                                       miniPFxPT_cut=o.miniPFRelIsoxPT_cut,
                                       lepton=o.lepton)],
                  noOut=True, histFileName=o.output2, histDirName="plots1")
#p2.maxEntries=20
#p.maxEntries=100

p.run()
p2.run()

