#!/bin/bash

############ GET AND PREPARE THE DATASET (note these functions have to run called from inside CProGAN-ME)

mnistds(){
  wget -P /tmp/mnistds http://yann.lecun.com/exdb/mnist/train-images-idx3-ubyte.gz
  wget -P /tmp/mnistds http://yann.lecun.com/exdb/mnist/train-labels-idx1-ubyte.gz
  mkdir datasets/mnist
  python dataset_tool.py create_mnist datasets/mnist/ /tmp/mnistds/
}

celebahqds(){
  wget -P /tmp/celebahqds/ https://s3.cern.ch/swift/v1/gan-bucket/img_celeba.zip # images
  unzip /tmp/celebahqds/img_celeba.zip -d /tmp/celebahqds
  wget -P /tmp/deltas/ https://s3.cern.ch/swift/v1/gan-bucket/.zip # # deltas
  unzip /tmp/deltas/.zip
  mkdir datasets/celebahq
  python dataset_tool.py create_celebahq datasets/celebahq /tmp/celebahqds/ /tmp/deltas
}

celebads(){
  wget -P /tmp/celebads/ https://s3.cern.ch/swift/v1/gan-bucket/img_align_celeba_png.zip # images
  unzip /tmp/celebads/img_align_celeba_png.zip -d /tmp/celebads/
  mkdir datasets/celeba
  python dataset_tool.py create_celeba datasets/celeba /tmp/celebads/ --images_amount $IMAGES_AMOUNT # TODO: (if) provided via testsCatalog.yaml
}

unosatds(){ # TODO
  wget -P /tmp/unosatds/ https://s3.cern.ch/swift/v1/gan-bucket/img_align_celeba_png.zip # records or images? if records, then dataset_tool.py is not needed
  unzip /tmp/unosatds/.zip
  mkdir datasets/unosatds
  python dataset_tool.py create_from_images datasets/unosatds /tmp/unosatds/ --images_amount $IMAGES_AMOUNT # TODO: (if) provided via testsCatalog.yaml
}

personds(){
  wget -P /tmp/ https://s3.cern.ch/swift/v1/gan-bucket/person.zip # records or images? if records, then dataset_tool.py is not needed
  unzip /tmp/person.zip -d /tmp
  mkdir datasets/person
  python dataset_tool.py create_from_images datasets/person/ /tmp/person/ --images_amount $IMAGES_AMOUNT # TODO: (if) provided via testsCatalog.yaml
}


mkdir datasets

############ CONFIGURATION (for mnist with fp16 and 4 gpus)

sed -i "s/desc += '-celebahq'/#desc += '-celebahq'/" config.py
sed -i "s/#desc += '-mnist'/desc += '-mnist'/" config.py

sed -i "s/desc += '-fp32'/#desc += '-fp32'/" config.py # TODO: this fails for CProGAN-ME
sed -i "s/#desc += '-fp16'/desc += '-fp16'/" config.py

sed -i "s/desc += '-preset-v2-1gpu'/#desc += '-preset-v2-1gpu'/" config.py
sed -i "s/#desc += '-preset-v2-4gpus'/desc += '-preset-v2-4gpus'/" config.py

sed -i "s/#desc += '-VERBOSE'/desc += '-VERBOSE'/" config.py # TODO: y's is different than k's


############ START TRAINING

python train.py

############ ACCESS RESULTS

ls -la config.result_dir

ls $config.result_dir/network-final.pkl
