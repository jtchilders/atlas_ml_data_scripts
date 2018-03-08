#include "CaloDump/CaloDump.h"

#include "GaudiKernel/MsgStream.h"
#include "GaudiKernel/ISvcLocator.h"
#include "GaudiKernel/PropertyMgr.h"
#include "GaudiKernel/IToolSvc.h"
#include "StoreGate/StoreGate.h"
#include "GaudiKernel/ServiceHandle.h"

#include "CaloEvent/CaloCellContainer.h"
#include "CaloEvent/CaloCell.h"
#include "CaloEvent/CaloCompactCellContainer.h"

#include "TileIdentifier/TileTBID.h"
#include "TileEvent/TileCell.h"
#include "TileEvent/TileCellContainer.h"

#include "CaloIdentifier/CaloID.h"
#include "CaloDetDescr/CaloDetDescrManager.h"
#include "CaloEvent/CaloCell.h"
#include "CaloEvent/CaloCellContainer.h"

#include "xAODTruth/TruthEvent.h"
#include "xAODTruth/TruthVertex.h"
#include "xAODTruth/TruthParticle.h"
#include "xAODTruth/TruthParticleAuxContainer.h"
#include "xAODTruth/TruthEventAuxContainer.h"
#include "xAODTruth/TruthEventContainer.h"
#include "AthContainers/ConstDataVector.h"
#include "xAODJet/JetContainer.h"

#include "EventInfo/EventInfo.h"
#include "EventInfo/EventID.h"


const double pi2 = 6.28318;
const double GeV = 1000.0;


MyAlg::MyAlg(const std::string& name, ISvcLocator* pSvcLocator)
  : AthAlgorithm( name , pSvcLocator )
  , m_Threshold( 0.3 )
  , m_cellContainerName( "AllCalo" )
  , m_truthEventsContainerName( "TruthEvents" )
  , m_truthParticlesContainerName( "TruthParticles" )
  , m_rootFilename( "calocells.root" )
  , m_jetAuxContainerName( "AntiKt4TruthJets" )
{
  // Properties go here
  declareProperty( "energyThreshold" , m_Threshold ); //Threshold in GeV
  declareProperty( "cellsContainerName" , m_cellContainerName ); //SG Cell Container
  declareProperty( "truthEventsAuxContainerName", m_truthEventsAuxContainerName);
  declareProperty( "truthEventsContainerName" , m_truthEventsContainerName ); //SG TruthEvents Container
  declareProperty( "truthParticlesContainerName" , m_truthParticlesContainerName ); // xAOD::TruthParticleAuxContainer_v1_TruthParticlesAux.
  declareProperty( "rootFilename" , m_rootFilename ); // root filename
  declareProperty( "jetAuxContainerName", m_jetAuxContainerName); // xAOD::JetAuxContainer_v1_AntiKt4TruthJetsAux.

}


