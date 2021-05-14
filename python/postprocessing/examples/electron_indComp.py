import ROOT
from ROOT import TPad
import time
from optparse import OptionParser
from electron_recl import * 

ROOT.gROOT.SetBatch(True)

p=OptionParser()
p.add_option('-i', '--input',  type='string', dest='inFile',
             action="append", help='input analyzed file')

p.add_option('-o', '--output', type='string', dest='output', help='output file location')


(o,a) = p.parse_args()

inFile=[]
for i in range(0, len(o.inFile)):
    inFile.append(ROOT.TFile(o.inFile[i], "READ"))


def main():
    print("plots starting ...")
    time.sleep(1)
    
    files=[]
    for idx, val in enumerate(o.inFile):
        files.append((o.inFile[idx], inFile[idx])) 


    #print("efficiencies ...")
    time.sleep(.5)
    
    plots=[("h_ele_ip3d",  'reco electron ip3d'),
           ("h_ele_sip3d",         'reco electron sip3d'),
           ("h_ele_pfRelIso03_all",  'reco electron pfRelIso03_all'),
           ("h_ele_pfRelIso03_allxPT",   'reco electron pfRelIso03_allxPT'),
           ("
           ("h_ele_bTagDeepCSV", "reco electron bTagDeepCSV"),
           ]

    for pl in plots:
        Layered_plot(pl, "plots1", " (GeV)", "efficiency", files, output=o.output, file_name="")

    #print("unmatch hists ...")
    #time.sleep(.5)

    #hists=[("h_ele_pt_unmatch",           'reco electron pt'),
    #       ("h_ele_pt_unmatch_barrel",    'reco electron pt'),
    #       ("h_ele_pt_unmatch_endcap",    'reco electron pt'),]

    #zoom_files=files[1:]

    #for h in hists:
    #    Layered_plot(h, "plots1", " (GeV)", "", files, output=o.output, stats=0)
    #    Layered_plot(h, "plots1", " (GeV)", "", zoom_files, output=o.output, stats=0, file_name='_zoom')

if __name__ == "__main__":
    main()

 
