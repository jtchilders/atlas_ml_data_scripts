#!/usr/bin/env python
import os,sys,optparse,logging,h5py,numpy,ROOT
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



def main():
   ''' convert root to hdf5 '''
   logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s:%(name)s:%(message)s')

   parser = optparse.OptionParser(description='')
   parser.add_option('-i','--input',dest='input',help='input')
   parser.add_option('-m','--maps',dest='maps',action='store_true',default=False,help='dump calo maps')
   parser.add_option('-p','--plot',dest='plot',action='store_true',default=False,help='plot calorimeter data')
   parser.add_option('-o','--output',dest='output',default='output.hdf5',help='hdf5 output file name')
   options,args = parser.parse_args()

   
   manditory_args = [
                     'input',
                  ]

   for man in manditory_args:
      if options.__dict__[man] is None:
         logger.error('Must specify option: ' + man)
         parser.print_help()
         sys.exit(-1)
   
   if not options.plot:
      ROOT.gROOT.SetBatch()
   
   outfile = h5py.File(options.output,'w')

   can = ROOT.TCanvas('can','can',0,0,800,600)
   
   rootfile = ROOT.TFile(options.input)
   tree = rootfile.Get('calocells')
   num_events = tree.GetEntriesFast()
   print 'number of events: ',num_events
   
   max_eta = 1.5
   deta = 0.05
   netabins = int(max_eta/deta*2.)
   print ' max eta: %5.2f delta eta: %5.2f eta bins: %5i' % (max_eta,deta,netabins)
   
   max_phi = 2.*numpy.pi
   dphi = 2.*numpy.pi/64.
   nphibins = 64
   print ' max phi: %5.2f delta phi: %5.2f phi bins: %5i' % (max_phi,dphi,nphibins)
   
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
   for event in tree:
      electron = None
      positron = None
      logger.info('n particles: %10i',event.n_truthparticles)
      for pid,peta,pphi,ppt,pstat in zip(event.particle_id,
                                         event.particle_eta,
                                         event.particle_phi,
                                         event.particle_pt,
                                         event.particle_status):

         print '>> %5i %6.4f %6.4f %5.1f %5i ' % (pid,peta,pphi,ppt,pstat)
         
         if pid == 11 and electron is None:
            electron = [peta,pphi,ppt]
         if pid == -11 and positron is None:
            positron = [peta,pphi,ppt]

         #if electron is not None and positron is not None: break
      

      if not(numpy.fabs(electron[0]) <= 1.5 and numpy.fabs(positron[0]) <= 1.5):
         continue

      truth_data = [[11]+electron,[-11]+positron]
      output_truth.append(truth_data)
      output_event = numpy.zeros((2,netabins,nphibins))
         
      logger.info('n lar cells: %10i',event.lar_n_cells)

      # create histogram for human eyes
      if options.plot:
         lar2dhist = ROOT.TH2D('lar2dhist',';#eta,#phi',100,-5,5,64,-3.14159,3.14159)
         lar2dmap = ROOT.TGraph()
         lar2dmap.SetName('lar2dmap')
         lar2dmap.SetTitle(';#eta,#phi')
         tile2dhist = ROOT.TH2D('tile2dhist',';#eta,#phi',100,-5,5,64,-3.14159,3.14159)
         tile2dmap = ROOT.TGraph()
         tile2dmap.SetName('tile2dmap')
         tile2dmap.SetTitle(';#eta,#phi')
         tile2dmap_section = ROOT.TH2D('tile2dmap_section',';#eta,#phi',1000,-5,5,64,-3.14159,3.14159)
         tile2dmap_module = ROOT.TH2D('tile2dmap_module',';#eta,#phi',1000,-5,5,64,-3.14159,3.14159)

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
            output_event[0][etabin][phibin] += ecal_Et
            #print ecal_eta,etabin,ecal_phi,phibin

         if options.maps and not dump_ecal:
            f.write('%10.4f %10.4f %10.2f %10.2f %10.2f  %5i %5i %5i %5i %5i\n' % (ecal_eta,ecal_phi,ecal_x,ecal_y,ecal_z,ecal_barrel_ec,ecal_sampling,ecal_region,ecal_hw_eta,ecal_hw_phi))

         if options.plot:
            if ecal_Et > 1:
               lar2dhist.Fill(ecal_eta,ecal_phi,ecal_Et)
            if ecal_barrel_ec == 1 or ecal_barrel_ec == -1:
               lar2dmap.SetPoint(lar2dmap.GetN()+1,ecal_eta,ecal_phi)
         
      if options.maps and not dump_ecal:
         f.close()
         dump_ecal = True

      if options.plot:
         lar2dhist.Draw('colz')
         can.SaveAs('lar2dhist.png')
         raw_input('press enter...')
         lar2dmap.Draw('ap')
         can.SaveAs('lar2dmap.png')
         raw_input('press enter...')
      
      logger.info('n tile cells: %10i',event.tile_n_cells)

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
            output_event[1][etabin][phibin] += ecal_Et

         if options.maps and not dump_hcal:
            f.write('%10.4f %10.4f %10.2f %10.2f %10.2f  %5i %5i %5i %5i\n' % (tile_eta,tile_phi,tile_x,tile_y,tile_z,tile_section,tile_module,tile_tower,tile_sample))
         
         if options.plot:
            if tile_Et > 1:
               tile2dhist.Fill(tile_eta,tile_phi,tile_Et)
            tile2dmap.SetPoint(tile2dmap.GetN()+1,tile_eta,tile_phi)
            tile2dmap_section.Fill(tile_eta,tile_phi,tile_section)
            tile2dmap_module.Fill(tile_eta,tile_phi,tile_module)

      if options.maps and not dump_hcal:
         f.close()
         dump_hcal = True
      
      if options.plot:
         tile2dhist.Draw('colz')
         can.SaveAs('tile2dhist.png')
         raw_input('press enter...')
         tile2dmap.Draw('ap')
         can.SaveAs('tile2dmap.png')
         raw_input('press enter...')
         tile2dmap_section.Draw('colz')
         can.SaveAs('tile2dmap_section.png')
         raw_input('press enter...')
         tile2dmap_module.Draw('colz')
         can.SaveAs('tile2dmap_module.png')
      
      output_events.append(output_event)
      logger.info('events written: %8i',len(output_events))
   
   calocells = outfile.create_group('calocells')
   truth = outfile.create_group('truth')

   ccdata = calocells.create_dataset('calocelldata',(len(output_events),2,netabins,nphibins),
                                 #chunks=(data_chunk_size,2,netabins,nphibins),
                                 dtype=numpy.float16,
                                 #maxshape=(None,2,netabins,nphibins)
                                 )
   ccdata[...] = output_events

   tdata = truth.create_dataset('truthdata',(len(output_truth),2,4),dtype=numpy.float16)
   tdata[...] = output_truth


   outfile.close()



if __name__ == "__main__":
   main()

