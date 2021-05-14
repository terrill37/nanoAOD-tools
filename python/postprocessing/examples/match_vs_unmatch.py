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
    time.sleep(1)
   
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
           ("h_ele_pt",                   'reco electron pt'),
           ("h_ele_mvaFall17_WP80",       'reco electron WP80'),
           ("h_ele_mva_small",            'reco electron mva_small'),
           ("h_ele_upper_ip3d",                 'reco electron ip3d'),
           ("h_ele_upper_sip3d",                'reco electron sip3d'),
           ("h_ele_upper_pfRelIso03_all",       'reco electron relative isolation'),
           ("h_ele_upper_pfRelIso03_allxPT",    'reco electron isolation'),
           ("h_ele_upper_bTagDeepCSV",          'reco electron deepCSV score'),
           ("h_ele_upper_lostHits",             'reco electron lostHits'),
           ("h_ele_upper_VLooseFOEleID",        'reco electron VLooseFOEleID'),
           ("h_ele_upper_tightEleID",           'reco electron tightEleID'),
           ("h_ele_upper_convVeto",             'reco electron convVeto'),
           ("h_ele_upper_mva",                  'reco electron mva'),
           ("h_ele_upper_pt",                   'reco electron pt'),
           ("h_ele_upper_mvaFall17_WP80",       'reco electron WP80'),
           ("h_ele_upper_mva_small",            'reco electron mva_small'),
           ("h_ele_lower_ip3d",                 'reco electron ip3d'),
           ("h_ele_lower_sip3d",                'reco electron sip3d'),
           ("h_ele_lower_pfRelIso03_all",       'reco electron relative isolation'),
           ("h_ele_lower_pfRelIso03_allxPT",    'reco electron isolation'),
           ("h_ele_lower_bTagDeepCSV",          'reco electron deepCSV score'),
           ("h_ele_lower_lostHits",             'reco electron lostHits'),
           ("h_ele_lower_VLooseFOEleID",        'reco electron VLooseFOEleID'),
           ("h_ele_lower_tightEleID",           'reco electron tightEleID'),
           ("h_ele_lower_convVeto",             'reco electron convVeto'),
           ("h_ele_lower_mva",                  'reco electron mva'),
           ("h_ele_lower_pt",                   'reco electron pt'), 
           ("h_ele_lower_mvaFall17_WP80",       'reco electron WP80'),
           ("h_ele_lower_mva_small",            'reco electron mva_small'),
           ("h_ele_barrel_ip3d",                 'reco electron ip3d'),
           ("h_ele_barrel_sip3d",                'reco electron sip3d'),
           ("h_ele_barrel_pfRelIso03_all",       'reco electron relative isolation'),
           ("h_ele_barrel_pfRelIso03_allxPT",    'reco electron isolation'),
           ("h_ele_barrel_bTagDeepCSV",          'reco electron deepCSV score'),
           ("h_ele_barrel_lostHits",             'reco electron lostHits'),
           ("h_ele_barrel_VLooseFOEleID",        'reco electron VLooseFOEleID'),
           ("h_ele_barrel_tightEleID",           'reco electron tightEleID'),
           ("h_ele_barrel_convVeto",             'reco electron convVeto'),
           ("h_ele_barrel_mva",                  'reco electron mva'),
           ("h_ele_barrel_pt",                   'reco electron pt'),
           ("h_ele_barrel_mvaFall17_WP80",       'reco electron WP80'),
           ("h_ele_barrel_mva_small",            'reco electron mva_small'),
           ("h_ele_upper_barrel_ip3d",                 'reco electron ip3d'),
           ("h_ele_upper_barrel_sip3d",                'reco electron sip3d'),
           ("h_ele_upper_barrel_pfRelIso03_all",       'reco electron relative isolation'),
           ("h_ele_upper_barrel_pfRelIso03_allxPT",    'reco electron isolation'),
           ("h_ele_upper_barrel_bTagDeepCSV",          'reco electron deepCSV score'),
           ("h_ele_upper_barrel_lostHits",             'reco electron lostHits'),
           ("h_ele_upper_barrel_VLooseFOEleID",        'reco electron VLooseFOEleID'),
           ("h_ele_upper_barrel_tightEleID",           'reco electron tightEleID'),
           ("h_ele_upper_barrel_convVeto",             'reco electron convVeto'),
           ("h_ele_upper_barrel_mva",                  'reco electron mva'),
           ("h_ele_upper_barrel_pt",                   'reco electron pt'),
           ("h_ele_upper_barrel_mvaFall17_WP80",       'reco electron WP80'),
           ("h_ele_upper_barrel_mva_small",            'reco electron mva_small'),
           ("h_ele_lower_barrel_ip3d",                 'reco electron ip3d'),
           ("h_ele_lower_barrel_sip3d",                'reco electron sip3d'),
           ("h_ele_lower_barrel_pfRelIso03_all",       'reco electron relative isolation'),
           ("h_ele_lower_barrel_pfRelIso03_allxPT",    'reco electron isolation'),
           ("h_ele_lower_barrel_bTagDeepCSV",          'reco electron deepCSV score'),
           ("h_ele_lower_barrel_lostHits",             'reco electron lostHits'),
           ("h_ele_lower_barrel_VLooseFOEleID",        'reco electron VLooseFOEleID'),
           ("h_ele_lower_barrel_tightEleID",           'reco electron tightEleID'),
           ("h_ele_lower_barrel_convVeto",             'reco electron convVeto'),
           ("h_ele_lower_barrel_mva",                  'reco electron mva'),
           ("h_ele_lower_barrel_pt",                   'reco electron pt'), 
           ("h_ele_lower_barrel_mvaFall17_WP80",             'reco electron WP80'),
           ("h_ele_lower_barrel_mva_small",            'reco electron mva_small'),
           ("h_ele_endcap_ip3d",                 'reco electron ip3d'),
           ("h_ele_endcap_sip3d",                'reco electron sip3d'),
           ("h_ele_endcap_pfRelIso03_all",       'reco electron relative isolation'),
           ("h_ele_endcap_pfRelIso03_allxPT",    'reco electron isolation'),
           ("h_ele_endcap_bTagDeepCSV",          'reco electron deepCSV score'),
           ("h_ele_endcap_lostHits",             'reco electron lostHits'),
           ("h_ele_endcap_VLooseFOEleID",        'reco electron VLooseFOEleID'),
           ("h_ele_endcap_tightEleID",           'reco electron tightEleID'),
           ("h_ele_endcap_convVeto",             'reco electron convVeto'),
           ("h_ele_endcap_mva",                  'reco electron mva'),
           ("h_ele_endcap_pt",                   'reco electron pt'),
           ("h_ele_endcap_mvaFall17_WP80",       'reco electron WP80'),
           ("h_ele_endcap_mva_small",            'reco electron mva_small'),
           ("h_ele_upper_endcap_ip3d",                 'reco electron ip3d'),
           ("h_ele_upper_endcap_sip3d",                'reco electron sip3d'),
           ("h_ele_upper_endcap_pfRelIso03_all",       'reco electron relative isolation'),
           ("h_ele_upper_endcap_pfRelIso03_allxPT",    'reco electron isolation'),
           ("h_ele_upper_endcap_bTagDeepCSV",          'reco electron deepCSV score'),
           ("h_ele_upper_endcap_lostHits",             'reco electron lostHits'),
           ("h_ele_upper_endcap_VLooseFOEleID",        'reco electron VLooseFOEleID'),
           ("h_ele_upper_endcap_tightEleID",           'reco electron tightEleID'),
           ("h_ele_upper_endcap_convVeto",             'reco electron convVeto'),
           ("h_ele_upper_endcap_mva",                  'reco electron mva'),
           ("h_ele_upper_endcap_pt",                   'reco electron pt'),
           ("h_ele_upper_endcap_mvaFall17_WP80",       'reco electron WP80'),
           ("h_ele_upper_endcap_mva_small",            'reco electron mva_small'),
           ("h_ele_lower_endcap_ip3d",                 'reco electron ip3d'),
           ("h_ele_lower_endcap_sip3d",                'reco electron sip3d'),
           ("h_ele_lower_endcap_pfRelIso03_all",       'reco electron relative isolation'),
           ("h_ele_lower_endcap_pfRelIso03_allxPT",    'reco electron isolation'),
           ("h_ele_lower_endcap_bTagDeepCSV",          'reco electron deepCSV score'),
           ("h_ele_lower_endcap_lostHits",             'reco electron lostHits'),
           ("h_ele_lower_endcap_VLooseFOEleID",        'reco electron VLooseFOEleID'),
           ("h_ele_lower_endcap_tightEleID",           'reco electron tightEleID'),
           ("h_ele_lower_endcap_convVeto",             'reco electron convVeto'),
           ("h_ele_lower_endcap_mva",                  'reco electron mva'),
           ("h_ele_lower_endcap_pt",                   'reco electron pt'), 
           ("h_ele_lower_endcap_mvaFall17_WP80",       'reco electron WP80'),
           ("h_ele_lower_endcap_mva_small",            'reco electron mva_small'),
           ("h_ele_outside_ip3d",                 'reco electron ip3d'),
           ("h_ele_outside_sip3d",                'reco electron sip3d'),
           ("h_ele_outside_pfRelIso03_all",       'reco electron relative isolation'),
           ("h_ele_outside_pfRelIso03_allxPT",    'reco electron isolation'),
           ("h_ele_outside_bTagDeepCSV",          'reco electron deepCSV score'),
           ("h_ele_outside_lostHits",             'reco electron lostHits'),
           ("h_ele_outside_VLooseFOEleID",        'reco electron VLooseFOEleID'),
           ("h_ele_outside_tightEleID",           'reco electron tightEleID'),
           ("h_ele_outside_convVeto",             'reco electron convVeto'),
           ("h_ele_outside_mva",                  'reco electron mva'),
           ("h_ele_outside_pt",                   'reco electron pt'),
           ("h_ele_outside_mvaFall17_WP80",       'reco electron WP80'),
           ("h_ele_upper_outside_mva_small",            'reco electron mva_small'),
           ("h_ele_upper_outside_ip3d",                 'reco electron ip3d'),
           ("h_ele_upper_outside_sip3d",                'reco electron sip3d'),
           ("h_ele_upper_outside_pfRelIso03_all",       'reco electron relative isolation'),
           ("h_ele_upper_outside_pfRelIso03_allxPT",    'reco electron isolation'),
           ("h_ele_upper_outside_bTagDeepCSV",          'reco electron deepCSV score'),
           ("h_ele_upper_outside_lostHits",             'reco electron lostHits'),
           ("h_ele_upper_outside_VLooseFOEleID",        'reco electron VLooseFOEleID'),
           ("h_ele_upper_outside_tightEleID",           'reco electron tightEleID'),
           ("h_ele_upper_outside_convVeto",             'reco electron convVeto'),
           ("h_ele_upper_outside_mva",                  'reco electron mva'),
           ("h_ele_upper_outside_pt",                   'reco electron pt'),
           ("h_ele_upper_outside_mvaFall17_WP80",       'reco electron WP80'),
           ("h_ele_lower_outside_ip3d",                 'reco electron ip3d'),
           ("h_ele_lower_outside_sip3d",                'reco electron sip3d'),
           ("h_ele_lower_outside_pfRelIso03_all",       'reco electron relative isolation'),
           ("h_ele_lower_outside_pfRelIso03_allxPT",    'reco electron isolation'),
           ("h_ele_lower_outside_bTagDeepCSV",          'reco electron deepCSV score'),
           ("h_ele_lower_outside_lostHits",             'reco electron lostHits'),
           ("h_ele_lower_outside_VLooseFOEleID",        'reco electron VLooseFOEleID'),
           ("h_ele_lower_outside_tightEleID",           'reco electron tightEleID'),
           ("h_ele_lower_outside_convVeto",             'reco electron convVeto'),
           ("h_ele_lower_outside_mva",                  'reco electron mva'),
           ("h_ele_lower_outside_pt",                   'reco electron pt'), 
           ("h_ele_lower_outside_mvaFall17_WP80",       'reco electron WP80'),
           ("h_ele_lower_outside_mva_small",            'reco electron mva_small'),
           ("h_ele_lower_miniPFRelIso_allxPT",          'reco electron miniPFRelIsoxPT'),
           ("h_ele_lower_miniPFRelIso_all",          'reco electron miniPFRelIso'),
           ]
    
    for h in hists:
        match_unmatch(h, "plots1", "", inFile, output=o.output, maxY=1., stats=0, file_name=o.f_name)
       # if 'pfRelIso03' in h[0]:
       #     match_unmatch(h, "plots1", "", inFile, output=o.output, 
       #                   maxY=1., stats=0, file_name=o.f_name+'_full', normal=False)
            
