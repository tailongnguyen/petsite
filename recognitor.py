import numpy as np
import keras
import argparse
import cv2
import pickle
import os
from keras.models import Model
from keras.callbacks import EarlyStopping, LearningRateScheduler, ModelCheckpoint
from keras.layers.pooling import GlobalAveragePooling2D
from keras.layers import Dense
from concurrent.futures import ThreadPoolExecutor, wait


argparser = argparse.ArgumentParser(
    description='Train and validate YOLO_v2 model on any dataset')

argparser.add_argument(
    '-f',
    '--folder')

IMG_SHAPE = (299, 299, 3)
NUM_CLASS = 50
BATCH_SIZE = 8
NUM_EPOCH = 100

def worker(dataset, idx):
    l_bound = idx*BATCH_SIZE
    r_bound = (idx+1)*BATCH_SIZE

    if r_bound > dataset.shape[0]:
        r_bound = dataset.shape[0]
        l_bound = r_bound - BATCH_SIZE

    img_batch = dataset[l_bound:r_bound]

    batch_x = []
    batch_y = []

    for idx in range(img_batch.shape[0]):
        try:
            im_path, im_label = img_batch[idx].rstrip('\n').split('\t')
            im = cv2.imread(args.folder, im_path)
            one_hot_label = np.ones(NUM_CLASS)
            one_hot_label[im_label] = 1
            if im is None:
                continue

            if len(im.shape) > 3:
                im = im[:, :, :3]

            im = cv2.resize(im, (IMG_SIZE, IMG_SIZE))
            assert im is not None

            batch_x.append(im)
            batch_y.append(one_hot_label)

        except AssertionError:
            print("{} not exist. Skipping.".format(im_path))

    batch_x = np.asarray(batch_x)
    batch_y = np.asarray(batch_y)
    return batch_x, batch_y


def read_batches(dataset):
    pool = ThreadPoolExecutor(1)  # Run a single I/O thread in parallel
    future = pool.submit(worker, dataset[0:BATCH_SIZE])
    for i in range(1, len(dataset)//BATCH_SIZE + 1):
        wait([future])
        minibatch = future.result()
        # While the current minibatch is being consumed, prepare the next
        future = pool.submit(worker, dataset, i)
        yield minibatch

    # Wait for the last minibatch
    wait([future])
    minibatch = future.result()
    yield minibatch


def get_model():
    base_model = keras.applications.xception.Xception(
        include_top=False, weights='imagenet', input_tensor=None, input_shape=IMG_SHAPE, pooling=None, classes=NUM_CLASS)
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(1024, activation='relu')(x)
    predictions = Dense(NUM_CLASS, activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)
    if os.path.isfile('./best_weights.h5'):
         model.load_weights('./best_weights.h5')
         print("Loaded weights!")
    else:
         print("No weights detected. Using random weights!")

    return model


def plotting(x, y, xname, yname, title):
    plt.figure()
    plt.xlabel(xname)
    plt.ylabel(yname)
    plt.title(title)
    plt.plot(x, y)
    plt.savefig(title)

def main():
    dataset = open('petdata.txt', 'r').readlines()
    model = get_model()
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
    
    history = {"train_loss": [], "train_acc": []}
    non_improved = 0
    tolerance = 20
    best_acc = 0
    for ep in range(NUM_EPOCH):
        np.random.shuffle(dataset)
        if non_improved > tolerance:
            print("Stop training because of contiguous non-improved epochs!")
            with open('history.pkl', 'wb') as f:
                pickle.dump(history, f, pickle.HIGHEST_PROTOCOL)
            plotting(np.arange(
                ep), history['train_loss'], "Epoch", "Loss", "History Loss")
            plotting(np.arange(
                ep), history['train_acc'], "Epoch", "Accuracy", "History Accuracy")
            return

        batch_acc = []
        batch_loss = []
        it = 0
        for batch_x, batch_y in read_batches(dataset):
            it+=1
            loss, acc = model.train_on_batch(batch_x, batch_y)
            batch_loss.append(loss)
            batch_acc.append(acc)
            if it < len(dataset)//BATCH_SIZE:
                sys.stdout.write("\rBatch {}/{} | Ep {} | loss: {:.3f} | acc: {:.5f}".format(loss, acc))
            else:
                it = 0
                sys.stdout.write(
                    "\rBatch {}/{} | Ep {} | loss: {:.3f} | acc: {:.5f}\n".format(np.mean(batch_loss), np.mean(batch_acc)))

            sys.stdout.flush()

        history["train_loss"].append(np.mean(batch_loss))
        history["train_acc"].append(np.mean(batch_acc))

        if np.mean(batch_acc) > best_acc:
            best_acc = np.mean(batch_acc)
            print("Validation accuracy improved! Saving weights to {}...".format("best_weights.h5"))
            model.save_weights("best_weights.h5")
        else:
            print("Validation accuracy not improved!")
            non_improved += 1



