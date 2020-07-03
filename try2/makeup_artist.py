from PIL import Image
import PIL
import numpy as np
import argparse
import cv2
import math
import matplotlib as mp
from statistics import mode
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten, BatchNormalization
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import MaxPooling2D
import os
AgeList = []
GenderList = []
EmotionDict ={}
EmotionList = []

class Makeup_artist(object):
    def __init__(self):
        pass

    def apply_makeup(self, img):
        faceProto = "opencv_face_detector.pbtxt"
        faceModel = "opencv_face_detector_uint8.pb"
        ageProto = "age_deploy.prototxt"
        ageModel = "age_net.caffemodel"
        genderProto = "gender_deploy.prototxt"
        genderModel = "gender_net.caffemodel"

        MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
        ageList = ['(17-20)', '(4-6)', '(8-12)', '(15-17)',
                   '(20-25)', '(30-35)', '(40-45)', '(50+)']
        genderList = ['Male', 'Female' ]

        faceNet = cv2.dnn.readNet(faceModel, faceProto)
        ageNet = cv2.dnn.readNet(ageModel, ageProto)
        genderNet = cv2.dnn.readNet(genderModel, genderProto)

    # ----------------------------------------------------------------

    # Create the model
        model = Sequential()

        model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(48,48,1)))
        model.add(BatchNormalization())
        model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))

        model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
        model.add(BatchNormalization())
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))

        model.add(Flatten())
        model.add(Dense(1024, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(7, activation='softmax'))

        model.load_weights('model.h5')

    # prevents openCL usage and unnecessary logging messages
        cv2.ocl.setUseOpenCL(False)

    # dictionary which assigns each label an emotion (alphabetical order)
        emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful",
                        3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}

    # start the webcam feed
       # video = cv2.VideoCapture(0)
        #padding = 20
    # Variable cap used once

        #while cv2.waitKey(1) < 0 and not None:
        numpy_image=np.array(img)  

# convert to a openCV2 image, notice the COLOR_RGB2BGR which means that 
# the color is converted from RGB to BGR format
        frame=cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)


        facecasc = cv2.CascadeClassifier(
               'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = facecasc.detectMultiScale(
        gray, scaleFactor=1.3, minNeighbors=5)
#        finals=None


        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (255, 0, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]
            cropped_img = np.expand_dims(np.expand_dims(
                cv2.resize(roi_gray, (48, 48)), -1), 0)
            prediction = model.predict(cropped_img)
            maxindex = int(np.argmax(prediction))
            EmotionList.append(emotion_dict[maxindex])
            cv2.putText(frame, emotion_dict[maxindex], (
                x, y-60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

            blob = cv2.dnn.blobFromImage(
               frame, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
            genderNet.setInput(blob)
            genderPreds = genderNet.forward()
            gender = genderList[genderPreds[0].argmax()]
            GenderList.append(f'Gender: {gender}')

            ageNet.setInput(blob)
            agePreds = ageNet.forward()
            age = ageList[agePreds[0].argmax()]
            AgeList.append(f'Age: {age[1:-1]} years')

            cv2.putText(frame, f'{gender}, {age}', (x + 150, y - 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2, cv2.LINE_AA)

            
        finals=Image.fromarray(
                          cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                         )       

        return finals