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

p.add_option('-f', '--file_name', type='string', dest='f_name', default='', 
             help='adds additional name to plots for differentiation from others with similar name')

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


#    print("efficiencies ...")
#    time.sleep(.5)
    
#    plots=[("gen_ele_efficiency_barrel",  'gen electron pt'),
#           ("gen_ele_efficiency",         'gen electron pt'),
#           ("gen_ele_efficiency_endcap",  'gen electron pt'),
#           ("gen_ele_efficiency_inner",   'gen electron pt'),
#           ]

#    for pl in plots:
#        Layered_plot(pl, "plots1", " (GeV)", "efficiency", files, output=o.output, maxY=1, file_name=o.f_name)

    print("reco hists ...")
    time.sleep(.5)

    hists=[("h_ele_ip3d",                 'reco electron ip3d'),
           ("h_ele_sip3d",                'reco electron sip3d'),
           ("h_ele_pfRelIso03_all",       'reco electron relative isolation'),
           ("h_ele_pfRelIso03_allxPT",    'reco electron isolation'),
           ("h_ele_bTagDeepCSV",          'reco electron deepCSV score'),
           ("h_ele_lostHits",             'reco electron lostHits'),
           ("h_ele_VLooseFOEleID",        'reco electron VLooseFOEleID'),
           ("h_ele_tightEleID",           'reco electron tightEleID'),
           ("h_ele_convVeto",             'reco electron convVeto'),
           ("h_ele_mva",                  'reco electron mva'),
           ("h_ele_mva_small",            'reco electron mva'),
           ("h_ele_mvaFall17_WP80",       'reco electron WP80'),
           ]

    zoom_files=files[1:]

    for h in hists:
        Layered_plot(h, "plots1", "", "", files, output=o.output, stats=0, file_name=o.f_name)
        Layered_plot(h, "plots1", "", "", zoom_files, output=o.output, stats=0, file_name=o.f_name+'_zoom')
        #Layered_plot(h, "plots1", "", "", files, output=o.output, stats=0, file_name=o.f_name+'_log', log=True)
    
    print("2d hists ...")
    time.sleep(.5)

    hists2d=[("h_ele_pt_mva"),
             ("h_ele_eta_mva"),]

    for h2 in hists2d:
        Hist_2d(h2, "plots1", "", "eta", "reco electron pt (GeV)", files, o.output,
                maxY=None, stats=0, file_name="")

    print("end plotting")

if __name__ == "__main__":
    main()

 
