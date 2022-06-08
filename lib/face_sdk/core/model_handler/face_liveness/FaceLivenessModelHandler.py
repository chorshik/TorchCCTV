import logging.config

from torchvision.transforms import transforms

logging.config.fileConfig("config/logging.conf")
logger = logging.getLogger('sdk')

import numpy as np
import torch

from ..BaseModelHandler import BaseModelHandler
from ....utils.BuzException import *


class FaceLivenessModelHandler(BaseModelHandler):
    def __init__(self, model, device, cfg):
        super().__init__(model, device, cfg)

    def inference_on_image(self, image):
        try:
            image = self._preprocess(image)
        except Exception as e:
            raise e
        image = image.unsqueeze(0)
        mask, binary = self.model.forward(image)
        res = torch.mean(mask).item()

        return res

    def _preprocess(self, image):
        if not isinstance(image, np.ndarray):
            logger.error('The input should be the ndarray read by cv2!')
            raise InputError()

        tfms = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ])

        image = tfms(image)
        return image
