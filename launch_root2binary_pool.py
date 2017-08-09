#!/usr/bin/env python
import os,sys,optparse,logging,glob,subprocess
import multiprocessing,itertools
import root2binary_v2
logger = logging.getLogger(__name__)

def main():
   logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s:%(name)s:%(message)s')

   parser = optparse.OptionParser(description='')
   parser.add_option('-i','--input',dest='input',help='input ROOT files glob "/path/to/files/ROOT*" ')
   parser.add_option('-o','--output-path',dest='output_path',help='output path',default='')
   parser.add_option('-n','--njets',dest='njets',default=2,help='the number of jets in this sample')
   options,args = parser.parse_args()

   
   manditory_args = [
                     'input',
                     'output_path',
                     'njets',
                  ]

   for man in manditory_args:
      if options.__dict__[man] is None:
         logger.error('Must specify option: ' + man)
         parser.print_help()
         sys.exit(-1)
   
   ROOTfilenames = glob.glob(options.input)

   # remove partial transfers
   new_list = []

   for file in ROOTfilenames:
      if 'part' in file:
         continue
      else:
         new_list.append((file,options.output_path,options.njets))
   ROOTfilenames = new_list

   logger.info('number input files: %s',len(ROOTfilenames))
   logger.info('   %s',ROOTfilenames[0])
   
   output = []
   njets = []
   for file in ROOTfilenames:
      output.append(options.output_path)
      njets.append(options.njets)
   

   pool = multiprocessing.Pool(5)

   

   result = pool.map(root2binary_v2.create_images,ROOTfilenames)
   
   print result

      



if __name__ == "__main__":
   main()
