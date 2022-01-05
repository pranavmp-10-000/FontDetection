import streamlit as st
import tensorflow as tf
from PIL import Image
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

class_names = ['Roboto-Regular',
 'FredokaOne-Regular',
 'PTSerif-Regular',
 'Dancing+Script-Regular',
 'Oswald-Regular',
 'PatuaOne-Regular',
 'Arimo-Regular',
 'NotoSans-Regular',
 'Open+Sans-Regular',
 'Ubuntu-Regular']

predictB = False

def predict(model,image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
 
    # Performing OTSU threshold
    ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    
    # Specify structure shape and kernel size.
    # Kernel size increases or decreases the area
    # of the rectangle to be detected.
    # A smaller value like (10, 10) will detect
    # each word instead of a sentence.
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
    
    # Applying dilation on the threshold image
    dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)
    
    # Finding contours
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL,
                                                    cv2.CHAIN_APPROX_NONE)

    im2 = image.copy()
    text_boxes = []
    text_boxes_xy = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        
        # Drawing a rectangle on copied image
        rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 1)
        
        # Cropping the text block for giving input to OCR
        cropped = im2[y:y + h, x:x + w]
        text_boxes.append(cropped)
        text_boxes_xy.append((x,y,w,h))
    prediction = np.zeros((len(text_boxes),1))
    output = {"detectedFonts":[]}
    for i in range(len(text_boxes)):
        pred_x = cv2.cvtColor(text_boxes[i],cv2.COLOR_RGB2GRAY)
        pred_x = cv2.resize(pred_x,(64,64))[np.newaxis,:,:]
        prediction = model.predict(np.array(pred_x))
        logits = tf.nn.softmax(prediction)
        max_index = np.argmax(logits)
        output['detectedFonts'].append({'boundingBox':text_boxes_xy[i],"font":class_names[max_index],"confidence":np.max(logits)})
    return output


def load_image(file):
    image = Image.open(file)
    image = image.resize((512,512))
    return image

st.title("Font Detection App")

def button_click(image):
    wd = os.getcwd()
    model = tf.keras.models.load_model(wd+'/Models/FinalModel.h5')

    prediction = predict(model,image)
    st.write(prediction)

if predictB==False:
    uploaded_file = st.file_uploader("Choose a file",type=["png","jpg","jpeg"])

    if uploaded_file is not None:

        # To See details
        file_details = {"filename":uploaded_file.name, "filetype":uploaded_file.type,
                        "filesize":uploaded_file.size}
        #st.write(file_details)

        # To View Uploaded Image
        image = load_image(uploaded_file)
        st.image(image)
        st.button("Predict Font",on_click=button_click(np.array(image)))


    
    