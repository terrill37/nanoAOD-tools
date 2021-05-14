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
    print("starting plotting ...")
    time.sleep(.5)

    hists=[("h_ele_mva",                'reco electron mva'),
           ("h_ele_upper_mva",          'reco electron mva'),
           ("h_ele_lower_mva",          'reco electron mva'),
           ("h_ele_barrel_mva",         'reco electron mva'),
           ("h_ele_upper_barrel_mva",   'reco electron mva'),
           ("h_ele_lower_barrel_mva",   'reco electron mva'),
           ("h_ele_endcap_mva",         'reco electron mva'),
           ("h_ele_lower_endcap_mva",   'reco electron mva'),
           ("h_ele_upper_endcap_mva",   'reco electron mva'),
           ]

    for h in hists:
        workingPoint(h, 'plots1', 'efficiency', inFile, o.output)

    print('end plotting ...')

if __name__=="__main__":
    main()
