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
DetFlags.detdescr.ID_setOn()
DetFlags.detdescr.Calo_setOff()
DetFlags.detdescr.Tile_setOff()
DetFlags.detdescr.Muon_setOff()

globalflags.ConditionsTag = 'OFLCOND-MC15c-SDR-09'
globalflags.DetDescrVersion = 'ATLAS-R2-2015-03-01-00'

include ("RecExCond/AllDet_detDescr.py")

#filelist = ['/atlasfs/atlas/hpc/mc15_13TeV.423001.ParticleGun_single_photon_egammaET.recon.AOD.e3566_s2141_s2132_r6476/AOD.05074737._005584.pool.root.1'] 
#filelist = glob.glob('/lcrc/group/ATLAS/atlasfs/local/rwang/ML/mldata/mc15_13TeV.361702.AlpgenPythiaEvtGen_P2012_ZeeNp2.simulRDO.07354230._000001.pool.root.1')

print 'filelist = ',len(filelist)

ServiceMgr.EventSelector.InputCollections = filelist

from AthenaCommon.AlgSequence import AlgSequence
theJob = AlgSequence()

# Number of Events to process
theApp.EvtMax = -1

from CaloMon.CaloMonConf import MyAlgHits
theJob += MyAlgHits( OutputLevel = INFO )

#MyAlgHits.rootFilename = "sihits.root"
MyAlgHits.rootFilename = rootFilename

AthenaEventLoopMgr = Service("AthenaEventLoopMgr")
AthenaEventLoopMgr.OutputLevel = INFO
MsgSvc = Service("MessageSvc")
MsgSvc.defaultLimit = 100000000
MsgSvc.OutputLevel = INFO



