import ROOT
from ROOT import TPad
import time
from optparse import OptionParser


ROOT.gROOT.SetBatch(True)

p=OptionParser()
p.add_option('--input1',  type='string', dest='inFile1', help='input analyzed file')
p.add_option('--input2',  type='string', dest='inFile2', help='second input analyzed file')
p.add_option('-o', '--output', type='string', dest='output', help='output file location')

(o,a) = p.parse_args()

inputFile_1 = ROOT.TFile(o.inFile1, "READ")
inputFile_2 = ROOT.TFile(o.inFile2, "READ")

import os
if not os.path.exists(o.output):
    os.mkdir(o.output)

def multipad(plot_name, plot_dir, file_name="", log_on=False, units=" (GeV)", legend=False, yTitle="Entries",
             stats=1, colz=False, fileNames=[o.inFile1, o.inFile2]):
    
    can = ROOT.TCanvas()

    plots = []
    leg   = ROOT.TLegend(0.55, 0.35, 0.85, 0.55)
    leg.SetBorderSize(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.035)
    
    for i in range(0, len(plot_name), 1):
        hist1 = inputFile_1.Get(plot_dir + '/' + plot_name[i][0])
        hist2 = inputFile_2.Get(plot_dir + '/' + plot_name[i][0])
        
        h1_label = collection(fileNames[0])
        h2_label = collection(fileNames[1])

        pad1 = TPad("pad1", "pad1", 0.0, 0.5, 1.0, 0.95)   
        pad1.Draw()
        pad1.SetBottomMargin(0)
        
        can.cd()

        pad2 = TPad("pad2", "pad2", 0.0, 0.05, 1.0, 0.5)
        pad2.Draw()
        pad2.SetTopMargin(0)
        pad2.SetBottomMargin(0.25)

        pad1.cd()
        
        #hist one setup
        hist1.SetTitle("")
        hist1.SetLineColor(h1_label[1])
        hist1.SetMarkerColor(h1_label[1])
        hist1.GetYaxis().SetTitleSize(0.075)
        hist1.GetYaxis().SetTitle(yTitle+" "+h1_label[0])
        hist1.GetYaxis().SetLabelSize(0.075)
        hist1.GetXaxis().SetTitleSize(0)
        hist1.GetXaxis().SetLabelSize(0)
        hist1.GetYaxis().SetTitleOffset(0.3)

        #hist two setup
        hist2.SetTitle("")
        hist2.SetLineColor(h2_label[1])
        hist2.SetMarkerColor(h2_label[1])
        hist2.GetYaxis().SetTitleSize(0.075)
        hist2.GetYaxis().SetTitle(yTitle+" "+h2_label[0])
        hist2.GetYaxis().SetLabelSize(0.075)
        hist2.GetXaxis().SetLabelSize(0.075)
        hist2.GetXaxis().SetTitleSize(0.12)
        hist2.GetYaxis().SetTitleOffset(0.3)

        #leg.AddEntry(hist, plot_name[i][0], 'L')
        if stats == 0:
            hist1.SetStats(stats)
            hist2.SetStats(stats)

        if colz:
            hist1.Draw('colz')
            pad2.cd()
            hist2.Draw('colz')
            can.cd()
        
        else:
            hist1.Draw()
            pad2.cd()
            hist2.Draw()
            can.cd()

        if legend: leg.Draw('same')

        can.SaveAs(o.output+'/'+plot_name[i][0]+file_name+'.png')
        can.Clear()

def eff_comp(plot_name, plot_dir, maxY=None, file_name="", log_on=False, units=" (GeV)", 
             legend=False, yTitle="Entries", stats=1, 
             inputFiles=[inputFile_1, inputFile_2], inputNames=[o.inFile1,o.inFile2]):

    can = ROOT.TCanvas()

    plots = []
    leg   = ROOT.TLegend(0.65, 0.15, 0.9, 0.25)
    leg.SetBorderSize(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.035)
    
    max_y=[0]
    for i in range(0, len(inputFiles), 1):
        hist = inputFiles[i].Get(plot_dir + '/' + plot_name[0])
        
        label = collection(inputNames[i])
        
        hist.SetLineColor(label[1])
        hist.SetMarkerColor(label[1])
        hist.SetMarkerStyle(i)

        hist.GetYaxis().SetTitle(yTitle)
        hist.GetXaxis().SetTitle(plot_name[1]+units)
        
        if maxY != None:
            hist.GetYaxis().SetRangeUser(0.0, maxY+.1*maxY)
        
        else:
            max_y.append(hist.GetMaximum())
            if max_y[i+1]>max_y[i]:
                max_val = max_y[i+1]
                #print(max_val)

            
            #hist.GetYaxis().SetRangeUser(0.0, max_y+.1*max_y)

        leg.AddEntry(hist, label[0], 'L')
        if stats == 0:
            hist.SetStats(stats)

        plots.append(hist)

    can.cd()
    if maxY==None:
        plots[0].GetYaxis().SetRangeUser(0.0, (max_val)+.1*(max_val))
    
    plots[0].Draw()
    for j in range(1, len(plots), 1):
        plots[j].Draw('same')

    if legend: leg.Draw('same')

    can.SaveAs(o.output+'/'+plot_name[0]+file_name+'_comp.png')
    can.Clear()
        
def collection(file_name):
    collections = [('LepGood',ROOT.kBlue), ('LepAll',ROOT.kRed)]
    for i, label in enumerate(collections):
        if label[0] in file_name:
            return label


def main():
    print('eta distribution comp ... ')
    time.sleep(1)

    eta_dist = [("h_ele_pt_eta", ROOT.kBlack, 'reco electron pt')]
    multipad(eta_dist, 'plots1', yTitle="reco electron Eta", colz=True, stats=0)

    print('efficiencies ...')
    time.sleep(1)

    eff_plots = [("gen_ele_efficiency_barrel",  'electron pt'),
                 ("gen_ele_efficiency",         'electron pt'),
                 ("gen_ele_efficiency_endcap",  'electron pt'),
                 ("gen_ele_efficiency_inner",   'electron pt'),
                 ]

    for j, plot in enumerate(eff_plots):
        eff_comp(plot, 'plots1', maxY=1, legend=True, yTitle='match efficiency')

    unmatch_plots = [("h_ele_pt_unmatch",        'electron pt'),
                     ("h_ele_pt_unmatch_barrel", 'electron pt'),
                     ("h_ele_pt_unmatch_endcap", 'electron pt'),
                     ("h_ele_pt_match",          'electron pt'),
                     ("h_ele_pt_match_barrel",   'electron pt'),
                     ("h_ele_pt_match_endcap",   'electron pt'),
                     #("h_ele_pt_match_inner",    'electron pt'),
                    ]
    for k, plot in enumerate(unmatch_plots):
        eff_comp(plot, 'plots1', legend=True, yTitle='match efficiency', stats=0)

if __name__ == "__main__":
    main()

