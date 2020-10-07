FROM tensorflow/tensorflow:1.15.2-gpu

WORKDIR /root

RUN apt update

RUN apt install -y wget git nano

RUN git clone https://github.com/cern-it-efp/CProGAN-ME
RUN git clone https://github.com/tkarras/progressive_growing_of_gans

# Add PYTHONPATH to bashrc
RUN echo export PYTHONPATH=/root/progressive_growing_of_gans >> ~/.bashrc
RUN export PYTHONPATH=/root/progressive_growing_of_gans

#Install requirements with pip
RUN pip install -r ~/progressive_growing_of_gans/requirements-pip.txt

WORKDIR /root/CProGAN-ME
