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

parser.add_option("-c", "--collection", dest="collect",
                  default = "LepGood", help= "collection name")

parser.add_option("--particle", dest="part", default="electron", help="particle name")

#parser.add_option("--pfRelIso03_all", dest="pfRelIso03_all",
#                  default = False, action="store_true", help="turn on pfRelIso03_all cut")
#
#parser.add_option("--pfRelIso03_allxPT", dest="pfRelIso03_allxPT",
#                  default = False, action="store_true", help="turn on pfRelIso03_all*pT cut")
#
#parser.add_option("--ip3d", dest="ip3d",
#                  default = False, action="store_true", help="turn on ip3d cut")
#
#parser.add_option("--sip3d", dest="sip3d",
#                  default = False, action="store_true", help="turn on sip3d cut")
#
#parser.add_option("--deepCSV", dest="BTagDeepCSV",
#                  default = False, action="store_true", help="turn on deepCSV cut")
#
#parser.add_option("--lostHits", dest="lostHits",
#                  default = False, action="store_true", help="turn on lostHits cut")
#
#parser.add_option("--VLooseFOEleID", dest="VLooseFOEleID",
#                  default=False, action="store_true", help="turn on VLooseFOEleID")
#
#parser.add_option("--convVeto", dest="convVeto",
#                  default=False, action="store_true", help="turn on convVeto")
#
#parser.add_option("--tightEleID", dest="tightEleID", 
#                  default=False, action="store_true", help="turn on tightEleID")

(o, a) = parser.parse_args()           

