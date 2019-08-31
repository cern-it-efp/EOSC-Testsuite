#!/bin/bash
\cp -rf ${NVIDIA_PATH}/usr/lib/modules/${KERNEL_VERSION}/video /lib/modules/${KERNEL_VERSION}
depmod -a
modprobe -r nouveau
modprobe nvidia
modprobe nvidia-uvm
nvidia-mkdevs
\cp -rfn ${NVIDIA_PATH}/bin /opt/nvidia-host
\cp -rfn ${NVIDIA_PATH}/lib64 /opt/nvidia-host
