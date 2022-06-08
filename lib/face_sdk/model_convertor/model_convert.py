import sys
import torch
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

import definitions
from lib.face_sdk.models.network_def.mobilefacenet_def import MobileFaceNet

model = MobileFaceNet(512, 7, 7)
model_dict = model.state_dict()

pretrained_model = ''
if not torch.cuda.is_available():
    pretrained_dict = torch.load(pretrained_model, map_location=torch.device('cpu'))['state_dict']
else:
    pretrained_dict = torch.load(pretrained_model)

new_pretrained_dict = {}
for k in model_dict:
    new_pretrained_dict[k] = pretrained_dict['backbone.'+k]

model_dict.update(new_pretrained_dict)
model.load_state_dict(model_dict)
#model.cuda()
model.cpu()
torch.save(model, 'face_recognition_mv.pkl')
