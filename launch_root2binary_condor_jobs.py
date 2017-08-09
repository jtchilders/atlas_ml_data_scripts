#!/usr/bin/env python
import os,sys,optparse,logging,glob,subprocess,stat
logger = logging.getLogger(__name__)

sys.path.append('/users/hpcusers/svn/tools/python/')
import CondorJob

script = '''#!/usr/bin/env bash
export PATH=/opt/rh/python27/root/usr/bin:$PATH
export PYTHONPATH=/opt/rh/python27/root/usr/lib64/python2.7/site-packages:$PYTHONPATH
export LD_LIBRARY_PATH=/opt/rh/python27/root/usr/lib64:/opt/rh/python27/root/usr/lib:$LD_LIBRARY_PATH
source /share/sl6/root/bin/thisroot.sh
/users/hpcusers/dumpCaloCells/root2binary_v2.py $@
'''

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
         new_list.append(file)
   ROOTfilenames = new_list

   logger.info('number input files: %s',len(ROOTfilenames))
   
   open('root2binary.sh','w').write(script)
   st = os.stat('root2binary.sh')
   os.chmod('root2binary.sh',st.st_mode | stat.S_IEXEC)
   

   for ROOTfilename in ROOTfilenames:
      
      transfer_output = ''
      
      #transfer_output = ROOTfilename


      job = CondorJob.CondorJob(
         executable = 'root2binary.sh',
         arguments  = '-i ' + ROOTfilename + ' -o ' + options.output_path,
         output     = os.path.basename(ROOTfilename) + '.stdout',
         error      = os.path.basename(ROOTfilename) + '.stderr',
         log        = os.path.basename(ROOTfilename) + '.condorlog',
         )

      job.submit()

      



if __name__ == "__main__":
   main()
