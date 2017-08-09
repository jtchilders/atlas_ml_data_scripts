#!/usr/bin/env python
import os,sys,optparse,logging,glob,json
#sys.path.append('/share/sl6/root/lib')
try:
   sys.path.remove('/users/jchilders/.local/lib/python2.7/site-packages')
except:
   pass
import ROOT
import numpy
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
   11:'electron',
   12:'electronneutrino',
   13:'muon',
   14:'muonneutrino',
   15:'tau',
   16:'tauneutrino',

   21:'jet',
   22:'photon',

   1:'jet',
   2:'jet',
   3:'jet',
   4:'jet',
   5:'jet',
   6:'jet',
}


plot = False

def main():
   ''' convert root to hdf5 '''
   logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s:%(name)s:%(message)s')

   parser = optparse.OptionParser(description='')
   parser.add_option('-i','--input',dest='input',help='input filename')
   parser.add_option('-o','--output-path',dest='output_path',default='.',help='path where to output data')
   parser.add_option('-n','--njets',dest='njets',default=2,help='set this value to the number of jets in the sample being processed')
   options,args = parser.parse_args()
   
   manditory_args = [
                     'input',
                  ]

   for man in manditory_args:
      if options.__dict__[man] is None:
         logger.error('Must specify option: ' + man)
         parser.print_help()
         sys.exit(-1)
   

   create_images([options.input,options.output_path,options.njets])

