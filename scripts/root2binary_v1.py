#!/usr/bin/env python
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
   parser.add_option('-m','--maps',dest='maps',action='store_true',default=False,help='dump calo maps')
   parser.add_option('-p','--plot',dest='plot',action='store_true',default=False,help='plot calorimeter data')
   parser.add_option('--plot3d',dest='plot3d',action='store_true',default=False,help='plot the 3D layout of the calos. This will only run once, present the 3D plot, then exit after a button is pressed.')
   parser.add_option('-o','--output-path',dest='output_path',default='.',help='path where to output data')
   parser.add_option('-n','--njets',dest='njets',default=2,help='set this value to the number of jets in the sample being processed')
   parser.add_option('--img-deta',dest='image_deta',default=0.3,help='the width of the cropped image of 1 particle measured in eta.')
   parser.add_option('--img-dphi',dest='image_dphi',default=0.3,help='the height of the cropped image of 1 particle measured in phi.')
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



   if not options.plot and not options.plot3d:
      ROOT.gROOT.SetBatch()
  
   can = ROOT.TCanvas('can','can',0,0,800,600)
   cand = ROOT.TCanvas('cand','cand',0,0,800,600)
   cand.Divide(2,1)
   can.cd()
   
   tree = ROOT.TChain('calocells')
   for file in filelist:
      tree.AddFile(file)

   #rootfile = ROOT.TFile(options.input)
   #tree = rootfile.Get('calocells')
   num_events = tree.GetEntries()
   logger.info('number of events: %i',num_events)
   
   max_eta = 1.5
   deta = 0.05
   netabins = int(max_eta/deta*2.)
   logger.info(' max eta: %5.2f delta eta: %5.2f eta bins: %5i',max_eta,deta,netabins)
   
   max_phi = 2.*numpy.pi
   dphi = 2.*numpy.pi/64.
   nphibins = 64
   logger.info(' max phi: %5.2f delta phi: %5.2f phi bins: %5i',max_phi,dphi,nphibins)

   image_eta_width = 1.0
   image_phi_height = dphi * 10.
   image_eta_bins = int(image_eta_width / deta)
   image_phi_bins = int(image_phi_height / dphi)
   logger.info('image size = %d x %d',image_eta_bins,image_phi_bins)
   logger.info('image eta width: %f    image phi height: %f',image_eta_width,image_phi_height)
   
   
   drlj = 0.3
   min_energy = 0.1

   # data array [event number, eta bin, phi bin, em(0) / had(1) calo layer ]
   #data_chunk_size = 10
   #h5ds = outfile.create_dataset('calocells',(0,2,netabins,nphibins),
                                 #chunks=(data_chunk_size,2,netabins,nphibins),
   #                              dtype=numpy.float16,
   #                              maxshape=(None,2,netabins,nphibins))
   #print 'dataset shape:',h5ds.shape                           

   dump_ecal = False
   dump_hcal = False
   #evtnum = 0
   output_events = []
   output_truth = []
   event_number = 0
   for event in tree:
      event_number += 1
      #if event_number % 100 == 0:
      logger.info('particle %d of %d',event_number,num_events)
      electron = None
      positron = None
      logger.debug('n particles: %10i',event.n_truthparticles)
      particles = []
      can.cd()
      
      # find the electron/positron
      # keep a list of all the status == 3 particles
      for pid,peta,pphi,ppt,pstat in zip(event.particle_id,
                                         event.particle_eta,
                                         event.particle_phi,
                                         event.particle_pt,
                                         event.particle_status):
         
         
         
         if pid == 11 and electron is None:
            logger.debug('e>> %5i %12.4f %12.4f %5.1f %7i ',pid,peta,pphi,ppt,pstat)
            electron = {'id':pid,'eta':peta,'phi':pphi,'pt':ppt,'r':numpy.sqrt(peta*peta+pphi*pphi)}
         elif pid == -11 and positron is None:
            logger.debug('p>> %5i %12.4f %12.4f %5.1f %7i ',pid,peta,pphi,ppt,pstat)
            positron = {'id':pid,'eta':peta,'phi':pphi,'pt':ppt,'r':numpy.sqrt(peta*peta+pphi*pphi)}
         elif pstat == 3 and numpy.fabs(pid) in (range(1,9) + [21]):
            logger.debug('o>> %5i %12.4f %12.4f %5.1f %7i ',pid,peta,pphi,ppt,pstat)
            particles.append({'eta':peta,'phi':pphi,'pt':ppt,'id':pid,'r':numpy.sqrt(peta*peta+pphi*pphi)})
         else:
           logger.debug('x>> %5i %12.4f %12.4f %5.1f %7i ',pid,peta,pphi,ppt,pstat) 
            
      
      # list all the jets, eliminate them if they overlap with electron/positron
      jets = []
      for jeta,jphi,jpt,jm in zip(event.tjet_eta,
                                  event.tjet_phi,
                                  event.tjet_pt,
                                  event.tjet_m):
         # eliminate jets that over lap with elections
         jr = numpy.sqrt( jeta*jeta + jphi*jphi )
         if ( numpy.fabs( jr - electron['r']) > drlj and numpy.fabs( jr - positron['r']) ):
            logger.debug('j>> %5s %6.4f %6.4f %5.1f ',' ',jeta,jphi,jpt)
            jets.append({'eta':jeta,'phi':jphi,'pt':jpt,'r':numpy.sqrt(jeta*jeta+jphi*jphi)})
      
      #logger.debug('electron: %s',electron)
      #logger.debug('positron:%s',positron)

      # remove all but the last njets worth of partons:
      nparticles = len(particles)
      for i in range(nparticles-options.njets):
         del particles[0]

      # loop to match jet to parton
      dr_max = 0.4
      dpt = 5
      jet_particle_match = []
      for particle in particles:
         logger.debug('p>> %5s %6.4f %6.4f %5.1f ',particle['id'],particle['eta'],particle['phi'],particle['pt'])
         candidates = []
         for jet in jets:
            etadiff = jet['eta'] - particle['eta']
            phidiff = jet['phi'] - particle['phi']
            dr = numpy.sqrt( etadiff*etadiff + phidiff*phidiff )
            if dr < dr_max:
               logger.debug('j>> %5s %6.4f %6.4f %5.1f ',' ',jet['eta'],jet['phi'],jet['pt'])
               candidates.append(jet)

         if len(candidates) == 1:
            jet_particle_match.append({'jet':candidates[0],'particle':particle})
         elif len(candidates) == 0:
            logger.warning('there are no matching jets')
         else:
            logger.warning('there are more than one jets that match this particle')
      
      truth_data = [electron,positron]

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
      
      if len(jet_particle_match) != options.njets:
         logger.warning(' found %d matches but there are %d jets ',len(jet_particle_match),options.njets)
         #continue
      
      # remove objects not inside the eta window defined by max_eta
      logger.debug('truth objects before eta range cut: %i',len(truth_data))
      new_truth_data = []
      for truthobj in truth_data:
         if numpy.fabs(truthobj['eta']) < max_eta:
            new_truth_data.append(truthobj)
      truth_data = new_truth_data
      logger.debug('truth objects after eta range cut: %i',len(truth_data))
      if len(truth_data) == 0: continue



      # now I have all my truth data
      output_truth.append(truth_data)
      
      # now I need to create cropped images of these truth objects
      output_event = numpy.zeros((2,netabins,nphibins))
      
      logger.debug('n lar cells: %10i',event.lar_n_cells)

      # create histogram for human eyes
      if options.plot:
         lar2dhist = ROOT.TH2D('lar2dhist',';#eta,#phi',netabins,-max_eta,max_eta,nphibins,-3.14159,3.14159)
         lar2dmap = ROOT.TGraph()
         lar2dmap.SetName('lar2dmap')
         lar2dmap.SetTitle(';#eta,#phi')
         tile2dhist = ROOT.TH2D('tile2dhist',';#eta,#phi',netabins,-max_eta,max_eta,nphibins,-3.14159,3.14159)
         tile2dmap = ROOT.TGraph()
         tile2dmap.SetName('tile2dmap')
         tile2dmap.SetTitle(';#eta,#phi')
         tile2dmap_section = ROOT.TH2D('tile2dmap_section',';#eta,#phi',1000,-5,5, 64,-numpy.pi,numpy.pi)
         tile2dmap_module = ROOT.TH2D('tile2dmap_module',';#eta,#phi',1000,-5,5, 64,-numpy.pi,numpy.pi)
      if options.plot3d:
         lar3d = ROOT.TGraph2D()
         lar3d.SetName('lar3d')
         lar3d.SetTitle(';x;y;z')
         lar3d.SetMarkerSize(0.3)
         lar3d.SetMarkerStyle(20)
         lar3d.SetMarkerColor(ROOT.kGreen)
         tile3d = ROOT.TGraph2D()
         tile3d.SetName('tile3d')
         tile3d.SetTitle(';x;y;z')
         tile3d.SetMarkerStyle(20)
         tile3d.SetMarkerSize(0.5)
         tile3d.SetMarkerColor(ROOT.kRed)

      if options.maps and not dump_ecal:
         f = open('lar_map.txt','w')
         f.write('%10s %10s %10s %10s %10s  %5s %5s %5s %5s %5s\n' % ('eta','phi','x','y','z','brl_ec','sampl','regn','hweta','hwphi'))

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
            etabin = int((ecal_eta + max_eta) / deta)
            phibin = int((ecal_phi + numpy.pi + 0.0001) / dphi)
            if ecal_Et > min_energy:
               output_event[0][etabin][phibin] += ecal_Et
            #print ecal_eta,etabin,ecal_phi,phibin

         if options.maps and not dump_ecal:
            f.write('%10.4f %10.4f %10.2f %10.2f %10.2f  %5i %5i %5i %5i %5i\n' % (ecal_eta,ecal_phi,ecal_x,ecal_y,ecal_z,ecal_barrel_ec,ecal_sampling,ecal_region,ecal_hw_eta,ecal_hw_phi))

         if options.plot:
            if ecal_Et > min_energy:
               lar2dhist.Fill(ecal_eta,ecal_phi,ecal_Et)
            if ecal_barrel_ec == 1 or ecal_barrel_ec == -1:
               lar2dmap.SetPoint(lar2dmap.GetN()+1,ecal_eta,ecal_phi)
         if options.plot3d:
            if numpy.fabs(ecal_barrel_ec) == 1:
               lar3d.SetPoint(lar3d.GetN(),ecal_x,ecal_y,ecal_z)

         
      if options.maps and not dump_ecal:
         f.close()
         dump_ecal = True

      if options.plot:
         lar2dhist.Draw('colz')
         can.SaveAs('lar2dhist.png')
         #raw_input('press enter...')
         lar2dmap.Draw('ap')
         can.SaveAs('lar2dmap.png')
         #raw_input('press enter...')
      
      logger.debug('n tile cells: %10i',event.tile_n_cells)

      if options.maps and not dump_hcal:
         f = open('tile_map.txt','w')
         f.write('%10.4s %10.4s %10.2s %10.2s %10.2s  %5s %5s %5s %5s\n' % ('eta','phi','x','y','z','sect','mod','tow','sampl'))
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
            etabin = int((tile_eta + max_eta) / deta)
            phibin = int((tile_phi + numpy.pi + 0.0001) / dphi)
            if tile_Et > min_energy: 
               output_event[1][etabin][phibin] += tile_Et

         if options.maps and not dump_hcal:
            f.write('%10.4f %10.4f %10.2f %10.2f %10.2f  %5i %5i %5i %5i\n' % (tile_eta,tile_phi,tile_x,tile_y,tile_z,tile_section,tile_module,tile_tower,tile_sample))
         
         if options.plot:
            if tile_Et > min_energy:
               tile2dhist.Fill(tile_eta,tile_phi,tile_Et)
            tile2dmap.SetPoint(tile2dmap.GetN()+1,tile_eta,tile_phi)
            tile2dmap_section.Fill(tile_eta,tile_phi,tile_section)
            tile2dmap_module.Fill(tile_eta,tile_phi,tile_module)
         if options.plot3d:
            tile3d.SetPoint(tile3d.GetN(),tile_x,tile_y,tile_z)

      if options.maps and not dump_hcal:
         f.close()
         dump_hcal = True
      
      if options.plot:
         tile2dhist.Draw('colz')
         can.SaveAs('tile2dhist.png')
         #raw_input('press enter...')
         tile2dmap.Draw('ap')
         can.SaveAs('tile2dmap.png')
         #raw_input('press enter...')
         tile2dmap_section.Draw('colz')
         can.SaveAs('tile2dmap_section.png')
         #raw_input('press enter...')
         tile2dmap_module.Draw('colz')
         can.SaveAs('tile2dmap_module.png')
         
         cand.cd(1)
         lar2dhist.Draw('colz')
         cand.cd(2)
         tile2dhist.Draw('colz')
         #raw_input('...')

      if options.plot3d:
         can.cd()
         tile3d.Draw('ap')
         lar3d.Draw('p same')
         raw_input('...')
         sys.exit(-1)
      
      output_events.append(output_event)
      logger.debug('events written: %8i',len(output_events))
      
      for obj in truth_data:
         logger.debug('truth obj: %5s %6.4f %6.4f %5.1f ',obj['id'],obj['eta'],obj['phi'],obj['pt'])
         subimg = numpy.zeros((image_eta_bins,image_phi_bins,2),dtype=numpy.float32)
         fpid = numpy.fabs(obj['id'])
         
         obj_etabin = int((obj['eta'] + max_eta) / deta)
         obj_etabin_min = obj_etabin - int(image_eta_bins/2.)
         obj_etabin_max = obj_etabin + int(image_eta_bins/2.)
         
         if obj_etabin_min < 0:
            obj_etabin_max = obj_etabin_max + numpy.fabs(obj_etabin_min)
            obj_etabin_min = 0

         if obj_etabin_max >= netabins:
            obj_etabin_min = obj_etabin_min - (obj_etabin_max - netabins - 1)
            obj_etabin_max = netabins - 1

         obj_phibin = int((obj['phi'] + numpy.pi + 0.0001) / dphi)
         obj_phibin_min = obj_phibin - int(image_phi_bins/2.)
         obj_phibin_max = obj_phibin + int(image_phi_bins/2.)
         
         phibins = range(obj_phibin_min,obj_phibin_max)
         for i in range(len(phibins)):
            bin = phibins[i]
            if bin < 0:
               phibins[i] = nphibins + bin
            elif bin >= nphibins:
               phibins[i] = bin - nphibins


         if obj_phibin_min < 0:
            obj_phibin_max = obj_phibin_max + numpy.fabs(obj_phibin_min)
            obj_phibin_min = 0

         if obj_phibin_max >= nphibins:
            obj_phibin_min = obj_phibin_min - (obj_phibin_max - nphibins - 1)
            obj_phibin_max = nphibins - 1

         logger.debug('obj eta bin: %i %i %i',obj_etabin_min,obj_etabin,obj_etabin_max)
         logger.debug('obj phi bin: %i %s',obj_phibin,str(phibins))

         
         # loop over the whole image to fill the smaller image
         
         for eta_bin in xrange(output_event.shape[1]):
            if obj_etabin_min < eta_bin and eta_bin <= obj_etabin_max:
               subimg_etabin = eta_bin - obj_etabin_min - 1
               for phi_bin in xrange(output_event.shape[2]):
                  if phi_bin in phibins:
                     for layer in xrange(output_event.shape[0]):
                        subimg_phibin = phibins.index(phi_bin)
                        subimg[subimg_etabin][subimg_phibin][layer] = output_event[layer][eta_bin][phi_bin]

         combined_event = [obj,subimg]
         
         filename = options.output_path + '/subimg_%s_n%08d.data' % (LEP_JET[fpid],file_counters_per_pid[LEP_JET[fpid]])
         logger.debug(' writing file: ' + filename)
         f = open(filename,'wb')
         f.write(subimg.tobytes())
         f.close()
         file_counters_per_pid[LEP_JET[fpid]] += 1

         f = open(filename.replace('.data','.json'),'w')
         f.write(json.dumps(obj))
         f.close()

         #raw_input('...')
	 #import numpy as np
         #filename = options.output_path + '/subimg_npy_%s_n%08d.data' % (LEP_JET[fpid],file_counters_per_pid[LEP_JET[fpid]])
         #logger.debug(' writing file: ' + filename)
	 #np.save(filename, subimg)
                  


      #break

   f = open('test.bin','w')
   for event in output_events:
      logger.debug('event size %i',len(event.tobytes()))
      f.write(event.tobytes())
   
   



if __name__ == "__main__":
   main()

