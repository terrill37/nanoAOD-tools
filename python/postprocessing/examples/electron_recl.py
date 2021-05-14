import ROOT
from ROOT import TPad
import time
from optparse import OptionParser


ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetPalette(ROOT.kRainBow)
#ROOT.gStyle.SetPalette(ROOT.kPastel)

#p=OptionParser()
#p.add_option('-i', '--input',  type='string', dest='inFile',
#             action="append", help='input analyzed file')
#
#p.add_option('-o', '--output', type='string', dest='output', help='output file location')
#
#
#(o,a) = p.parse_args()
#
#inFile=[]
#for i in range(0, len(o.inFile)):
#    inFile.append(ROOT.TFile(o.inFile[i], "READ"))


#import os
#if not os.path.exists(o.output):
#    os.mkdir(o.output)

def hist_change(histName):
    ele_loc = histName.find('ele_')+3
    histInsert = histName[:ele_loc]+"_recl"+histName[ele_loc:]
    return histInsert

def collection(file_name):
    collections = [('LepGood',ROOT.kBlue), 
                   ('LepAll',ROOT.kRed), 
                   ('LepRecl', ROOT.kGreen), 
                   ('pfRelIso03xPT', ROOT.kCyan),
                   ('pfRelIso03', ROOT.kMagenta),
                   ('sip3d', ROOT.kViolet),
                   ('ip3d', ROOT.kOrange),
                   ('deepCSV', ROOT.kPink-9),
                   ('lostHits', ROOT.kGray+2),
                   ('convVeto', ROOT.kViolet+7),
                   ('tightEleID', ROOT.kSpring),
                   ('VLooseFOEleID', ROOT.kPink+10),
                   ]
    #print(file_name)
    for i, label in enumerate(collections):
        #print("in label check loop")
        if label[0] in file_name:
            #print(file_name)
            #print(label)
            return label

    return ('unknown', ROOT.kBlack)

def Layered_plot(plot_name, plot_dir, units, yTitle, feels, output,
                 maxY=None, stats=None, legend=True, file_name="", log=False):
    can = ROOT.TCanvas()
    #can.SetPalette(68)
    pad1= ROOT.TPad("pad1","pad1", 0, 0, 0.8, 1)
    pad2= ROOT.TPad("pad2","pad2", 0.8, 0, 1, 1)
    pad1.SetRightMargin(0.01)
    pad2.SetLeftMargin(.01)
    pad2.SetRightMargin(0)
    
    pad1.Draw()
    pad2.Draw()

    plots=[]
    for idx, File in enumerate(feels):
       # if "LepRecl" in File[0]:
           # plots.append(File[1].Get(plot_dir + '/' + hist_change(plot_name[0])))
        
        #else:
        plots.append(File[1].Get(plot_dir + '/' + plot_name[0]))

    leg = ROOT.TLegend(0, 0.25, 1, .75)
    leg.SetBorderSize(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.1)

    max_y=[0]
    max_val=0
    for i in range(0, len(plots), 1):
        label = collection(feels[i][0])
        
        #plots[i].SetLineColor(label[1])
        #plots[i].SetMarkerColor(label[1])

        plots[i].GetYaxis().SetTitle(yTitle)
        plots[i].GetXaxis().SetTitle(plot_name[1]+units)
        
        if maxY != None:
            plots[i].GetYaxis().SetRangeUser(0, maxY + .1*maxY)

        else:
            max_y.append(plots[i].GetMaximum())
            if max_y[i+1]>max_y[i] and max_y[i+1]>max_val:
                max_val = max_y[i+1]
                #print(max_val, feels[i])

        leg.AddEntry(plots[i], label[0], 'L')
        if stats == 0:
            plots[i].SetStats(stats)
        else:                     #ksiourmen
            ROOT.gStyle.SetOptStat(111111)

    #print(max_y)
    #print(max_val)
    
    pad1.SetLogy(log)
    pad1.cd()
    
    #print(len(plots))
    if maxY==None:
        plots[0].GetYaxis().SetRangeUser(0.0, (max_val)+.1*(max_val))
    
    if "h_" in plot_name[0]:
        ext="HIST"
    else:
        ext=""

    plots[0].Draw(""+ext)
    for plot in plots[1:]:
        plot.Draw("PLC PMC same"+ext)

    pad2.cd()
    if legend: leg.Draw("same")

    can.SaveAs(output+'/'+plot_name[0]+file_name+'_comp.png')
    can.Clear()

