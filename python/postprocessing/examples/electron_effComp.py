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
inFile2=[]
file2=[]
for i in range(0, len(o.inFile)):
    inFile.append(ROOT.TFile(o.inFile[i], "READ"))
    file2_name=o.inFile[i].replace('.root','_2.root')
    file2.append(file2_name)
    inFile2.append(ROOT.TFile(file2_name, "READ"))

def main():
    print("plots starting ...")
    time.sleep(1)
    
    files=[]
    files2=[]
    for idx, val in enumerate(o.inFile):
        files.append((o.inFile[idx], inFile[idx])) 
        files2.append((file2[idx], inFile2[idx]))

    print("efficiencies ...")
    time.sleep(.5)
    
    plots=[("gen_ele_efficiency_barrel",  'gen electron pt'),
           ("gen_ele_efficiency",         'gen electron pt'),
           ("gen_ele_efficiency_endcap",  'gen electron pt'),
           ("gen_ele_efficiency_inner",   'gen electron pt'),
           ]

    for pl in plots:
        Layered_plot(pl, "plots1", " (GeV)", "efficiency", files, output=o.output, maxY=1, file_name=o.f_name)

    print("unmatch hists ...")
    time.sleep(.5)

    hists=[("h_ele_pt_unmatch",           'reco electron pt'),
           ("h_ele_pt_unmatch_barrel",    'reco electron pt'),
           ("h_ele_pt_unmatch_endcap",    'reco electron pt'),]

    zoom_files=files[1:]

    for h in hists:
        Layered_plot(h, "plots1", " (GeV)", "", files, output=o.output, stats=0, file_name=o.f_name)
        if not len(zoom_files)==0:
            Layered_plot(h, "plots1", " (GeV)", "", zoom_files, output=o.output, stats=0, file_name=o.f_name+'_zoom')
    
    print("matched versus unmatched normalized ...")
    hists=["h_ele_pt_unmatch", "h_ele_pt_match"]
           
    hists2=[["h_ele_lower_match_pfRelIso03_all","h_ele_lower_unmatch_pfRelIso03_all"],
            ["h_ele_lower_match_pfRelIso03_allxPT","h_ele_lower_unmatch_pfRelIso03_allxPT"],
            ["h_ele_lower_match_miniPFRelIso_all","h_ele_lower_unmatch_miniPFRelIso_all"],
            ["h_ele_lower_match_miniPFRelIso_allxPT","h_ele_lower_unmatch_miniPFRelIso_allxPT"]]


    for j, f_name in enumerate(files):
        #print(f_name)
        plot_int_comp(hists, "plots1", "electron p_{T} (GeV)", "", f_name, output=o.output,
                      stats=0, legend=True, file_name="_ele_pt")
        #for hist in hists2:
        #    print(hist)
        #    plot_int_comp(hist, "plots1", "", "", files2[j], output=o.output,
        #                  stats=0, legend=True, file_name="_full_test", normal=False)

    #hists2=[["h_ele_lower_match_pfRelIso03_all","h_ele_lower_unmatch_pfRelIso03_all"],
     #       ["h_ele_lower_match_pfRelIso03_allxPT","h_ele_lower_unmatch_pfRelIso03_allxPT"]]



    print("end plotting")

if __name__ == "__main__":
    main()

 
