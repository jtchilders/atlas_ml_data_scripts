# atlas_ml_data_scripts
All my scripts related to created ATLAS data for ML studies.

#install CaloMon
asetup 20.7.5.1,AtlasProduction,slc6,here

cd CaloMon/cmt/
cmt make
cmt make install
cd -
athena CaloMon/share/runMyAlgHits.py

#to run
athena -c "filelist=['/lcrc/group/ATLAS/atlasfs/local/rwang/ML/mldata/mc15_13TeV.361702.AlpgenPythiaEvtGen_P2012_ZeeNp2.simul.ESD/ESD.07354230._000001.pool.root.1'];rootFilename='run/test.root'" CaloMon/share/runMyAlg.py 
