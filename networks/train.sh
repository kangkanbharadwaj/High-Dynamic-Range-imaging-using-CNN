#!/bin/bash

cd /home/bharadwaj/ImageSegmentation/data/streetObjects2Data
logfile="2d_dense-$(date +%F_%R).log"
snapshotIter="$(ls snapshot/*.solverstate.h5 | grep -o "_[0-9]*[.]" | sed -e "s/^_//" -e "s/.$//" | xargs printf "%010d\n" | sort | tail -1 | sed -e "s/^0*//")"

if [ "x${snapshotIter}" != "x" ]; then
lastSnapshot="snapshot/2d_dense_snapshot_iter_${snapshotIter}.solverstate.h5"
    continueFromSnapshot="-snapshot ${lastSnapshot}"
    echo "Continuing from snapshot ${lastSnapshot}" > ${logfile}
else
    continueFromSnapshot=""
    echo "Starting new training" > ${logfile}
fi 

HDF5_DISABLE_VERSION_CHECK=1 time caffe train   --solver=2d_dense-solver.prototxt -sigint_effect snapshot ${continueFromSnapshot} 2>&1| tee ${logfile} 
