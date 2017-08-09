#!/usr/bin/env python2.7
import os,sys,optparse,logging,numpy,ROOT,json,glob
ROOT.gStyle.SetOptStat(0)
#import tensorflow as tf
logger = logging.getLogger(__name__)

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
   parser.add_option('-i','--input',dest='input',help='glob input for files,use quotes, should only be globbing for the data files. json files will be assumed')
   
   options,args = parser.parse_args()
   
   
   manditory_args = [
                     'input',
                  ]

   for man in manditory_args:
      if options.__dict__[man] is None:
         logger.error('Must specify option: ' + man)
         parser.print_help()
         sys.exit(-1)
   
   filelist = glob.glob(options.input)

   ecal_can = ROOT.TCanvas('cantile','cantile',0,0,800,600)
   hcal_can = ROOT.TCanvas('canlar','canlar',0,0,800,600)
  

   max_eta = 1.5
   netabins = 60
   etabinsize = 2.*max_eta / netabins

   nphibins = 64
   max_phi = numpy.pi
   min_phi = -numpy.pi
   phibinsize = 2. * ( max_phi - min_phi ) / nphibins
   
     
   event_number = 0
   for datafile in filelist:
      image = numpy.fromfile(open(datafile))
      image = image.reshape(60,64,2)

      truth = json.load(open(datafile.replace('.data','.json')))

      ecal_hist = ROOT.TH2D('ecal',';#eta;#phi',netabins,-max_eta,max_eta,nphibins,min_phi,max_phi)
      hcal_hist = ROOT.TH2D('hcal',';#eta;#phi',netabins,-max_eta,max_eta,nphibins,min_phi,max_phi)

      for etabin in xrange(netabins):
         eta = etabin * etabinsize - max_eta
         for phibin in xrange(nphibins):
            phi = phibin * phibinsize + min_phi
            ecal_hist.Fill(eta,phi,image[etabin][phibin][0])
            hcal_hist.Fill(eta,phi,image[etabin][phibin][1])
      
      ecal_can.cd()
      ecal_hist.Draw('colz')
      
      for p in truth:
         x1 = 1.*(p['eta']+max_eta)/float(netabins)
         y1 = 1.*(p['phi']-min_phi)/float(nphibins)
         logger.info(str(p))
         r1 = 0.1
         r2 = 0.2
         p['el'] = ROOT.TEllipse(p['eta'],p['phi'],r1,r2)
         p['el'].SetFillStyle(0)
         p['el'].Draw('same')
      
      ecal_can.Update()
      hcal_can.cd()
      hcal_hist.Draw('colz')
 
      for p in truth:
         x1 = 1.*(p['eta']+max_eta)/float(netabins)
         y1 = 1.*(p['phi']-min_phi)/float(nphibins)
         logger.info(str(p))
         r1 = 0.1
         r2 = 0.2
         p['el'] = ROOT.TEllipse(p['eta'],p['phi'],r1,r2)
         p['el'].SetFillStyle(0)
         p['el'].Draw('same')
      

      hcal_can.Update()
      
      #break
      raw_input('...')
      
            



if __name__ == "__main__":
   main()

