from datetime import datetime
from pathlib import Path
import os
import pickle
import logging
import sys

sys.path.append(str(Path(__file__).parent))

import cv2
import numpy as np
import yaml
from imutils import paths

from lib.face_sdk.core.model_loader.face_detection.FaceDetModelLoader import FaceDetModelLoader
from lib.face_sdk.core.model_handler.face_detection.FaceDetModelHandler import FaceDetModelHandler
from lib.face_sdk.core.model_loader.face_alignment.FaceAlignModelLoader import FaceAlignModelLoader
from lib.face_sdk.core.model_handler.face_alignment.FaceAlignModelHandler import FaceAlignModelHandler
from lib.face_sdk.core.image_cropper.arcface_cropper.FaceRecImageCropper import FaceRecImageCropper
from lib.face_sdk.core.model_loader.face_recognition.FaceRecModelLoader import FaceRecModelLoader
from lib.face_sdk.core.model_handler.face_recognition.FaceRecModelHandler import FaceRecModelHandler
import definitions

logger = logging.getLogger('create_db')

model_path = 'models'
with open('config/model_conf.yaml') as f:
    model_conf = yaml.full_load(f)

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

model_category = 'face_recognition'
model_name = model_conf[scene][model_category]
logger.info('Start to load the face recognition model...')
try:
    faceRecModelLoader = FaceRecModelLoader(model_path, model_category, model_name)
    model, cfg = faceRecModelLoader.load_model()
    faceRecModelHandler = FaceRecModelHandler(model, 'cpu', cfg)
except Exception as e:
    logger.error('Failed to load face recognition model.')
    logger.error(e)
    sys.exit(-1)
else:
    logger.info('Success!')


face_cropper = FaceRecImageCropper()


known_face_feature = []
known_face_metadata = []
imagePaths = list(paths.list_images('data/faces'))


def create_database():
    for (i, imagePath) in enumerate(imagePaths):
        name = imagePath.split(os.path.sep)[-1].split('.')[0]

        image = cv2.imread(imagePath)
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        dets = faceDetModelHandler.inference_on_image(image)
        face_nums = dets.shape[0]

        for i in range(face_nums):
            landmarks = faceAlignModelHandler.inference_on_image(image, dets[i])
            landmarks_list = []
            for (x, y) in landmarks.astype(np.int32):
                landmarks_list.extend((x, y))
            cropped_image = face_cropper.crop_image_by_mat(image, landmarks_list)

            face_image = cv2.resize(cropped_image, (150, 150), fx=0.25, fy=0.25)

            feature = faceRecModelHandler.inference_on_image(cropped_image)

            known_face_feature.append(feature)
            known_face_metadata.append({
                "ident": name,
                "first_seen_this_interaction": datetime.now(),
                "last_seen": datetime.now(),
                "seen_count": 1,
                "seen_frames": 1,
                "face_image": face_image,
            })

    data = [np.array(known_face_feature), known_face_metadata]

    f = open("data/database/faces_jetson2.dat", "wb")
    f.write(pickle.dumps(data))
    f.close()
