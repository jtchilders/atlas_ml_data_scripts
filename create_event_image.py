#!/usr/bin/env python
import os,sys,optparse,logging,numpy,ROOT,json,glob,time,copy
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
   ''' convert root events to numpy arrays '''
   logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s:%(name)s:%(message)s')

   parser = optparse.OptionParser(description='')
   parser.add_option('-g','--glob-string',dest='glob_string',help='glob input for files,use quotes; "/path/to/files/*.root" ')
   parser.add_option('-n','--nimages',dest='nimages',help='number of images per numpy data file',type='int',default=100)
   parser.add_option('-o','--output-path',dest='output_path',default='.',help='path where to output numpy data')
   parser.add_option('-j','--njets',dest='njets',type='int',default=2,help='number of jets in the sample, used for jet-parton matching')
   parser.add_option('--max-eta',dest='max_eta',type='float',help='maximum fabs(eta) to include',default=1.5)
   parser.add_option('--deta',dest='deta',type='float',help='eta bin size',default=0.05)
   parser.add_option('--dphi',dest='dphi',type='float',help='phi bin size',default=2.*numpy.pi/64.)
   parser.add_option('--minE',dest='minE',type='float',help='minimum energy deposit to include in image',default=0.1)
   parser.add_option('--jl-overlap',dest='jl_overlap',type='float',help='jet-lepton overlap removal exclusion radius',default=0.4)
   parser.add_option('--dr_match',dest='dr_match',type='float',help='parton-jet overlap match radius',default=0.4)
   options,args = parser.parse_args()
   

   file_counters_per_pid = {}
   for pid,name in LEP_JET.iteritems():
      file_counters_per_pid[name] = 0
   
   manditory_args = [
                     'glob_string',
                     'nimages',
                     'output_path',
                     'njets',
                     'max_eta',
                     'deta',
                     'dphi',
                     'minE',
                     'jl_overlap',
                     'dr_match',
                  ]

   for man in manditory_args:
      if options.__dict__[man] is None:
         logger.error('Must specify option: ' + man)
         parser.print_help()
         sys.exit(-1)
   
   filelist = sorted(glob.glob(options.glob_string))

   logger.info('processing %s files',len(filelist))

   
   tree = ROOT.TChain('calocells')
   for file in filelist:
      tree.AddFile(file)

   num_events = tree.GetEntries()

   logger.info('number of events: %i',num_events)
   logger.info('images per output file: %d',options.nimages)
   logger.info('njets:        %d',options.njets)
   logger.info('max eta:      %5.2f',options.max_eta)
   logger.info('deta:         %5.2f',options.deta)
   logger.info('dphi:         %5.2f',options.dphi)
   logger.info('minE:         %5.2f',options.minE)
   logger.info('jl overlap:   %5.2f',options.jl_overlap)
   logger.info('dr match:     %5.2f',options.dr_match)

   netabins = int( options.max_eta / options.deta * 2. )
   min_eta = -1.*options.max_eta
   nphibins = int( 2. * numpy.pi / options.dphi )

   logger.info('eta bins:     %5.2f',netabins)
   logger.info('phi bins:     %5.2f',nphibins)
            

   event_number = 0
   output_events = []
   output_truth = []
   output_ids = []
   file_counter = 0
   for event in tree:
      event_number += 1
      logger.info('particle %d of %d',event_number,num_events)

      partons,leptons,jets = get_objects(event,options.jl_overlap)
      logger.debug('partons: %s',len(partons))
      #for obj in partons:
      #   logger.debug('  %10s%10.2f%10.2f%10.2f',obj['pid'],obj['eta'],obj['phi'],obj['pt'])

      partons = partons[-options.njets:]

      logger.debug('leptons: %s',len(leptons))
      #for obj in leptons:
      #   logger.debug('  %10s%10.2f%10.2f%10.2f',obj['pid'],obj['eta'],obj['phi'],obj['pt'])
      logger.debug('jets: %s',len(jets))

      matches = match_jets_partons(partons,jets,options.njets,options.dr_match)
      logger.debug('matches: %s',len(matches))
      #for obj in matches:
      #   logger.debug('  %10s%10.2f%10.2f%10.2f',obj['parton']['pid'],obj['jet']['eta'],obj['jet']['phi'],obj['jet']['pt'])

      truth_objects = []

      # skip events with leptons outside max eta
      outside_max_eta = False
      for lepton in leptons:
         if numpy.fabs(lepton['eta']) > options.max_eta:
            outside_max_eta = True
            break
         truth_objects.append([lepton['pid'],lepton['eta'],lepton['phi'],lepton['pt']])
      if outside_max_eta: 
         logger.info('event contains leptons outside max eta %s. Skipping event',options.max_eta)
         continue

      # skip events with match jets outside eta
      for match in matches:
         if numpy.fabs(match['jet']['eta']) > options.max_eta:
            outside_max_eta = True
            break
         truth_objects.append([match['parton']['pid'],match['jet']['eta'],match['jet']['phi'],lepton['pt']])
      if outside_max_eta:
         logger.info('event contains jets outside max eta %s. Skipping event',options.max_eta)
         continue
      
      
      # now create the output image with 2 channels
      output_event = numpy.zeros((2,netabins,nphibins))
      
      
      logger.debug('n lar cells: %10i',event.lar_n_cells)


      #ecal_data = numpy.zeros((netabins,nphibins),dtype=numpy.float16)
      #start = time.clock()
      for i in xrange(event.lar_n_cells):
         
         ecal_eta                      = event.lar_eta[i]
         ecal_phi                      = event.lar_phi[i]
         ecal_Et                       = event.lar_Et[i]
         ecal_x                        = event.lar_x[i]
         ecal_y                        = event.lar_y[i]
         ecal_z                        = event.lar_z[i]
         ecal_bad_cell                 = event.lar_bad_cell[i]
         ecal_barrel_ec                = event.lar_barrel_ec[i]
         ecal_sampling                 = event.lar_sampling[i]
         ecal_region                   = event.lar_region[i]
         ecal_hw_eta                   = event.lar_hw_eta[i]
         ecal_hw_phi                   = event.lar_hw_phi[i]
         ecal_is_em                    = event.lar_is_em[i]
         ecal_is_em_barrel             = event.lar_is_em_barrel[i]
         ecal_is_em_endcap             = event.lar_is_em_endcap[i]
         ecal_is_em_endcap_inner       = event.lar_is_em_endcap_inner[i]
         ecal_is_em_endcap_outer       = event.lar_is_em_endcap_outer[i]
         ecal_is_hec                   = event.lar_is_hec[i]
         ecal_is_fcal                  = event.lar_is_fcal[i]

         
         if min_eta <= ecal_eta and ecal_eta <= options.max_eta and ecal_Et > options.minE:
            channel = 0 # em channel
            if ecal_is_hec:
               channel = 1 # had channel
            etabin = int((ecal_eta + options.max_eta) / options.deta)
            phibin = int((ecal_phi + numpy.pi + 0.0001) / options.dphi)
            output_event[channel][etabin][phibin] += ecal_Et
            #print ecal_eta,etabin,ecal_phi,phibin
      #logger.info('time: %s',time.clock() - start)

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

         if min_eta <= tile_eta and tile_eta <= options.max_eta and tile_Et > options.minE:
            etabin = int((tile_eta + options.max_eta) / options.deta)
            phibin = int((tile_phi + numpy.pi + 0.0001) / options.dphi)
            output_event[1][etabin][phibin] += tile_Et

      
      output_events.append(output_event)
      output_truth.append(truth_objects)
      output_ids.append(event.event_number)
      logger.info('events collected: %8i %8i',len(output_events),len(output_truth))
      
      if len(output_events) >= options.nimages:
         
         filename = get_output_filename(options.output_path,filelist,file_counter)
         file_counter += 1
         
         logger.info(' writing file: %s',filename)
         numpy.savez_compressed(filename,event_images=output_events,output_truth=output_truth,event_ids=output_ids)

         output_events = []
         output_truth = []

   filename = get_output_filename(options.output_path,filelist,file_counter)
   file_counter += 1
   
   logger.info(' writing file: %s',filename)
   numpy.savez_compressed(filename,event_images=output_events,output_truth=output_truth,event_ids=output_ids)

   output_events = []

   logger.info(' processed %s events',event_number)
  

