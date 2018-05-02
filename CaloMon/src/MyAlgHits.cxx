#include "CaloMon/MyAlgHits.h"

#include "GaudiKernel/MsgStream.h"
#include "GaudiKernel/ISvcLocator.h"
#include "GaudiKernel/PropertyMgr.h"
#include "GaudiKernel/IToolSvc.h"
#include "StoreGate/StoreGate.h"
#include "GaudiKernel/ServiceHandle.h"

#include "EventInfo/EventInfo.h"
#include "EventInfo/EventID.h"


//InDetRawData includes
#include "InDetRawData/PixelRDO_Container.h"
#include "InDetRawData/SCT_RDO_Container.h"
#include "InDetRawData/PixelRDO_Collection.h"
#include "InDetRawData/SCT_RDO_Collection.h"


#include "InDetIdentifier/PixelID.h"
#include "InDetIdentifier/SCT_ID.h"

#include "InDetReadoutGeometry/SiDetectorElement.h"
#include "InDetReadoutGeometry/SiDetectorManager.h"
#include "GeoPrimitives/GeoPrimitives.h"

MyAlgHits::MyAlgHits(const std::string& name, ISvcLocator* pSvcLocator)
  : AthAlgorithm( name , pSvcLocator )
  , m_PixContainerName( "PixelRDOs" )
  , m_SCTContainerName( "SCT_RDOs" )
//  , m_LArContainerName( "LArRawChannels" )
//  , m_TileContainerName( "TileRawChannelCnt" )
  , m_rootFilename( "sihits.root" )
{
  // Properties go here
  declareProperty( "pixcontainerName" , m_PixContainerName ); //Pixel Hits Container
  declareProperty( "sctcontainerName" , m_SCTContainerName ); //SCT Hits Container
  declareProperty( "rootFilename" , m_rootFilename ); // root filename
}