def Normalize(hist):
    '''normalize histograms'''
    if hist.Integral():
        hist.Scale(1./hist.Integral())

    return hist

def plot_int_comp(plot_names, plot_dir, units, yTitle, File, output,
                  maxY=None, stats=None, legend=True, file_name="", log=False, normal=True, palette=False):
    '''internal plot comp for plots in same file
        
        plot_names
        ----------
            list of hist names
    '''
    
    can = ROOT.TCanvas()
    
    pad1= ROOT.TPad("pad1","pad1", 0, 0, 0.8, 1)
    pad2= ROOT.TPad("pad2","pad2", 0.8, 0, 1, 1)
    pad1.SetRightMargin(0.01)
    pad2.SetLeftMargin(.01)
    pad2.SetRightMargin(0)
    
    pad1.Draw()
    pad2.Draw()

    plots=[]
    for idx, hist in enumerate(plot_names):
        #print(File)
        #collect hists from input File
        plot=File[1].Get(plot_dir + '/' + hist)
        #print(plot)
        #normalize
        if normal:
            plot=Normalize(plot)

        #add to list of plots
        plots.append(plot)

    leg = ROOT.TLegend(0, 0.25, 1, .75)
    leg.SetBorderSize(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.1)

    max_y=[0]
    max_val=0
    label = collection(File[0])
    for i in range(0, len(plots), 1):
        #label = collection(File)
        
        #plots[i].SetLineColor(label[1])
        #plots[i].SetMarkerColor(label[1])

        plots[i].GetYaxis().SetTitle(yTitle)
        plots[i].GetXaxis().SetTitle(units)
        
        if maxY != None:
            plots[i].GetYaxis().SetRangeUser(0, maxY + .1*maxY)

        else:
            max_y.append(plots[i].GetMaximum())
            if max_y[i+1]>max_y[i] and max_y[i+1]>max_val:
                max_val = max_y[i+1]
        
        if 'unmatch' in plot_names[i]:
            name='unmatch'
            plots[i].SetLineColor(ROOT.kRed)

        elif 'match' in plot_names[i]:
            name='match'
            plots[i].SetLineColor(ROOT.kBlack)
        
        else:
            name=plot_names[i][6:]
            print name
        
        leg.AddEntry(plots[i], name, 'L')
        if stats == 0:
            plots[i].SetStats(stats)
    
    #print(max_y)
    #print(max_val)
    
    pad1.SetLogy(log)

    pad1.cd()
    if maxY==None:
        plots[0].GetYaxis().SetRangeUser(0.0, (max_val)+.1*(max_val))
    
    if "h_" in plot_names[0]:
        ext="HIST"
    else:
        ext=""
    if palette:
        ext=ext+" PLC"

    plots[0].Draw(""+ext)
    for plot in plots[1:]:
        plot.Draw("same"+ext)

    pad2.cd()
    if legend: leg.Draw("same")

    can.SaveAs(output+'/'+label[0]+file_name+'_comp.png')
    can.Clear()

def match_add(name, plot_dir, inFile):
    #add match or unmatch to plot name in correct position
    #returns match or unmatch plot
    extensions=["match", "unmatch"]
    hists=[]
    #print(name)
    for ext in extensions:
        if ("upper" in name) or ("lower" in name):
            plot_name=name[:11]+'_'+ext+name[11:]
         #   print(plot_name)
        else:
            plot_name=name[:5]+'_'+ext+name[5:]
          #  print(plot_name)
        
        plot=inFile.Get(plot_dir+'/'+plot_name)
        #print(plot)
        hists.append(plot)
    
    return hists, extensions
    

