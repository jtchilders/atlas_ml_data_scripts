#!/usr/bin/env python2.7
import os,sys,optparse,logging,numpy,ROOT,json,glob
ROOT.gStyle.SetOptStat(0)
#import tensorflow as tf
logger = logging.getLogger(__name__)

# mapping for tile
'''
*  element     range       meaning
*  -------     -----       -------
*
*  ros         1 to 4      ReadOutSystem number ( 1,2 = pos/neg Barrel (side A/C)
*                                                 3,4 = pos/neg Ext.Barrel (side A/C) )
*  drawer      0 to 63     64 drawers (modules) in one cylinder (phi-slices)
*  channel     0 to 47     channel number in the drawer
*  adc         0 to 1      ADC number for the channel (0 = low gain, 1 = high gain)
'''

# lar mapping
'''
* Definition and range of values for the elements of the identifier are: <p>
* <pre>
*             Connected channels :
*             ------------------
* element           range              meaning
* -------           -----              -------
* 
* barrel_ec        +/-1             positive/negative barrel - A/C side or P/M half barrel
* "                +/-2             positive/negative endcap outer wheel - A/C side 
* "                +/-3             positive/negative endcap inner wheel - A/C side
* 
* sampling         0                both presamplers
* "                [1,3]            barrel and endcap outer wheel 
* "                [1,2]            endcap inner wheel
* 
* region           0                both presamplers
* "                [0,1]            barrel sampling 1 and 2 
* "                0                barrel sampling 3
* "
* "                [0,5]            endcap outer wheel sampling 1
* "                0                endcap inner wheel sampling 1
* "                [0,1]            endcap outer wheel sampling 2
* "                0                endcap inner wheel sampling 2
* "                0                endcap outer wheel sampling 3
* 
* 
* eta for barrel   [0,60]         presampler - 0< eta <1.52 - deta is approximately equal to 0.025
* "                [0,447]        sampling 1 region 0  0   < eta < 1.4   - deta = 0.025/8 
* "                [0,2]          sampling 1 region 1  1.4 < eta < 1.475 - deta = 0.025
* "                [0,55]         sampling 2 region 0  0   < eta < 1.4   - deta = 0.025 
* "                0              sampling 2 region 1  1.4 < eta < 1.475 - deta = 0.075
* "                [0,26]         sampling 3 region 0  0   < eta < 1.35  - deta = 0.050 
* "
* phi for barrel   [0,63]         barrel presampler   - dphi = 0.1
* "                [0,63]         sampling 1 region 0 - dphi = 0.1
* "                [0,255]        sampling 1 region 1 - dphi = 0.025
* "                [0,255]        sampling 2 region 0 - dphi = 0.025
* "                [0,255]        sampling 2 region 1 - dphi = 0.025
* "                [0,255]        sampling 3 region 0 - dphi = 0.025
* 
* number of cells in barrel :
* presampler :  7808
* sampling 1 : 58752
* sampling 2 : 29184
* sampling 3 : 13824
* total      :109568
* 
* eta for endcap   [0,11]      presampler  sampling 0 region 0  1.5   < eta < 1.8   - deta = 0.025
* "                0           outer wheel sampling 1 region 0  1.375 < eta < 1.425 - deta = 0.05  
* "                [0,2]       outer wheel sampling 1 region 1  1.425 < eta < 1.5   - deta = 0.025
* "                [0,95]      outer wheel sampling 1 region 2  1.5   < eta < 1.8   - deta = 0.025/8
* "                [0,47]      outer wheel sampling 1 region 3  1.8   < eta < 2.0   - deta = 0.025/6
* "                [0,63]      outer wheel sampling 1 region 4  2.0   < eta < 2.4   - deta = 0.025/4 
* "                [0,3]       outer wheel sampling 1 region 5  2.4   < eta < 2.5   - deta = 0.025
* "                [0,6]       inner wheel sampling 1 region 0  2.5   < eta < 3.2   - deta = 0.1
* "                0           outer wheel sampling 2 region 0  1.375 < eta < 1.425 - deta = 0.05
* "                [0,42]      outer wheel sampling 2 region 1  1.425 < eta < 2.5   - deta = 0.025
* "                [0,6]       inner wheel sampling 2 region 0  2.5   < eta < 3.2   - deta = 0.1
* "                [0,19]      outer wheel sampling 3 region 0  1.5   < eta < 2.5   - deta = 0.05 
* 
* phi for endcap   [0,63]      presampler  sampling 0 region 0       - dphi = 0.1
* "                [0,63]      outer wheel sampling 1 regions [0,5]  - dphi = 0.1 
* "                [0,63]      inner wheel sampling 1 region  0      - dphi = 0.1 
* "                [0,255]     outer wheel sampling 2 regions [0,1]  - dphi = 0.025
* "                [0,63]      inner wheel sampling 2 region 0       - dphi = 0.1
* "                [0,255]     outer wheel sampling 3 region 0       - dphi = 0.025
* 
* number of cells in endcap :
* presampler  :  1536
* Outer wheel:
* sampling 1  : 27648
* sampling 2  : 22528
* sampling 3  : 10240
* total       : 60416
* Inner wheel:
* sampling 1  :   896
* sampling 2  :   896
* total       :  1792
* 
* Grand Total : 63744     
'''

