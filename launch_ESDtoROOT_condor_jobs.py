#!/usr/bin/env python
import os,sys,optparse,logging,glob,subprocess
logger = logging.getLogger(__name__)

sys.path.append('/users/hpcusers/svn/tools/python/athena/')
import athena_condor_job

def main():
   logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s:%(name)s:%(message)s')

   parser = optparse.OptionParser(description='')
   parser.add_option('-i','--input',dest='input',help='input')
   parser.add_option('-o','--output-path',dest='output_path',help='output path',default='.')

   options,args = parser.parse_args()

   
   manditory_args = [
                     'input',
                  ]

   for man in manditory_args:
      if options.__dict__[man] is None:
         logger.error('Must specify option: ' + man)
         parser.print_help()
         sys.exit(-1)

   ESDfilenames = glob.glob(options.input)

   logger.info('number input files: %d',len(ESDfilenames))

   existingROOTFilenames = glob.glob(options.output_path + '/ROOT.*')

   logger.info('existing output files: %d',len(existingROOTFilenames))

   # remove already transferred files
   for existingROOTFilename in existingROOTFilenames:
      try:
         remove_filename = os.path.join(os.path.dirname(ESDfilenames[0]),os.path.basename(existingROOTFilename).replace('ROOT','ESD'))
         ESDfilenames.remove(remove_filename)
      except ValueError:
         pass

   logger.info('number of input files after skimming: %d',len(ESDfilenames))

   # -r -x "--inputHITSFile=/users/hpcusers/dumpCaloCells/mc15_13TeV.361700.AlpgenPythiaEvtGen_P2012_ZeeNp0.simul.HITS.e4721_s2726/HITS.07356308._011390.pool.root.1 --outputESDFile=ESD.07356308._011390.pool.root.1 --conditionsTag=default:OFLCOND-MC15c-SDR-09 --geometryVersion=default:ATLAS-R2-2015-03-01-00 --digiSteeringConf=StandardSignalOnlyTruth" -j "20.7.5.1,AtlasProduction,here" -i /users/hpcusers/dumpCaloCells/mc15_13TeV.361700.AlpgenPythiaEvtGen_P2012_ZeeNp0.simul.HITS.e4721_s2726/HITS.07356308._011390.pool.root.1 -o ESD.07356308._011390.pool.root.1

   for ESDfilename in ESDfilenames:
      
      ROOTfilename = os.path.basename(ESDfilename).replace('ESD','ROOT')
      
      
      athena_condor_job.athena_condor_job(
         'athena',
         '-c "filelist=[\'' + ESDfilename + '\'];rootFilename=\'' + ROOTfilename + '\'" ' + ' /users/hpcusers/dumpCaloCells/run/runMyAlg.py ',
         '--testarea=/users/hpcusers/dumpCaloCells 20.7.5.1,AtlasProduction',
         athena_condor_job.ATLASLocalRootBase,
         ESDfilename,
         ROOTfilename,
         os.path.basename(ESDfilename) + '.athena_script.sh',
         os.path.basename(ESDfilename) + '.condor_submit.txt',
         os.path.basename(ESDfilename) + '.stdout',
         os.path.basename(ESDfilename) + '.stderr',
         os.path.basename(ESDfilename) + '.condorlog',
         )

      



if __name__ == "__main__":
   main()
