# Nvidia driver installer for centos

ARG CENTOS_VERSION=7

FROM centos:${CENTOS_VERSION} as kmod_builder
LABEL name="nvidia-driver-installer" \
      version="0.2" \
      architecture="x86_64"

ARG KERNEL_VERSION=3.10.0-1062.9.1.el7.x86_64
ARG NVIDIA_DRIVER_VERSION=415.18

RUN yum update -y

RUN yum install -y curl git binutils cpp gcc bc make pkgconfig pciutils unzip && \
      #elfutils-libelf-devel openssl-devel module-init-tools && \
    yum install -y kernel-devel-${KERNEL_VERSION} kernel-headers-${KERNEL_VERSION} && \
    yum autoremove -y && \
    yum clean all

ENV NVIDIA_DRIVER_URL "http://download.nvidia.com/XFree86/Linux-x86_64/${NVIDIA_DRIVER_VERSION}/NVIDIA-Linux-x86_64-${NVIDIA_DRIVER_VERSION}-no-compat32.run"

ENV KERNEL_PATH /usr/src/kernels
ENV NVIDIA_PATH /opt/nvidia
ENV NVIDIA_BUILD_PATH ${NVIDIA_PATH}/build
ENV NVIDIA_DL_PATH ${NVIDIA_PATH}/download

# NVIDIA driver
WORKDIR ${NVIDIA_DL_PATH}

RUN curl ${NVIDIA_DRIVER_URL} -o nv_driver_installer.run && \
    chmod +x nv_driver_installer.run

RUN ${NVIDIA_PATH}/download/nv_driver_installer.run \
      -z \
      --silent \
      --no-precompiled-interface \
      --kernel-source-path=${KERNEL_PATH}/${KERNEL_VERSION} \
      --kernel-name=${KERNEL_VERSION} \
      --no-nouveau-check \
      --no-nvidia-modprobe \
      --no-check-for-alternate-installs \
      --no-backup \
      --no-rpms \
      --no-drm \
      --x-prefix=/tmp/null \
      --x-module-path=/tmp/null \
      --x-library-path=/tmp/null \
      --x-sysconfig-path=/tmp/null \
      --no-glvnd-egl-client \
      --no-glvnd-glx-client \
      --no-install-libglvnd \
      --no-libglx-indirect \
      --no-install-compat32-libs \
      --installer-prefix=${NVIDIA_BUILD_PATH} \
      --utility-prefix=${NVIDIA_BUILD_PATH} \
      --opengl-prefix=${NVIDIA_BUILD_PATH} && \
      mv ${NVIDIA_BUILD_PATH}/lib ${NVIDIA_BUILD_PATH}/lib64

RUN mkdir -p ${NVIDIA_BUILD_PATH}/usr/lib/modules/ && \
    cp -rf /usr/lib/modules/${KERNEL_VERSION} ${NVIDIA_BUILD_PATH}/usr/lib/modules/${KERNEL_VERSION}


###   DEPLOY   ###
FROM centos:${CENTOS_VERSION}
LABEL name="nvidia-driver-installer" \
      version="0.2" \
      architecture="x86_64"

ARG KERNEL_VERSION=3.10.0-1062.9.1.el7.x86_64
ARG NVIDIA_DRIVER_VERSION=415.18

RUN yum update -y && \
    yum install -y module-init-tools pciutils && \
    yum autoremove -y && \
    yum clean all

ENV NVIDIA_DRIVER_VERSION ${NVIDIA_DRIVER_VERSION}
ENV KERNEL_VERSION ${KERNEL_VERSION}

ENV KERNEL_PATH /usr/src/kernels
ENV NVIDIA_PATH /opt/nvidia
ENV NVIDIA_BIN_PATH ${NVIDIA_PATH}/bin
ENV NVIDIA_LIB_PATH ${NVIDIA_PATH}/lib
ENV NVIDIA_MODULES_PATH ${NVIDIA_LIB_PATH}/modules/${KERNEL_VERSION}/kernel/drivers/video

COPY --from=kmod_builder /opt/nvidia/build ${NVIDIA_PATH}
COPY nvidia-mkdevs.sh ${NVIDIA_BIN_PATH}/nvidia-mkdevs
COPY install-drv.sh ${NVIDIA_BIN_PATH}/install-drv

ENV PATH $PATH:${NVIDIA_BIN_PATH}
ENV LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${NVIDIA_LIB_PATH}

#problem here: on the original version by kosamara these chmod were not needed! is it because he had done it locally before building the image?
#RUN chmod +x ${NVIDIA_BIN_PATH}/nvidia-mkdevs && chmod +x ${NVIDIA_BIN_PATH}/install-drv
CMD ["install-drv"]