#    match_unmatch(hists[9], "plots1", "", inFile, output=o.output, maxY=1., stats=0, file_name=o.f_name)
    
    hists2=[("h_ele_lower_match_pfRelIso03_all","h_ele_lower_unmatch_pfRelIso03_all"),
            ("h_ele_lower_match_pfRelIso03_allxPT","h_ele_lower_unmatch_pfRelIso03_allxPT"),
            ("h_ele_lower_match_miniPFRelIso_all","h_ele_lower_unmatch_miniPFRelIso_all"),
            ("h_ele_lower_match_miniPFRelIso_allxPT","h_ele_lower_unmatch_miniPFRelIso_allxPT"),]

    
    #(file2[idx], inFile2[idx]) 
    
    File=[o.inFile, inFile]
    for hist in hists2:
        hist_name=hist[0].replace("match", "").replace("h_ele","")
        plot_int_comp(hist, "plots1", "", "", File, output=o.output,
                          stats=0, legend=True, file_name=hist_name, normal=False)



    print("2d hists ...")
    time.sleep(.5)

    hists2d=[("h_ele_match_pt_mva"),
             ("h_ele_match_eta_mva"),
             ("h_ele_unmatch_pt_mva"),
             ("h_ele_unmatch_eta_mva"),
             ("h_ele_split_pt_mva"),
             ("h_ele_match_pt_pfRelIso"),
             ("h_ele_match_pt_pfRelIsoxPT"),
             ("h_ele_match_pt_miniPFRelIsoxPT"),
             ("h_ele_match_pt_ip3d"),
             ("h_ele_match_pt_sip3d"),
             ("h_ele_match_pt_bTagDeepCSV"),
             ("h_ele_match_pt_convVeto"),
             ("h_ele_match_pt_lostHits"),]

    for h2 in hists2d:
        Hist_2d(h2, "plots1", [("", inFile,),], o.output,
                maxY=None, stats=0, file_name="", col=False)

    print("end plotting")

if __name__ == "__main__":
    main()

 
