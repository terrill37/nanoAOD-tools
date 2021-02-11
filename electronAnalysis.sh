#input_dir=/afs/cern.ch/user/w/wterrill/public/soft_lepton/CMSSW_10_4_0/src/CMGTools/TTHAnalysis/cfg/ch_outdir_dec18_ULtest_qcd
input_dir=/eos/user/w/wterrill/softlepton_root/ch_outdir_dec18_ULtest_qcd

python PhysicsTools/NanoAODTools/python/postprocessing/examples/electronAnalysis.py \
    -i $input_dir/Higgsino_N2N1_Chunk0.root \
    -o OutputHists/histOut_LepGood.root\
    -c LepGood

#input=/afs/cern.ch/user/w/wterrill/public/soft_lepton/CMSSW_10_4_0/src/OutputHists/histOut_LepGood.root
#output=/eos/user/w/wterrill/www/projects/softlepton/electron_analysis_LepGood
#
#python PhysicsTools/NanoAODTools/python/postprocessing/examples/electronAnalysis_viewer.py \
#    -i $input \
#    -o $output