class deltaR(Module):
    def __init__(self, particle):
        self.writeHistFile = True
        if particle=="electron" or particle=="Electron":
            self.pdgID=11;
        elif particle=="muon"   or particle=="Muon":
            self.pdgID=13

        #self.pfRelIso03_all    = pfRelIso03_all
        #self.pfRelIso03_allxPT = pfRelIso03_allxPT
        #self.VLooseFOEleID     = VLooseFOEleID_on
        #self.ip3d              = ip3d  
        #self.sip3d             = sip3d
        #self.BTagDeepCSV       = BTagDeepCSV
        #self.lostHits          = lostHits_on
        #self.tightEleID        = tightEleID_on
        #self.convVeto          = convVeto

        # helper function
        f = lambda p: (abs(p.pdgId) in [11,13] # lepton
                       and p.statusFlags & (1<<13) # last copy
                       and ((p.statusFlags & (1<<10)) # tau OR
                            or ((p.statusFlags & (1<<0)) and (p.statusFlags & (1<<8))))) # prompt+ hard proc
        self.genLeptonSelector = f
    
    #def Recleaner(self, lepton):
    #    #returns whether lepton passed from specified cuts
    #    
    #    #list of cut parameters
    #    pfRelIso_cut    = 0.5   #unitless
    #    pfRelIsoxPT_cut = 5.0   #GeV
    #    ip3d_cut        = 0.01  #cm 
    #    sip3d_cut       = 2     #unitless (in sigma)
    #    DeepCSV_cut     = 0.1241   #unitless
    #    
    #    if self.pfRelIso03_allxPT: 
    #        if not lepton.pfRelIso03_all * lepton.pt< pfRelIsoxPT_cut:
    #            return False

    #    if self.pfRelIso03_all:
    #        #print("pfRelIso03_all")
    #        if not lepton.pfRelIso03_all < pfRelIso_cut:
    #            return False
    #
    #    if self.VLooseFOEleID: 
    #        if not VLooseFOEleID(lepton, 2018):
    #            #print(VLooseFOEleID(lepton,2018))
    #            return VLooseFOEleID(lepton, 2018)

    #    if self.tightEleID:
    #        if not tightEleID(lepton, 2018):
    #            return tightEleID(lepton, 2018)

    #    if self.convVeto:
    #        if not lepton.convVeto:
    #            return False
    #
    #    if self.ip3d:
    #        if not abs(lepton.ip3d) < ip3d_cut:
    #            return False
    #
    #    if self.sip3d:
    #        if not lepton.sip3d < sip3d_cut:
    #            return False
    #    
    #    if self.BTagDeepCSV:
    #        if not lepton.jetBTagDeepCSV < DeepCSV_cut:
    #            return False
    #    
    #    if self.lostHits:
    #        #print(lepton.lostHits)
    #        if not lepton.lostHits==0:
    #         #   print("lostHits failed")
    #    #        print("lostHits: ", lepton.lostHits)
    #            return False

    #    else:
    #        return True

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
        #print("before plot booking")
        # gen leptons
        self.bookTH1("h_lep_deltaR"      ,";Gen electron delta_R [];entries",50,0,4)
        self.bookTH1("h_lep_deltaR_dM5"  ,";Gen electron delta_R [];entries",50,0,4)
        self.bookTH1("h_lep_deltaR_dM10" ,";Gen electron delta_R [];entries",50,0,4)
        
        self.bookTH1("h_lep1_dRgreat0p3_pfRelIso03_allxPT" ," ;first reco electron pfRelIso03_all*pt; entries",55,-.5,4)
        self.bookTH1("h_lep1_dRless0p3_pfRelIso03_allxPT" ,"  ;first reco electron pfRelIso03_all*pt; entries",55,-.5,4)
        self.bookTH1("h_lep2_dRgreat0p3_pfRelIso03_allxPT" ,";second reco electron pfRelIso03_all*pt; entries",55,-.5,4)
        self.bookTH1("h_lep2_dRless0p3_pfRelIso03_allxPT" ," ;second reco electron pfRelIso03_all*pt; entries",55,-.5,4)
        self.bookTH1("h_lep1_dRgreat0p3_miniPFRelIso_allxPT" ," ;first reco electron miniPFRelIso_all*pt; entries",55,-.5,4)
        self.bookTH1("h_lep1_dRless0p3_miniPFRelIso_allxPT" ,"  ;first reco electron miniPFRelIso_all*pt; entries",55,-.5,4)
        self.bookTH1("h_lep2_dRgreat0p3_miniPFRelIso_allxPT" ,";second reco electron miniPFRelIso_all*pt; entries",55,-.5,4)
        self.bookTH1("h_lep2_dRless0p3_miniPFRelIso_allxPT" ," ;second reco electron miniPFRelIso_all*pt; entries",55,-.5,4)

        
        #pt subtraction
        self.bookTH1("h_lep1_dRless0p3_pfRelIso03_allxPTsubPT" ,"  ;first reco electron pfRelIso03_all*pt-second_pt; entries",55,-4,4)
        self.bookTH1("h_lep1_dRgreat0p3_pfRelIso03_allxPTsubPT" ,"  ;first reco electron pfRelIso03_all*pt-second_pt; entries",55,-4,4)
        self.bookTH1("h_lep2_dRless0p3_pfRelIso03_allxPTsubPT" ,"  ;second reco electron pfRelIso03_all*pt-first_pt; entries",55,-4,4)
        self.bookTH1("h_lep2_dRgreat0p3_pfRelIso03_allxPTsubPT" ,"  ;second reco electron pfRelIso03_all*pt-first_pt; entries",55,-4,4)
 

 
 

        self.bookTH1("h_lep1_dRgreat0p3_pfRelIso03_all" ," ;first reco electron pfRelIso03_all; entries",55,-.5,4)
        self.bookTH1("h_lep1_dRless0p3_pfRelIso03_all" ,"  ;first reco electron pfRelIso03_all; entries",55,-.5,4)
        self.bookTH1("h_lep2_dRgreat0p3_pfRelIso03_all" ,";second reco electron pfRelIso03_all; entries",55,-.5,4)
        self.bookTH1("h_lep2_dRless0p3_pfRelIso03_all" ," ;second reco electron pfRelIso03_all; entries",55,-.5,4)

        self.bookTH1("h_lep1_dRgreat0p3_miniPFRelIso_all" ,";first reco electron miniPFRelIso_all; entries",55,-.5,4)
        self.bookTH1("h_lep1_dRless0p3_miniPFRelIso_all" ," ;first reco electron miniPFRelIso_all; entries",55,-.5,4)
        self.bookTH1("h_lep2_dRgreat0p3_miniPFRelIso_all" ,";second reco electron miniPFRelIso_all; entries",55,-.5,4)
        self.bookTH1("h_lep2_dRless0p3_miniPFRelIso_all" ," ;second reco electron miniPFRelIso_all; entries",55,-.5,4)

        
        #debug       
        self.bookObject("h_lep_debug", ROOT.TH2F("h_lep_debug",";Reco lep match count;Gen lep count", 4,0,4, 4,0,4))
        self.bookObject("h_lep_pt_vs_relIso03", ROOT.TH2F("h_lep_pt_vs_relIso03",";Reco lep pt;Reco lep RelIso03", 50,0,10, 50,-0.5, 4))
        self.bookTH1("h_highest_pt" ," ; reco electron highest pT; entries",2,0,2)
        self.bookObject("h_lep1_dR_miniPFRelIso", ROOT.TH2F("h_lep1_dR_miniPFRelIso",";Gen lep $\Delta R$;reco lep miniPFRelIso", 40,0,4, 55,-.5,4))

        #self.bookObject("h_ele_pt_eta", ROOT.TH2F("h_ele_pt_eta",";Reco electron p_{T} [GeV];Reco electron #eta", 20,0,10, 10,-2.7,2.7))

                
    def endJob(self):
        #self.MakeRatio("gen_ele_efficiency",        self.h_gen_ele_pt_match,        self.h_gen_ele_pt )
        #self.MakeRatio("gen_ele_efficiency_barrel", self.h_gen_ele_pt_match_barrel, self.h_gen_ele_pt_barrel)
        #self.MakeRatio("gen_ele_efficiency_endcap", self.h_gen_ele_pt_match_endcap, self.h_gen_ele_pt_endcap)
        #self.MakeRatio("gen_ele_efficiency_out",    self.h_gen_ele_pt_match_out,    self.h_gen_ele_pt_out)
        #self.MakeRatio("gen_ele_efficiency_inner",  self.h_gen_ele_pt_match_inner,  self.h_gen_ele_pt_inner)
        
        #self.MakeRatio("gen_mu_efficiency", self.h_gen_mu_pt_match, self.h_gen_mu_pt )
        
        Module.endJob(self)
        
    def analyze(self, event):
        # all reco leptons
        if o.collect=="LepRecl":
            leptons = Collection(event, 'LepGood')

        else:
            leptons = Collection(event, o.collect)

        leps = filter( lambda lep: abs(lep.pdgId)==self.pdgID, leptons)

        # truth / generator-level leptons
        gen_particles = Collection(event, "GenPart")
        for ip, p in enumerate(gen_particles): 
            #print(p.pdgID)
            p.idx = ip
        
        gen_leptons          = filter(self.genLeptonSelector, gen_particles)
        gen_leps             = filter(lambda lep: abs(lep.pdgId)==self.pdgID, gen_leptons)
        
        gen_leps_barrel = filter(lambda lep: abs(lep.eta)<=1.47, gen_leps)
        gen_leps_endcap = filter(lambda lep: 2.5>abs(lep.eta)>1.47, gen_leps)
        gen_leps_out    = filter(lambda lep: 2.5<=abs(lep.eta), gen_leps)

        # record truth_to_reco mapping
        truth_to_reco_ele = dict()

        # reco electron loop
        ele_count = 0
        ele_match_count = 0
        lep_match_idx=[]
        for ele_idx, ele in enumerate(leps):
            ele_count += 1
            
            isTruthMatch=(ele.genPartIdx>=0 and ele.genPartFlav==1)
            if isTruthMatch:
                lep_match_idx.append(ele_idx)
                ele_match_count += 1        
        
        gen_count = 0
        for gen_idx, gen in enumerate(gen_leps):
            gen_count += 1

        if ele_match_count==2 and gen_count==2:
            #print(lep_match_idx)
            #print("matches: ", ele_match_count)
            #print("gen part: ", gen_count)
            dR = gen_leps[0].p4().DeltaR(gen_leps[1].p4())
            self.h_lep_deltaR.Fill(dR)
            
            self.h_lep1_dR_miniPFRelIso.Fill(dR, leps[lep_match_idx[0]].miniPFRelIso_all)

            if leps[0].pt >= leps[1].pt:
                self.h_highest_pt.Fill(0)
            elif leps[0].pt < leps[1].pt:
                self.h_highest_pt.Fill(1)

            if event.GenModel_SMS_N2N1_higgsino_100_95p00:
                self.h_lep_deltaR_dM5.Fill(dR)

            if event.GenModel_SMS_N2N1_higgsino_100_90p00:
                self.h_lep_deltaR_dM10.Fill(dR)
            
            if dR>0.3:
                self.h_lep1_dRgreat0p3_pfRelIso03_allxPT.Fill(leps[lep_match_idx[0]].pfRelIso03_all * leps[lep_match_idx[0]].pt)
                self.h_lep2_dRgreat0p3_pfRelIso03_allxPT.Fill(leps[lep_match_idx[1]].pfRelIso03_all * leps[lep_match_idx[1]].pt)
                self.h_lep1_dRgreat0p3_pfRelIso03_all.Fill(leps[lep_match_idx[0]].pfRelIso03_all)
                self.h_lep2_dRgreat0p3_pfRelIso03_all.Fill(leps[lep_match_idx[1]].pfRelIso03_all)
                
                self.h_lep1_dRgreat0p3_miniPFRelIso_allxPT.Fill(leps[lep_match_idx[0]].miniPFRelIso_all * leps[0].pt)
                self.h_lep2_dRgreat0p3_miniPFRelIso_allxPT.Fill(leps[lep_match_idx[1]].miniPFRelIso_all * leps[1].pt)
                self.h_lep1_dRgreat0p3_miniPFRelIso_all.Fill(leps[lep_match_idx[0]].miniPFRelIso_all)
                self.h_lep2_dRgreat0p3_miniPFRelIso_all.Fill(leps[lep_match_idx[1]].miniPFRelIso_all)
                
                self.h_lep1_dRgreat0p3_pfRelIso03_allxPTsubPT.Fill(leps[lep_match_idx[0]].miniPFRelIso_all*leps[lep_match_idx[0]].pt - leps[lep_match_idx[1]].pt)
                self.h_lep2_dRgreat0p3_pfRelIso03_allxPTsubPT.Fill(leps[lep_match_idx[1]].miniPFRelIso_all*leps[lep_match_idx[1]].pt - leps[lep_match_idx[0]].pt)


            elif dR<=0.3:
                self.h_lep1_dRless0p3_pfRelIso03_allxPT.Fill(leps[lep_match_idx[0]].pfRelIso03_all * leps[lep_match_idx[0]].pt)
                self.h_lep2_dRless0p3_pfRelIso03_allxPT.Fill(leps[lep_match_idx[1]].pfRelIso03_all * leps[lep_match_idx[1]].pt)
                self.h_lep1_dRless0p3_pfRelIso03_all.Fill(leps[lep_match_idx[0]].pfRelIso03_all)
                self.h_lep2_dRless0p3_pfRelIso03_all.Fill(leps[lep_match_idx[1]].pfRelIso03_all)
                
                self.h_lep1_dRless0p3_miniPFRelIso_allxPT.Fill(leps[lep_match_idx[0]].miniPFRelIso_all * leps[lep_match_idx[0]].pt)
                self.h_lep2_dRless0p3_miniPFRelIso_allxPT.Fill(leps[lep_match_idx[1]].miniPFRelIso_all * leps[lep_match_idx[1]].pt)
                self.h_lep1_dRless0p3_miniPFRelIso_all.Fill(leps[lep_match_idx[0]].miniPFRelIso_all)
                self.h_lep2_dRless0p3_miniPFRelIso_all.Fill(leps[lep_match_idx[1]].miniPFRelIso_all)
                
                self.h_lep1_dRless0p3_pfRelIso03_allxPTsubPT.Fill(leps[lep_match_idx[0]].miniPFRelIso_all*leps[lep_match_idx[0]].pt - leps[lep_match_idx[1]].pt)
                self.h_lep2_dRless0p3_pfRelIso03_allxPTsubPT.Fill(leps[lep_match_idx[1]].miniPFRelIso_all*leps[lep_match_idx[1]].pt - leps[lep_match_idx[0]].pt)

        self.h_lep_debug.Fill(ele_match_count, gen_count)
        if len(leps)>0 and ele_match_count==2:
            self.h_lep_pt_vs_relIso03.Fill(leps[lep_match_idx[0]].pt, leps[lep_match_idx[0]].pfRelIso03_all)

        # return True to keep the event if we're saving another tree
        return True

preselection = "GenMET_pt>50"
files = ["file:"+o.input_file+
         ",file:/eos/user/w/wterrill/softlepton_root/ch_outdir_dec18_ULtest_qcd/reclean/Higgsino_N2N1_Chunk0_Friend.root"]

#friend=["file:/eos/user/w/wterrill/softlepton_root/ch_outdir_dec18_ULtest_qcd/reclean/Higgsino_N2N1_Chunk0_Friend.root"]
p= PostProcessor(".", files, cut=preselection, branchsel=None, modules=[
                  deltaR(particle=o.part)],
                  noOut=True, histFileName=o.output, histDirName="plots1")
#p2.maxEntries=20
#p.maxEntries=100

p.run()