PIDS = {
   11:'electron',
   12:'electronneutrino',
   13:'muon',
   14:'muonneutrino',
   15:'tau',
   16:'tauneutrino',

   21:'gluon',
   22:'photon',

   1:'up',
   2:'down',
   3:'strange',
   4:'charm',
   5:'bottom',
   6:'top',
}

LEP_JET={
   11:'lepton',
   12:'leptonneutrino',
   13:'lepton',
   14:'leptonneutrino',
   15:'lepton',
   16:'leptonneutrino',

   21:'jet',
   22:'photon',

   1:'jet',
   2:'jet',
   3:'jet',
   4:'jet',
   5:'jet',
   6:'jet',
}


def main():
   ''' convert root to hdf5 '''
   logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s:%(name)s:%(message)s')

   parser = optparse.OptionParser(description='')
   parser.add_option('-i','--input',dest='input',help='glob input for files,use quotes')
   
   parser.add_option('-n','--njets',dest='njets',default=2,help='set this value to the number of jets in the sample being processed')
   options,args = parser.parse_args()
   

   file_counters_per_pid = {}
   for pid,name in LEP_JET.iteritems():
      file_counters_per_pid[name] = 0
   
   manditory_args = [
                     'input',
                  ]

   for man in manditory_args:
      if options.__dict__[man] is None:
         logger.error('Must specify option: ' + man)
         parser.print_help()
         sys.exit(-1)
   
   filelist = glob.glob(options.input)

   cantile = ROOT.TCanvas('cantile','cantile',0,0,800,600)
   canlar = ROOT.TCanvas('canlar','canlar',0,0,800,600)
   
   tree = ROOT.TChain('calocells')
   for file in filelist:
      tree.AddFile(file)

   max_eta = 1.5
   netabins = 60

   nphibins = 64
   max_phi = numpy.pi
   min_phi = -numpy.pi
   
   #rootfile = ROOT.TFile(options.input)
   #tree = rootfile.Get('calocells')
   num_events = tree.GetEntries()
   logger.info('number of events: %i',num_events)
   
   event_number = 0
   for event in tree:
      event_number += 1
      #if event_number % 100 == 0:
      logger.info('event %d of %d',event_number,num_events)
      leptons = []
      logger.debug('n particles: %10i',event.n_truthparticles)
      particles = []
      
      # find the electron/positron
      # keep a list of all the status == 3 particles
      for pid,peta,pphi,ppt,pstat in zip(event.particle_id,
                                         event.particle_eta,
                                         event.particle_phi,
                                         event.particle_pt,
                                         event.particle_status):
         
         
         if pstat == 3 and numpy.fabs(peta) < max_eta:
            if numpy.fabs(pid) in [11,13,15]:
               logger.info('lepton>> %5i %12.4f %12.4f %5.1f %7i ',pid,peta,pphi,ppt,pstat)
               leptons.append({'id':pid,'eta':peta,'phi':pphi,'pt':ppt,'r':numpy.sqrt(peta*peta+pphi*pphi)})
         
            elif numpy.fabs(pid) in (range(1,9) + [21]):
               logger.debug('o>> %5i %12.4f %12.4f %5.1f %7i ',pid,peta,pphi,ppt,pstat)
               particles.append({'eta':peta,'phi':pphi,'pt':ppt,'id':pid,'r':numpy.sqrt(peta*peta+pphi*pphi)})
            else:
               logger.debug('x>> %5i %12.4f %12.4f %5.1f %7i ',pid,peta,pphi,ppt,pstat) 
      
      if len(leptons) == 0:
         logger.info('no leptons')
         continue
            
      
      # list all the jets, eliminate them if they overlap with electron/positron
      jets = []
      for jeta,jphi,jpt,jm in zip(event.tjet_eta,
                                  event.tjet_phi,
                                  event.tjet_pt,
                                  event.tjet_m):
         # eliminate jets that over lap with elections
         jr = numpy.sqrt( jeta*jeta + jphi*jphi )
         overlaps = False
         for lep in leptons:
            if numpy.fabs( jr - lep['r']) < 0.4:
               overlaps = True
         if not overlaps and numpy.fabs(jeta) < max_eta:
            logger.info('jets>> %5s %6.4f %6.4f %5.1f ',' ',jeta,jphi,jpt)
            jets.append({'eta':jeta,'phi':jphi,'pt':jpt,'r':numpy.sqrt(jeta*jeta+jphi*jphi)})
      
      if len(jets) == 0:
         logger.info('no jets')
         continue

      # loop to match jet to parton
      dr_max = 0.4
      dpt = 5
      jet_particle_match = []
      for particle in particles:
         logger.debug('p>> %5s %6.4f %6.4f %5.1f ',particle['id'],particle['eta'],particle['phi'],particle['pt'])
         candidates = []
         pt_max_index = -1
         pt_max = 0
         for jet in jets:
            etadiff = jet['eta'] - particle['eta']
            phidiff = jet['phi'] - particle['phi']
            dr = numpy.sqrt( etadiff*etadiff + phidiff*phidiff )
            if dr < dr_max:
               logger.debug('j>> %5s %6.4f %6.4f %5.1f ',' ',jet['eta'],jet['phi'],jet['pt'])
               candidates.append(jet)
               if jet['pt'] > pt_max:
                  pt_max_index = len(candidates)
                  pt_max = jet['pt']

         if len(candidates) == 1:
            jet_particle_match.append({'jet':candidates[0],'particle':particle})
         elif len(candidates) == 0:
            logger.warning('there are no matching jets')
         else:
            logger.warning('there are more than one jets that match this particle')
            jet_particle_match.append({'jet':candidates[pt_max_index],'particle':particle})
      
      truth_data = leptons
      
      logger.info(' jet_particle_match n = %i',len(jet_particle_match))
      for match in jet_particle_match:
         p = match['particle']
         j = match['jet']
         logger.info('>>><<<')
         logger.info('particle: %6.3f %6.3f %5.1f %3d',p['eta'],p['phi'],p['pt'],p['id'])
         logger.info('jet:      %6.3f %6.3f %5.1f ',j['eta'],j['phi'],j['pt'])
         j['id'] = p['id']
         j['truth_pt'] = p['pt']
         
         truth_data.append(j)
      

      # remove objects not inside the eta window defined by max_eta
      logger.debug('truth objects before eta range cut: %i',len(truth_data))
      new_truth_data = []
      for truthobj in truth_data:
         if numpy.fabs(truthobj['eta']) < 1.5:
            new_truth_data.append(truthobj)
      truth_data = new_truth_data
      logger.debug('truth objects after eta range cut: %i',len(truth_data))
      if len(truth_data) == 0: continue

      # create histogram for human eyes
      
      lar2dhist = ROOT.TH2D('lar2dhist','Liquid Argon Calo Cell E_{T};#eta;#phi',netabins,-max_eta,max_eta,nphibins,min_phi,max_phi)
      
      tile2dhist = ROOT.TH2D('tile2dhist','Tile Calo Cell E_{T};#eta;#phi',netabins,-max_eta,max_eta,nphibins,min_phi,max_phi)
         
         

      #ecal_data = numpy.zeros((netabins,nphibins),dtype=numpy.float16)
      for i in xrange(event.lar_n_cells):
         
         ecal_eta       = event.lar_eta[i]
         ecal_phi       = event.lar_phi[i]
         ecal_Et        = event.lar_Et[i]
         ecal_x         = event.lar_x[i]
         ecal_y         = event.lar_y[i]
         ecal_z         = event.lar_z[i]
         ecal_bad_cell  = event.lar_bad_cell[i]
         ecal_barrel_ec = event.lar_barrel_ec[i]
         ecal_sampling  = event.lar_sampling[i]
         ecal_region    = event.lar_region[i]
         ecal_hw_eta    = event.lar_hw_eta[i]
         ecal_hw_phi    = event.lar_hw_phi[i]
         
         if ecal_Et > 0.5:
            lar2dhist.Fill(ecal_eta,ecal_phi,ecal_Et)
         
      for i in xrange(event.tile_n_cells):
         
         tile_eta       = event.tile_eta[i]
         tile_phi       = event.tile_phi[i]
         tile_Et        = event.tile_Et[i]
         tile_x         = event.tile_x[i]
         tile_y         = event.tile_y[i]
         tile_z         = event.tile_z[i]
         tile_bad_cell  = event.tile_bad_cell[i]
         tile_section   = event.tile_section[i]
         tile_module    = event.tile_module[i]
         tile_tower     = event.tile_tower[i]
         tile_sample    = event.tile_sample[i]

         if tile_Et > 0.5:
            tile2dhist.Fill(tile_eta,tile_phi,tile_Et)
                 
      cantile.cd() 
      tile2dhist.Draw('colz')
      cantile.SaveAs('tile2dhist.png')
         
      
      canlar.cd()
      lar2dhist.Draw('colz')
      canlar.SaveAs('lar2dhist.png')
      sys.stdout.flush()
      raw_input('...')
      
   



if __name__ == "__main__":
   main()

