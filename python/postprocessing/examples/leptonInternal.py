from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from importlib import import_module
import os
import ROOT

from array import array

ROOT.PyConfig.IgnoreCommandLineOptions = True

from CMGTools.TTHAnalysis.tools.nanoAOD.susySOS_modules import *

class LeptonAnalysis_steps(Module):
    def __init__(self, pfRelIso03_all, pfRelIso03_allxPT, ip3d, sip3d, BTagDeepCSV, lostHits_on,
                 VLooseFOEleID_on, tightEleID_on, convVeto, softId, collect, miniPF_cut, miniPFxPT_cut,
                 lepton='electron'):
        self.writeHistFile = True
        self.collect = collect

        self.pfRelIso03_all    = pfRelIso03_all
        self.pfRelIso03_allxPT = pfRelIso03_allxPT
        self.ip3d              = ip3d
        self.sip3d             = sip3d
        self.VLooseFOEleID     = VLooseFOEleID_on
        self.tightEleID        = tightEleID_on
        self.convVeto          = convVeto
        self.BTagDeepCSV       = BTagDeepCSV
        self.lostHits          = lostHits_on
        self.softId            = softId

        self.miniPF_cut        = miniPF_cut
        self.miniPFxPT_cut     = miniPFxPT_cut

        self.lepton            = lepton

        f = lambda p: (abs(p.pdgId) in [11,13] # lepton
                       and p.statusFlags & (1<<13) # last copy
                       and ((p.statusFlags & (1<<10)) # tau OR
                            or ((p.statusFlags & (1<<0)) and (p.statusFlags & (1<<8))))) # prompt+ hard proc

        self.genLeptonSelector = f

    def Recleaner(self, lepton):
        pfRelIso_cut    = 0.5   #unitless
        pfRelIsoxPT_cut = 5.0   #GeV
        ip3d_cut        = 0.01  #cm
        sip3d_cut       = 2     #unitless (in sigma)
        DeepCSV_cut     = 0.1241   #unitless

        #print("in Recleaner")

        if self.pfRelIso03_allxPT:
            if self.lepton=="softElectron" and lepton.ID > 1:
                if not lepton.trkRelIso*lepton.pt < pfRelIsoxPT_cut:
                    return False

            elif abs(lepton.pdgId)==11 and lepton.pt<5:
                if not lepton.miniPFRelIso_all * lepton.pt < self.miniPFxPT_cut:
                    return False
            else:
                if not lepton.pfRelIso03_all * lepton.pt < pfRelIsoxPT_cut:
                    return False

        #print('between step 1 and 2')
        if self.pfRelIso03_all:
            #print("pfRelIso03_all")
            if self.lepton=="softElectron" and lepton.ID > 1:
                if not lepton.trkRelIso < pfRelIso_cut:
                    return False
            
            elif abs(lepton.pdgId)==11 and lepton.pt<5:
                if not lepton.miniPFRelIso_all < self.miniPF_cut:
                    return False
            else:
                if not lepton.pfRelIso03_all < pfRelIso_cut:
                    return False

        #print('between step 2 and 3')
        if self.VLooseFOEleID:
            if not VLooseFOEleID(lepton, 2018):
                #print(VLooseFOEleID(lepton,2018))
                return False

        #print('between step 3 and 4')
        if self.tightEleID:
            if self.lepton=="softElectron" and lepton.ID > 1:
                if not softEleID(lepton, 2018):
                    return False
            else:
                if not tightEleID(lepton, 2018):
                    return False

        #print('between step 4 and 5')
        if self.convVeto:
            if not lepton.convVeto:
                return False

        #print('between step 5 and 6')
        if self.ip3d:
            if not abs(lepton.ip3d) < ip3d_cut:
                return False

        #print('between step 6 and 7')
        if self.sip3d:
            if not lepton.sip3d < sip3d_cut:
                return False

        #print('between step 7 and 8')
        if self.BTagDeepCSV:
            if not lepton.jetBTagDeepCSV < DeepCSV_cut:
                return False

        #print('between step 8 and 9')
        if self.softId:
            if not lepton.softId==True:
                return False

        #print('between step 9 and 10')
        #print("lostHits: ", lepton.lostHits)
        if self.lostHits:
            if lepton.lostHits != 0:
                print lepton.lostHits
                return False

        #print('end of Recleaner')
        return True

    def bookTH1(self, hist_name, hist_title, nbins, xlo, xhi):
        
        if (self.lepton=="muon") or (self.lepton=="Muon"):
            hist_name2=hist_name.replace("lep", "mu")
        elif(self.lepton=="electron") or (self.lepton=="Electron") or (self.lepton=="softElectron"):
            hist_name2=hist_name.replace("lep","ele")
        
        h = ROOT.TH1F(hist_name2, hist_title, nbins, xlo, xhi)
        setattr(self, hist_name, h)

        self.addObject( getattr(self, hist_name) )

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

    def beginJob(self, histFile, histDirName):
        Module.beginJob(self, histFile, histDirName)
        

        #self.out = wrappedOutputTree
        #self.out.branch("test", "F")

   #     # GEN ELECTRONS
   #     self.bookTH1("h_gen_lep_match_ip3d"              ,";gen lepton ip3d  ;entries",20,-0.2,0.2)
   #     self.bookTH1("h_gen_lep_match_sip3d"             ,";gen lepton sip3d ;entries",20,0,3)
   #     self.bookTH1("h_gen_lep_match_pfRelIso03_all"    ,";gen lepton pfRelIso03_all ;entries",30,0,1)
   #     self.bookTH1("h_gen_lep_match_pfRelIso03_allxPT" ,";gen lepton pfRelIso03_allxPT ;entries",20,0,5)
   #     self.bookTH1("h_gen_lep_match_bTagDeepCSV"       ,";gen lepton bTagDeepCSV ;entries",40,0,1)
   #     self.bookTH1("h_gen_lep_match_lostHits"          ,";gen lepton lostHits ;entries", 10, 0, 5)
   #     self.bookTH1("h_gen_lep_match_VLooseFOEleID"     ,";gen lepton VLooseFOEleID; entries", 2, 0, 2)
   #     self.bookTH1("h_gen_lep_match_tightEleID"        ,";gen lepton tightEleID; entries", 2, 0, 2)
   #     self.bookTH1("h_gen_lep_match_convVeto"          ,";gen lepton convVeto; entries", 2, 0, 2)
   #     self.bookTH1("h_gen_lep_match_mva"               ,";gen lepton mva score; entries", 30, -2, 10)

        # RECO ELECTRONS
        self.bookTH1("h_lep_ip3d"                ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_sip3d"               ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_pfRelIso03_all"      ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_pfRelIso03_allxPT"   ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_miniPFRelIso_all"    ,";Reco lepton miniPFRelIso_all ;entries",30,0,5)
        self.bookTH1("h_lep_miniPFRelIso_allxPT" ,";Reco lepton miniPFRelIso_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_bTagDeepCSV"         ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_lostHits"            ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_VLooseFOEleID"       ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_tightEleID"          ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_convVeto"            ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_mva"                 ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_pt"                  ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_mvaFall17_WP80"      ,";Reco lepton mvaFall17V2noIso_WP80; entries", 2, 0, 2)
        self.bookTH1("h_lep_mva_small"           ,";Reco lepton mva score; entries", 30, -1, 1)
        self.bookTH1("h_lep_trkRelIso"           ,";Reco lepton trkRelIso; entries", 30, 0, 5)
        self.bookTH1("h_lep_trkRelIsoxPT"        ,";Reco lepton trkRelIsoxPT; entries", 30, 0, 5)

        ## matched
        self.bookTH1("h_lep_match_ip3d"                ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_match_sip3d"               ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_match_pfRelIso03_all"      ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_match_pfRelIso03_allxPT"   ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_match_miniPFRelIso_all"    ,";Reco lepton miniPFRelIso_all ;entries",30,0,.05)
        self.bookTH1("h_lep_match_miniPFRelIso_allxPT" ,";Reco lepton miniPFRelIso_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_match_bTagDeepCSV"         ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_match_lostHits"            ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_match_VLooseFOEleID"       ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_match_tightEleID"          ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_match_convVeto"            ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_match_mva"                 ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_match_pt"                  ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_match_mvaFall17_WP80"      ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_match_mva_small"           ,";Reco lepton mva score", 30, -1, 1)
        self.bookTH1("h_lep_match_trkRelIso"           ,";Reco lepton trkRelIso; entries", 30, 0, 5)
        self.bookTH1("h_lep_match_trkRelIsoxPT"        ,";Reco lepton trkRelIsoxPT; entries", 30, 0, 5)

        ## unmatched
        self.bookTH1("h_lep_unmatch_ip3d"                ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_unmatch_sip3d"               ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_unmatch_pfRelIso03_all"      ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_unmatch_miniPFRelIso_allxPT" ,";Reco lepton miniPFRelIso_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_unmatch_miniPFRelIso_all"    ,";Reco lepton miniPFRelIso_all ;entries",30,0,.05)
        self.bookTH1("h_lep_unmatch_pfRelIso03_allxPT"   ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_unmatch_bTagDeepCSV"         ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_unmatch_lostHits"            ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_unmatch_VLooseFOEleID"       ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_unmatch_tightEleID"          ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_unmatch_convVeto"            ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_unmatch_mva"                 ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_unmatch_pt"                  ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_unmatch_mvaFall17_WP80"      ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_unmatch_mva_small"           ,";Reco lepton mva score", 30, -1, 1)
        self.bookTH1("h_lep_unmatch_trkRelIso"           ,";Reco lepton trkRelIso; entries", 30, 0, 5)
        self.bookTH1("h_lep_unmatch_trkRelIsoxPT"        ,";Reco lepton trkRelIsoxPT; entries", 30, 0, 5)

        ### split lower
        #### matched
        self.bookTH1("h_lep_lower_match_ip3d"                ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_lower_match_sip3d"               ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_lower_match_pfRelIso03_all"      ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_lower_match_pfRelIso03_allxPT"   ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_lower_match_miniPFRelIso_all"    ,";Reco lepton miniPFRelIso_all ;entries",30,0,5)
        self.bookTH1("h_lep_lower_match_miniPFRelIso_allxPT" ,";Reco lepton miniPFRelIso_allxPT ;entries",25,0,2)
        self.bookTH1("h_lep_lower_match_bTagDeepCSV"         ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_lower_match_lostHits"            ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_lower_match_VLooseFOEleID"       ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_lower_match_tightEleID"          ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_lower_match_convVeto"            ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_lower_match_mva"                 ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_lower_match_pt"                  ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_lower_match_mvaFall17_WP80"      ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_lower_match_mva_small"           ,";Reco lepton mva score", 30, -1, 1)
        self.bookTH1("h_lep_lower_match_trkRelIso"           ,";Reco lepton trkRelIso; entries", 30, 0, 5)
        self.bookTH1("h_lep_lower_match_trkRelIsoxPT"        ,";Reco lepton trkRelIsoxPT; entries", 30, 0, 5)

        #### unmatched (2<pt<5)
        self.bookTH1("h_lep_lower_unmatch_ip3d"              ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_lower_unmatch_sip3d"             ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_lower_unmatch_pfRelIso03_all"    ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_lower_unmatch_pfRelIso03_allxPT" ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_lower_unmatch_miniPFRelIso_all"    ,";Reco lepton miniPFRelIso03_all ;entries",30,0,5)
        self.bookTH1("h_lep_lower_unmatch_miniPFRelIso_allxPT" ,";Reco lepton miniPFRelIso_allxPT ;entries",25,0,2)
        self.bookTH1("h_lep_lower_unmatch_bTagDeepCSV"       ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_lower_unmatch_lostHits"          ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_lower_unmatch_VLooseFOEleID"     ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_lower_unmatch_tightEleID"        ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_lower_unmatch_convVeto"          ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_lower_unmatch_mva"               ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_lower_unmatch_pt"                ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_lower_unmatch_mvaFall17_WP80"    ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_lower_unmatch_mva_small"         ,";Reco lepton mva score", 30, -1, 1)
        self.bookTH1("h_lep_lower_unmatch_trkRelIso"         ,";Reco lepton trkRelIso; entries", 30, 0, 5)
        self.bookTH1("h_lep_lower_unmatch_trkRelIsoxPT"      ,";Reco lepton trkRelIsoxPT; entries", 30, 0, 5)

        ### split upper (5<pt<10)
        ## matched
        self.bookTH1("h_lep_upper_match_ip3d"              ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_upper_match_sip3d"             ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_upper_match_pfRelIso03_all"    ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_upper_match_pfRelIso03_allxPT" ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_upper_match_miniPFRelIso_all"    ,";Reco lepton miniPFRelIso_all ;entries",30,0,.05)
        self.bookTH1("h_lep_upper_match_miniPFRelIso_allxPT" ,";Reco lepton miniPFRelIso_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_upper_match_bTagDeepCSV"       ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_upper_match_lostHits"          ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_upper_match_VLooseFOEleID"     ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_upper_match_tightEleID"        ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_upper_match_convVeto"          ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_upper_match_mva"               ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_upper_match_pt"                ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_upper_match_mvaFall17_WP80"    ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_upper_match_mva_small"         ,";Reco lepton mva score", 30, -1, 1)
        self.bookTH1("h_lep_upper_match_trkRelIso"         ,";Reco lepton trkRelIso; entries", 30, 0, 5)

        ## unmatched
        self.bookTH1("h_lep_upper_unmatch_ip3d"              ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_upper_unmatch_sip3d"             ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_upper_unmatch_pfRelIso03_all"    ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_upper_unmatch_pfRelIso03_allxPT" ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_upper_unmatch_miniPFRelIso_all"    ,";Reco lepton miniPFRelIso_all ;entries",30,0,.05)
        self.bookTH1("h_lep_upper_unmatch_miniPFRelIso_allxPT" ,";Reco lepton miniPFRelIso_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_upper_unmatch_bTagDeepCSV"       ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_upper_unmatch_lostHits"          ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_upper_unmatch_VLooseFOEleID"     ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_upper_unmatch_tightEleID"        ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_upper_unmatch_convVeto"          ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_upper_unmatch_mva"               ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_upper_unmatch_pt"                ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_upper_unmatch_mvaFall17_WP80"    ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_upper_unmatch_mva_small"         ,";Reco lepton mva score", 30, -1, 1)
        self.bookTH1("h_lep_upper_unmatch_trkRelIso"         ,";Reco lepton trkRelIso; entries", 30, 0, 5)

        #barrel
        self.bookTH1("h_lep_barrel_ip3d"              ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_barrel_sip3d"             ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_barrel_pfRelIso03_all"    ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_barrel_pfRelIso03_allxPT" ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_barrel_miniPFRelIso_all"    ,";Reco lepton miniPFRelIso_all ;entries",30,0,.05)
        self.bookTH1("h_lep_barrel_miniPFRelIso_allxPT" ,";Reco lepton miniPFRelIso_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_barrel_bTagDeepCSV"       ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_barrel_lostHits"          ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_barrel_VLooseFOEleID"     ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_barrel_tightEleID"        ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_barrel_convVeto"          ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_barrel_mva"               ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_barrel_pt"                ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_barrel_mvaFall17_WP80"    ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_barrel_mva_small"         ,";Reco lepton mva score", 30, -1, 1)
        self.bookTH1("h_lep_barrel_trkRelIso"         ,";Reco lepton trkRelIso; entries", 30, 0, 5)
        self.bookTH1("h_lep_barrel_trkRelIsoxPT"        ,";Reco lepton trkRelIsoxPT; entries", 30, 0, 5)

        ## matched
        self.bookTH1("h_lep_match_barrel_ip3d"              ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_match_barrel_sip3d"             ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_match_barrel_pfRelIso03_all"    ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_match_barrel_pfRelIso03_allxPT" ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_match_barrel_miniPFRelIso_all"    ,";Reco lepton miniPFRelIso_all ;entries",30,0,.05)
        self.bookTH1("h_lep_match_barrel_miniPFRelIso_allxPT" ,";Reco lepton miniPFRelIso_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_match_barrel_bTagDeepCSV"       ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_match_barrel_lostHits"          ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_match_barrel_VLooseFOEleID"     ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_match_barrel_tightEleID"        ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_match_barrel_convVeto"          ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_match_barrel_mva"               ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_match_barrel_pt"                ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_match_barrel_mvaFall17_WP80"    ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_match_barrel_mva_small"         ,";Reco lepton mva score", 30, -1, 1)
        self.bookTH1("h_lep_match_barrel_trkRelIso"         ,";Reco lepton trkRelIso; entries", 30, 0, 5)
        self.bookTH1("h_lep_match_barrel_trkRelIsoxPT"      ,";Reco lepton trkRelIsoxPT; entries", 30, 0, 5)

        ## unmatched
        self.bookTH1("h_lep_unmatch_barrel_ip3d"              ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_unmatch_barrel_sip3d"             ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_unmatch_barrel_pfRelIso03_all"    ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_unmatch_barrel_pfRelIso03_allxPT" ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_unmatch_barrel_miniPFRelIso_all"    ,";Reco lepton miniPFRelIso_all ;entries",30,0,.05)
        self.bookTH1("h_lep_unmatch_barrel_miniPFRelIso_allxPT" ,";Reco lepton miniPFRelIso_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_unmatch_barrel_bTagDeepCSV"       ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_unmatch_barrel_lostHits"          ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_unmatch_barrel_VLooseFOEleID"     ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_unmatch_barrel_tightEleID"        ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_unmatch_barrel_convVeto"          ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_unmatch_barrel_mva"               ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_unmatch_barrel_pt"                ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_unmatch_barrel_mvaFall17_WP80"    ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_unmatch_barrel_mva_small"         ,";Reco lepton mva score", 30, -1, 1)
        self.bookTH1("h_lep_unmatch_barrel_trkRelIso"         ,";Reco lepton trkRelIso; entries", 30, 0, 5)
        self.bookTH1("h_lep_unmatch_barrel_trkRelIsoxPT"      ,";Reco lepton trkRelIsoxPT; entries", 30, 0, 5)

        ### split lower
        #### matched
        self.bookTH1("h_lep_lower_match_barrel_ip3d"              ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_lower_match_barrel_sip3d"             ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_lower_match_barrel_pfRelIso03_all"    ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_lower_match_barrel_pfRelIso03_allxPT" ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_lower_match_barrel_miniPFRelIso_all"    ,";Reco lepton miniPFRelIso_all ;entries",30,0,.05)
        self.bookTH1("h_lep_lower_match_barrel_miniPFRelIso_allxPT" ,";Reco lepton miniPFRelIso_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_lower_match_barrel_bTagDeepCSV"       ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_lower_match_barrel_lostHits"          ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_lower_match_barrel_VLooseFOEleID"     ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_lower_match_barrel_tightEleID"        ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_lower_match_barrel_convVeto"          ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_lower_match_barrel_mva"               ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_lower_match_barrel_pt"                ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_lower_match_barrel_mvaFall17_WP80"    ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_lower_match_barrel_mva_small"         ,";Reco lepton mva score", 30, -1, 1)
        self.bookTH1("h_lep_lower_match_barrel_trkRelIso"         ,";Reco lepton trkRelIso; entries", 30, 0, 5)
        self.bookTH1("h_lep_lower_match_barrel_trkRelIsoxPT"      ,";Reco lepton trkRelIsoxPT; entries", 30, 0, 5)

        #### unmatched (2<pt<5)
        self.bookTH1("h_lep_lower_unmatch_barrel_ip3d"              ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_lower_unmatch_barrel_sip3d"             ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_lower_unmatch_barrel_pfRelIso03_all"    ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_lower_unmatch_barrel_pfRelIso03_allxPT" ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_lower_unmatch_barrel_miniPFRelIso_all"    ,";Reco lepton miniPFRelIso_all ;entries",30,0,.05)
        self.bookTH1("h_lep_lower_unmatch_barrel_miniPFRelIso_allxPT" ,";Reco lepton miniPFRelIso_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_lower_unmatch_barrel_bTagDeepCSV"       ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_lower_unmatch_barrel_lostHits"          ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_lower_unmatch_barrel_VLooseFOEleID"     ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_lower_unmatch_barrel_tightEleID"        ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_lower_unmatch_barrel_convVeto"          ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_lower_unmatch_barrel_mva"               ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_lower_unmatch_barrel_pt"                ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_lower_unmatch_barrel_mvaFall17_WP80"    ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_lower_unmatch_barrel_mva_small"         ,";Reco lepton mva score", 30, -1, 1)
        self.bookTH1("h_lep_lower_unmatch_barrel_trkRelIso"         ,";Reco lepton trkRelIso; entries", 30, 0, 5)
        self.bookTH1("h_lep_lower_unmatch_barrel_trkRelIsoxPT"      ,";Reco lepton trkRelIsoxPT; entries", 30, 0, 5)

        ### split upper (5<pt<10)
        ## matched
        self.bookTH1("h_lep_upper_match_barrel_ip3d"              ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_upper_match_barrel_sip3d"             ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_upper_match_barrel_pfRelIso03_all"    ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_upper_match_barrel_pfRelIso03_allxPT" ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_upper_match_barrel_miniPFRelIso_all"    ,";Reco lepton miniPFRelIso_all ;entries",30,0,.05)
        self.bookTH1("h_lep_upper_match_barrel_miniPFRelIso_allxPT" ,";Reco lepton miniPFRelIso_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_upper_match_barrel_bTagDeepCSV"       ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_upper_match_barrel_lostHits"          ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_upper_match_barrel_VLooseFOEleID"     ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_upper_match_barrel_tightEleID"        ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_upper_match_barrel_convVeto"          ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_upper_match_barrel_mva"               ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_upper_match_barrel_pt"                ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_upper_match_barrel_mvaFall17_WP80"    ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_upper_match_barrel_mva_small"         ,";Reco lepton mva score", 30, -1, 1)
        self.bookTH1("h_lep_upper_match_barrel_trkRelIso"         ,";Reco lepton trkRelIso; entries", 30, 0, 5)
        self.bookTH1("h_lep_upper_match_barrel_trkRelIsoxPT"      ,";Reco lepton trkRelIsoxPT; entries", 30, 0, 5)

        ## unmatched
        self.bookTH1("h_lep_upper_unmatch_barrel_ip3d"              ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_upper_unmatch_barrel_sip3d"             ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_upper_unmatch_barrel_pfRelIso03_all"    ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_upper_unmatch_barrel_pfRelIso03_allxPT" ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_upper_unmatch_barrel_miniPFRelIso_all"    ,";Reco lepton miniPFRelIso_all ;entries",30,0,.05)
        self.bookTH1("h_lep_upper_unmatch_barrel_miniPFRelIso_allxPT" ,";Reco lepton miniPFRelIso_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_upper_unmatch_barrel_bTagDeepCSV"       ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_upper_unmatch_barrel_lostHits"          ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_upper_unmatch_barrel_VLooseFOEleID"     ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_upper_unmatch_barrel_tightEleID"        ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_upper_unmatch_barrel_convVeto"          ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_upper_unmatch_barrel_mva"               ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_upper_unmatch_barrel_pt"                ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_upper_unmatch_barrel_mvaFall17_WP80"    ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_upper_unmatch_barrel_mva_small"         ,";Reco lepton mva score", 30, -1, 1)
        self.bookTH1("h_lep_upper_unmatch_barrel_trkRelIso"         ,";Reco lepton trkRelIso; entries", 30, 0, 5)
        self.bookTH1("h_lep_upper_unmatch_barrel_trkRelIsoxPT"      ,";Reco lepton trkRelIsoxPT; entries", 30, 0, 5)

        #endcap
        self.bookTH1("h_lep_endcap_ip3d"              ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_endcap_sip3d"             ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_endcap_pfRelIso03_all"    ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_endcap_pfRelIso03_allxPT" ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_endcap_miniPFRelIso_all"    ,";Reco lepton miniPFRelIso_all ;entries",30,0,.05)
        self.bookTH1("h_lep_endcap_miniPFRelIso_allxPT" ,";Reco lepton miniPFRelIso_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_endcap_bTagDeepCSV"       ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_endcap_lostHits"          ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_endcap_VLooseFOEleID"     ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_endcap_tightEleID"        ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_endcap_convVeto"          ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_endcap_mva"               ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_endcap_pt"                ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_endcap_mvaFall17_WP80"    ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_endcap_mva_small"         ,";Reco lepton mva score", 30, -1, 1)
        self.bookTH1("h_lep_endcap_trkRelIso"         ,";Reco lepton trkRelIso; entries", 30, 0, 5)
        if (self.lepton=="muon") or (self.lepton=="Muon"):
            self.bookTH1("h_lep_endcap_cleanmask"          ,";Reco lepton mva score", 30, -1, 1)
            self.bookTH1("h_lep_endcap_dxy"                ,";Reco lepton mva score", 30, -1, 1)
            self.bookTH1("h_lep_endcap_dxyErr"             ,";Reco lepton mva score", 30, -1, 1)
            self.bookTH1("h_lep_endcap_dxybs"              ,";Reco lepton mva score", 30, -1, 1)
            self.bookTH1("h_lep_endcap_dz"                 ,";Reco lepton mva score", 30, -1, 1)
            self.bookTH1("h_lep_endcap_dzErr"              ,";Reco lepton mva score", 30, -1, 1)
            self.bookTH1("h_lep_endcap_highPurity"         ,";Reco lepton mva score", 30, -1, 1)
            self.bookTH1("h_lep_endcap_ip3d"               ,";Reco lepton mva score", 30, -1, 1)
            self.bookTH1("h_lep_endcap_isGlobal"           ,";Reco lepton mva score", 30, -1, 1)
            self.bookTH1("h_lep_endcap_isTracker"          ,";Reco lepton mva score", 30, -1, 1)
            self.bookTH1("h_lep_endcap_mvaID"              ,";Reco lepton mva score", 30, -1, 1)
            self.bookTH1("h_lep_endcap_mvaLowPt"           ,";Reco lepton mva score", 30, -1, 1)
            self.bookTH1("h_lep_endcap_mvaTTH"             ,";Reco lepton mva score", 30, -1, 1)
            self.bookTH1("h_lep_endcap_nStations"          ,";Reco lepton mva score", 30, -1, 1)
            self.bookTH1("h_lep_endcap_nTrackerLayers"     ,";Reco lepton mva score", 30, -1, 1)
            self.bookTH1("h_lep_endcap_segmentComp"        ,";Reco lepton mva score", 30, -1, 1)
            self.bookTH1("h_lep_endcap_softMva"            ,";Reco lepton mva score", 30, -1, 1)

        ## matched
        self.bookTH1("h_lep_match_endcap_ip3d"              ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_match_endcap_sip3d"             ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_match_endcap_pfRelIso03_all"    ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_match_endcap_pfRelIso03_allxPT" ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_match_endcap_miniPFRelIso_all"    ,";Reco lepton miniPFRelIso_all ;entries",30,0,.05)
        self.bookTH1("h_lep_match_endcap_miniPFRelIso_allxPT" ,";Reco lepton miniPFRelIso_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_match_endcap_bTagDeepCSV"       ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_match_endcap_lostHits"          ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_match_endcap_VLooseFOEleID"     ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_match_endcap_tightEleID"        ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_match_endcap_convVeto"          ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_match_endcap_mva"               ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_match_endcap_pt"                ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_match_endcap_mvaFall17_WP80"    ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_match_endcap_mva_small"         ,";Reco lepton mva score", 30, -1, 1)
        self.bookTH1("h_lep_match_endcap_trkRelIso"         ,";Reco lepton trkRelIso; entries", 30, 0, 5)

        ## unmatched
        self.bookTH1("h_lep_unmatch_endcap_ip3d"              ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_unmatch_endcap_sip3d"             ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_unmatch_endcap_pfRelIso03_all"    ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_unmatch_endcap_pfRelIso03_allxPT" ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_unmatch_endcap_miniPFRelIso_all"    ,";Reco lepton miniPFRelIso_all ;entries",30,0,.05)
        self.bookTH1("h_lep_unmatch_endcap_miniPFRelIso_allxPT" ,";Reco lepton miniPFRelIso_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_unmatch_endcap_bTagDeepCSV"       ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_unmatch_endcap_lostHits"          ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_unmatch_endcap_VLooseFOEleID"     ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_unmatch_endcap_tightEleID"        ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_unmatch_endcap_convVeto"          ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_unmatch_endcap_mva"               ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_unmatch_endcap_pt"                ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_unmatch_endcap_mvaFall17_WP80"    ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_unmatch_endcap_mva_small"         ,";Reco lepton mva score", 30, -1, 1)
        self.bookTH1("h_lep_unmatch_endcap_trkRelIso"         ,";Reco lepton trkRelIso; entries", 30, 0, 5)

        ### split lower
        #### matched
        self.bookTH1("h_lep_lower_match_endcap_ip3d"              ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_lower_match_endcap_sip3d"             ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_lower_match_endcap_pfRelIso03_all"    ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_lower_match_endcap_pfRelIso03_allxPT" ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_lower_match_endcap_miniPFRelIso_all"    ,";Reco lepton miniPFRelIso_all ;entries",30,0,.05)
        self.bookTH1("h_lep_lower_match_endcap_miniPFRelIso_allxPT" ,";Reco lepton miniPFRelIso_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_lower_match_endcap_bTagDeepCSV"       ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_lower_match_endcap_lostHits"          ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_lower_match_endcap_VLooseFOEleID"     ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_lower_match_endcap_tightEleID"        ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_lower_match_endcap_convVeto"          ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_lower_match_endcap_mva"               ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_lower_match_endcap_pt"                ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_lower_match_endcap_mvaFall17_WP80"    ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_lower_match_endcap_mva_small"         ,";Reco lepton mva score", 30, -1, 1)
        self.bookTH1("h_lep_lower_match_endcap_trkRelIso"         ,";Reco lepton trkRelIso; entries", 30, 0, 5)

        #### unmatched (2<pt<5)
        self.bookTH1("h_lep_lower_unmatch_endcap_ip3d"              ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_lower_unmatch_endcap_sip3d"             ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_lower_unmatch_endcap_pfRelIso03_all"    ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_lower_unmatch_endcap_pfRelIso03_allxPT" ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_lower_unmatch_endcap_miniPFRelIso_all"    ,";Reco lepton miniPFRelIso_all ;entries",30,0,.05)
        self.bookTH1("h_lep_lower_unmatch_endcap_miniPFRelIso_allxPT" ,";Reco lepton miniPFRelIso_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_lower_unmatch_endcap_bTagDeepCSV"       ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_lower_unmatch_endcap_lostHits"          ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_lower_unmatch_endcap_VLooseFOEleID"     ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_lower_unmatch_endcap_tightEleID"        ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_lower_unmatch_endcap_convVeto"          ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_lower_unmatch_endcap_mva"               ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_lower_unmatch_endcap_pt"                ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_lower_unmatch_endcap_mvaFall17_WP80"    ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_lower_unmatch_endcap_mva_small"         ,";Reco lepton mva score", 30, -1, 1)
        self.bookTH1("h_lep_lower_unmatch_endcap_trkRelIso"         ,";Reco lepton trkRelIso; entries", 30, 0, 5)

        ### split upper (5<pt<10)
        ## matched
        self.bookTH1("h_lep_upper_match_endcap_ip3d"              ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_upper_match_endcap_sip3d"             ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_upper_match_endcap_pfRelIso03_all"    ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_upper_match_endcap_pfRelIso03_allxPT" ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_upper_match_endcap_miniPFRelIso_all"    ,";Reco lepton miniPFRelIso_all ;entries",30,0,.05)
        self.bookTH1("h_lep_upper_match_endcap_miniPFRelIso_allxPT" ,";Reco lepton miniPFRelIso_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_upper_match_endcap_bTagDeepCSV"       ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_upper_match_endcap_lostHits"          ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_upper_match_endcap_VLooseFOEleID"     ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_upper_match_endcap_tightEleID"        ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_upper_match_endcap_convVeto"          ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_upper_match_endcap_mva"               ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_upper_match_endcap_pt"                ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_upper_match_endcap_mvaFall17_WP80"    ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_upper_match_endcap_mva_small"         ,";Reco lepton mva score", 30, -1, 1)
        self.bookTH1("h_lep_upper_match_endcap_trkRelIso"         ,";Reco lepton trkRelIso; entries", 30, 0, 5)

        ## unmatched
        self.bookTH1("h_lep_upper_unmatch_endcap_ip3d"              ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_upper_unmatch_endcap_sip3d"             ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_upper_unmatch_endcap_pfRelIso03_all"    ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_upper_unmatch_endcap_pfRelIso03_allxPT" ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_upper_unmatch_endcap_miniPFRelIso_all"    ,";Reco lepton miniPFRelIso_all ;entries",30,0,.05)
        self.bookTH1("h_lep_upper_unmatch_endcap_miniPFRelIso_allxPT" ,";Reco lepton miniPFRelIso_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_upper_unmatch_endcap_bTagDeepCSV"       ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_upper_unmatch_endcap_lostHits"          ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_upper_unmatch_endcap_VLooseFOEleID"     ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_upper_unmatch_endcap_tightEleID"        ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_upper_unmatch_endcap_convVeto"          ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_upper_unmatch_endcap_mva"               ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_upper_unmatch_endcap_pt"                ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_upper_unmatch_endcap_mvaFall17_WP80"    ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_upper_unmatch_endcap_mva_small"         ,";Reco lepton mva score", 30, -1, 1)
        self.bookTH1("h_lep_upper_unmatch_endcap_trkRelIso"         ,";Reco lepton trkRelIso; entries", 30, 0, 5)

        #outside
        self.bookTH1("h_lep_outside_ip3d"              ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_outside_sip3d"             ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_outside_pfRelIso03_all"    ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_outside_pfRelIso03_allxPT" ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_outside_bTagDeepCSV"       ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_outside_lostHits"          ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_outside_VLooseFOEleID"     ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_outside_tightEleID"        ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_outside_convVeto"          ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_outside_mva"               ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_outside_pt"                ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_outside_mvaFall17_WP80"    ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_outside_mva_small"         ,";Reco lepton mva score", 30, -1, 1)
        self.bookTH1("h_lep_outside_trkRelIso"         ,";Reco lepton trkRelIso; entries", 30, 0, 5)

        ## matched
        self.bookTH1("h_lep_match_outside_ip3d"              ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_match_outside_sip3d"             ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_match_outside_pfRelIso03_all"    ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_match_outside_pfRelIso03_allxPT" ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_match_outside_bTagDeepCSV"       ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_match_outside_lostHits"          ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_match_outside_VLooseFOEleID"     ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_match_outside_tightEleID"        ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_match_outside_convVeto"          ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_match_outside_mva"               ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_match_outside_pt"                ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_match_outside_mvaFall17_WP80"    ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_match_outside_mva_small"         ,";Reco lepton mva score", 30, -1, 1)

        ## unmatched
        self.bookTH1("h_lep_unmatch_outside_ip3d"              ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_unmatch_outside_sip3d"             ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_unmatch_outside_pfRelIso03_all"    ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_unmatch_outside_pfRelIso03_allxPT" ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_unmatch_outside_bTagDeepCSV"       ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_unmatch_outside_lostHits"          ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_unmatch_outside_VLooseFOEleID"     ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_unmatch_outside_tightEleID"        ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_unmatch_outside_convVeto"          ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_unmatch_outside_mva"               ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_unmatch_outside_pt"                ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_unmatch_outside_mvaFall17_WP80"    ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_unmatch_outside_mva_small"         ,";Reco lepton mva score", 30, -1, 1)

        ### split lower
        #### matched
        self.bookTH1("h_lep_lower_match_outside_ip3d"              ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_lower_match_outside_sip3d"             ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_lower_match_outside_pfRelIso03_all"    ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_lower_match_outside_pfRelIso03_allxPT" ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_lower_match_outside_bTagDeepCSV"       ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_lower_match_outside_lostHits"          ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_lower_match_outside_VLooseFOEleID"     ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_lower_match_outside_tightEleID"        ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_lower_match_outside_convVeto"          ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_lower_match_outside_mva"               ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_lower_match_outside_pt"                ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_lower_match_outside_mvaFall17_WP80"    ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_lower_match_outside_mva_small"         ,";Reco lepton mva score", 30, -1, 1)

        #### unmatched (2<pt<5)
        self.bookTH1("h_lep_lower_unmatch_outside_ip3d"              ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_lower_unmatch_outside_sip3d"             ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_lower_unmatch_outside_pfRelIso03_all"    ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_lower_unmatch_outside_pfRelIso03_allxPT" ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_lower_unmatch_outside_bTagDeepCSV"       ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_lower_unmatch_outside_lostHits"          ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_lower_unmatch_outside_VLooseFOEleID"     ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_lower_unmatch_outside_tightEleID"        ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_lower_unmatch_outside_convVeto"          ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_lower_unmatch_outside_mva"               ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_lower_unmatch_outside_pt"                ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_lower_unmatch_outside_mvaFall17_WP80"    ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_lower_unmatch_outside_mva_small"         ,";Reco lepton mva score", 30, -1, 1)

        ### split upper (5<pt<10)
        ## matched
        self.bookTH1("h_lep_upper_match_outside_ip3d"              ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_upper_match_outside_sip3d"             ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_upper_match_outside_pfRelIso03_all"    ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_upper_match_outside_pfRelIso03_allxPT" ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_upper_match_outside_bTagDeepCSV"       ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_upper_match_outside_lostHits"          ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_upper_match_outside_VLooseFOEleID"     ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_upper_match_outside_tightEleID"        ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_upper_match_outside_convVeto"          ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_upper_match_outside_mva"               ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_upper_match_outside_pt"                ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_upper_match_outside_mvaFall17_WP80"    ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_upper_match_outside_mva_small"         ,";Reco lepton mva score", 30, -1, 1)

        ## unmatched
        self.bookTH1("h_lep_upper_unmatch_outside_ip3d"              ,";Reco lepton ip3d  ;entries",20,-0.002,0.2)
        self.bookTH1("h_lep_upper_unmatch_outside_sip3d"             ,";Reco lepton sip3d ;entries",20,0,3)
        self.bookTH1("h_lep_upper_unmatch_outside_pfRelIso03_all"    ,";Reco lepton pfRelIso03_all ;entries",30,0,.05)
        self.bookTH1("h_lep_upper_unmatch_outside_pfRelIso03_allxPT" ,";Reco lepton pfRelIso03_allxPT ;entries",20,0,5)
        self.bookTH1("h_lep_upper_unmatch_outside_bTagDeepCSV"       ,";Reco lepton bTagDeepCSV ;entries",40,0,1)
        self.bookTH1("h_lep_upper_unmatch_outside_lostHits"          ,";Reco lepton lostHits ;entries", 10, 0, 5)
        self.bookTH1("h_lep_upper_unmatch_outside_VLooseFOEleID"     ,";Reco lepton VLooseFOEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_upper_unmatch_outside_tightEleID"        ,";Reco lepton tightEleID; entries", 2, 0, 2)
        self.bookTH1("h_lep_upper_unmatch_outside_convVeto"          ,";Reco lepton convVeto; entries", 2, 0, 2)
        self.bookTH1("h_lep_upper_unmatch_outside_mva"               ,";Reco lepton mva score; entries", 30, -2, 10)
        self.bookTH1("h_lep_upper_unmatch_outside_pt"                ,";Reco lepton p_{T}; entries", 30, 0, 10)
        self.bookTH1("h_lep_upper_unmatch_outside_mvaFall17_WP80"    ,";Reco lepton mvaFall17V2noIso_WP80", 2, 0, 2)
        self.bookTH1("h_lep_upper_unmatch_outside_mva_small"         ,";Reco lepton mva score", 30, -1, 1)

        ## 2d hists booking
        self.bookObject("h_lep_pt_mva",
             ROOT.TH2F("h_lep_pt_mva",";Reco lepton p_{T} [GeV]; Reco lepton mva", 20,0,10, 10,-5,10))

        self.bookObject("h_lep_eta_mva",
             ROOT.TH2F("h_lep_eta_mva",";Reco lepton #eta; Reco lepton mva", 10,-2.7,2.7, 30,-5,10))

        self.bookObject("h_lep_pt_pfRelIso",
             ROOT.TH2F("h_lep_pt_pfRelIso",";Reco lepton p_{T} [GeV]; Reco lepton pfRelIso03_all", 20,0,10, 50,-0.5,4))

        self.bookObject("h_lep_pt_pfRelIsoxPT",
             ROOT.TH2F("h_lep_pt_pfRelIsoxPT",";Reco lepton p_{T} [GeV]; Reco lepton pfRelIso03_all*p_{T} [GeV]", 20,0,10, 50,-0.5,4))

        self.bookObject("h_lep_pt_trkRelIso",
             ROOT.TH2F("h_lep_pt_pfRelIsoxPT",";Reco lepton p_{T} [GeV]; Reco lepton pfRelIso03_all*p_{T} [GeV]", 20,0,10, 50,-0.5,4))

        self.bookObject("h_lep_pt_miniPFRelIso",
             ROOT.TH2F("h_lep_pt_miniPFRelIso",";Reco lepton p_{T} [GeV]; Reco lepton miniPFRelIso03_all", 20,0,10, 50,-0.5,4))

        self.bookObject("h_lep_pt_miniPFRelIsoxPT",
             ROOT.TH2F("h_lep_pt_miniPFRelIsoxPT",";Reco lepton p_{T} [GeV]; Reco lepton miniPFRelIso03_all*p_{T} [GeV]", 20,0,10, 50,-0.5,4))

        self.bookObject("h_lep_pt_ip3d",
             ROOT.TH2F("h_lep_pt_ip3d",";Reco lepton p_{T} [GeV]; Reco lepton ip3d", 20,0,10, 20,-0.002,.2))

        self.bookObject("h_lep_pt_sip3d",
             ROOT.TH2F("h_lep_pt_sip3d",";Reco lepton p_{T} [GeV]; Reco lepton sip3d", 20,0,10, 20,0,3))

        self.bookObject("h_lep_pt_bTagDeepCSV",
             ROOT.TH2F("h_lep_pt_bTagDeepCSV",";Reco lepton p_{T} [GeV]; Reco lepton bTagDeepCSV", 20,0,10, 42,-0.01,1.01))

        self.bookObject("h_lep_pt_convVeto",
             ROOT.TH2F("h_lep_pt_convVeto",";Reco lepton p_{T} [GeV]; Reco lepton convVeto", 20,0,10, 2,0,2))
        self.bookObject("h_lep_pt_lostHits",
             ROOT.TH2F("h_lep_pt_lostHits",";Reco lepton p_{T} [GeV]; Reco lepton lostHits", 20,0,10, 10,0,5))


        ### matched
        self.bookObject("h_lep_match_pt_mva",
             ROOT.TH2F("h_lep_match_pt_mva",";Reco lepton p_{T} [GeV]; Reco lepton mva", 20,0,10, 30,-5,10))

        self.bookObject("h_lep_match_eta_mva",
             ROOT.TH2F("h_lep_match_eta_mva",";Reco lepton #eta; Reco lepton mva", 10, -2.7, 2.7, 30,-5, 10))

        self.bookObject("h_lep_match_pt_pfRelIso",
             ROOT.TH2F("h_lep_match_pt_pfRelIso",";Reco lepton p_{T} [GeV]; Reco lepton pfRelIso03_all", 20,0,10, 50,-0.5,4))

        self.bookObject("h_lep_match_pt_pfRelIsoxPT",
             ROOT.TH2F("h_lep_match_pt_pfRelIsoxPT",";Reco lepton p_{T} [GeV]; Reco lepton pfRelIso03_all*p_{T} [GeV]", 20,0,10, 50,-0.5,4))

        self.bookObject("h_lep_match_pt_miniPFRelIso",
             ROOT.TH2F("h_lep_match_pt_miniPFRelIso",";Reco lepton p_{T} [GeV]; Reco lepton miniPFRelIso_all", 20,0,10, 50,-0.5,4))

        self.bookObject("h_lep_match_pt_miniPFRelIsoxPT",
             ROOT.TH2F("h_lep_match_pt_miniPFRelIsoxPT",";Reco lepton p_{T} [GeV]; Reco lepton miniPFRelIso_all*p_{T} [GeV]", 20,0,10, 50,-0.5,4))


        self.bookObject("h_lep_match_pt_ip3d",
             ROOT.TH2F("h_lep_match_pt_ip3d",";Reco lepton p_{T} [GeV]; Reco lepton ip3d", 20,0,10, 20,-0.002,.2))

        self.bookObject("h_lep_match_pt_sip3d",
             ROOT.TH2F("h_lep_match_pt_sip3d",";Reco lepton p_{T} [GeV]; Reco lepton sip3d", 20,0,10, 20,0,3))

        self.bookObject("h_lep_match_pt_bTagDeepCSV",
             ROOT.TH2F("h_lep_match_pt_bTagDeepCSV",";Reco lepton p_{T} [GeV]; Reco lepton bTagDeepCSV", 20,0,10, 42,-0.01,1.01))

        self.bookObject("h_lep_match_pt_convVeto",
             ROOT.TH2F("h_lep_match_pt_convVeto",";Reco lepton p_{T} [GeV]; Reco lepton convVeto", 20,0,10, 2,0,2))
        self.bookObject("h_lep_match_pt_lostHits",
             ROOT.TH2F("h_lep_match_pt_lostHits",";Reco lepton p_{T} [GeV]; Reco lepton lostHits", 20,0,10, 10,0,5))



        #### pt split (2<pt<5 and 5<pt<10)
        arr=array('d', (2, 5, 10))
        arr_eta=array('d', (-2.5, -1.47, 1.47, 2.5))

        self.bookObject("h_lep_split_pt_mva",
             ROOT.TH2F("h_lep_split_pt_mva",
                       ";Reco lepton p_{T} [GeV]; Reco lepton mva", len(arr)-1, arr, 30,-5,10))

        self.bookObject("h_lep_split_eta_mva",
             ROOT.TH2F("h_lep_split_eta_mva",
                       ";Reco lepton #eta; Reco lepton mva", len(arr_eta)-1, arr, 30, -5, 10))

        ### unmatched
        self.bookObject("h_lep_unmatch_pt_mva",
              ROOT.TH2F("h_lep_unmatch_pt_mva",";Reco lepton p_{T} [GeV]; Reco lepton mva", 20,0,10, 30,-5,10))

        self.bookObject("h_lep_unmatch_eta_mva",
              ROOT.TH2F("h_lep_unmatch_eta_mva",";Reco lepton #eta; Reco lepton mva", 10,-2.7,2.7, 30,-5,10))


    def endJob(self):
      #  print('endJob')

        Module.endJob(self)
    
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

    def analyze(self, event):
        if not self.collect == "LepRecl":
            leptons = Collection(event, self.collect)
        else:
            leptons = Collection(event, "LepGood")

        gen_particles = Collection(event, "GenPart")
        gen_leptons   = filter(self.genLeptonSelector, gen_particles)
        #gen_electrons = filter(lambda lep: abs(lep.pdgId)==11, gen_leptons)
        
        if (self.lepton == 'electron') or (self.lepton == 'Electron'):
            lepton_use     = filter(lambda lep: abs(lep.pdgId)==11, leptons)
            gen_lepton_use = filter(lambda lep: abs(lep.pdgId)==11, gen_leptons)
        
        elif (self.lepton == 'softElectron'):
            lepton_use     = filter(lambda lep: abs(lep.pdgId)==11 and lep.ID>1, leptons)
            gen_lepton_use = filter(lambda lep: abs(lep.pdgId)==11, gen_leptons)

        elif (self.lepton == 'muon') or (self.lepton == 'Muon'):
            lepton_use     = filter(lambda lep: abs(lep.pdgId)==13, leptons)
            gen_lepton_use = filter(lambda lep: abs(lep.pdgId)==13, gen_leptons)

        #electrons = filter( lambda lep: abs(lep.pdgId)==11, leptons)

        #gen_particles = Collection(event, "GenPart")
        for ip, p in enumerate(gen_particles):
            p.idx = ip

        #record truth_to_reco mapping
        truth_to_reco_ele = dict()

        #recl = True
        #if self.collect == "LepRecl":
        #    recl = ele.isLepTight_Recl

        # reco electron loop
        for lep_idx, ele in enumerate(lepton_use):
            match=False
            if self.lepton=='softElectron':
                match=self.truthMatch(ele, gen_lepton_use)
                #print(ele.genPartIdx, match)
            
            recl = True
            barrel  = (abs(ele.eta)<=1.47)
            endcap  = (2.5>abs(ele.eta)>1.47)
            outside = (2.5<=abs(ele.eta))

            #print(self.collect)
            if self.collect == "LepRecl":
             #   print("is LepRecl")
                recl = ele.isLepTight_Recl
                                                    #prompt ele            ele from prompt tau
            isTruthMatch = (ele.genPartIdx >= 0 and (ele.genPartFlav==1 or ele.genPartFlav==15))

            if self.Recleaner(ele) and recl:
                self.h_lep_ip3d.Fill(ele.ip3d)
                self.h_lep_sip3d.Fill(ele.sip3d)
                self.h_lep_pfRelIso03_all.Fill(ele.pfRelIso03_all) 
                self.h_lep_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                self.h_lep_miniPFRelIso_all.Fill(ele.miniPFRelIso_all)
                self.h_lep_miniPFRelIso_allxPT.Fill(ele.miniPFRelIso_all * ele.pt)
                self.h_lep_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                self.h_lep_lostHits.Fill(ele.lostHits)
                self.h_lep_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                self.h_lep_tightEleID.Fill(tightEleID(ele, 2018))
                self.h_lep_convVeto.Fill(ele.convVeto)
                self.h_lep_pt.Fill(ele.pt)
                self.h_lep_trkRelIso.Fill(ele.trkRelIso)
                if ele.pt<=10:
                    self.h_lep_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))

                if ele.pt <= 5:
                    #mva = calculateRawMVA(getattr(ele, 'mvaFall17V2noIsoFromMini'))
                    #mva_small = getattr(ele, 'mvaFall17V2noIsoFromMini')
                    mva = -999
                    mva_small = -999

                elif ele.pt > 5:
                    mva = calculateRawMVA(getattr(ele, 'mvaFall17V2noIso'))
                    mva_small = getattr(ele, 'mvaFall17V2noIso')

                self.h_lep_mva.Fill(mva)
                self.h_lep_mva_small.Fill(mva_small)

                self.h_lep_pt_mva.Fill( ele.pt, mva )
                self.h_lep_eta_mva.Fill( ele.eta, mva )
                self.h_lep_split_pt_mva.Fill(ele.pt, mva)
                self.h_lep_split_eta_mva.Fill(ele.eta, mva)
                
                self.h_lep_pt_trkRelIso.Fill(ele.pt, ele.trkRelIso)
                self.h_lep_pt_pfRelIso.Fill(ele.pt, ele.pfRelIso03_all)
                self.h_lep_pt_pfRelIsoxPT.Fill(ele.pt, ele.pfRelIso03_all * ele.pt)
                self.h_lep_pt_miniPFRelIso.Fill(ele.pt, ele.miniPFRelIso_all)
                self.h_lep_pt_miniPFRelIsoxPT.Fill(ele.pt, ele.miniPFRelIso_all*ele.pt)
                self.h_lep_pt_ip3d.Fill( ele.pt, ele.ip3d )
                self.h_lep_pt_sip3d.Fill( ele.pt, ele.sip3d )
                self.h_lep_pt_bTagDeepCSV.Fill( ele.pt, ele.jetBTagDeepCSV )
                self.h_lep_pt_convVeto.Fill( ele.pt, ele.convVeto )
                self.h_lep_pt_lostHits.Fill( ele.pt, ele.lostHits )

                if isTruthMatch or match:
                    #more match hists
                    self.h_lep_match_ip3d.Fill(ele.ip3d)
                    self.h_lep_match_sip3d.Fill(ele.sip3d)
                    self.h_lep_match_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                    self.h_lep_match_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                    self.h_lep_match_miniPFRelIso_all.Fill(ele.miniPFRelIso_all)
                    self.h_lep_match_miniPFRelIso_allxPT.Fill(ele.miniPFRelIso_all * ele.pt)
                    self.h_lep_match_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                    self.h_lep_match_lostHits.Fill(ele.lostHits)
                    self.h_lep_match_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                    self.h_lep_match_tightEleID.Fill(tightEleID(ele, 2018))
                    self.h_lep_match_convVeto.Fill(ele.convVeto)
                    self.h_lep_match_pt.Fill(ele.pt)
                    self.h_lep_match_trkRelIso.Fill(ele.trkRelIso)
                    if ele.pt<=10:
                        self.h_lep_match_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                    self.h_lep_match_mva.Fill(mva)
                    self.h_lep_match_mva_small.Fill(mva_small)

                    self.h_lep_match_pt_mva.Fill( ele.pt, mva )
                    self.h_lep_match_eta_mva.Fill( ele.eta, mva )

                    self.h_lep_match_pt_pfRelIso.Fill(ele.pt, ele.pfRelIso03_all)
                    self.h_lep_match_pt_pfRelIsoxPT.Fill(ele.pt, ele.pfRelIso03_all*ele.pt)
                    self.h_lep_match_pt_miniPFRelIso.Fill(ele.pt, ele.miniPFRelIso_all)
                    self.h_lep_match_pt_miniPFRelIsoxPT.Fill(ele.pt, ele.miniPFRelIso_all*ele.pt)
                    self.h_lep_match_pt_ip3d.Fill( ele.pt, ele.ip3d )
                    self.h_lep_match_pt_sip3d.Fill( ele.pt, ele.sip3d )
                    self.h_lep_match_pt_bTagDeepCSV.Fill( ele.pt, ele.jetBTagDeepCSV )
                    self.h_lep_match_pt_convVeto.Fill( ele.pt, ele.convVeto )
                    self.h_lep_match_pt_lostHits.Fill( ele.pt, ele.lostHits )

                    if ele.pt>2 and ele.pt<5:
                        self.h_lep_lower_match_ip3d.Fill(ele.ip3d)
                        self.h_lep_lower_match_sip3d.Fill(ele.sip3d)
                        self.h_lep_lower_match_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                        self.h_lep_lower_match_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                        self.h_lep_lower_match_miniPFRelIso_all.Fill(ele.miniPFRelIso_all)
                        self.h_lep_lower_match_miniPFRelIso_allxPT.Fill(ele.miniPFRelIso_all * ele.pt)
                        self.h_lep_lower_match_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                        self.h_lep_lower_match_lostHits.Fill(ele.lostHits)
                        self.h_lep_lower_match_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                        self.h_lep_lower_match_tightEleID.Fill(tightEleID(ele, 2018))
                        self.h_lep_lower_match_convVeto.Fill(ele.convVeto)
                        self.h_lep_lower_match_mva.Fill(mva)
                        self.h_lep_lower_match_pt.Fill(ele.pt)
                        self.h_lep_lower_match_trkRelIso.Fill(ele.trkRelIso)
                        if ele.pt<=10:
                            self.h_lep_lower_match_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                        self.h_lep_lower_match_mva_small.Fill(mva_small)
                    #self.h_lep_match_pt_mva.Fill( ele.pt, mva )
                    #self.h_lep_match_eta_mva.Fill( ele.eta, mva )

                    elif ele.pt>=5 and ele.pt<10:
                        self.h_lep_upper_match_ip3d.Fill(ele.ip3d)
                        self.h_lep_upper_match_sip3d.Fill(ele.sip3d)
                        self.h_lep_upper_match_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                        self.h_lep_upper_match_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                        self.h_lep_upper_match_miniPFRelIso_all.Fill(ele.miniPFRelIso_all)
                        self.h_lep_upper_match_miniPFRelIso_allxPT.Fill(ele.miniPFRelIso_all * ele.pt)
                        self.h_lep_upper_match_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                        self.h_lep_upper_match_lostHits.Fill(ele.lostHits)
                        self.h_lep_upper_match_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                        self.h_lep_upper_match_tightEleID.Fill(tightEleID(ele, 2018))
                        self.h_lep_upper_match_convVeto.Fill(ele.convVeto)
                        self.h_lep_upper_match_mva.Fill(mva)
                        self.h_lep_upper_match_pt.Fill(ele.pt)
                        self.h_lep_upper_match_trkRelIso.Fill(ele.trkRelIso)
                        if ele.pt<=10:
                            self.h_lep_upper_match_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                        self.h_lep_upper_match_mva_small.Fill(mva_small)

                    #self.h_lep_match_pt_mva.Fill( ele.pt, mva )
                    #self.h_lep_match_eta_mva.Fill( ele.eta, mva )

                elif not (isTruthMatch or match): #not isTruthMatch:
                    #more unmatch plots
                    self.h_lep_unmatch_ip3d.Fill(ele.ip3d)
                    self.h_lep_unmatch_sip3d.Fill(ele.sip3d)
                    self.h_lep_unmatch_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                    self.h_lep_unmatch_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                    self.h_lep_unmatch_miniPFRelIso_all.Fill(ele.miniPFRelIso_all)
                    self.h_lep_unmatch_miniPFRelIso_allxPT.Fill(ele.miniPFRelIso_all * ele.pt)
                    self.h_lep_unmatch_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                    self.h_lep_unmatch_lostHits.Fill(ele.lostHits)
                    self.h_lep_unmatch_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                    self.h_lep_unmatch_tightEleID.Fill(tightEleID(ele, 2018))
                    self.h_lep_unmatch_convVeto.Fill(ele.convVeto)
                    self.h_lep_unmatch_pt.Fill(ele.pt)
                    self.h_lep_unmatch_mva.Fill(mva)
                    self.h_lep_unmatch_trkRelIso.Fill(ele.trkRelIso)
                    if ele.pt<=10:
                        self.h_lep_unmatch_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                    self.h_lep_unmatch_mva_small.Fill(mva_small)

                    self.h_lep_unmatch_pt_mva.Fill( ele.pt, mva )
                    self.h_lep_unmatch_eta_mva.Fill( ele.eta, mva )

                    if ele.pt>2 and ele.pt<5:
                        self.h_lep_lower_unmatch_ip3d.Fill(ele.ip3d)
                        self.h_lep_lower_unmatch_sip3d.Fill(ele.sip3d)
                        self.h_lep_lower_unmatch_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                        self.h_lep_lower_unmatch_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                        self.h_lep_lower_unmatch_miniPFRelIso_all.Fill(ele.miniPFRelIso_all)
                        self.h_lep_lower_unmatch_miniPFRelIso_allxPT.Fill(ele.miniPFRelIso_all * ele.pt)
                        self.h_lep_lower_unmatch_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                        self.h_lep_lower_unmatch_lostHits.Fill(ele.lostHits)
                        self.h_lep_lower_unmatch_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                        self.h_lep_lower_unmatch_tightEleID.Fill(tightEleID(ele, 2018))
                        self.h_lep_lower_unmatch_convVeto.Fill(ele.convVeto)
                        self.h_lep_lower_unmatch_mva.Fill(mva)
                        self.h_lep_lower_unmatch_pt.Fill(ele.pt)
                        self.h_lep_lower_unmatch_trkRelIso.Fill(ele.trkRelIso)
                        if ele.pt<=10:
                            self.h_lep_lower_unmatch_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                        self.h_lep_lower_unmatch_mva_small.Fill(mva_small)

                    #self.h_lep_match_pt_mva.Fill( ele.pt, mva )
                    #self.h_lep_match_eta_mva.Fill( ele.eta, mva )

                    elif ele.pt>=5 and ele.pt<10:
                        self.h_lep_upper_unmatch_ip3d.Fill(ele.ip3d)
                        self.h_lep_upper_unmatch_sip3d.Fill(ele.sip3d)
                        self.h_lep_upper_unmatch_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                        self.h_lep_upper_unmatch_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                        self.h_lep_upper_unmatch_miniPFRelIso_all.Fill(ele.miniPFRelIso_all)
                        self.h_lep_upper_unmatch_miniPFRelIso_allxPT.Fill(ele.miniPFRelIso_all * ele.pt)
                        self.h_lep_upper_unmatch_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                        self.h_lep_upper_unmatch_lostHits.Fill(ele.lostHits)
                        self.h_lep_upper_unmatch_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                        self.h_lep_upper_unmatch_tightEleID.Fill(tightEleID(ele, 2018))
                        self.h_lep_upper_unmatch_convVeto.Fill(ele.convVeto)
                        self.h_lep_upper_unmatch_mva.Fill(mva)
                        self.h_lep_upper_unmatch_pt.Fill(ele.pt)
                        self.h_lep_upper_unmatch_trkRelIso.Fill(ele.trkRelIso)
                        if ele.pt<=10:
                            self.h_lep_upper_unmatch_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                        self.h_lep_upper_unmatch_mva_small.Fill(mva_small)

                #FIXME stopped here adding miniPFRelIso
                if barrel:
                    self.h_lep_barrel_ip3d.Fill(ele.ip3d)
                    self.h_lep_barrel_sip3d.Fill(ele.sip3d)
                    self.h_lep_barrel_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                    self.h_lep_barrel_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                    self.h_lep_barrel_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                    self.h_lep_barrel_lostHits.Fill(ele.lostHits)
                    self.h_lep_barrel_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                    self.h_lep_barrel_tightEleID.Fill(tightEleID(ele, 2018))
                    self.h_lep_barrel_convVeto.Fill(ele.convVeto)
                    self.h_lep_barrel_pt.Fill(ele.pt)
                    self.h_lep_barrel_trkRelIso.Fill(ele.trkRelIso)
                    if ele.pt<=10:
                        self.h_lep_barrel_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                    self.h_lep_barrel_mva.Fill(mva)
                    self.h_lep_barrel_mva_small.Fill(mva_small)

                    #self.h_lep_pt_mva.Fill( ele.pt, mva )
                    #self.h_lep_eta_mva.Fill( ele.eta, mva )

                    if isTruthMatch or match:
                        #more match hists
                        self.h_lep_match_barrel_ip3d.Fill(ele.ip3d)
                        self.h_lep_match_barrel_sip3d.Fill(ele.sip3d)
                        self.h_lep_match_barrel_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                        self.h_lep_match_barrel_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                        self.h_lep_match_barrel_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                        self.h_lep_match_barrel_lostHits.Fill(ele.lostHits)
                        self.h_lep_match_barrel_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                        self.h_lep_match_barrel_tightEleID.Fill(tightEleID(ele, 2018))
                        self.h_lep_match_barrel_convVeto.Fill(ele.convVeto)
                        self.h_lep_match_barrel_pt.Fill(ele.pt)
                        self.h_lep_match_barrel_trkRelIso.Fill(ele.trkRelIso)
                        if ele.pt<=10:
                            self.h_lep_match_barrel_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                        self.h_lep_match_barrel_mva.Fill(mva)
                        self.h_lep_match_barrel_mva_small.Fill(mva_small)
                        #self.h_lep_match_pt_mva.Fill( ele.pt, mva )
                        #self.h_lep_match_eta_mva.Fill( ele.eta, mva )

                        if ele.pt>2 and ele.pt<5:
                            self.h_lep_lower_match_barrel_ip3d.Fill(ele.ip3d)
                            self.h_lep_lower_match_barrel_sip3d.Fill(ele.sip3d)
                            self.h_lep_lower_match_barrel_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                            self.h_lep_lower_match_barrel_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                            self.h_lep_lower_match_barrel_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                            self.h_lep_lower_match_barrel_lostHits.Fill(ele.lostHits)
                            self.h_lep_lower_match_barrel_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                            self.h_lep_lower_match_barrel_tightEleID.Fill(tightEleID(ele, 2018))
                            self.h_lep_lower_match_barrel_convVeto.Fill(ele.convVeto)
                            self.h_lep_lower_match_barrel_mva.Fill(mva)
                            self.h_lep_lower_match_barrel_pt.Fill(ele.pt)
                            self.h_lep_lower_match_barrel_trkRelIso.Fill(ele.trkRelIso)
                            if ele.pt<=10:
                                self.h_lep_lower_match_barrel_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                            self.h_lep_lower_match_barrel_mva_small.Fill(mva_small)
                        #self.h_lep_match_pt_mva.Fill( ele.pt, mva )
                        #self.h_lep_match_eta_mva.Fill( ele.eta, mva )

                        elif ele.pt>=5 and ele.pt<10:
                            self.h_lep_upper_match_barrel_ip3d.Fill(ele.ip3d)
                            self.h_lep_upper_match_barrel_sip3d.Fill(ele.sip3d)
                            self.h_lep_upper_match_barrel_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                            self.h_lep_upper_match_barrel_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                            self.h_lep_upper_match_barrel_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                            self.h_lep_upper_match_barrel_lostHits.Fill(ele.lostHits)
                            self.h_lep_upper_match_barrel_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                            self.h_lep_upper_match_barrel_tightEleID.Fill(tightEleID(ele, 2018))
                            self.h_lep_upper_match_barrel_convVeto.Fill(ele.convVeto)
                            self.h_lep_upper_match_barrel_mva.Fill(mva)
                            self.h_lep_upper_match_barrel_pt.Fill(ele.pt)
                            self.h_lep_upper_match_barrel_trkRelIso.Fill(ele.trkRelIso)
                            if ele.pt<=10:
                                self.h_lep_upper_match_barrel_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                            self.h_lep_upper_match_barrel_mva_small.Fill(mva_small)
                        #self.h_lep_match_pt_mva.Fill( ele.pt, mva )
                        #self.h_lep_match_eta_mva.Fill( ele.eta, mva )

                    elif not (isTruthMatch or match): #not isTruthMatch:
                        #more unmatch plots
                        self.h_lep_unmatch_barrel_ip3d.Fill(ele.ip3d)
                        self.h_lep_unmatch_barrel_sip3d.Fill(ele.sip3d)
                        self.h_lep_unmatch_barrel_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                        self.h_lep_unmatch_barrel_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                        self.h_lep_unmatch_barrel_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                        self.h_lep_unmatch_barrel_lostHits.Fill(ele.lostHits)
                        self.h_lep_unmatch_barrel_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                        self.h_lep_unmatch_barrel_tightEleID.Fill(tightEleID(ele, 2018))
                        self.h_lep_unmatch_barrel_convVeto.Fill(ele.convVeto)
                        self.h_lep_unmatch_barrel_pt.Fill(ele.pt)
                        self.h_lep_unmatch_barrel_mva.Fill(mva)
                        self.h_lep_unmatch_barrel_trkRelIso.Fill(ele.trkRelIso)
                        if ele.pt<=10:
                            self.h_lep_unmatch_barrel_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                        self.h_lep_unmatch_barrel_mva_small.Fill(mva_small)
                        #self.h_lep_unmatch_pt_mva.Fill( ele.pt, mva )
                        #self.h_lep_unmatch_eta_mva.Fill( ele.eta, mva )

                        if ele.pt>2 and ele.pt<5:
                            self.h_lep_lower_unmatch_barrel_ip3d.Fill(ele.ip3d)
                            self.h_lep_lower_unmatch_barrel_sip3d.Fill(ele.sip3d)
                            self.h_lep_lower_unmatch_barrel_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                            self.h_lep_lower_unmatch_barrel_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                            self.h_lep_lower_unmatch_barrel_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                            self.h_lep_lower_unmatch_barrel_lostHits.Fill(ele.lostHits)
                            self.h_lep_lower_unmatch_barrel_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                            self.h_lep_lower_unmatch_barrel_tightEleID.Fill(tightEleID(ele, 2018))
                            self.h_lep_lower_unmatch_barrel_convVeto.Fill(ele.convVeto)
                            self.h_lep_lower_unmatch_barrel_mva.Fill(mva)
                            self.h_lep_lower_unmatch_barrel_pt.Fill(ele.pt)
                            self.h_lep_lower_unmatch_barrel_trkRelIso.Fill(ele.trkRelIso)
                            if ele.pt<=10:
                                self.h_lep_lower_unmatch_barrel_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                            self.h_lep_lower_unmatch_barrel_mva_small.Fill(mva_small)
                        #self.h_lep_match_pt_mva.Fill( ele.pt, mva )
                        #self.h_lep_match_eta_mva.Fill( ele.eta, mva )

                        elif ele.pt>=5 and ele.pt<10:
                            self.h_lep_upper_unmatch_barrel_ip3d.Fill(ele.ip3d)
                            self.h_lep_upper_unmatch_barrel_sip3d.Fill(ele.sip3d)
                            self.h_lep_upper_unmatch_barrel_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                            self.h_lep_upper_unmatch_barrel_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                            self.h_lep_upper_unmatch_barrel_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                            self.h_lep_upper_unmatch_barrel_lostHits.Fill(ele.lostHits)
                            self.h_lep_upper_unmatch_barrel_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                            self.h_lep_upper_unmatch_barrel_tightEleID.Fill(tightEleID(ele, 2018))
                            self.h_lep_upper_unmatch_barrel_convVeto.Fill(ele.convVeto)
                            self.h_lep_upper_unmatch_barrel_mva.Fill(mva)
                            self.h_lep_upper_unmatch_barrel_pt.Fill(ele.pt)
                            self.h_lep_upper_unmatch_barrel_trkRelIso.Fill(ele.trkRelIso)
                            if ele.pt<=10:
                                self.h_lep_upper_unmatch_barrel_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                            self.h_lep_upper_unmatch_barrel_mva_small.Fill(mva_small)

                if endcap:
                    self.h_lep_endcap_ip3d.Fill(ele.ip3d)
                    self.h_lep_endcap_sip3d.Fill(ele.sip3d)
                    self.h_lep_endcap_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                    self.h_lep_endcap_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                    self.h_lep_endcap_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                    self.h_lep_endcap_lostHits.Fill(ele.lostHits)
                    self.h_lep_endcap_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                    self.h_lep_endcap_tightEleID.Fill(tightEleID(ele, 2018))
                    self.h_lep_endcap_convVeto.Fill(ele.convVeto)
                    self.h_lep_endcap_pt.Fill(ele.pt)
                    self.h_lep_endcap_trkRelIso.Fill(ele.trkRelIso)
                    if ele.pt<=10:
                        self.h_lep_endcap_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                    self.h_lep_endcap_mva.Fill(mva)
                    self.h_lep_endcap_mva_small.Fill(mva_small)

                    #self.h_lep_pt_mva.Fill( ele.pt, mva )
                    #self.h_lep_eta_mva.Fill( ele.eta, mva )

                    if isTruthMatch or match:
                        #more match hists
                        self.h_lep_match_endcap_ip3d.Fill(ele.ip3d)
                        self.h_lep_match_endcap_sip3d.Fill(ele.sip3d)
                        self.h_lep_match_endcap_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                        self.h_lep_match_endcap_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                        self.h_lep_match_endcap_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                        self.h_lep_match_endcap_lostHits.Fill(ele.lostHits)
                        self.h_lep_match_endcap_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                        self.h_lep_match_endcap_tightEleID.Fill(tightEleID(ele, 2018))
                        self.h_lep_match_endcap_convVeto.Fill(ele.convVeto)
                        self.h_lep_match_endcap_pt.Fill(ele.pt)
                        self.h_lep_match_endcap_trkRelIso.Fill(ele.trkRelIso)
                        if ele.pt<=10:
                            self.h_lep_match_endcap_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                        self.h_lep_match_endcap_mva.Fill(mva)
                        self.h_lep_match_endcap_mva_small.Fill(mva_small)

                        #self.h_lep_match_pt_mva.Fill( ele.pt, mva )
                        #self.h_lep_match_eta_mva.Fill( ele.eta, mva )

                        if ele.pt>2 and ele.pt<5:
                            self.h_lep_lower_match_endcap_ip3d.Fill(ele.ip3d)
                            self.h_lep_lower_match_endcap_sip3d.Fill(ele.sip3d)
                            self.h_lep_lower_match_endcap_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                            self.h_lep_lower_match_endcap_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                            self.h_lep_lower_match_endcap_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                            self.h_lep_lower_match_endcap_lostHits.Fill(ele.lostHits)
                            self.h_lep_lower_match_endcap_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                            self.h_lep_lower_match_endcap_tightEleID.Fill(tightEleID(ele, 2018))
                            self.h_lep_lower_match_endcap_convVeto.Fill(ele.convVeto)
                            self.h_lep_lower_match_endcap_mva.Fill(mva)
                            self.h_lep_lower_match_endcap_pt.Fill(ele.pt)
                            self.h_lep_lower_match_endcap_trkRelIso.Fill(ele.trkRelIso)
                            if ele.pt<=10:
                                self.h_lep_lower_match_endcap_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                            self.h_lep_lower_match_endcap_mva_small.Fill(mva_small)
                        #self.h_lep_match_pt_mva.Fill( ele.pt, mva )
                        #self.h_lep_match_eta_mva.Fill( ele.eta, mva )

                        elif ele.pt>=5 and ele.pt<10:
                            self.h_lep_upper_match_endcap_ip3d.Fill(ele.ip3d)
                            self.h_lep_upper_match_endcap_sip3d.Fill(ele.sip3d)
                            self.h_lep_upper_match_endcap_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                            self.h_lep_upper_match_endcap_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                            self.h_lep_upper_match_endcap_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                            self.h_lep_upper_match_endcap_lostHits.Fill(ele.lostHits)
                            self.h_lep_upper_match_endcap_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                            self.h_lep_upper_match_endcap_tightEleID.Fill(tightEleID(ele, 2018))
                            self.h_lep_upper_match_endcap_convVeto.Fill(ele.convVeto)
                            self.h_lep_upper_match_endcap_mva.Fill(mva)
                            self.h_lep_upper_match_endcap_pt.Fill(ele.pt)
                            self.h_lep_upper_match_endcap_trkRelIso.Fill(ele.trkRelIso)
                            if ele.pt<=10:
                                self.h_lep_upper_match_endcap_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                            self.h_lep_upper_match_endcap_mva_small.Fill(mva_small)
                        #self.h_lep_match_pt_mva.Fill( ele.pt, mva )
                        #self.h_lep_match_eta_mva.Fill( ele.eta, mva )

                    elif not (isTruthMatch or match): #not isTruthMatch:
                        #more unmatch plots
                        self.h_lep_unmatch_endcap_ip3d.Fill(ele.ip3d)
                        self.h_lep_unmatch_endcap_sip3d.Fill(ele.sip3d)
                        self.h_lep_unmatch_endcap_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                        self.h_lep_unmatch_endcap_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                        self.h_lep_unmatch_endcap_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                        self.h_lep_unmatch_endcap_lostHits.Fill(ele.lostHits)
                        self.h_lep_unmatch_endcap_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                        self.h_lep_unmatch_endcap_tightEleID.Fill(tightEleID(ele, 2018))
                        self.h_lep_unmatch_endcap_convVeto.Fill(ele.convVeto)
                        self.h_lep_unmatch_endcap_pt.Fill(ele.pt)
                        self.h_lep_unmatch_endcap_mva.Fill(mva)
                        self.h_lep_unmatch_endcap_trkRelIso.Fill(ele.trkRelIso)
                        if ele.pt<=10:
                            self.h_lep_unmatch_endcap_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                        self.h_lep_unmatch_endcap_mva_small.Fill(mva_small)

                        #self.h_lep_unmatch_pt_mva.Fill( ele.pt, mva )
                        #self.h_lep_unmatch_eta_mva.Fill( ele.eta, mva )

                        if ele.pt>2 and ele.pt<5:
                            self.h_lep_lower_unmatch_endcap_ip3d.Fill(ele.ip3d)
                            self.h_lep_lower_unmatch_endcap_sip3d.Fill(ele.sip3d)
                            self.h_lep_lower_unmatch_endcap_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                            self.h_lep_lower_unmatch_endcap_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                            self.h_lep_lower_unmatch_endcap_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                            self.h_lep_lower_unmatch_endcap_lostHits.Fill(ele.lostHits)
                            self.h_lep_lower_unmatch_endcap_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                            self.h_lep_lower_unmatch_endcap_tightEleID.Fill(tightEleID(ele, 2018))
                            self.h_lep_lower_unmatch_endcap_convVeto.Fill(ele.convVeto)
                            self.h_lep_lower_unmatch_endcap_mva.Fill(mva)
                            self.h_lep_lower_unmatch_endcap_pt.Fill(ele.pt)
                            self.h_lep_lower_unmatch_endcap_trkRelIso.Fill(ele.trkRelIso)
                            if ele.pt<=10:
                                self.h_lep_lower_unmatch_endcap_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                            self.h_lep_lower_unmatch_endcap_mva_small.Fill(mva_small)
                        #self.h_lep_match_pt_mva.Fill( ele.pt, mva )
                        #self.h_lep_match_eta_mva.Fill( ele.eta, mva )

                        elif ele.pt>=5 and ele.pt<10:
                            self.h_lep_upper_unmatch_endcap_ip3d.Fill(ele.ip3d)
                            self.h_lep_upper_unmatch_endcap_sip3d.Fill(ele.sip3d)
                            self.h_lep_upper_unmatch_endcap_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                            self.h_lep_upper_unmatch_endcap_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                            self.h_lep_upper_unmatch_endcap_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                            self.h_lep_upper_unmatch_endcap_lostHits.Fill(ele.lostHits)
                            self.h_lep_upper_unmatch_endcap_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                            self.h_lep_upper_unmatch_endcap_tightEleID.Fill(tightEleID(ele, 2018))
                            self.h_lep_upper_unmatch_endcap_convVeto.Fill(ele.convVeto)
                            self.h_lep_upper_unmatch_endcap_mva.Fill(mva)
                            self.h_lep_upper_unmatch_endcap_pt.Fill(ele.pt)
                            self.h_lep_upper_unmatch_endcap_trkRelIso.Fill(ele.trkRelIso)
                            if ele.pt<=10:
                                self.h_lep_upper_unmatch_endcap_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                            self.h_lep_upper_unmatch_endcap_mva_small.Fill(mva_small)

                if outside:
                    self.h_lep_outside_ip3d.Fill(ele.ip3d)
                    self.h_lep_outside_sip3d.Fill(ele.sip3d)
                    self.h_lep_outside_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                    self.h_lep_outside_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                    self.h_lep_outside_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                    self.h_lep_outside_lostHits.Fill(ele.lostHits)
                    self.h_lep_outside_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                    self.h_lep_outside_tightEleID.Fill(tightEleID(ele, 2018))
                    self.h_lep_outside_convVeto.Fill(ele.convVeto)
                    self.h_lep_outside_pt.Fill(ele.pt)
                    #self.h_lep_outside_trkRelIso.Fill(ele.trkRelIso)
                    if ele.pt<=10:
                        self.h_lep_outside_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                    self.h_lep_outside_mva.Fill(mva)
                    self.h_lep_outside_mva_small.Fill(mva_small)

                    #self.h_lep_pt_mva.Fill( ele.pt, mva )
                    #self.h_lep_eta_mva.Fill( ele.eta, mva )

                    if isTruthMatch or match:
                        #more match hists
                        self.h_lep_match_outside_ip3d.Fill(ele.ip3d)
                        self.h_lep_match_outside_sip3d.Fill(ele.sip3d)
                        self.h_lep_match_outside_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                        self.h_lep_match_outside_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                        self.h_lep_match_outside_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                        self.h_lep_match_outside_lostHits.Fill(ele.lostHits)
                        self.h_lep_match_outside_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                        self.h_lep_match_outside_tightEleID.Fill(tightEleID(ele, 2018))
                        self.h_lep_match_outside_convVeto.Fill(ele.convVeto)
                        self.h_lep_match_outside_pt.Fill(ele.pt)
                        if ele.pt<=10:
                            self.h_lep_match_outside_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                        self.h_lep_match_outside_mva.Fill(mva)
                        self.h_lep_match_outside_mva_small.Fill(mva_small)

                        #self.h_lep_match_pt_mva.Fill( ele.pt, mva )
                        #self.h_lep_match_eta_mva.Fill( ele.eta, mva )

                        if ele.pt>2 and ele.pt<5:
                            self.h_lep_lower_match_outside_ip3d.Fill(ele.ip3d)
                            self.h_lep_lower_match_outside_sip3d.Fill(ele.sip3d)
                            self.h_lep_lower_match_outside_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                            self.h_lep_lower_match_outside_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                            self.h_lep_lower_match_outside_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                            self.h_lep_lower_match_outside_lostHits.Fill(ele.lostHits)
                            self.h_lep_lower_match_outside_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                            self.h_lep_lower_match_outside_tightEleID.Fill(tightEleID(ele, 2018))
                            self.h_lep_lower_match_outside_convVeto.Fill(ele.convVeto)
                            self.h_lep_lower_match_outside_mva.Fill(mva)
                            self.h_lep_lower_match_outside_pt.Fill(ele.pt)
                            if ele.pt<=10:
                                self.h_lep_lower_match_outside_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                            self.h_lep_lower_match_outside_mva_small.Fill(mva_small)
                        #self.h_lep_match_pt_mva.Fill( ele.pt, mva )
                        #self.h_lep_match_eta_mva.Fill( ele.eta, mva )

                        elif ele.pt>=5 and ele.pt<10:
                            self.h_lep_upper_match_outside_ip3d.Fill(ele.ip3d)
                            self.h_lep_upper_match_outside_sip3d.Fill(ele.sip3d)
                            self.h_lep_upper_match_outside_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                            self.h_lep_upper_match_outside_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                            self.h_lep_upper_match_outside_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                            self.h_lep_upper_match_outside_lostHits.Fill(ele.lostHits)
                            self.h_lep_upper_match_outside_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                            self.h_lep_upper_match_outside_tightEleID.Fill(tightEleID(ele, 2018))
                            self.h_lep_upper_match_outside_convVeto.Fill(ele.convVeto)
                            self.h_lep_upper_match_outside_mva.Fill(mva)
                            self.h_lep_upper_match_outside_pt.Fill(ele.pt)
                            if ele.pt<=10:
                                self.h_lep_upper_match_outside_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                            self.h_lep_upper_match_outside_mva_small.Fill(mva_small)

                        #self.h_lep_match_pt_mva.Fill( ele.pt, mva )
                        #self.h_lep_match_eta_mva.Fill( ele.eta, mva )

                    elif not (isTruthMatch or match): #not isTruthMatch:
                        #more unmatch plots
                        self.h_lep_unmatch_outside_ip3d.Fill(ele.ip3d)
                        self.h_lep_unmatch_outside_sip3d.Fill(ele.sip3d)
                        self.h_lep_unmatch_outside_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                        self.h_lep_unmatch_outside_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                        self.h_lep_unmatch_outside_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                        self.h_lep_unmatch_outside_lostHits.Fill(ele.lostHits)
                        self.h_lep_unmatch_outside_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                        self.h_lep_unmatch_outside_tightEleID.Fill(tightEleID(ele, 2018))
                        self.h_lep_unmatch_outside_convVeto.Fill(ele.convVeto)
                        self.h_lep_unmatch_outside_pt.Fill(ele.pt)
                        self.h_lep_unmatch_outside_mva.Fill(mva)
                        if ele.pt<=10:
                            self.h_lep_unmatch_outside_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                        self.h_lep_unmatch_outside_mva_small.Fill(mva_small)

                        #self.h_lep_unmatch_pt_mva.Fill( ele.pt, mva )
                        #self.h_lep_unmatch_eta_mva.Fill( ele.eta, mva )

                        if ele.pt>2 and ele.pt<5:
                            self.h_lep_lower_unmatch_outside_ip3d.Fill(ele.ip3d)
                            self.h_lep_lower_unmatch_outside_sip3d.Fill(ele.sip3d)
                            self.h_lep_lower_unmatch_outside_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                            self.h_lep_lower_unmatch_outside_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                            self.h_lep_lower_unmatch_outside_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                            self.h_lep_lower_unmatch_outside_lostHits.Fill(ele.lostHits)
                            self.h_lep_lower_unmatch_outside_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                            self.h_lep_lower_unmatch_outside_tightEleID.Fill(tightEleID(ele, 2018))
                            self.h_lep_lower_unmatch_outside_convVeto.Fill(ele.convVeto)
                            self.h_lep_lower_unmatch_outside_mva.Fill(mva)
                            self.h_lep_lower_unmatch_outside_pt.Fill(ele.pt)
                            if ele.pt<=10:
                                self.h_lep_lower_unmatch_outside_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                            self.h_lep_lower_unmatch_outside_mva_small.Fill(mva_small)

                        #self.h_lep_match_pt_mva.Fill( ele.pt, mva )
                        #self.h_lep_match_eta_mva.Fill( ele.eta, mva )

                        elif ele.pt>=5 and ele.pt<10:
                            self.h_lep_upper_unmatch_outside_ip3d.Fill(ele.ip3d)
                            self.h_lep_upper_unmatch_outside_sip3d.Fill(ele.sip3d)
                            self.h_lep_upper_unmatch_outside_pfRelIso03_all.Fill(ele.pfRelIso03_all)
                            self.h_lep_upper_unmatch_outside_pfRelIso03_allxPT.Fill(ele.pfRelIso03_all * ele.pt)
                            self.h_lep_upper_unmatch_outside_bTagDeepCSV.Fill(ele.jetBTagDeepCSV)
                            self.h_lep_upper_unmatch_outside_lostHits.Fill(ele.lostHits)
                            self.h_lep_upper_unmatch_outside_VLooseFOEleID.Fill(VLooseFOEleID(ele, 2018))
                            self.h_lep_upper_unmatch_outside_tightEleID.Fill(tightEleID(ele, 2018))
                            self.h_lep_upper_unmatch_outside_convVeto.Fill(ele.convVeto)
                            self.h_lep_upper_unmatch_outside_mva.Fill(mva)
                            self.h_lep_upper_unmatch_outside_pt.Fill(ele.pt)
                            if ele.pt<=10:
                                self.h_lep_upper_unmatch_outside_mvaFall17_WP80.Fill(getattr(ele, 'mvaFall17V2Iso_WP80'))
                            self.h_lep_upper_unmatch_outside_mva_small.Fill(mva_small)

   #     for gen_ele in gen_lepton_use:
   #         isRecoMatch = (gen_ele.idx in truth_to_reco_ele)
   #         #recl=True
   #         #if self.collect == "LepRecl":
   #          #   recl=gen_ele.isLepTight_Recl
   #
   #         if isRecoMatch:
   #             self.h_gen_lep_match_ip3d.Fill(gen_ele.ip3d)
   #             self.h_gen_lep_match_sip3d.Fill(gen_ele.sip3d)
   #             self.h_gen_lep_match_pfRelIso03_all.Fill(gen_ele.pfRelIso03_all)
   #             self.h_gen_lep_match_pfRelIso03_allxPT.Fill(gen_ele.pfRelIso03_all * ele.pt)
   #             self.h_gen_lep_match_bTagDeepCSV.Fill(gen_ele.jetBTagDeepCSV)
   #             self.h_gen_lep_match_lostHits.Fill(gen_ele.lostHits)
   #             self.h_gen_lep_match_VLooseFOEleID.Fill(VLooseFOEleID(gen_ele, 2018))
   #             self.h_gen_lep_match_tightEleID.Fill(tightEleID(gen_ele, 2018))
   #             self.h_gen_lep_match_convVeto.Fill(gen_ele.convVeto)
   #
   #             #mva = calculateRawMVA(getattr(gen_ele, 'mvaFall17V2noIso'))
   #             #self.h_gen_lep_match_mva.Fill(mva)

        return True


