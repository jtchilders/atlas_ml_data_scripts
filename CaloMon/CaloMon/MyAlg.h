#ifndef MyAlg_h
#define MyAlg_h

#include "AthenaBaseComps/AthAlgorithm.h"

#include "GaudiKernel/ToolHandle.h"
#include "GaudiKernel/ITHistSvc.h"
#include "CLHEP/Units/SystemOfUnits.h"
#include "StoreGate/StoreGateSvc.h"

#include "TileConditions/TileInfo.h"
#include "CaloIdentifier/TileID.h"
#include "CaloIdentifier/LArEM_ID.h"
#include "TileIdentifier/TileHWID.h"
#include "TileConditions/TileCablingService.h"

#include "CaloIdentifier/CaloID.h"
#include "CaloIdentifier/CaloIdManager.h"

#include "TTree.h"
#include "TFile.h"

class CaloCell_ID;

#include <string>
#include <vector>
#include <fstream>


/////////////////////////////////////////////////////////////////////////////
class MyAlg : public AthAlgorithm
{

public:
  MyAlg (const std::string& name, ISvcLocator* pSvcLocator);
  virtual ~MyAlg();
  StatusCode initialize();
  StatusCode execute();
  StatusCode finalize();

  StatusCode GetCells();

private:

  double m_Threshold;
  std::string m_cellContainerName;
  std::string m_truthEventsContainerName;
  std::string m_truthEventsAuxContainerName;
  std::string m_truthParticlesContainerName;
  std::string m_rootFilename;
  std::string m_jetAuxContainerName;
  
  int  m_events_all;
  /// a handle on Store Gate
  StoreGateSvc* m_storeGate;
  StoreGateSvc* m_detStore;

  const TileInfo* m_tileInfo;
  const TileID* m_tileID;
  const TileHWID* m_tileHWID;
  const TileCablingService* m_cabling;
  const CaloCell_ID* m_caloCellHelper;
  const CaloIdManager*  m_caloMgr;

  TTree* m_roottree;
  
  unsigned short int m_run_number;
  unsigned int m_event_number;
  unsigned int m_lumi_block;
  unsigned int m_time_stamp;

  unsigned int m_n_truthparticles;
  std::vector<short int> m_particle_id;
  std::vector<float> m_particle_eta;
  std::vector<float> m_particle_phi;
  std::vector<float> m_particle_E;
  std::vector<float> m_particle_pt;
  std::vector<unsigned short int> m_particle_status;

  unsigned int m_n_truthjets;
  std::vector<float> m_tjet_eta;
  std::vector<float> m_tjet_phi;
  std::vector<float> m_tjet_pt;
  std::vector<float> m_tjet_m;