MyAlgHits::~MyAlgHits() {}


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
StatusCode MyAlgHits::initialize(){

  MsgStream log(msgSvc(), name());
  log << MSG::INFO << "initialize()" << endreq;

  m_events_all=0;

  m_rootfile = new TFile(m_rootFilename.c_str(),"recreate");
  m_roottree = new TTree("sihits","tree for silicon hits");

  m_roottree->Branch("run_number",&m_run_number,"run_number/s");
  m_roottree->Branch("event_number",&m_event_number,"event_number/I");
  m_roottree->Branch("lumi_block",&m_lumi_block,"lumi_block/I");
  m_roottree->Branch("time_stamp",&m_time_stamp,"time_stamp/I");

  // PIXEL RDO
  m_roottree->Branch("PIX_rdoID","vector<unsigned long long>", &m_pix_rdoID);
  m_roottree->Branch("PIX_rdoWord","vector<unsigned int>", &m_pix_rdoWord);
  m_roottree->Branch("PIX_barrelEndcap","vector<int>", &m_pix_barrelEndcap);
  m_roottree->Branch("PIX_layerDisk","vector<int>", &m_pix_layerDisk);
  m_roottree->Branch("PIX_phiModule","vector<int>", &m_pix_phiModule);
  m_roottree->Branch("PIX_etaModule","vector<int>", &m_pix_etaModule);
  m_roottree->Branch("PIX_phiIndex","vector<int>", &m_pix_phiIndex);
  m_roottree->Branch("PIX_etaIndex","vector<int>", &m_pix_etaIndex);
  m_roottree->Branch("PIX_ToT","vector<int>", &m_pix_ToT); // time over threshold value (0-255)
  m_roottree->Branch("PIX_BCID","vector<int>", &m_pix_BCID); // beam crossing ID
  m_roottree->Branch("PIX_LVL1A","vector<int>", &m_pix_LVL1A); // Level1 accept (0-15)
  m_roottree->Branch("PIX_LVL1ID","vector<int>", &m_pix_LVL1ID); // ATLAS LVL1 (0-255)

  m_roottree->Branch("PIX_position_x","vector<float>", &m_pix_position_x);
  m_roottree->Branch("PIX_position_y","vector<float>", &m_pix_position_y);
  m_roottree->Branch("PIX_position_z","vector<float>", &m_pix_position_z);
  m_roottree->Branch("PIX_position_phiPitch","vector<float>", &m_pix_position_phipitch);
  m_roottree->Branch("PIX_position_etaPitch","vector<float>", &m_pix_position_etapitch);
  m_roottree->Branch("PIX_position_thickness","vector<float>", &m_pix_position_thickness);

  // SCT RDO
  m_roottree->Branch("SCT_rdoID","vector<unsigned long long>", &m_sct_rdoID);
  m_roottree->Branch("SCT_rdoWord","vector<unsigned int>", &m_sct_rdoWord);
  m_roottree->Branch("SCT_barrelEndcap","vector<int>", &m_sct_barrelEndcap);
  m_roottree->Branch("SCT_layerDisk","vector<int>", &m_sct_layerDisk);
  m_roottree->Branch("SCT_phiModule","vector<int>", &m_sct_phiModule);
  m_roottree->Branch("SCT_etaModule","vector<int>", &m_sct_etaModule);
  m_roottree->Branch("SCT_side","vector<int>", &m_sct_side);
  m_roottree->Branch("SCT_strip","vector<int>", &m_sct_strip);
  m_roottree->Branch("SCT_groupSize","vector<int>", &m_sct_groupSize);
  
  m_roottree->Branch("SCT_position_x","vector<float>", &m_sct_position_x);
  m_roottree->Branch("SCT_position_y","vector<float>", &m_sct_position_y);
  m_roottree->Branch("SCT_position_z","vector<float>", &m_sct_position_z);
  m_roottree->Branch("SCT_position_phiPitch","vector<float>", &m_sct_position_phipitch);
  m_roottree->Branch("SCT_position_etaPitch","vector<float>", &m_sct_position_etapitch);
  m_roottree->Branch("SCT_position_thickness","vector<float>", &m_sct_position_thickness);
  
  CHECK( service("StoreGateSvc", m_storeGate) );
  CHECK( service("DetectorStore",m_detStore));

  // Get the pixel helper from the detector store
  StatusCode sc = detStore()->retrieve(m_pixelId, "PixelID");
  if( !sc.isSuccess() ) {
    log << MSG::ERROR << "Could not get PixelID helper !" << endreq;
    return StatusCode::FAILURE;
  }

  // Get the sct helper from the detector store
  sc = m_detStore->retrieve(m_sctId, "SCT_ID");
  if( !sc.isSuccess() ) {
    log << MSG::ERROR << "Could not get SCT_ID helper !" << endreq;
    return StatusCode::FAILURE;
  }

  //const IGeoModelSvc * m_geoModelSvc;
  //sc = service("GeoModelSvc",m_geoModelSvc);
  //if (sc.isFailure()) {
    //log << MSG::ERROR << "GeoModelSvc service not found !" << endreq;
    //return StatusCode::FAILURE;
  //}


  sc=detStore()->retrieve(m_pixelManager,"Pixel");
  if (sc.isFailure() || !m_pixelManager) {
    log << MSG::ERROR << "Could not find the Pixel Manager !" << endreq;
    return StatusCode::FAILURE;
  }
  
  sc=detStore()->retrieve(m_sctManager,"SCT");
  if (sc.isFailure() || !m_sctManager) {
    log << MSG::ERROR << "Could not find the SCT Manager !" << endreq;
    return StatusCode::FAILURE;
  }

  return StatusCode::SUCCESS;

}



// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
StatusCode MyAlgHits::execute() {

  MsgStream log(msgSvc(), name());

  m_events_all++;
  if (m_events_all<=10 ||
      (m_events_all<=100 && (m_events_all%10) == 0) ||
      (m_events_all<=1000 && (m_events_all%100) == 0)  ||
      (m_events_all>=1000 && (m_events_all%1000) == 0)  ) {
    log <<  MSG::INFO << "##### - Event processed: " << m_events_all << endreq;
  };

  CHECK( GetHits() );

  return StatusCode::SUCCESS;

}



// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
StatusCode MyAlgHits::finalize() {
  MsgStream log(msgSvc(), name());
  log << MSG::INFO << "finalize()" << endreq;
  m_rootfile->cd();
  m_roottree->Write();
  m_rootfile->Close();
  return StatusCode::SUCCESS;
}



// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
StatusCode MyAlgHits::GetHits() {

  MsgStream log(messageService(), name());

  log <<MSG::DEBUG << "Call MyAlgHits::GetHits()" << endreq;

  // get event info
  const EventInfo* eventInfo = 0;
  CHECK( evtStore()->retrieve( eventInfo) );
  const EventID* evtid = eventInfo->event_ID();
  m_run_number = evtid->run_number();
  m_event_number = evtid->event_number();
  m_lumi_block = evtid->lumi_block();
  m_time_stamp = evtid->time_stamp();
  
  m_pix_rdoID.clear();
  m_pix_rdoWord.clear();
  m_pix_barrelEndcap.clear();
  m_pix_layerDisk.clear();
  m_pix_phiModule.clear();
  m_pix_etaModule.clear();
  m_pix_phiIndex.clear();
  m_pix_etaIndex.clear();
  m_pix_ToT.clear();
  m_pix_BCID.clear();
  m_pix_LVL1A.clear();
  m_pix_LVL1ID.clear();
  m_pix_position_x.clear();
  m_pix_position_y.clear();
  m_pix_position_z.clear();
  m_pix_position_phipitch.clear();
  m_pix_position_etapitch.clear();
  m_pix_position_thickness.clear();
  
  m_sct_rdoID.clear();
  m_sct_rdoWord.clear();
  m_sct_barrelEndcap.clear();
  m_sct_layerDisk.clear();
  m_sct_phiModule.clear();
  m_sct_etaModule.clear();
  m_sct_side.clear();
  m_sct_strip.clear();
  m_sct_groupSize.clear();
  m_sct_position_x.clear();
  m_sct_position_y.clear();
  m_sct_position_z.clear();
  m_sct_position_phipitch.clear();
  m_sct_position_etapitch.clear();
  m_sct_position_thickness.clear();
  
  const PixelRDO_Container* pixhitCont;
  StatusCode sc=m_storeGate->retrieve( pixhitCont, m_PixContainerName);
  if( sc.isFailure()  ||  !pixhitCont ) {
    log << MSG::ERROR
        << "No RDO container found with the name:" << m_PixContainerName
        << endreq;
    return StatusCode::FAILURE;
  }
  const SCT_RDO_Container* scthitCont;
  sc=m_storeGate->retrieve( scthitCont, m_SCTContainerName);
  if( sc.isFailure()  ||  !scthitCont ) {
    log << MSG::ERROR
        << "No RDO container found with the name:" << m_SCTContainerName
        << endreq;
    return StatusCode::FAILURE;
  }
  log << MSG::DEBUG  << "total Pix hits are " << pixhitCont->size() << endreq;
  for(PixelRDO_Container::const_iterator it=pixhitCont->begin();it!=pixhitCont->end() ; ++it) { // Pixel ROD Loop
    const InDetRawDataCollection<PixelRDORawData>* PixelCollection(&(**it));
    int pixi=0;
    for(InDetRawDataCollection<PixelRDORawData>::const_iterator pix_itr=PixelCollection->begin(); pix_itr!=PixelCollection->end(); ++pix_itr) {
      Identifier pixId=(*pix_itr)->identify();
      const int pixBrlEc(m_pixelId->barrel_ec(pixId));
      const unsigned int rdoWord((*pix_itr)->getWord());
      const int pixLayerDisk(m_pixelId->layer_disk(pixId));
      const int pixPhiMod(m_pixelId->phi_module(pixId));
      const int pixEtaMod(m_pixelId->eta_module(pixId));
      const int pixPhiIx(m_pixelId->phi_index(pixId));
      const int pixEtaIx(m_pixelId->eta_index(pixId));
      const int pixToT((*pix_itr)->getToT());
      const int pixBCID((*pix_itr)->getBCID());
      const int pixLVL1A((*pix_itr)->getLVL1A());
      const int pixLVL1ID((*pix_itr)->getLVL1ID());
      log << MSG::DEBUG  << "Hit "<< pixi<<" : Pixel " << pixBrlEc <<":"<< pixLayerDisk << " module phi " << pixPhiMod << " eta " << pixEtaMod << " -- pixel phi index: " << pixPhiIx << " eta index: " << pixEtaIx << " ToT: " << pixToT << endreq;
      const unsigned long long pix_rdoID_int = pixId.get_compact();
      m_pix_rdoID.push_back(pix_rdoID_int);
      m_pix_rdoWord.push_back(rdoWord);
      m_pix_barrelEndcap.push_back(pixBrlEc);
      m_pix_layerDisk.push_back(pixLayerDisk);
      m_pix_phiModule.push_back(pixPhiMod);
      m_pix_etaModule.push_back(pixEtaMod);
      m_pix_phiIndex.push_back(pixPhiIx);
      m_pix_etaIndex.push_back(pixEtaIx);
      m_pix_ToT.push_back(pixToT);
      m_pix_BCID.push_back(pixBCID);
      m_pix_LVL1A.push_back(pixLVL1A);
      m_pix_LVL1ID.push_back(pixLVL1ID);
      //**  @class PixelID
      //** @verbatim
      //**    element           range    bits          meaning
      //**    -------           -----    ----          -------
      //**    barrel_ec          0         2            barrel 
      //**                    -4  / 4                     neg ec /  pos ec (-4 and +4 for DBM)
      //**    layer_disk       0 to 2      2          for barrel
      //**                     0 to 2      2          for ec
      //**    phi_module       0 to <29    5   for barrel (depends upon layer)
      //**                     0 to <72    7   for ec     (depends upon disk)
      //**    eta_module       0 to 12     4   for barrel, along z
      //**                     0 to 1      1   for ec, along r
      //**    phi_index        0 to 327    9   for barrel, pixel coordinate along r/phi
      //**                     0 to 192    8   for ec,      "
      //**    eta_index        0 to 205    8   for barrel, pixel coordinate along z
      //**                     0 to 164    8   for ec,       "       "        "   r
      //** @endverbatim
      const InDetDD::SiDetectorElement* element=m_pixelManager->getDetectorElement(pixId);
      if (pixi==0){
        log << MSG::DEBUG  << " Pixel module center = " << element->center() << endreq;
        log << MSG::DEBUG  << " Pixel module width = " << element->width()/CLHEP::mm << ", length (mm) = " << element->length()/CLHEP::mm << ", thick (mm) = " << element->thickness()/CLHEP::mm << endreq;
      }
      //**Pixel Module size 16.8 x 60.8 mm2
      //**Pixel size 50 x 400 μm2
      //width/phi_index = 50μm
      Amg::Vector2D localPos = element->rawLocalPositionOfCell(pixId);
      Amg::Vector3D globalPos = element->globalPosition(localPos);
      log << MSG::DEBUG << " Pixel Global pos" << " x (mm) = " << globalPos.x()/CLHEP::mm<< ", y (mm) = " << globalPos.y()/CLHEP::mm<< ", z (mm) = " << globalPos.z()/CLHEP::mm <<endreq;
      log << MSG::DEBUG << " phi pitch = " << element->phiPitch()<< ", eta pitch = " << element->etaPitch() <<endreq;
      m_pix_position_x.push_back(globalPos.x()/CLHEP::mm);
      m_pix_position_y.push_back(globalPos.y()/CLHEP::mm);
      m_pix_position_z.push_back(globalPos.z()/CLHEP::mm);
      m_pix_position_phipitch.push_back(element->phiPitch()/CLHEP::degree);
      m_pix_position_etapitch.push_back(element->etaPitch());
      m_pix_position_thickness.push_back(element->thickness()/CLHEP::mm);
      
      ++pixi;
    }
  }
  for(SCT_RDO_Container::const_iterator it=scthitCont->begin();it!=scthitCont->end() ; ++it) { // sct ROD Loop
    const InDetRawDataCollection<SCT_RDORawData>* SCTCollection(&(**it));
    int scti=0;
    for(InDetRawDataCollection<SCT_RDORawData>::const_iterator sct_itr=SCTCollection->begin(); sct_itr!=SCTCollection->end(); ++sct_itr) {
      const Identifier sctId((*sct_itr)->identify());
      const unsigned int rdoWord((*sct_itr)->getWord());
      const int sctBrlEc(m_sctId->barrel_ec(sctId)); // 0: barrel, 2: endcap
      const int sctLayerDisk(m_sctId->layer_disk(sctId));
      const int sctPhiMod(m_sctId->phi_module(sctId));
      const int sctEtaMod(m_sctId->eta_module(sctId));
      const int sctSide(m_sctId->side(sctId));
      const int sctStrip(m_sctId->strip(sctId));
      const int sctGroupSize((*sct_itr)->getGroupSize());
      //log << MSG::DEBUG  << "Hit "<< scti<<" : SCT "<< sctBrlEc<<":"<<sctLayerDisk <<" module phi " << sctPhiMod<< " eta " << sctPhiMod << " -- sct side: " << sctSide << " strip: " << sctStrip << " group size: " << sctGroupSize << endreq;
      const unsigned long long sct_rdoID_int = sctId.get_compact();
      m_sct_rdoID.push_back(sct_rdoID_int);
      m_sct_rdoWord.push_back(rdoWord);
      m_sct_barrelEndcap.push_back(sctBrlEc);
      m_sct_layerDisk.push_back(sctLayerDisk);
      m_sct_phiModule.push_back(sctPhiMod);
      m_sct_etaModule.push_back(sctEtaMod);
      m_sct_side.push_back(sctSide);
      m_sct_strip.push_back(sctStrip);
      m_sct_groupSize.push_back(sctGroupSize);
      //**  @class SCT_ID
      //** @verbatim
      //**    element           range              meaning
      //**    -------           -----              -------
      //**    barrel_ec          0                 barrel
      //**                    -2  / 2         neg ec /  pos ec
      //**    layer_disk       0 to 3            for barrel
      //**                     0 to 8            for ec
      //**    phi_module       0 to <56   for barrel (depends upon layer)
      //**                     0 to <52   for ec     (depends upon wheel)
      //**    eta_module      -6 to -1    for neg barrel, along z
      //**                     1 to 6     for pos barrel, along z
      //**                     0 to 2     for ec, along r
      //**    side             0 to 1     inner/outer of pairs of Si crystals
      //**    strip            0 to 767   strip number
      //**  These can be different for Upgrade layouts. In particular, we add a row index just before strip.
      //** @endverbatim
      const InDetDD::SiDetectorElement* element=m_sctManager->getDetectorElement(sctId);
      if (scti==0){
        log << MSG::DEBUG  << " SCT module center = " << element->center() << endreq;
        log << MSG::DEBUG  << " SCT module width, length (mm) = "  << element->width()/CLHEP::mm << ", length (mm) = " << element->length()/CLHEP::mm << ", thick (mm) = " << element->thickness()/CLHEP::mm << endreq;
      }
      Amg::Vector2D localPos = element->rawLocalPositionOfCell(sctId);
      Amg::Vector3D globalPos = element->globalPosition(localPos);
      log << MSG::DEBUG << " SCT Global pos " << "x (mm) = " << globalPos.x()/CLHEP::mm<< ", y (mm) = " << globalPos.y()/CLHEP::mm<< ", z (mm) = " << globalPos.z()/CLHEP::mm <<endreq;
      log << MSG::DEBUG << " phi pitch = " << element->phiPitch()<< ", eta pitch = " << element->etaPitch() <<endreq;
      m_sct_position_x.push_back(globalPos.x()/CLHEP::mm);
      m_sct_position_y.push_back(globalPos.y()/CLHEP::mm);
      m_sct_position_z.push_back(globalPos.z()/CLHEP::mm);
      m_sct_position_phipitch.push_back(element->phiPitch()/CLHEP::degree);
      m_sct_position_etapitch.push_back(element->etaPitch());
      m_sct_position_thickness.push_back(element->thickness()/CLHEP::mm);
      

      ++scti;
    }
  }
  /*
  for(LAr_RDO_Container::const_iterator it=larhitCont->begin();it!=larhitCont->end() ; ++it) { // lar ROD Loop
    const InDetRawDataCollection<LAr_RDORawData>* LArCollection(&(**it));
    int lari=0;
    for(InDetRawDataCollection<LAr_RDORawData>::const_iterator lar_itr=LArCollection->begin(); lar_itr!=LArCollection->end(); ++lar_itr) {
      const HWIdentifier larID(lar_itr->identify());
      const int rawEnergy(lar_itr->energy());
      const int rawTime(lar_itr->time());
      const uint16_t rawQual(lar_itr->quality());
      const uint16_t rawProv(lar_itr->provenance());
      CaloGain::CaloGain larGain(lar_itr->gain());

      const unsigned long long larID_int = larID.get_compact();
      const int larGain_int = (int)larGain;
      m_larID->push_back(larID_int);
      m_energy->push_back(rawEnergy);
      m_time->push_back(rawTime);
      m_qual->push_back(rawQual);
      m_prov->push_back(rawProv);
      m_gain->push_back(larGain_int);
      const InDetDD::SiDetectorElement* element=m_larManager->getDetectorElement(larId);
      if (lari==0){
        log << MSG::DEBUG  << " LAr module center = " << element->center() << endreq;
        log << MSG::DEBUG  << " LAr module width, length (mm) = "  << element->width()/CLHEP::mm << ", length (mm) = " << element->length()/CLHEP::mm << ", thick (mm) = " << element->thickness()/CLHEP::mm << endreq;
      }
      Amg::Vector2D localPos = element->rawLocalPositionOfCell(larId);
      Amg::Vector3D globalPos = element->globalPosition(localPos);
      log << MSG::DEBUG << " LAr Global pos " << "x (mm) = " << globalPos.x()/CLHEP::mm<< ", y (mm) = " << globalPos.y()/CLHEP::mm<< ", z (mm) = " << globalPos.z()/CLHEP::mm <<endreq;
      log << MSG::DEBUG << " phi pitch = " << element->phiPitch()<< ", eta pitch = " << element->etaPitch() <<endreq;
      m_lar_position_x.push_back(globalPos.x()/CLHEP::mm);
      m_lar_position_y.push_back(globalPos.y()/CLHEP::mm);
      m_lar_position_z.push_back(globalPos.z()/CLHEP::mm);
      m_lar_position_phipitch.push_back(element->phiPitch()/CLHEP::degree);
      m_lar_position_etapitch.push_back(element->etaPitch());
      m_lar_position_thickness.push_back(element->thickness()/CLHEP::mm);
      

      ++lari;
    }
  }
  */
  m_roottree->Fill();

  // End of execution for each event
  return StatusCode::SUCCESS;

}


