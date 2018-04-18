#!/usr/bin/env python
import os,sys,optparse,logging,glob,subprocess
logger = logging.getLogger(__name__)

sys.path.append('/users/hpcusers/svn/tools/python/athena/')
import athena_condor_job

def main():
   logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s:%(name)s:%(message)s')

   parser = optparse.OptionParser(description='')
   parser.add_option('-i','--input',dest='input',help='input')
   parser.add_option('-o','--output-path',dest='output_path',help='output path',default='')
   options,args = parser.parse_args()

   
   manditory_args = [
                     'input',
                  ]

   for man in manditory_args:
      if options.__dict__[man] is None:
         logger.error('Must specify option: ' + man)
         parser.print_help()
         sys.exit(-1)
   HITSfilenames = glob.glob(options.input)

   # remove partial transfers
   new_list = []
   for file in HITSfilenames:
      if 'part' in file:
         continue
      else:
         new_list.append(file)
   HITSfilenames = new_list

   logger.info('number input files: %s',len(HITSfilenames))

   existingESDFilenames = glob.glob(options.output_path + '/ESD.*')

   logger.info('existing output files: %s',len(existingESDFilenames))

   # remove already transferred files
   for existingESDFilename in existingESDFilenames:
      try:
         HITSfilenames.remove(os.path.join(os.path.dirname(HITSfilenames[0]),os.path.basename(existingESDFilename).replace('ESD','HITS')))
      except ValueError:
         pass

   logger.info('number of input files after skimming: %s',len(HITSfilenames))

   # -r -x "--inputHITSFile=/users/hpcusers/dumpCaloCells/mc15_13TeV.361700.AlpgenPythiaEvtGen_P2012_ZeeNp0.simul.HITS.e4721_s2726/HITS.07356308._011390.pool.root.1 --outputESDFile=ESD.07356308._011390.pool.root.1 --conditionsTag=default:OFLCOND-MC15c-SDR-09 --geometryVersion=default:ATLAS-R2-2015-03-01-00 --digiSteeringConf=StandardSignalOnlyTruth" -j "20.7.5.1,AtlasProduction,here" -i /users/hpcusers/dumpCaloCells/mc15_13TeV.361700.AlpgenPythiaEvtGen_P2012_ZeeNp0.simul.HITS.e4721_s2726/HITS.07356308._011390.pool.root.1 -o ESD.07356308._011390.pool.root.1

   for HITSfilename in HITSfilenames:
      
      ESDfilename = os.path.basename(HITSfilename).replace('HITS','ESD')
      transfer_output = ''
      #if options.output_path != '':
      #   ESDfilename = os.path.join(options.output_path,ESDfilename)
      #else:
      transfer_output = ESDfilename

      transfer_output_remaps = { 'log.HITtoRDO':HITSfilename + '.log.HITtoRDO',
                                 'log.RDOtoESD':HITSfilename + '.log.RDOtoESD',
                                }


      athena_condor_job.athena_condor_job(
         'Reco_tf.py',
         '--inputHITSFile=' + os.path.basename(HITSfilename) + ' --outputESDFile=' + ESDfilename,
         '20.7.5.1,AtlasProduction,here',
         athena_condor_job.ATLASLocalRootBase,
         HITSfilename,
         transfer_output,
         os.path.basename(HITSfilename) + '.Reco_tf_script.sh',
         os.path.basename(HITSfilename) + '.condor_submit.txt',
         os.path.basename(HITSfilename) + '.stdout',
         os.path.basename(HITSfilename) + '.stderr',
         os.path.basename(HITSfilename) + '.condorlog',
         transfer_output_remaps,
         )

      



if __name__ == "__main__":
   main()
