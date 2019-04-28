import cv2
from irecruit import app
from flask import redirect, url_for
import numpy as np


class VideoCameraDetection(object):

    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_frame(self, count):

        # feature extraction
        face_classifier = cv2.CascadeClassifier('C:\\Users\\hp\\PycharmProjects\\Main_Project\\haarcascade_frontalface_default.xml')

        # feature extraction
        def face_extractor(img):

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_classifier.detectMultiScale(gray, 1.3, 5)

            if faces is ():
                return None

            for (x, y, w, h) in faces:
                cropped_face = img[y:y + h, x:x + w]

            return cropped_face

        # configure cam
        cap = cv2.VideoCapture(0)


        # displaying and storing faces
        while True:
            ret, frame = cap.read()
            if face_extractor(frame) is not None:

                count += 1
                face = cv2.resize(face_extractor(frame), (200, 200))
              #  face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

                file_name_path = 'C:\\Users\\hp\\PycharmProjects\\Main_Project\\faces\\user' + str(count) + '.jpg'
                cv2.imwrite(file_name_path, cv2.cvtColor(face, cv2.COLOR_BGR2GRAY))
                ret, jpeg = cv2.imencode('.jpg', cv2.putText(face, str(count), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2))
                print(count)
                #requests.post('http://127.0.0.1:5000/detection', json={"counts:count"})
                if cv2.waitKey(1) == 13:
                    break
                return jpeg.tobytes(), count

              #  cv2.imshow('Face Cropper', face)

            else:
                print("Face not Found")
                pass

        cap.release()
        cv2.destroyAllWindows()


