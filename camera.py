#!/usr/bin/env python

import cv2
import numpy as np
# listdir:for fetching data from a directory
from os import listdir
from os.path import isfile, join
from flask import render_template
import warnings

data_path = 'C:\\Users\\hp\\PycharmProjects\\Main_Project\\faces\\'
onlyfiles = [f for f in listdir(data_path) if isfile(join(data_path, f))]

Training_Data, Labels = [], []

for i, files in enumerate(onlyfiles):
    image_path = data_path + onlyfiles[i]
    images = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    Training_Data.append(np.asarray(images, dtype=np.uint8))
    Labels.append(i)

Labels = np.asarray(Labels, dtype=np.int32)

model = cv2.face.LBPHFaceRecognizer_create()


model.train(np.asarray(Training_Data), np.asarray(Labels))

print("Model Training Complete")
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')


class VideoCamera(object):
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.video = cv2.VideoCapture(0)
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')

    def __del__(self):
        self.video.release()

    def get_frame(self):
        face_classifier = cv2.CascadeClassifier('C:\\Users\\hp\\PycharmProjects\\Main_Project\\'
                                                'haarcascade_frontalface_default.xml')

        def face_detector(img, size=0.5):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_classifier.detectMultiScale(gray, 1.3, 5)

            if faces is ():
                return img, []

            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                roi = img[y:y + h, x:x + w]
                roi = cv2.resize(roi, (200, 200))

            return img, roi

        while True:

            ret, frame = self.video.read()
            image, face = face_detector(frame)

            try:
                '''faces = face_cascade.detectMultiScale(image, 1.3, 5)
                for (x, y, w, h) in faces:
                    cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    ret, jpeg = cv2.imencode('.jpg', image)
                    return jpeg.tobytes()'''

                face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                result = model.predict(face)
                count = 0

                if result[1] < 500:
                    confidence = int(100 * (1 - (result[1]) / 300))
                    display_string = str(confidence) + '% Confidence it is user'
                    # ret, jpeg = cv2.imencode('.jpg', cv2.putText(image, display_string, (100, 120), cv2.FONT_HERSHEY_COMPLEX, 1, (250, 120, 255), 2)

                # FACE CHECKING
                if confidence > 87:
                    count = 1
                    ret, jpeg = cv2.imencode('.jpg',
                                             cv2.putText(image, "Unlocked", (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1,
                                                         (0, 255, 0), 2))
                    return jpeg.tobytes(), count

                    # cv2.putText(image, "Unlocked", (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    # cv2.imshow('Face Cropper', image)
                else:

                    ret, jpeg = cv2.imencode('.jpg',
                                             cv2.putText(image, "Locked", (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1,
                                                         (0, 0, 255), 2))
                    return jpeg.tobytes(), count

                    # cv2.putText(image, "Locked", (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
                    # cv2.imshow('Face Cropper', image)'''




            except:
                faces = face_cascade.detectMultiScale(image, 1.3, 5)
                for (x, y, w, h) in faces:
                    cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    ret, jpeg = cv2.imencode('.jpg', image)
                    return jpeg.tobytes()
        # success, image = self.video.read()
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        # faces = face_cascade.detectMultiScale(image, 1.3, 5)
        # for (x, y, w, h) in faces:
        #   cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
        # ret, jpeg = cv2.imencode('.jpg', image)
    # return jpeg.tobytes()
