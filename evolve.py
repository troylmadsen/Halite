#!/usr/bin/env python

import os
# from shutil import copyfile

generation = 0

while True:
    print("!!!Beginning generation " + str(generation))

    # Clear away old files from a data-creator
    os.system('del *.log')
    os.system('del *.hlt')
    os.system('del *.vec')
    os.system('del data.gameout')
    os.system('del train.in')
    os.system('del train.out')

    # # Create a copy of the model behavior to compete
    # copyfile("model_checkpoint_128_batch_10_epochs.h5py", "model_checkpoint_128_batch_10_epochsX.h5py")

    # Run the training
    os.system("python Training_Data.py")

    # # Remove copied file
    # os.remove("model_checkpoint_128_batch_10_epochsX.h5py")

    # Rename old generation behavior
    os.rename("model_checkpoint_128_batch_10_epochs.h5py", "model_checkpoint_128_batch_10_epochs-Gen-{}.h5py".format(generation))

    # Train the model with results
    os.system("python model-trainer.py")

    # Increment generation number
    generation += 1
