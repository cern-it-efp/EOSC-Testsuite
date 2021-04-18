#!/usr/bin/env python3

# source: proGAN's train.py

import pickle
import numpy as np
import tensorflow as tf
import PIL.Image

# Initialize TensorFlow session.
tf.InteractiveSession()

# Import official CelebA-HQ networks.
with open('network-final.pkl', 'rb') as file:
    G, D, Gs = pickle.load(file)

# Generate latent vectors.
#latents = np.random.RandomState(1000).randn(1000, *Gs.input_shapes[0][1:]) # 1000 random latents
#latents = latents[[477, 56, 83, 887, 583, 391, 86, 340, 341, 415]] # hand-picked top-10

# Generate dummy labels (not used by the official networks).
#labels = np.zeros([latents.shape[0]] + Gs.input_shapes[1][1:])

# Run the generator to produce a set of images.
#images = Gs.run(latents, labels)


def setup_snapshot_image_grid(G, training_set,
    size    = '1080p',      # '1080p' = to be viewed on 1080p display, '4k' = to be viewed on 4k display.
    layout  = 'random'):    # 'random' = grid contents are selected randomly, 'row_per_class' = each row corresponds to one class label.

    # Select size
    gw = 1; gh = 1
    if size == '1080p':
        gw = np.clip(1920 // G.output_shape[3], 3, 32)
        gh = np.clip(1080 // G.output_shape[2], 2, 32)
    if size == '4k':
        gw = np.clip(3840 // G.output_shape[3], 7, 32)
        gh = np.clip(2160 // G.output_shape[2], 4, 32)

    # Fill in reals and labels.
    reals = np.zeros([gw * gh] + training_set.shape, dtype=training_set.dtype)
    labels = np.zeros([gw * gh, training_set.label_size], dtype=training_set.label_dtype)
    for idx in range(gw * gh):
        x = idx % gw; y = idx // gw
        while True:
            real, label = training_set.get_minibatch_np(1)
            if layout == 'row_per_class' and training_set.label_size > 0:
                if label[0, y % training_set.label_size] == 0.0:
                    continue
            reals[idx] = real[0]
            labels[idx] = label[0]
            break

    # Generate latents.
    latents = np.random.randn(gw * gh, 128).astype(np.float32)
    return (gw, gh), reals, labels, latents


grid_size, grid_reals, grid_labels, grid_latents = setup_snapshot_image_grid(G, training_set, **config.grid)


size= int(128)

real1= grid_reals[:,:, :(size),:(size)]
real2= grid_reals[:,:, (size):,:(size)]
real3= grid_reals[:,:, :(size),(size):]
real1=(real1.astype(np.float32)-127)/128
real2=(real2.astype(np.float32)-127)/128
real3=(real3.astype(np.float32)-127)/128

latents = np.random.randn(120, 3, 128, 128)
left = np.concatenate((real1, real2), axis=2)
right = np.concatenate((real3, latents), axis=2)
lat_and_cond = np.concatenate((left, right), axis=3)



fake_images_out_small = Gs.run(lat_and_cond, grid_labels, minibatch_size=sched.minibatch//config.num_gpus)
fake_image_out_right =np.concatenate((real3, fake_images_out_small), axis=2)

fake_image_out_left = np.concatenate((real1, real2), axis=2)
grid_fakes = np.concatenate((fake_image_out_left, fake_image_out_right), axis=3)
misc.save_image_grid(grid_fakes, os.path.join(result_subdir, 'infe.png'), drange=drange_net, grid_size=grid_size)
