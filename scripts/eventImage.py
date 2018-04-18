#!/usr/bin/env python
import os,sys,optparse,logging,numpy,ROOT,json,glob
import sys
sys.path.append("modules/")
import math

from AtlasStyle import *
from AtlasUtils import *

gROOT.Reset()
gStyle.SetOptStat(111111)
gROOT.SetStyle("ATLAS");



def main():
  logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s:%(name)s:%(message)s')

  parser = optparse.OptionParser(description='')
  parser.add_option('-ih','--inputhits',dest='inputhits',default="run/"help='glob input for hits files,use quotes')
  parser.add_option('-ic','--inputcalo',dest='inputcalo',help='glob input for calo files,use quotes')
  parser.add_option('-p','--plot',dest='plot',action='store_true',default=False,help='plot raw data')
  parser.add_option('--plot3d',dest='plot3d',action='store_true',default=False,help='plot the 3D layout of the calos. This will only run once, present the 3D plot, then exit after a button is pressed.')
  parser.add_option('-o','--output-path',dest='output_path',default='.',help='path where to output data')
  parser.add_option('-n','--njets',dest='njets',default=2,help='set this value to the number of jets in the sample being processed')
  parser.add_option('--img-deta',dest='image_deta',default=0.3,help='the width of the cropped image of 1 particle measured in eta.')
  parser.add_option('--img-dphi',dest='image_dphi',default=0.3,help='the height of the cropped image of 1 particle measured in phi.')
  options,args = parser.parse_args()

  filelisthits = glob.glob(options.inputhits)
  filelistcalo = glob.glob(options.inputcalo)
  treehits = ROOT.TChain('sihits')
  treecalo = ROOT.TChain('calocells')
  for fileh,filec in filelisthits, filelistcalo:
    treehits.AddFile(fileh)
    treecalo.AddFile(filec)

   num_events = tree.GetEntries()
   logger.info('number of events: %i',num_events)

   
if __name__ == "__main__":
   main()