def get_output_filename(path,filelist,file_counter):
   return path + '/%s_%08d.npz' %(os.path.basename(filelist[0]),file_counter)
   
def get_objects(event,drlj = 0.4):


   # find the electron/positron
   # keep a list of all the status == 3 particles
   partons = []
   leptons = []
   for pid,peta,pphi,ppt,pstat in zip(event.particle_id,
                                      event.particle_eta,
                                      event.particle_phi,
                                      event.particle_pt,
                                      event.particle_status):

      if pstat == 3:
         if is_parton(pid):
            r = numpy.array([peta,pphi])
            partons.append({'pid':pid,'eta':peta,'phi':pphi,'pt':ppt, 'r':r})
         elif is_lepton(pid):
            r = numpy.array([peta,pphi])
            leptons.append({'pid':pid,'eta':peta,'phi':pphi,'pt':ppt, 'r':r})
   
   jets = []
   for jeta,jphi,jpt,jm in zip(event.tjet_eta,
                               event.tjet_phi,
                               event.tjet_pt,
                               event.tjet_m):
      # eliminate jets that over lap with elections
      jr = numpy.array([jeta,jphi])
      overlap = False
      for lepton in leptons:
         if numpy.linalg.norm(jr - lepton['r']) < drlj:
            overlap = True
            break
      if not overlap:
         jets.append({'eta':jeta,'phi':jphi,'pt':jpt,'m':jm,'r':jr})

   return partons,leptons,jets

def match_jets_partons(partons,jets,njets,dr_match=0.4):

   matches = []
   for parton in partons:
      matched_jets = []
      for jet in jets:
         dr = numpy.linalg.norm(jet['r'] - parton['r'])
         if dr < dr_match:
            matched_jets.append(jet)
      
      if len(matched_jets) > 1:
         highest_pt = 0
         highest_index = -1
         for i in range(len(matched_jets)):
            if matched_jets[i]['pt'] > highest_pt:
               highest_pt = matched_jets[i]['pt']
               highest_index = i

         jet = matched_jets[highest_index]
         matches.append({'parton':parton,'jet':jet})
      elif len(matched_jets) == 1:
         jet = matched_jets[0]
         matches.append({'parton':parton,'jet':jet})
   
   newmatches = []
   if len(matches) > njets:
      # keep the highest njets in pt
      newlist = sorted(matches, key=lambda k: k['jet']['pt'])
      newmatches = newlist[:njets]
      matches = newmatches

         
   return matches

      



def is_lepton(pid):
   tpid = numpy.fabs(pid)
   if tpid in [11,13,15]:
      return True
   return False

def is_parton(pid):
   tpid = numpy.fabs(pid)
   if tpid == 21 or tpid <= 6:
      return True
   return False

if __name__ == "__main__":
   main()