  unsigned int m_tile_n_cells;
  std::vector<float> m_tile_cell_x,m_tile_cell_y,m_tile_cell_z,m_tile_cell_Et;
  std::vector<float> m_tile_cell_eta,m_tile_cell_phi;
  std::vector<bool> m_tile_cell_bad;
  std::vector<short int> m_tile_section,m_tile_module,m_tile_tower,m_tile_sample;

/**
   * 0033 * 
   * 0034 * @class TileID
   * 0035 * @brief Helper class for TileCal offline identifiers
   * 0036 * @author Alexander Solodkov
   * 0037 *
   * 0038 * This class provides an interface to generate an identifier or  a range
   * 0039 * for the Tile Calorimeter detector subsystem.
   * 0040 *
   * 0041 * Definition and the range of values for the elements of the identifier:
   * 0042 * <pre>
   * 0043 *
   * 0044 *  element     range       meaning
   * 0045 *  -------     -----       -------
   * 0046 *
   * 0047 *  section     1 to 15     section number  ( 1 = Barrel
   * 0048 *                                            2 = Extended Barrel
   * 0049 *                                            3 = Gap Detector
   * 0050 *                                                i.e. gap scin E1-E4 and ITC cells D4, C10
   * 0051 *                                            4 = Ancillary detectors )
   * 0052 *                           section codes 5 and 6 are used internally
   * 0053 *                           for supercell barrel and extbarrel, respectively.
   * 0054 *  side       -1 to 1      -1 = negative eta, 1 = positive eta, 0 = undefined (both sides) 
   * 0055 *  module      0 to 63     module number by phi
   * 0056 *  tower(eta)  0 to 15     0-15 = tower number by pseudorapidity with 0.1 increment in eta
   * 0057 *                          Attention! in PhysTDR data last tower is 16
   * 0058 *  sample      0 to 15     0 = A, 1 = B = BC = C, 2 = D, 3 = special gap scin cells E1-E4
   * 0059 *                          4-15 = individual tiles, used in Cesium calibration data
   * 0060 *  pmt         0 to 1      PMT number in the cell (0 = side close to module with smaller number)
   * 0061 *  adc         0 to 1      ADC number for the PMT (0 = low gain, 1 = high gain)
   * 0062 *
   * 0063 * </pre>
   * 0064 */

  
  unsigned int m_lar_n_cells;
  std::vector<float> m_lar_cell_x,m_lar_cell_y,m_lar_cell_z,m_lar_cell_Et;
  std::vector<float> m_lar_cell_eta,m_lar_cell_phi;
  std::vector<bool> m_lar_cell_bad,m_lar_is_em,m_lar_is_em_barrel,
                    m_lar_is_em_endcap,m_lar_is_em_endcap_inner,
                    m_lar_is_em_endcap_outer,m_lar_is_hec,m_lar_is_fcal;
  std::vector<short int> m_lar_barrel_ec,m_lar_sampling,m_lar_region,m_lar_eta,m_lar_phi;
 /**
  * 0150    * return neg_pos according to : <br>
  * 0151    * 
  * 0152    * <pre>
  * 0153    * element           range              meaning
  * 0154    * -------           -----              -------
  * 0155    * 
  * 0156    * barrel_ec        +/-1             positive/negative barrel - A/C side or P/M half barrel
  * 0157    * "                +/-2             positive/negative endcap outer wheel - A/C side 
  * 0158    * "                +/-3             positive/negative endcap inner wheel - A/C side
  * 0159    * 
  * 0160    * </pre> 
  * 0161    **/


/**
 * 0165    * return sampling according to : <br>
 * 0166    * 
 * 0167    * element           range              meaning
 * 0168    * -------           -----              -------
 * 0169    * 
 * 0170    * sampling         0                both presamplers
 * 0171    * "                [1,3]            barrel and endcap outer wheel 
 * 0172    * "                [1,2]            endcap inner wheel
 * 0173    * 
 * 0174    * </pre> 
 * 0175    */

/**
 * 0180    * return region according to : <br>
 * 0181    * 
 * 0182    * <pre>
 * 0183    * 
 * 0184    * element           range              meaning
 * 0185    * -------           -----              -------
 * 0186    * 
 * 0187    * region           0               both presamplers
 * 0188    * "                [0,1]           barrel sampling 1 and 2 
 * 0189    * "                0               barrel sampling 3
 * 0190    * "
 * 0191    * "                [0,5]           endcap outer wheel sampling 1 (cells)
 * 0192    * "                0,[2,5]         endcap outer wheel sampling 1 (supercells)
 * 0193    * "                0               endcap inner wheel sampling 1 (cells)
 * 0194    * "                [0,1]           endcap inner wheel sampling 1 (supercells)
 * 0195    * "                [0,1]           endcap outer wheel sampling 2
 * 0196    * "                0               endcap inner wheel sampling 2 (cells)
 * 0197    * "                [0,1]           endcap inner wheel sampling 2 (supercells)
 * 0198    * "                0               endcap outer wheel sampling 3
 * 0199    * 
 * 0200    * </pre> 
 * 0201    */


/**
 * 0205    * return eta according to : <br>
 * 0206    * 
 * 0207    * <pre>
 * 0208    * Cells:
 * 0209    * element           range              meaning
 * 0210    * -------           -----              -------
 * 0211    * 
 * 0212    * eta for barrel   [0,60]         presampler - 0< eta <1.52 - deta is approximately equal to 0.025
 * 0213    * "                [0,447]        sampling 1 region 0  0   < eta < 1.4   - deta = 0.025/8 
 * 0214    * "                [0,2]          sampling 1 region 1  1.4 < eta < 1.475 - deta = 0.025
 * 0215    * "                [0,55]         sampling 2 region 0  0   < eta < 1.4   - deta = 0.025 
 * 0216    * "                0              sampling 2 region 1  1.4 < eta < 1.475 - deta = 0.075
 * 0217    * "                [0,26]         sampling 3 region 0  0   < eta < 1.35  - deta = 0.050 
 * 0218    * "
 * 0219    * 
 * 0220    * eta for endcap   [0,11]      presampler  sampling 0 region 0  1.5   < eta < 1.8   - deta = 0.025
 * 0221    * "                0           outer wheel sampling 1 region 0  1.375 < eta < 1.425 - deta = 0.05  
 * 0222    * "                [0,2]       outer wheel sampling 1 region 1  1.425 < eta < 1.5   - deta = 0.025
 * 0223    * "                [0,95]      outer wheel sampling 1 region 2  1.5   < eta < 1.8   - deta = 0.025/8
 * 0224    * "                [0,47]      outer wheel sampling 1 region 3  1.8   < eta < 2.0   - deta = 0.025/6
 * 0225    * "                [0,63]      outer wheel sampling 1 region 4  2.0   < eta < 2.4   - deta = 0.025/4 
 * 0226    * "                [0,3]       outer wheel sampling 1 region 5  2.4   < eta < 2.5   - deta = 0.025
 * 0227    * "                [0,6]       inner wheel sampling 1 region 0  2.5   < eta < 3.2   - deta = 0.1
 * 0228    * "                0           outer wheel sampling 2 region 0  1.375 < eta < 1.425 - deta = 0.05
 * 0229    * "                [0,42]      outer wheel sampling 2 region 1  1.425 < eta < 2.5   - deta = 0.025
 * 0230    * "                [0,6]       inner wheel sampling 2 region 0  2.5   < eta < 3.2   - deta = 0.1
 * 0231    * "                [0,19]      outer wheel sampling 3 region 0  1.5   < eta < 2.5   - deta = 0.05 
 * 0232    * 
 * 0233    * Supercells:
 * 0234    * element           range              meaning
 * 0235    * -------           -----              -------
 * 0236    * 
 * 0237    * eta for barrel   [0,15]         presampler - 0< eta <1.52 - deta is approximately equal to 0.1
 * 0238    * "                [0,55]         sampling 1 region 0  0   < eta < 1.4   - deta = 0.025
 * 0239    * "                [0,2]          sampling 1 region 1  1.4 < eta < 1.475 - deta = 0.025
 * 0240    * "                [0,55]         sampling 2 region 0  0   < eta < 1.4   - deta = 0.025 
 * 0241    * "                0              sampling 2 region 1  1.4 < eta < 1.475 - deta = 0.075
 * 0242    * "                [0,13]         sampling 3 region 0  0   < eta < 1.35  - deta = 0.1
 * 0243    * "
 * 0244    * 
 * 0245    * eta for endcap   [0,2]       presampler  sampling 0 region 0  1.5   < eta < 1.8   - deta = 0.1
 * 0246    * "                0           outer wheel sampling 1 region 0  1.375 < eta < 1.425 - deta = 0.125
 * 0247    * "                [0,11]      outer wheel sampling 1 region 2  1.5   < eta < 1.8   - deta = 0.025
 * 0248    * "                [0,7]       outer wheel sampling 1 region 3  1.8   < eta < 2.0   - deta = 0.033
 * 0249    * "                [0,15]      outer wheel sampling 1 region 4  2.0   < eta < 2.4   - deta = 0.025
 * 0250    * "                0           outer wheel sampling 1 region 5  2.4   < eta < 2.5   - deta = 0.1
 * 0251    * "                [0,2]       inner wheel sampling 1 region 0  2.5   < eta < 3.1   - deta = 0.2
 * 0252    * "                0           inner wheel sampling 1 region 1  3.1   < eta < 3.2   - deta = 0.1
 * 0253    * "                0           outer wheel sampling 2 region 0  1.375 < eta < 1.425 - deta = 0.05
 * 0254    * "                [0,42]      outer wheel sampling 2 region 1  1.425 < eta < 2.5   - deta = 0.025
 * 0255    * "                [0,2]       inner wheel sampling 2 region 0  2.5   < eta < 3.1   - deta = 0.2
 * 0256    * "                0           inner wheel sampling 2 region 0  3.1   < eta < 3.2   - deta = 0.1
 * 0257    * "                [0,9]       outer wheel sampling 3 region 0  1.5   < eta < 2.5   - deta = 0.1
 * 0258    * 
 * 0259    *  -999 if disconnected channel
 * 0260    * </pre> 
 * 0261    */


/**
 * 0265    * return phi according to : <br>
 * 0266    * 
 * 0267    * <pre>
 * 0268    * element           range              meaning
 * 0269    * -------           -----              -------
 * 0270    * 
 * 0271    * 
 * 0272    * Cells:
 * 0273    * phi for barrel   [0,63]         barrel presampler   - dphi = 0.1
 * 0274    * "                [0,63]         sampling 1 region 0 - dphi = 0.1
 * 0275    * "                [0,255]        sampling 1 region 1 - dphi = 0.025
 * 0276    * "                [0,255]        sampling 2 region 0 - dphi = 0.025
 * 0277    * "                [0,255]        sampling 2 region 1 - dphi = 0.025
 * 0278    * "                [0,255]        sampling 3 region 1 - dphi = 0.025
 * 0279    * 
 * 0280    * 
 * 0281    * 
 * 0282    * phi for endcap   [0,63]      presampler  sampling 0 region 0       - dphi = 0.1
 * 0283    * "                [0,63]      outer wheel sampling 1 regions [0,5]  - dphi = 0.1 
 * 0284    * "                [0,63]      inner wheel sampling 1 regions 0      - dphi = 0.1 
 * 0285    * "                [0,255]     outer wheel sampling 2 regions [0,1]  - dphi = 0.025
 * 0286    * "                [0,63]      inner wheel sampling 2 region 0       - dphi = 0.1
 * 0287    * "                [0,255]     outer wheel sampling 3 region 0       - dphi = 0.025
 * 0288    * 
 * 0289    * Supercells:
 * 0290    * phi for barrel   [0,63]         barrel presampler   - dphi = 0.1
 * 0291    * "                [0,63]         sampling 1 region 0 - dphi = 0.1
 * 0292    * "                [0,63]         sampling 1 region 1 - dphi = 0.1
 * 0293    * "                [0,63]         sampling 2 region 0 - dphi = 0.1
 * 0294    * "                [0,63]         sampling 2 region 1 - dphi = 0.1
 * 0295    * "                [0,63]         sampling 3 region 1 - dphi = 0.1
 * 0296    * 
 * 0297    * 
 * 0298    * 
 * 0299    * phi for endcap   [0,63]      presampler  sampling 0 region 0       - dphi = 0.1
 * 0300    * "                [0,63]      outer wheel sampling 1 regions [0,5]  - dphi = 0.1 
 * 0301    * "                [0,31]      inner wheel sampling 1 regions 0      - dphi = 0.2
 * 0302    * "                [0,63]      outer wheel sampling 2 regions [0,1]  - dphi = 0.1
 * 0303    * "                [0,31]      inner wheel sampling 2 region 0       - dphi = 0.2
 * 0304    * "                [0,63]      outer wheel sampling 3 region 0       - dphi = 0.1
 * 0305    * 
 * 0306    *   -999 if disconnected channel
 * 0307    * </pre> 
 * 0308    */

  TFile* m_rootfile;

  

  /// get a handle on the Hist/TTree registration service
  ITHistSvc * m_thistSvc;

};

#endif
