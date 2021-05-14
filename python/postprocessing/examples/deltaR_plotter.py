import ROOT
from ROOT import TPad
import time
from optparse import OptionParser
from electron_recl import *

ROOT.gROOT.SetBatch(True)

p=OptionParser()
p.add_option('-i', '--input',  type='string', dest='inFile',
             help='input analyzed file')

p.add_option('-o', '--output', type='string', dest='output', help='output file location')

p.add_option('-f', '--file_name', type='string', dest='f_name', default='',
             help='adds additional name to plots for differentiation from others with similar name')

(o,a) = p.parse_args()

inFile=(ROOT.TFile(o.inFile, "READ"))

def main():
    print("plots starting ...")
    time.sleep(.5)

    hists2d=[("h_lep_debug"),
             ("h_lep_pt_vs_relIso03"),
             ("h_lep1_dR_miniPFRelIso"),]
    #print(h2)
    for h2 in hists2d:
        Hist_2d(h2, "plots1", [("", inFile,),], o.output,
                maxY=None, stats=0, file_name="", col=False)
   

    hist=["h_lep_deltaR",
          "h_lep_deltaR_dM10",
          "h_lep_deltaR_dM5",]
    
    hist2=["h_lep1_dRgreat0p3_pfRelIso03_allxPT",
           "h_lep2_dRgreat0p3_pfRelIso03_allxPT",
           "h_lep1_dRless0p3_pfRelIso03_allxPT",
           "h_lep2_dRless0p3_pfRelIso03_allxPT",
           "h_lep1_dRgreat0p3_pfRelIso03_all",
           "h_lep2_dRgreat0p3_pfRelIso03_all",
           "h_lep1_dRless0p3_pfRelIso03_all",
           "h_lep2_dRless0p3_pfRelIso03_all",
           "h_lep1_dRgreat0p3_miniPFRelIso_allxPT",
           "h_lep2_dRgreat0p3_miniPFRelIso_allxPT",
           "h_lep1_dRless0p3_miniPFRelIso_allxPT",
           "h_lep2_dRless0p3_miniPFRelIso_allxPT",
           "h_lep1_dRgreat0p3_miniPFRelIso_all",
           "h_lep2_dRgreat0p3_miniPFRelIso_all",
           "h_lep1_dRless0p3_miniPFRelIso_all",
           "h_lep2_dRless0p3_miniPFRelIso_all",
]
    hists_sub=["h_lep1_dRless0p3_pfRelIso03_allxPTsubPT",
               "h_lep2_dRless0p3_pfRelIso03_allxPTsubPT",
               "h_lep1_dRgreat0p3_pfRelIso03_allxPTsubPT",
               "h_lep2_dRgreat0p3_pfRelIso03_allxPTsubPT",]
    
    for h in hist:      
        Layered_plot([h,"gen electron delta_R"], "plots1", "", "", [[o.inFile,inFile]], o.output)
    for h in hist2:
        if "xPT" in h:
            axis_ext="xPT"
        else:
            axis_ext=""
        Layered_plot([h,"reco electron pfRelIso03_all"+axis_ext], "plots1", "", "", [[o.inFile,inFile]], o.output)
    for h in hists_sub:
        Layered_plot([h,"reco electron iso-pt"], "plots1", "", "", [[o.inFile,inFile]], o.output)

    plot_int_comp(hist, "plots1", "$Gen  Electron  \Delta R$","Entries", [o.inFile, inFile], o.output, normal=False, palette=True)
    
    Layered_plot(["h_highest_pt","largest p_{T} electron"], "plots1", "", "", [[o.inFile,inFile]], o.output)

    print("end plotting ...")

if __name__ == "__main__":
    main()

