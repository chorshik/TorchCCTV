import sys
from pathlib import Path
import logging
import pickle

sys.path.append(str(Path(__file__).parent))

import cv2
import numpy as np

from create_database import face_cropper, faceRecModelHandler, faceAlignModelHandler, faceDetModelHandler


mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING)
logger = logging.getLogger('api')

# create_database()


def load_known_faces():
    global known_face_feature, known_face_metadata

    try:
        with open("data/database/faces_jetson2.dat", "rb") as face_data_file:
            known_face_feature, known_face_metadata = pickle.load(face_data_file)
            print("Known faces.dat loaded from disk.")
    except FileNotFoundError as e:
        print("No previous face data found - starting with a blank known face list.")
        pass


video_capture = cv2.VideoCapture(0)

bbox = None
face_names = []
process_this_frame = True

load_known_faces()

while True:
    ret, frame = video_capture.read()
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        dets = faceDetModelHandler.inference_on_image(small_frame)
        face_nums = dets.shape[0]
        bbox = dets
        feature_list = []
        for i in range(face_nums):
            landmarks = faceAlignModelHandler.inference_on_image(small_frame, dets[i])
            landmarks_list = []
            for (x, y) in landmarks.astype(np.int32):
                landmarks_list.extend((x, y))
            cropped_image = face_cropper.crop_image_by_mat(small_frame, landmarks_list)
            feature = faceRecModelHandler.inference_on_image(cropped_image)
            feature_list.append(feature)

        face_names = []
        for feature in feature_list:
            scores = np.dot(known_face_feature, feature.transpose())
            score = scores.max()
            name = "Unknown"
            if score > 0.5:
                metadata = known_face_metadata[scores.argmax()]
                name = metadata["ident"]
            face_names.append(name)
            logger.info('The similarity score of two faces: %f' % score)
    process_this_frame = not process_this_frame

    # Display the results
    for box, name in zip(bbox, face_names):
        box = list(map(int, box))
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top = box[1] * 4
        right = box[2] * 4
        bottom = box[3] * 4
        left = box[0] * 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
