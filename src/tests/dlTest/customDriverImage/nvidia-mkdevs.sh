#!/bin/sh

# Count the number of NVIDIA controllers found.
NVDEVS=`lspci | grep -i NVIDIA`
N3D=`echo "$NVDEVS" | grep "3D controller" | wc -l`
NVGA=`echo "$NVDEVS" | grep "VGA compatible controller" | wc -l`
N=`expr $N3D + $NVGA - 1`

for i in `seq 0 $N`; do
    rm -f /dev/nvidia$i
    mknod -m 666 /dev/nvidia$i c 195 $i
done

rm -f /dev/nvidiactl
mknod -m 666 /dev/nvidiactl c 195 255

# Find out the major device number used by the nvidia-uvm driver
D=`grep nvidia-uvm /proc/devices | awk '{print $1}'`
rm -f /dev/nvidia-uvm
mknod -m 666 /dev/nvidia-uvm c $D 0
