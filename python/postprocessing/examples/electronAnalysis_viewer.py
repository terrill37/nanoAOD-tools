import ROOT
from ROOT import TPad
import time
from optparse import OptionParser


ROOT.gROOT.SetBatch(True)

p=OptionParser()
p.add_option('-i', '--input',  type='string', dest='inFile', help='input analyzed file')
p.add_option('--input2',  type='string', dest='inFile', help='second input analyzed file', default=None)
p.add_option('-o', '--output', type='string', dest='output', help='output file location')

(o,a) = p.parse_args()

inputFile = ROOT.TFile(o.inFile, "READ")

import os
if not os.path.exists(o.output):
    os.mkdir(o.output)

def plots(plot_name, plot_dir, file_name="", log_on=False, units=" (GeV)", legend=False, yTitle="Entries",
          stats=1, colz=False):
    
    can = ROOT.TCanvas()

    plots = []
    leg   = ROOT.TLegend(0.55, 0.35, 0.85, 0.55)
    leg.SetBorderSize(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.035)

    for i in range(0, len(plot_name), 1):
        hist = inputFile.Get(plot_dir + '/' + plot_name[i][0])

        hist.SetLineColor(plot_name[i][1])
        hist.SetMarkerColor(plot_name[i][1])

        hist.GetYaxis().SetTitle(yTitle)
        hist.GetXaxis().SetTitle(plot_name[i][2]+units)

        leg.AddEntry(hist, plot_name[i][0], 'L')
        if stats == 0:
            hist.SetStats(stats)
        
        plots.append(hist)

    can.cd()
    if colz:
        plots[0].Draw('colz')

    else:
        plots[0].Draw()
    for j in range(1, len(plots), 1):
        plots[j].Draw('same')

    if legend: leg.Draw('same')

    can.SaveAs(o.output+'/'+plot_name[i][0]+file_name+'.png')
    can.Clear()

    
    

def main():
    print("electron pt distributions ...")
    time.sleep(1)

    pt_plots = [("h_ele_pt",                  ROOT.kRed,           'pt' ),
                ("h_ele_pt_match",            ROOT.kOrange,        'pt' ),    
                ("h_ele_pt_match_barrel",     ROOT.kYellow +2,     'pt' ),    
                ("h_ele_pt_match_endcap",     ROOT.kGreen,         'pt' ),    
                ("h_gen_ele_pt",              ROOT.kBlue,          'pt' ),    
                ("h_gen_ele_pt_barrel",       ROOT.kViolet,        'pt' ),    
                ("h_gen_ele_pt_endcap",       ROOT.kRed,           'pt' ),    
                ("h_gen_ele_pt_match",        ROOT.kOrange +10,    'pt' ),    
                ("h_gen_ele_pt_match_barrel", ROOT.kYellow -5,     'pt' ),    
                ("h_gen_ele_pt_match_endcap", ROOT.kGreen +3,      'pt' ),    
                ("h_ele_pt_unmatch",          ROOT.kBlue -4,       'pt' ),    
                ("h_ele_pt_unmatch_barrel",   ROOT.kMagenta ,      'pt' ),    
                ("h_ele_pt_unmatch_endcap",   ROOT.kCyan +3,       'pt' ),    
                ]

    for j in range(0, len(pt_plots), 1):
        plots([pt_plots[j]], "plots1") 
    

    print("electron pt efficiencies ...")
    time.sleep(1)
    eff_plots = [("gen_ele_efficiency_barrel",        ROOT.kRed,     'pt'),
                 ("gen_ele_efficiency", ROOT.kBlue,    'pt'),
                 ("gen_ele_efficiency_endcap", ROOT.kSpring,  'pt'),
                 ("gen_ele_efficiency_inner",  ROOT.kMagenta, 'pt'),
                 ]

    for k in range(0, len(eff_plots), 1):
        plots([eff_plots[k]], "plots1")

    plots(eff_plots, "plots1", file_name="_comp", legend=True)
    
    print("electron eta distribution ...")
    time.sleep(1)
    eta_dist = [("h_ele_pt_eta", ROOT.kBlack, 'pt')]
    plots(eta_dist, "plots1", file_name="_comp", yTitle='Reco electron Eta', stats=0, colz=True)


if __name__ == "__main__":
    main()

