# echo "cleanup CaloMon CaloMon-00-00-00 in /lcrc/group/ATLAS/users/rwang/ML/atlas_ml_data_scripts"

if test "${CMTROOT}" = ""; then
  CMTROOT=/cvmfs/atlas.cern.ch/repo/sw/software/x86_64-slc6-gcc49-opt/20.7.5/CMT/v1r25p20140131; export CMTROOT
fi
. ${CMTROOT}/mgr/setup.sh
cmtCaloMontempfile=`${CMTROOT}/${CMTBIN}/cmt.exe -quiet build temporary_name`
if test ! $? = 0 ; then cmtCaloMontempfile=/tmp/cmt.$$; fi
${CMTROOT}/${CMTBIN}/cmt.exe cleanup -sh -pack=CaloMon -version=CaloMon-00-00-00 -path=/lcrc/group/ATLAS/users/rwang/ML/atlas_ml_data_scripts  $* >${cmtCaloMontempfile}
if test $? != 0 ; then
  echo >&2 "${CMTROOT}/${CMTBIN}/cmt.exe cleanup -sh -pack=CaloMon -version=CaloMon-00-00-00 -path=/lcrc/group/ATLAS/users/rwang/ML/atlas_ml_data_scripts  $* >${cmtCaloMontempfile}"
  cmtcleanupstatus=2
  /bin/rm -f ${cmtCaloMontempfile}
  unset cmtCaloMontempfile
  return $cmtcleanupstatus
fi
cmtcleanupstatus=0
. ${cmtCaloMontempfile}
if test $? != 0 ; then
  cmtcleanupstatus=2
fi
/bin/rm -f ${cmtCaloMontempfile}
unset cmtCaloMontempfile
return $cmtcleanupstatus

