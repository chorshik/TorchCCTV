import sys
from pathlib import Path

#pip install auto-py-to-exe

from lib.face_sdk.core.image_cropper.arcface_cropper.FaceRecImageCropper import FaceRecImageCropper
from lib.face_sdk.core.model_handler.face_alignment.FaceAlignModelHandler import FaceAlignModelHandler
from lib.face_sdk.core.model_handler.face_detection.FaceDetModelHandler import FaceDetModelHandler
from lib.face_sdk.core.model_loader.face_alignment.FaceAlignModelLoader import FaceAlignModelLoader
from lib.face_sdk.core.model_loader.face_detection.FaceDetModelLoader import FaceDetModelLoader

sys.path.append(str(Path(__file__).parent))

from definitions import CONFIG_LOGGING_PATH

import logging

mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING)
import logging.config

logging.config.fileConfig(CONFIG_LOGGING_PATH)
logger = logging.getLogger('api')

import yaml
import cv2
import numpy as np
from lib.face_sdk.core.model_loader.face_liveness.FaceLivenessModelLoader import FaceLivenessModelLoader
from lib.face_sdk.core.model_handler.face_liveness.FaceLivenessModelHandler import FaceLivenessModelHandler

with open('config/model_conf.yaml') as f:
    model_conf = yaml.full_load(f)

# common setting for all models, need not modify.
model_path = 'models'

scene = 'non-mask'
model_category = 'face_detection'
model_name = model_conf[scene][model_category]

logger.info('Start to load the face detection model...')
try:
    faceDetModelLoader = FaceDetModelLoader(model_path, model_category, model_name)
    model, cfg = faceDetModelLoader.load_model()
    faceDetModelHandler = FaceDetModelHandler(model, 'cpu', cfg)
except Exception as e:
    logger.error('Failed to load face detection Model.')
    logger.error(e)
    sys.exit(-1)
else:
    logger.info('Success!')

# face landmark model setting.
model_category = 'face_alignment'
model_name = model_conf[scene][model_category]
logger.info('Start to load the face landmark model...')
try:
    faceAlignModelLoader = FaceAlignModelLoader(model_path, model_category, model_name)
    model, cfg = faceAlignModelLoader.load_model()
    faceAlignModelHandler = FaceAlignModelHandler(model, 'cpu', cfg)
except Exception as e:
    logger.error('Failed to load face landmark model.')
    logger.error(e)
    sys.exit(-1)
else:
    logger.info('Success!')

model_category = 'face_liveness'
model_name = model_conf[scene][model_category]

logger.info('Start to load the face liveness model...')
try:
    faceLivenessModelLoader = FaceLivenessModelLoader(model_path, model_category, model_name)
    model, cfg = faceLivenessModelLoader.load_model()
    faceLivenessModelHandler = FaceLivenessModelHandler(model, 'cpu', cfg)
except Exception as e:
    logger.error('Failed to load face liveness Model.')
    logger.error(e)
    sys.exit(-1)
else:
    logger.info('Success!')

face_cropper = FaceRecImageCropper()
video_capture = cv2.VideoCapture(0)
bbox = None
process_this_frame = True

while True:
    ret, frame = video_capture.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    real = False

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        dets = faceDetModelHandler.inference_on_image(small_frame)
        face_nums = dets.shape[0]
        bbox = dets
        for i in range(face_nums):
            landmarks = faceAlignModelHandler.inference_on_image(small_frame, dets[i])
            landmarks_list = []
            for (x, y) in landmarks.astype(np.int32):
                landmarks_list.extend((x, y))
            cropped_image = face_cropper.crop_image_by_mat(small_frame, landmarks_list)

            res = faceLivenessModelHandler.inference_on_image(cropped_image)
            logger.info('The similarity score of spoofing face'': %f' % res)
            if res > 0.5:
                real = True

    process_this_frame = not process_this_frame

    # Display the results
    for box in bbox:
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
        if real:
            cv2.putText(frame, 'Real', (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        else:
            cv2.putText(frame, 'Fake', (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
