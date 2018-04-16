#ifndef MyAlgHits_h
#define MyAlgHits_h

#include "AthenaBaseComps/AthAlgorithm.h"

#include "GaudiKernel/ToolHandle.h"
#include "GaudiKernel/ITHistSvc.h"
#include "CLHEP/Units/SystemOfUnits.h"
#include "StoreGate/StoreGateSvc.h"

#include "TTree.h"
#include "TFile.h"

#include <string>
#include <vector>
#include <fstream>
 
class StoreGateSvc;

class PixelID;
class SCT_ID;
class TRT_ID;
namespace InDetDD {
  class SiDetectorManager;
}

/////////////////////////////////////////////////////////////////////////////
class MyAlgHits : public AthAlgorithm
{public:
  MyAlgHits (const std::string& name, ISvcLocator* pSvcLocator);
  virtual ~MyAlgHits();
  StatusCode initialize();
  StatusCode execute();
  StatusCode finalize();

  StatusCode GetHits();

private:
  std::string m_PixContainerName;
  std::string m_SCTContainerName;
  std::string m_rootFilename;
  
  int  m_events_all;
  
  // a handle on Store Gate
  StoreGateSvc* m_storeGate;
  StoreGateSvc* m_detStore;
  //ID helper
  const PixelID* m_pixelId;
  const SCT_ID* m_sctId;
  //Geo manager
  const InDetDD::SiDetectorManager* m_pixelManager;
  const InDetDD::SiDetectorManager* m_sctManager;

  
  TTree* m_roottree;
  
  unsigned short int m_run_number;
  unsigned int m_event_number;
  unsigned int m_lumi_block;
  unsigned int m_time_stamp;

  // Pixel RDO
  std::vector<unsigned long long> m_pix_rdoID;
  std::vector<unsigned int> m_pix_rdoWord;
  // PixelID
  std::vector<int> m_pix_barrelEndcap;
  std::vector<int> m_pix_layerDisk;
  std::vector<int> m_pix_phiModule;
  std::vector<int> m_pix_etaModule;
  std::vector<int> m_pix_phiIndex;
  std::vector<int> m_pix_etaIndex;
  // PixelRDORawData
  std::vector<int> m_pix_ToT;
  std::vector<int> m_pix_BCID;
  std::vector<int> m_pix_LVL1A;
  std::vector<int> m_pix_LVL1ID;
  // Hit globle position
  std::vector<float> m_pix_position_x;
  std::vector<float> m_pix_position_y;
  std::vector<float> m_pix_position_z;
  std::vector<float> m_pix_position_phipitch;
  std::vector<float> m_pix_position_etapitch;
  std::vector<float> m_pix_position_thickness;

  // SCT RDO
  std::vector<unsigned long long> m_sct_rdoID;
  std::vector<unsigned int> m_sct_rdoWord;
  // SCT_ID
  std::vector<int> m_sct_barrelEndcap;
  std::vector<int> m_sct_layerDisk;
  std::vector<int> m_sct_phiModule;
  std::vector<int> m_sct_etaModule;
  std::vector<int> m_sct_side;
  std::vector<int> m_sct_strip;
  // SCT_RDORawData
  std::vector<int> m_sct_groupSize;
  // Hit globle position
  std::vector<float> m_sct_position_x;
  std::vector<float> m_sct_position_y;
  std::vector<float> m_sct_position_z;
  std::vector<float> m_sct_position_phipitch;
  std::vector<float> m_sct_position_etapitch;
  std::vector<float> m_sct_position_thickness;

  
  TFile* m_rootfile;
  /// get a handle on the Hist/TTree registration service
  ITHistSvc * m_thistSvc;
};

#endif

