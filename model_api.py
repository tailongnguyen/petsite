from flask import Flask,request,json
import numpy as np
import keras
from keras.models import Model
from keras.layers.pooling import GlobalAveragePooling2D
from keras.layers import Dense
from flask_cors import CORS
import cv2
import os
import pickle
app = Flask(__name__)
CORS(app)
IMG_SHAPE = (256,256, 3)
NUM_CLASS = 45

def get_model():
    base_model = keras.applications.xception.Xception(
        include_top=False, weights='imagenet', input_tensor=None, input_shape=IMG_SHAPE, pooling=None, classes=NUM_CLASS)
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(1024, activation='relu')(x)
    predictions = Dense(NUM_CLASS, activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)
    model.load_weights('./weights.h5')
    print( "Loaded weights!")
    
    return model

model = get_model()
classes = ['abyssinian', 'americanbobtail', 'americancurl', 'americanshorthair', 'americanwirehair',
         'balinese', 'bengal', 'birman', 'bombay', 'burmese', 'burmilla', 'chartreux', 'cornishrex', 
         'coupari', 'egyptianmau', 'exoticshorthair', 'himalaya', 'japanesebobtail', 'javanese', 'korat', 
         'laperm', 'mainecoon', 'manx', 'munchkin', 'nebelung', 'norwegianforestcat', 'ocicat', 
         'orientalshorthair', 'persian', 'pixie-bob', 'ragamuffin', 'ragdoll', 'russianblue', 'savannah', 
         'selkirkrex', 'siamese', 'siberianforestcat', 'singapura', 'snowshoe', 'somali', 'sphynx', 'tonkinese', 
         'toyger', 'turkishangora', 'turkishvan']

@app.route("/classify", methods=['POST'])
def predict():
    image = request.data
    im = pickle.loads(image)
    print(im.shape)
    img = cv2.resize(im, IMG_SHAPE[:2])
    cl = model.predict(np.expand_dims(img, axis=0))
    rs = classes[np.argmax(cl)]
    print(rs)
    return rs

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050)
