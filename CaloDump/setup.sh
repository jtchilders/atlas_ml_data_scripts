#!/bin/bash

#
# Setup script - sets your environment for testing/installing CaloMon package
#

export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
export ALRB_localConfigDir=$HOME/localConfig
source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh --quiet
#source ${AtlasSetup}/scripts/asetup.sh 20.1.5.10,here #20.3.3.1,here #20.7.3.6,here
source ${AtlasSetup}/scripts/asetup.sh 20.7.5.1,here

export CMTINSTALLAREA=/blues/gpfs/group/3/ATLAS/users/jchilder/atlas_ml_data_scripts/CaloDump/InstallArea

echo "done."