def match_unmatch(plot_name, plot_dir, yTitle, File, output,
                  maxY=None, stats=None, legend=True, file_name="", log=False, normal=True):
    #make layered of specified matched or unmatched histogram

    #get proper match and unmatch plots pulled from file
    hists, ext=match_add(plot_name[0], plot_dir, File)
    #print(File)
    can=ROOT.TCanvas()
    
    leg = ROOT.TLegend(0.7, 0.6, 0.85, .75)
    leg.SetBorderSize(0)
    #leg.SetTextFont(1)
    #leg.SetTextSize(0.075)

    for i in range(0, len(hists), 1):
        #print(hists[i])
        if normal==True:
            hists[i]=Normalize(hists[i])
        #else:
         #   print 'unnormalized'
        
        if i==0:
            hists[i].Draw("HIST")
        else:
            hists[i].Draw("HIST same")
        
        if ext[i]=="match":
            hists[i].SetLineColor(ROOT.kGreen)

        else:
            hists[i].SetLineColor(ROOT.kRed)

        if stats==0:
            hists[i].SetStats(stats)

        if maxY != None:
            hists[i].GetYaxis().SetRangeUser(0, maxY + .1*maxY)
        
        leg.AddEntry(hists[i], ext[i], 'L')
    
    if legend:
        leg.Draw("same")

    can.SaveAs(output+'/'+plot_name[0]+file_name+'.png')

def Hist_2d(plot_name, plot_dir, Feels, output,
            maxY=None, stats=None, file_name="", col=True):
    
    ROOT.gStyle.SetPalette(ROOT.kPastel)    
    label=["",""]
    for f_name in Feels:
        can = ROOT.TCanvas()
        plot = f_name[1].Get(plot_dir + '/' + plot_name) 
   
        if col:
            label=collection(f_name[0])
        

        if stats == 0:
            plot.SetStats(stats)

        plot.Draw('colz')

        can.SaveAs(output+'/'+plot_name+'_'+label[0]+file_name+'.png')
        can.Clear()

def ratio(plot):
    #print(plot)
    nbins=plot.GetNbinsX()
    
    plotRatio_den = plot.Integral(0, nbins+1)
    xvals=[]
    yvals=[]
    n=0
    for i in range(0, nbins, 2):
        plotRatio_num = plot.Integral(i, nbins+1) 
        yvals.append(plotRatio_num/plotRatio_den)
        xvals.append(plot.GetXaxis().GetBinCenter(i))
        n=n+1

    return xvals, yvals, n

def workingPoint(plot_name, plot_dir, yTitle, File, output,
                 maxY=None, stats=None, legend=True, file_name="", log=False):
    #print(File)
    hists, ext=match_add(plot_name[0], plot_dir, File)
    can=ROOT.TCanvas()
    can.SetGrid()
    
    #print(hists)
    #graph=ROOT.TGraph(len(hists[0].GetNbinsX()/2)
    
    leg = ROOT.TLegend(0.7, 0.6, 0.85, .75)
    leg.SetBorderSize(0)
    gr=[]
    for i in range(0, len(hists)):
        xvals, yvals, n = ratio(hists[i])
        gr.append(ROOT.TGraph(n))
        for j in range(len(xvals)):
            gr[i].SetPoint(j, float(xvals[j]), float(yvals[j]))
        if 'match' in ext[i]: gr[i].SetLineColor(ROOT.kGreen)
        if 'unmatch' in ext[i]: gr[i].SetLineColor(ROOT.kRed)
        gr[i].SetLineWidth(4)
        gr[i].SetMarkerStyle(21)
        gr[i].GetXaxis().SetTitle(plot_name[1])
        gr[i].GetYaxis().SetTitle(yTitle)

        leg.AddEntry(gr[i], ext[i], 'L')

    for k in range(len(gr)):
        if k==0:
            gr[k].Draw("ALP")
        else:
            gr[k].Draw("LP")

    can.Update()
    can.GetFrame().SetFillColor(21)
    can.GetFrame().SetBorderSize(12)
    can.Modified
    can.Update()
    
    leg.Draw("same")
    can.SaveAs(output+'/'+plot_name[0]+'_working_point_'+file_name+'.png')

     
