#!/bin/bash

############ GET AND PREPARE THE DATASET

mnistds(){
  wget -P /tmp/mnist http://yann.lecun.com/exdb/mnist/train-images-idx3-ubyte.gz
  wget -P /tmp/mnist http://yann.lecun.com/exdb/mnist/train-labels-idx1-ubyte.gz
  mkdir datasets/mnist
  python dataset_tool.py create_mnist datasets/mnist/ /tmp/mnistds/
}

celebahqds(){
  wget -P /tmp/celebahqds/ ... # Cant download from google: max download quota reached
  mkdir datasets/celebahq
  python dataset_tool.py create_mnist datasets/celebahq /tmp/celebahqds/
}


############ CONFIGURATION (for mnist with fp16 and 4 gpus)

sed -i "s/desc += '-celebahq'/#desc += '-celebahq'/" config.py
sed -i "s/#desc += '-mnist'/desc += '-mnist'/" config.py

# one of the following two triggers the error: AttributeError: module 'tensorflow_core.contrib' has no attribute "nccl"

sed -i "s/desc += '-fp32'/#desc += '-fp32'/" config.py
sed -i "s/#desc += '-fp16'/desc += '-fp16'/" config.py

sed -i "s/desc += '-preset-v2-1gpu'/#desc += '-preset-v2-1gpu'/" config.py
sed -i "s/#desc += '-preset-v2-4gpus'/desc += '-preset-v2-4gpus'/" config.py

sed -i "s/#desc += '-VERBOSE'/desc += '-VERBOSE'/" config.py


############ START TRAINING

python train.py

############ ACCESS RESULTS

ls -la config.result_dir
