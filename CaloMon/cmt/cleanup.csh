# echo "cleanup CaloMon CaloMon-00-00-00 in /lcrc/group/ATLAS/users/rwang/ML/atlas_ml_data_scripts"

if ( $?CMTROOT == 0 ) then
  setenv CMTROOT /cvmfs/atlas.cern.ch/repo/sw/software/x86_64-slc6-gcc49-opt/20.7.5/CMT/v1r25p20140131
endif
source ${CMTROOT}/mgr/setup.csh
set cmtCaloMontempfile=`${CMTROOT}/${CMTBIN}/cmt.exe -quiet build temporary_name`
if $status != 0 then
  set cmtCaloMontempfile=/tmp/cmt.$$
endif
${CMTROOT}/${CMTBIN}/cmt.exe cleanup -csh -pack=CaloMon -version=CaloMon-00-00-00 -path=/lcrc/group/ATLAS/users/rwang/ML/atlas_ml_data_scripts  $* >${cmtCaloMontempfile}
if ( $status != 0 ) then
  echo "${CMTROOT}/${CMTBIN}/cmt.exe cleanup -csh -pack=CaloMon -version=CaloMon-00-00-00 -path=/lcrc/group/ATLAS/users/rwang/ML/atlas_ml_data_scripts  $* >${cmtCaloMontempfile}"
  set cmtcleanupstatus=2
  /bin/rm -f ${cmtCaloMontempfile}
  unset cmtCaloMontempfile
  exit $cmtcleanupstatus
endif
set cmtcleanupstatus=0
source ${cmtCaloMontempfile}
if ( $status != 0 ) then
  set cmtcleanupstatus=2
endif
/bin/rm -f ${cmtCaloMontempfile}
unset cmtCaloMontempfile
exit $cmtcleanupstatus