MyAlg::~MyAlg() {}


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
StatusCode MyAlg::initialize(){

  MsgStream log(msgSvc(), name());
  log << MSG::INFO << "initialize()" << endreq;

  m_events_all=0;

  m_rootfile = new TFile(m_rootFilename.c_str(),"recreate");
  m_roottree = new TTree("calocells","tree for calocells");

  m_roottree->Branch("run_number",&m_run_number,"run_number/s");
  m_roottree->Branch("event_number",&m_event_number,"event_number/I");
  m_roottree->Branch("lumi_block",&m_lumi_block,"lumi_block/I");
  m_roottree->Branch("time_stamp",&m_time_stamp,"time_stamp/I");


  m_roottree->Branch("n_truthparticles",&m_n_truthparticles,"n_truthparticles/I");
  m_roottree->Branch("particle_id","vector<short>",&m_particle_id);
  m_roottree->Branch("particle_eta","vector<float>",&m_particle_eta);
  m_roottree->Branch("particle_phi","vector<float>",&m_particle_phi);
  m_roottree->Branch("particle_E","vector<float>",&m_particle_E);
  m_roottree->Branch("particle_pt","vector<float>",&m_particle_pt);
  m_roottree->Branch("particle_status","vector<unsigned short>",&m_particle_status);

  m_roottree->Branch("n_truthjets",&m_n_truthjets,"n_truthjets/I");
  m_roottree->Branch("tjet_eta","vector<float>",&m_tjet_eta);
  m_roottree->Branch("tjet_phi","vector<float>",&m_tjet_phi);
  m_roottree->Branch("tjet_pt","vector<float>",&m_tjet_pt);
  m_roottree->Branch("tjet_m","vector<float>",&m_tjet_m);

  m_roottree->Branch("tile_n_cells",&m_tile_n_cells,"tile_n_cells/I");
  m_roottree->Branch("tile_x","vector<float>",&m_tile_cell_x);
  m_roottree->Branch("tile_y","vector<float>",&m_tile_cell_y);
  m_roottree->Branch("tile_z","vector<float>",&m_tile_cell_z);
  m_roottree->Branch("tile_Et","vector<float>",&m_tile_cell_Et);
  m_roottree->Branch("tile_eta","vector<float>",&m_tile_cell_eta);
  m_roottree->Branch("tile_phi","vector<float>",&m_tile_cell_phi);
  m_roottree->Branch("tile_bad_cell","vector<bool>",&m_tile_cell_bad);
  m_roottree->Branch("tile_section","vector<short>",&m_tile_section);
  m_roottree->Branch("tile_module","vector<short>",&m_tile_module);
  m_roottree->Branch("tile_tower","vector<short>",&m_tile_tower);
  m_roottree->Branch("tile_sample","vector<short>",&m_tile_sample);

  m_roottree->Branch("lar_n_cells",&m_lar_n_cells,"lar_n_cells/I");
  m_roottree->Branch("lar_x","vector<float>",&m_lar_cell_x);
  m_roottree->Branch("lar_y","vector<float>",&m_lar_cell_y);
  m_roottree->Branch("lar_z","vector<float>",&m_lar_cell_z);
  m_roottree->Branch("lar_Et","vector<float>",&m_lar_cell_Et);
  m_roottree->Branch("lar_eta","vector<float>",&m_lar_cell_eta);
  m_roottree->Branch("lar_phi","vector<float>",&m_lar_cell_phi);
  m_roottree->Branch("lar_bad_cell","vector<bool>",&m_lar_cell_bad);
  m_roottree->Branch("lar_barrel_ec","vector<short>",&m_lar_barrel_ec);
  m_roottree->Branch("lar_sampling","vector<short>",&m_lar_sampling);
  m_roottree->Branch("lar_region","vector<short>",&m_lar_region);
  m_roottree->Branch("lar_hw_eta","vector<short>",&m_lar_eta);
  m_roottree->Branch("lar_hw_phi","vector<short>",&m_lar_phi);
  m_roottree->Branch("lar_is_em","vector<bool>",&m_lar_is_em);
  m_roottree->Branch("lar_is_em_barrel","vector<bool>",&m_lar_is_em_barrel);
  m_roottree->Branch("lar_is_em_endcap","vector<bool>",&m_lar_is_em_endcap);
  m_roottree->Branch("lar_is_em_endcap_inner","vector<bool>",&m_lar_is_em_endcap_inner);
  m_roottree->Branch("lar_is_em_endcap_outer","vector<bool>",&m_lar_is_em_endcap_outer);
  m_roottree->Branch("lar_is_hec","vector<bool>",&m_lar_is_hec);
  m_roottree->Branch("lar_is_fcal","vector<bool>",&m_lar_is_fcal);
  
  
  CHECK( service("StoreGateSvc", m_storeGate) );


/*
  sc = service("DetectorStore", m_detStore);
  if ( sc.isFailure() ) {
    log << MSG::ERROR
        << "Unable to get pointer to DetectorStore Service" << endreq;
    return sc;
  }
*/

  /** get a handle on the NTuple and histogramming service */
/*  sc = service("THistSvc", m_thistSvc);
  if(sc.isFailure() ){
    log << MSG::ERROR
        << "Unable to retrieve pointer to THistSvc"
        << endreq;
    return sc;
  }*/

  CHECK( service("DetectorStore",m_detStore) );

  CHECK( m_detStore->retrieve(m_tileID) );

  CHECK( m_detStore->retrieve(m_tileHWID) );


  CHECK( m_detStore->retrieve(m_caloMgr) );
  

  m_caloCellHelper = m_caloMgr->getCaloCell_ID();
  if (!m_caloCellHelper) {
    log << MSG::ERROR << "Could not access CaloCell_ID helper" << endreq;
    return StatusCode::FAILURE;
  }


  return StatusCode::SUCCESS;

}



// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
StatusCode MyAlg::execute() {

  MsgStream log(msgSvc(), name());

  m_events_all++;
  if (m_events_all<=10 ||
      (m_events_all<=100 && (m_events_all%10) == 0) ||
      (m_events_all<=1000 && (m_events_all%100) == 0)  ||
      (m_events_all>=1000 && (m_events_all%1000) == 0)  ) {
    log <<  MSG::INFO << "##### - Event processed: " << m_events_all << endreq;
  };

  CHECK( GetCells() );

  return StatusCode::SUCCESS;

}



// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
StatusCode MyAlg::finalize() {
  MsgStream log(msgSvc(), name());
  log << MSG::INFO << "finalize()" << endreq;
  m_rootfile->cd();
  m_roottree->Write();
  m_rootfile->Close();
  return StatusCode::SUCCESS;
}



// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
StatusCode MyAlg::GetCells() {

  MsgStream log(messageService(), name());

  log <<MSG::DEBUG << "Call MyAlg::GetCells()" << endreq;

  // get event info
  const EventInfo* eventInfo = 0;
  CHECK( evtStore()->retrieve( eventInfo) );
  const EventID* evtid = eventInfo->event_ID();
  m_run_number = evtid->run_number();
  m_event_number = evtid->event_number();
  m_lumi_block = evtid->lumi_block();
  m_time_stamp = evtid->time_stamp();
  
  // Retrieve the xAOD truth objects
  //const xAOD::TruthEventAuxContainer* xTruthEventContainer = NULL;
  //CHECK( evtStore()->retrieve( xTruthEventContainer, m_truthEventsContainerName));

  //const xAOD::TruthEventAuxContainer* xTruthEventAuxContainer = NULL;
  //CHECK( evtStore()->retrieve( xTruthEventAuxContainer, m_truthEventsAuxContainerName));

  const xAOD::TruthParticleContainer* xTruthParticleContainer = NULL;
  CHECK( evtStore()->retrieve( xTruthParticleContainer, m_truthParticlesContainerName));
  //xAOD::TruthParticleContainer* truthParticleContainer = new xAOD::TruthParticleContainer();
  //truthParticleContainer->setStore(xTruthParticleContainer);
    //log <<MSG::DEBUG << "truth events: " << xTruthEventContainer->size() << endreq;
  //log <<MSG::DEBUG << "truth particles: " << xTruthParticleContainer->size() << endreq;

  m_particle_id.clear();
  m_particle_eta.clear();
  m_particle_phi.clear();
  m_particle_E.clear();
  m_particle_pt.clear();
  m_particle_status.clear();
 
  m_n_truthparticles = xTruthParticleContainer->size();
  bool have_z=false,have_e=false,have_p=false;
  short int pcount = 0;
  //int limit = 500,limit_counter =0;
  for (const xAOD::TruthParticle* p: *xTruthParticleContainer){
    
    //if( (p->pt()/GeV) > 0.7)
    
    if (p->status() == 3){
       log<<MSG::DEBUG<<" pdgid: " << p->pdgId() << " eta: " << p->eta() << " phi: " << p->phi() << " e: " << (p->e()/GeV) << " pt: " << (p->pt()/GeV) << " status: " << p->status() << endreq;
       m_particle_id.push_back(p->pdgId());
       m_particle_eta.push_back(p->eta());
       m_particle_phi.push_back(p->phi());
       m_particle_E.push_back((p->e()/GeV));
       m_particle_pt.push_back((p->pt()/GeV));
       m_particle_status.push_back(p->status());
       pcount++;
    }

/*
    if(p->status() == 3){
      log<<MSG::DEBUG<< " nChildren: " << p->nChildren() << endreq;
      for(int i=0;i<p->nChildren();++i){
         const xAOD::TruthParticle* child = p->child(i);
         log<<MSG::DEBUG<< "   child: pdgid: " << child->pdgId() << " eta: " << child->eta() << " phi: " << child->phi() << " e: " << (child->e()/GeV) << " pt: " << (child->pt()/GeV) << " status: " << child->status() << endreq;
      }
    }
*/
    
    //if(p->pdgId() == 23)
    //  log<<MSG::DEBUG<< "     Z: " << p->pdgId() << " " << p->eta() << " " << p->phi() << " " << (p->e()/GeV) << " " << (p->pt()/GeV) << " " << p->status() << endreq;

    //if(p->pdgId() == 11 and (p->pt()/GeV) > 1.)
    //  log<<MSG::DEBUG<< "     e: " << p->pdgId() << " " << p->eta() << " " << p->phi() << " " << (p->e()/GeV) << " " << (p->pt()/GeV) << " " << p->status() << endreq;
    
    //limit_counter++;
    //if(limit_counter>limit) break;
  }
  m_n_truthparticles = pcount;


  const xAOD::JetContainer* xJetContainer = NULL;
  CHECK( evtStore()->retrieve( xJetContainer, m_jetAuxContainerName));

  short int jcount = 0;
  for(const xAOD::Jet* j: *xJetContainer){
  //for( xAOD::JetContainer::const_iterator j = xJetContainer.begin(); j != xJetContainer.end() ; ++j){
     
     log<<MSG::DEBUG<<" tjet: " << jcount << " eta: " << j->eta() << " phi: " << j->phi() << " pt: " << j->pt() << " m: " << j->m() << endreq;
     m_tjet_eta.push_back(j->eta());
     m_tjet_phi.push_back(j->phi());
     m_tjet_pt.push_back(j->pt()/GeV);
     m_tjet_m.push_back(j->m()/GeV);
     jcount++;
  }
  m_n_truthjets = jcount;

  
  /*
  log<<MSG::DEBUG<<" found photon: pt = " << (photon->pt()/GeV) << " eta = " << photon->eta() << " phi = " << photon->phi() << endreq;
  const xAOD::TruthParticle* jet = NULL;
  for (const xAOD::TruthParticle* p: *xTruthParticleContainer){
    if(p->status() == photon->status() and !p->isPhoton()){
      jet = p;
      log<<MSG::DEBUG<< " found jet:    pt = " << (jet->pt()/GeV) << " eta = " << jet->eta() << " phi = " << jet->phi() << " pdgId = " << jet->pdgId() << " status = " << jet->status() << endreq;
      //break;
    }
  }
  //log<<MSG::DEBUG<< " found jet: pt = " << (jet->pt()/GeV) << " eta = " << jet->eta() << " phi = " << jet->phi() << endreq;
*/



/*
  for (const xAOD::TruthEvent* evt : *xTruthEventContainer) {
    
    const xAOD::TruthVertex* vtx = evt->signalProcessVertex();
    
    log<<MSG::DEBUG << " outgoing particles: " << vtx->nOutgoingParticles() << endreq;
    log<<MSG::DEBUG << " incomping particles: " << vtx->nIncomingParticles() << endreq;
    for(unsigned int np = 0;np<vtx->nOutgoingParticles();++np){
      const xAOD::TruthParticle* part = vtx->outgoingParticle(np);
      log<<MSG::DEBUG << "   particle: " << np << "; pdgid: " << part->pdgId() << " eta: " << part->eta() << " phi: " << part->phi() << " pt: " << (part->pt()/GeV) << " nParents: " << part->nParents() << " nChildren: " << part->nChildren() << endreq;
      for (unsigned int parent=0;parent<part->nParents();++parent)
         log<<MSG::DEBUG << "      parent: " << parent << " pdgid: " << part->parent(parent)->pdgId() << " eta: " << part->parent(parent)->eta() << " phi: " << part->parent(parent)->phi() << " pt: " << (part->parent(parent)->pt()/GeV) << " nParents: " << part->parent(parent)->nParents() << " nChildren: " << part->parent(parent)->nChildren() << endreq;
      for (unsigned int child=0;child<part->nChildren();++child){
         const xAOD::TruthParticle* cp = part->child(child);
         if(cp!=0)
         log<<MSG::DEBUG << "      child:  " << child << " pdgid: " << cp->pdgId() << " eta: " << cp->eta() << " phi: " << cp->phi() << " e: " << (cp->pt()/GeV) << "  nParents: " << cp->nParents() << " nChildren: " << cp->nChildren() << endreq;
      } 
    }

  }*/


  m_tile_n_cells = 0;
  m_tile_cell_x.clear();
  m_tile_cell_y.clear();
  m_tile_cell_z.clear();
  m_tile_cell_Et.clear();
  m_tile_cell_eta.clear();
  m_tile_cell_phi.clear();
  m_tile_cell_bad.clear();
  m_tile_section.clear();
  m_tile_module.clear();
  m_tile_tower.clear();
  m_tile_sample.clear();

  m_lar_n_cells = 0;
  m_lar_cell_x.clear();
  m_lar_cell_y.clear();
  m_lar_cell_z.clear();
  m_lar_cell_Et.clear();
  m_lar_cell_eta.clear();
  m_lar_cell_phi.clear();
  m_lar_cell_bad.clear();
  m_lar_barrel_ec.clear();
  m_lar_sampling.clear();
  m_lar_region.clear();
  m_lar_eta.clear();
  m_lar_phi.clear();
  m_lar_is_em.clear();
  m_lar_is_em_barrel.clear();
  m_lar_is_em_endcap.clear();
  m_lar_is_em_endcap_inner.clear();
  m_lar_is_em_endcap_outer.clear();
  m_lar_is_hec.clear();
  m_lar_is_fcal.clear();


  const  CaloCellContainer* cellCont = 0;
  //const CaloCompactCellContainer* cellCont = 0;
  StatusCode sc=m_storeGate->retrieve( cellCont, m_cellContainerName);
  if( sc.isFailure()  ||  !cellCont ) {
    log << MSG::ERROR
        << "No ESD container found in TDS with the name:" << m_cellContainerName
        << endreq;
    return StatusCode::FAILURE;
  }

  //log << MSG::INFO << " number of calo cells: " << cellCont->size() << endreq;


  CaloCellContainer::const_iterator iCell = cellCont->begin();
  CaloCellContainer::const_iterator lastCell  = cellCont->end();

  
  for( ; iCell != lastCell; ++iCell) {


    Identifier id;
    const CaloCell* cell_ptr = *iCell;     // pointer to cell object
    const Identifier cellId = cell_ptr->ID();

    
    
    //log << MSG::INFO << cell_ptr->x() << " " << cell_ptr->y() << " " << cell_ptr->z() << " " << cell_ptr->eta() << " " << cell_ptr->phi() << " " << (cell_ptr->energy()/GeV) << endreq;
    if(cell_ptr->energy()/GeV > 0.1){
       if(m_caloCellHelper->is_tile(cellId)){ 
         m_tile_n_cells++;
         m_tile_cell_x.push_back(cell_ptr->x());
         m_tile_cell_y.push_back(cell_ptr->y());
         m_tile_cell_z.push_back(cell_ptr->z());
         m_tile_cell_Et.push_back(cell_ptr->energy()/GeV*cell_ptr->sinTh());
         m_tile_cell_eta.push_back(cell_ptr->eta());
         m_tile_cell_phi.push_back(cell_ptr->phi());
         m_tile_cell_bad.push_back(cell_ptr->badcell());
         m_tile_section.push_back(m_caloCellHelper->section(cellId));
         m_tile_module.push_back(m_caloCellHelper->module(cellId));
         m_tile_tower.push_back(m_caloCellHelper->tower(cellId));
         m_tile_sample.push_back(m_caloCellHelper->sample(cellId));
       }
       else{
         m_lar_n_cells++;
         /*std::cout << " lar: " << m_lar_n_cells << " " << cell_ptr->x() << " " << cell_ptr->y() << " " 
                               << cell_ptr->z() << " " << (cell_ptr->energy()/GeV) << " " 
                               << cell_ptr->eta() << " " << cell_ptr->phi() << " "
                               << cell_ptr->badcell() << " " << m_caloCellHelper->pos_neg(cellId) << " "
                               << m_caloCellHelper->sampling(cellId) << " " << m_caloCellHelper->region(cellId) << " "
                               << m_caloCellHelper->eta(cellId) << " " << m_caloCellHelper->phi(cellId) << "\n";*/
         m_lar_cell_x.push_back(cell_ptr->x());
         m_lar_cell_y.push_back(cell_ptr->y());
         m_lar_cell_z.push_back(cell_ptr->z());
         m_lar_cell_Et.push_back(cell_ptr->energy()/GeV*cell_ptr->sinTh());
         m_lar_cell_eta.push_back(cell_ptr->eta());
         m_lar_cell_phi.push_back(cell_ptr->phi());
         m_lar_cell_bad.push_back(cell_ptr->badcell());
         m_lar_barrel_ec.push_back(m_caloCellHelper->pos_neg(cellId));
         m_lar_sampling.push_back(m_caloCellHelper->sampling(cellId));
         m_lar_region.push_back(m_caloCellHelper->region(cellId));
         m_lar_eta.push_back(m_caloCellHelper->eta(cellId));
         m_lar_phi.push_back(m_caloCellHelper->phi(cellId));
         m_lar_is_em.push_back(m_caloCellHelper->is_em(cellId));
         m_lar_is_em_barrel.push_back(m_caloCellHelper->is_em_barrel(cellId));
         m_lar_is_em_endcap.push_back(m_caloCellHelper->is_em_endcap(cellId));
         m_lar_is_em_endcap_inner.push_back(m_caloCellHelper->is_em_endcap_inner(cellId));
         m_lar_is_em_endcap_outer.push_back(m_caloCellHelper->is_em_endcap_outer(cellId));
         m_lar_is_hec.push_back(m_caloCellHelper->is_hec(cellId));
         m_lar_is_fcal.push_back(m_caloCellHelper->is_fcal(cellId));
       }
    }

/*
    if ( m_tileID->is_tile( cellId )) {

      const TileCell* tile_cell = dynamic_cast<const TileCell*> (cell_ptr);
      if (tile_cell!=0) {
        id = tile_cell->ID();

        short cell_isbad = 0 ; // use isCellBad(tile_cell, id)i from TileCellMonTool;
        // is cell is good
        if (cell_isbad >= 1) continue;
        energy = cell_ptr->energy() / GeV;
        // is energy above threshold?
        if (energy <  m_Threshold) continue;

        time = cell_ptr->time();
        eta = cell_ptr->eta();
        phi = cell_ptr->phi();
        if (phi<0) phi=pi2+phi;
        quality=cell_ptr->quality();
        region=m_tileID->region(id);
        module=m_tileID->module(id);
        section=m_tileID->section(id);
        sample=m_tileID->sample(id);
        tower=m_tileID->tower(id);
        x=cell_ptr->x();
        y=cell_ptr->y();
        z=cell_ptr->z();

        log << MSG::DEBUG  << "SC: Identifier: " << id << endreq;
        log << MSG::DEBUG <<
          "  region: " << region   <<
          "  system: " << m_tileID->system(id)  <<
          "  section: "<< section  <<
          "  side: "   << m_tileID->side(id)    <<
          "  sample: " << sample                <<
          "  tower: "  << tower                 <<
          "  module: " << module                <<
          "  pmt: "    << m_tileID->pmt(id)     <<
          "  adc: "    << m_tileID->adc(id)     <<
          "  Energy (GeV):"  << energy          <<
          "  Time "    << time                  <<
          "  Eta "    << eta                    <<
          "  Phi "    << phi                    <<
          "  x:  "    << x                      <<
          "  y:  "    << y                      <<
          "  z:  "    << z                      <<
          endreq ;
        

        ncells++;

        tolE=tolE+energy;

      }
    }
*/

  }
  std::cout << " lar cells written: " << m_lar_n_cells << "\n";

  m_roottree->Fill();

  //log << MSG::DEBUG  << "No of tile cells above threshold: " << ncells << endreq;

  // End of execution for each event
  return StatusCode::SUCCESS;

}
