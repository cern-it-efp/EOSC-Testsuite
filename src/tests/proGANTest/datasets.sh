#!/bin/bash

mnistds(){
  wget -P /tmp/mnistds http://yann.lecun.com/exdb/mnist/train-images-idx3-ubyte.gz
  wget -P /tmp/mnistds http://yann.lecun.com/exdb/mnist/train-labels-idx1-ubyte.gz
  mkdir -p datasets/mnist
  python dataset_tool.py create_mnist datasets/mnist/ /tmp/mnistds/
}

celebahqds(){
  wget -P /tmp/celebahqds/ https://s3.cern.ch/swift/v1/gan-bucket/img_celeba.zip # images
  unzip /tmp/celebahqds/img_celeba.zip -d /tmp/celebahqds
  wget -P /tmp/deltas/ https://s3.cern.ch/swift/v1/gan-bucket/.zip # # deltas
  unzip /tmp/deltas/.zip
  mkdir -p datasets/celebahq
  python dataset_tool.py create_celebahq datasets/celebahq /tmp/celebahqds/ /tmp/deltas
}

celebads(){
  wget -P /tmp/celebads/ https://s3.cern.ch/swift/v1/gan-bucket/img_align_celeba_png.zip # images
  unzip /tmp/celebads/img_align_celeba_png.zip -d /tmp/celebads/
  mkdir -p datasets/celeba
  python dataset_tool.py create_celeba datasets/celeba /tmp/celebads/ --images_amount $IMAGES_AMOUNT # TODO: (if) provided via testsCatalog.yaml
}

unosatds(){ # TODO
  wget -P /tmp/unosatds/ https://s3.cern.ch/swift/v1/gan-bucket/img_align_celeba_png.zip # records or images? if records, then dataset_tool.py is not needed
  unzip /tmp/unosatds/.zip
  mkdir -p datasets/unosatds
  python dataset_tool.py create_from_images datasets/unosatds /tmp/unosatds/ --images_amount $IMAGES_AMOUNT # TODO: (if) provided via testsCatalog.yaml
}

personds(){
  wget -P /tmp/ https://s3.cern.ch/swift/v1/gan-bucket/person.zip
  unzip /tmp/person.zip -d /tmp
  mkdir -p datasets/person
  python dataset_tool.py create_from_images datasets/person/ /tmp/person/ --images_amount $IMAGES_AMOUNT
}
