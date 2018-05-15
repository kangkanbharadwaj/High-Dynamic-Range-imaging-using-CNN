#!/bin/bash
#PBS -N 2d_dense-train
#PBS -S /bin/bash
#PBS -l nodes=1:ppn=1:gpus=1:nvidiaTITANX,walltime=24:00:00,mem=12gb
#PBS -q default-gpu
#PBS -m a
#PBS -M cicek@informatik.uni-freiburg.de
#PBS -j oe
#PBS -t 1-10%1
export CAFFE_ROOT=/home/cicek/mycaffe3D/
export PATH=/home/cicek/mycaffe3D//release/tools:/home/cicek/bindb2/build/release/bin:/home/cicek/pyviz/bin:/home/cicek/itools/shell:/home/cicek/itools/python/tools:/home/cicek/pymill/bin:/misc/software-lin/lmbsoft/cmake-3.5.2-Linux-x86_64/bin/:/misc/software-lin/lmbsoft/cuda-8.0.27/bin:/home/cicek/lmbunet/build/tools:/misc/software-lin/lmbsoft/iRoCS-Toolbox-1.1.2-x86_64-gcc4.8/bin:/home/cicek/software/x86_64-gcc5.4.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/home/cicek/software/x86_64-gcc5.4.0/bin=/misc/software-lin/vivi=/home/ummenhof/mysoftware/vivi/plugins/flowColor=/home/cicek/bindb2/src/
export LD_LIBRARY_PATH=/misc/software-lin/lmbsoft/cudnn-8.0-linux-x64-v5.0-rc/lib64:/home/cicek/bindb2/build/release/lib:/home/cicek/itools/build/release/lib:/usr/include/python3.5m/:/home/cicek/bindb2/src/:/home/cicek/lmbunet/build/lib:/misc/software-lin/lmbsoft/mdb-mdb/libraries/liblmdb/:/misc/software-lin/lmbsoft/cudnn-8.0-linux-x64-v5.1/lib64:/misc/software-lin/lmbsoft/cudnn-8.0-linux-x64-v5.0-rc/lib64:/home/cicek/bindb2/build/release/lib:/misc/software-lin/lmbsoft/cuda-8.0.27/lib64:/misc/software-lin/lmbsoft/cuda-8.0.27/lib:/home/falk/software/x86_64-gcc5.4.0/lib:/misc/software/lmbsoft/build/x86_64-gcc5.4.0/lib:/misc/software/lmbsoft/build/x86_64-gcc5.4.0/bin:/misc/software-lin/lmbsoft/iRoCS-Toolbox-1.1.2-x86_64-gcc4.8/lib:/usr/share/qt4/lib:/home/cicek/software/x86_64-gcc5.4.0/lib::/home/cicek/software/x86_64-gcc5.4.0/lib
cd /misc/lmbraid19/cicek/laura_frog_embryos/2d_dense

logfile="2d_dense-$(date +%F_%R).log"

snapshotIter="$(ls 2d_dense/*.solverstate.h5 | grep -o "_[0-9]*[.]" | sed -e "s/^_//" -e "s/.$//" | xargs printf "%010d\n" | sort | tail -1 | sed -e "s/^0*//")"

if [ "x${snapshotIter}" != "x" ]; then
lastSnapshot="2d_dense/2d_dense_snapshot_iter_${snapshotIter}.solverstate.h5"
    continueFromSnapshot="-snapshot ${lastSnapshot}"
    echo "Continuing from snapshot ${lastSnapshot}" > ${logfile}
else
    continueFromSnapshot=""
    echo "Starting new training" > ${logfile}
fi 

HDF5_DISABLE_VERSION_CHECK=1 time caffe train   --solver=2d_dense-solver.prototxt -sigint_effect snapshot ${continueFromSnapshot} 2>&1| tee ${logfile} 