def create_images(data):
   filename,output_path,njets = data
   logger.info('input filename: %s',filename)
   logger.info('output path:    %s',output_path)
   logger.info('njets:          %s',njets)
   tree = ROOT.TChain('calocells')
   tree.AddFile(filename)

   num_events = tree.GetEntries()
   logger.info('number of events: %i',num_events)
   
   max_eta = 1.5
   netabins = 60
   etabinsize = 2.*max_eta / netabins

   nphibins = 64
   max_phi = numpy.pi
   min_phi = -numpy.pi
   phibinsize = 2. * ( max_phi - min_phi ) / nphibins


   if plot:

      ecal_can = ROOT.TCanvas('ecal_can','ecal_can',100,0,800,600)
      hcal_can  = ROOT.TCanvas('hcal_can','hcal_can',900,0,800,600)
   
   
   file_counter=0
   
   drlj = 0.4
   min_energy = 0.1
                          
   output_events = []
   output_truth = []
   event_number = 0
   for event in tree:
      event_number += 1
      #if event_number % 100 == 0:
      logger.info('particle %d of %d',event_number,num_events)
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
               logger.debug('leptons  >> %5i %12.4f %12.4f %5.1f %7i ',pid,peta,pphi,ppt,pstat)
               leptons.append({'id':pid,'eta':peta,'phi':pphi,'pt':ppt,'r':numpy.sqrt(peta*peta+pphi*pphi)})
            elif numpy.fabs(pid) in (range(1,9) + [21]):
               logger.debug('particle >> %5i %12.4f %12.4f %5.1f %7i ',pid,peta,pphi,ppt,pstat)
               particles.append({'eta':peta,'phi':pphi,'pt':ppt,'id':pid,'r':numpy.sqrt(peta*peta+pphi*pphi)})
            else:
               logger.debug('other    >> %5i %12.4f %12.4f %5.1f %7i ',pid,peta,pphi,ppt,pstat)
      
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
            if numpy.fabs( jr - lep['r'] ) < drlj:
               overlaps = True
         if not overlaps and numpy.fabs(jeta) < max_eta:
            logger.debug('jet    >> %5s %6.4f %6.4f %5.1f ',' ',jeta,jphi,jpt)
            jets.append({'eta':jeta,'phi':jphi,'pt':jpt,'r':numpy.sqrt(jeta*jeta+jphi*jphi)})

      if len(jets) == njets:
         logger.info('no jets')
         continue

      # loop to match jet to parton
      dr_max = 0.2
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
                  pt_max_index = len(candidates) - 1
                  pt_max = jet['pt']

         if len(candidates) == 1:
            jet_particle_match.append({'jet':candidates[0],'particle':particle})
         elif len(candidates) == 0:
            logger.warning('there are no matching jets')
         else:
            logger.warning('there are more than one jets that match this particle %s %s %s',candidates,pt_max_index,pt_max)
            jet_particle_match.append({'jet':candidates[pt_max_index],'particle':particle})
      
      truth_data = leptons

      logger.debug(' jet_particle_match n = %i',len(jet_particle_match))
      for match in jet_particle_match:
         p = match['particle']
         j = match['jet']
         logger.debug('>>><<<')
         logger.debug('particle: %6.3f %6.3f %5.1f %3d',p['eta'],p['phi'],p['pt'],p['id'])
         logger.debug('jet:      %6.3f %6.3f %5.1f ',j['eta'],j['phi'],j['pt'])
         j['id'] = p['id']
         j['truth_pt'] = p['pt']
         truth_data.append(j)

      # now I have all my truth data
      output_truth = truth_data
      
      # now I need to create cropped images of these truth objects
      output_event = numpy.zeros((netabins,nphibins,2))
      
      logger.debug('n lar cells: %10i',event.lar_n_cells)

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
         
         if numpy.fabs(ecal_eta) <= max_eta:
            etabin = int((ecal_eta + max_eta) / etabinsize)
            phibin = int((ecal_phi + numpy.pi + 0.0001) / phibinsize)
            if ecal_Et > min_energy:
               output_event[etabin][phibin][0] += ecal_Et
            #print ecal_eta,etabin,ecal_phi,phibin
      
      logger.debug('n tile cells: %10i',event.tile_n_cells)

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

         if numpy.fabs(tile_eta) < max_eta:
            etabin = int((tile_eta + max_eta) / etabinsize)
            phibin = int((tile_phi + max_phi + 0.0001) / phibinsize)
            if tile_Et > min_energy: 
               output_event[etabin][phibin][1] += tile_Et
      
      
      classname = ''
      for lep in leptons:
         classname += LEP_JET[numpy.fabs(lep['id'])]
      
      tmp_output_path = os.path.join(output_path,classname)
      if not os.path.exists(tmp_output_path):
         os.makedirs(tmp_output_path)
      
      outputfilename = tmp_output_path + '/%s_%s_n%08d.data' % (os.path.basename(filename),classname,file_counter)
      logger.info(' writing file: ' + outputfilename)
      output_event.tofile(outputfilename)
      #f = open(outputfilename,'wb')
      #f.write(output_event.tobytes())
      #f.close()
      file_counter += 1

      f = open(outputfilename.replace('.data','.json'),'w')
      f.write(json.dumps(truth_data))
      f.close()

      ecal_hist = ROOT.TH2D('ecal',';#eta;#phi',netabins,-max_eta,max_eta,nphibins,min_phi,max_phi)
      hcal_hist = ROOT.TH2D('hcal',';#eta;#phi',netabins,-max_eta,max_eta,nphibins,min_phi,max_phi)

      if plot:
         for etabin in xrange(netabins):
            eta = etabin * etabinsize - max_eta
            for phibin in xrange(nphibins):
               phi = phibin * phibinsize + min_phi
               ecal_hist.Fill(eta,phi,output_event[etabin][phibin][0])
               hcal_hist.Fill(eta,phi,output_event[etabin][phibin][1])

         ecal_can.cd()
         ecal_hist.Draw('colz')
         for p in truth_data:
            r1 = 0.1
            r2 = 0.2
            print p
            p['el'] = ROOT.TEllipse(p['eta'],p['phi'],r1,r2)
            p['el'].SetFillStyle(0)
            if numpy.fabs(p['id']) in [11,13,15]:
               p['el'].SetLineColor(ROOT.kRed)
            else:
               p['el'].SetLineColor(ROOT.kGreen)
            p['el'].Draw('same')
         for j in jets:
            r1 = 0.05
            r2 = 0.05
            j['jel'] = ROOT.TEllipse(j['eta'],j['phi'],r1,r2)
            j['jel'].SetFillStyle(0)
            j['jel'].SetLineColor(ROOT.kBlue)
            j['jel'].Draw('same')

         ecal_can.Update()
         hcal_can.cd()
         hcal_hist.Draw('colz')
         for p in truth_data:
            p['el'].Draw('same')
         for j in jets:
            j['jel'].Draw('same')
         hcal_can.Update()


         raw_input('press a key to continue...')
 
   
   



if __name__ == "__main__":
   main()

