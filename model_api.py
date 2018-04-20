from flask import Flask,request,json
import numpy as np
from flask_cors import CORS
from recognitor import *
import cv2
import os
import pickle
app = Flask(__name__)
CORS(app)

model = get_model()
classes = ['abyssinian', 'alaskanmalamute', 'american bobtail', 'american shorthair', 'americanpitbullterrier', 'americanstaffordshireterrier', 'turkishangora', 'balinese', 'beagle', 'bengal', 'berger', 'birman', 'bombay', 'boxer', 'bullmastiff', 'burmese', 'cavalierkingcharlesspaniel', 'chihuahua', 'chowchow', 'dachshund', 'dalmatian', 'dobermannpinscher', 'englishcockerspaniel', 'englishmastiff',
           'greatdane', 'greatpyrenees', 'greyhound', 'huskysibir', 'japanese bobtail', 'labradorretriever', 'leonberger', 'maltese', 'newfoundland', 'pekingese', 'pembrokewelshcorgi', 'persian', 'pomeranian', 'pug', 'rottweiler', 'samoyed', 'shihtzu', 'sphynx', 'st.bernard', 'staffordshirebullterrier', 'tabby', 'vizsla', 'weimaraner', 'westhighlandwhiteterrier', 'whippet', 'yorkshireterrier']


@app.route("/classify", methods=['POST'])
def predict():
    image = request.data
    im = pickle.loads(image)
    img = cv2.resize(im, IMG_SHAPE[:2])
    cl = model.predict(np.expand_dims(img, axis=0))
    rs = classes[np.argmax(cl)]
    print(rs)
    return rs

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050)
