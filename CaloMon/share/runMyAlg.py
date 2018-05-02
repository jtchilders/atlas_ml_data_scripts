# ---------------------------------------------------------------------------------------------------
# Testing a basic script to test "MyAlg" on an ESD file
# ---------------------------------------------------------------------------------------------------
from AthenaCommon.Constants import *
from AthenaCommon.AppMgr import theApp
from AthenaCommon.AppMgr import ServiceMgr
from AthenaCommon.GlobalFlags  import globalflags
import AthenaPoolCnvSvc.ReadAthenaPool
import glob

from AthenaCommon.DetFlags import DetFlags
DetFlags.detdescr.ID_setOff()
DetFlags.detdescr.Calo_setOn()
DetFlags.detdescr.Tile_setOn()
DetFlags.detdescr.Muon_setOff()

globalflags.ConditionsTag = 'OFLCOND-MC15c-SDR-09'
globalflags.DetDescrVersion = 'ATLAS-R2-2015-03-01-00'


include ("RecExCond/AllDet_detDescr.py")

#from G4AtlasApps.SimFlags import SimFlags
#SimFlags.SimLayout = 'ATLAS-R2-2015-02-01-00' # 'ATLAS-GEO-16-00-00' # 'ATLAS-CSC-02-02-00'
#SimFlags.SimLayout = 'all:ATLAS-P2-SFCAL-01-00-00'

#include ("AtlasGeoModel/SetGeometryVersion.py")
#include ("AtlasGeoModel/GeoModelInit.py")
#GeoModelSvc = Service( "GeoModelSvc" )
#GeoModelSvc.AtlasVersion = 'default:ATLAS-R2-2015-03-01-00'

#ServiceMgr.EventSelector.InputCollections = [ 'RDO.CaloDigEx.pool.root' ] # not working
#ServiceMgr.EventSelector.InputCollections = [ '/users/jwebster/FTK/sandbox/data/data15_13TeV.00284484.express_express.recon.ESD.r7446_tid07363094_00/ESD.07363094._000025.pool.root.1' ]
#ServiceMgr.EventSelector.InputCollections = [ '/users/jwebster/FTK/sandbox/data/mc15_13TeV.361024.Pythia8EvtGen_A14NNPDF23LO_jetjet_JZ4W.recon.ESD.e3668_s2576_s2132_r6630_tid05496022_00/ESD.05496022._000901.pool.root.1' ]


#filelist = ['/atlasfs/atlas/hpc/mc15_13TeV.423001.ParticleGun_single_photon_egammaET.recon.AOD.e3566_s2141_s2132_r6476/AOD.05074737._005584.pool.root.1'] 
#filelist = ['/atlasfs/atlas/hpc/mc15_13TeV.423099.Pythia8EvtGen_A14NNPDF23LO_gammajet_DP8_17.merge.AOD.e4453_s2768_r7359_r6282/AOD.07289250._000055.pool.root.1']
#filelist = glob.glob('/atlasfs/atlas/hpc/mc15_13TeV.423001.ParticleGun_single_photon_egammaET.recon.AOD.e3566_s2806_r7607/*')
#filelist = glob.glob('/users/jchilders/mc15_13TeV.422005.ParticleGun_single_photon_Pt10.recon.ESD.e4459_s2726_r7059/ESD.07275499._*')
#filelist = glob.glob('/users/hpcusers/dumpCaloCells/mc15_14TeV.147806.PowhegPythia8_AU2CT10_Zee.recon.ESD.e1564_s2638_s2206_r7700/*.root.*')
#filelist = ['/grid/atlas/hpc/mldata/mc15_13TeV.361702.AlpgenPythiaEvtGen_P2012_ZeeNp2.simul.ESD/ESD.07354230._002126.pool.root.1']

#filelist = glob.glob('/users/hpcusers/dumpCaloCells/reco_condor_job/ESD.*')

#filelist = glob.glob('/lcrc/group/ATLAS/atlasfs/local/rwang/ML/mldata/mc15_13TeV.361702.AlpgenPythiaEvtGen_P2012_ZeeNp2.simul.ESD/ESD.07354230._000001.pool.root.1')

print 'filelist = ',len(filelist)

ServiceMgr.EventSelector.InputCollections = filelist

from AthenaCommon.AlgSequence import AlgSequence
theJob = AlgSequence()

# Number of Events to process
theApp.EvtMax = -1

from CaloMon.CaloMonConf import MyAlg
#theJob += MyAlg( OutputLevel = VERBOSE )
theJob += MyAlg( OutputLevel = INFO )

# energy thresholds 
MyAlg.energyThreshold = 0.3 # in GeV 
MyAlg.cellsContainerName = "AllCalo"
MyAlg.truthEventsContainerName = "TruthEventsAux."
MyAlg.truthParticlesContainerName = "TruthParticles"
MyAlg.jetAuxContainerName = "AntiKt4TruthJets"

#MyAlg.rootFilename = "myout.root"
MyAlg.rootFilename = rootFilename

AthenaEventLoopMgr = Service("AthenaEventLoopMgr")
AthenaEventLoopMgr.OutputLevel = DEBUG
MsgSvc = Service("MessageSvc")
MsgSvc.defaultLimit = 100000000
MsgSvc.OutputLevel = INFO

