import yaml

from train.ArcFace import ArcFace
from train.MagFace import MagFace


class HeadFactory:
    """Factory to produce head according to the head_conf.yaml

    Attributes:
        head_type(str): which head will be produce.
        head_param(dict): parsed params and it's value.
    """

    def __init__(self, head_type, head_conf_file):
        self.head_type = head_type
        with open(head_conf_file) as f:
            head_conf = yaml.load(f, Loader=yaml.FullLoader)
            self.head_param = head_conf[head_type]
        print('head param:')
        print(self.head_param)

    def get_head(self):
        if self.head_type == 'ArcFace':
            feat_dim = self.head_param['feat_dim'] # dimension of the output features, e.g. 512
            num_class = self.head_param['num_class'] # number of classes in the training set.
            margin_arc = self.head_param['margin_arc'] # cos(theta + margin_arc).
            margin_am = self.head_param['margin_am'] # cos_theta - margin_am.
            scale = self.head_param['scale'] # the scaling factor for cosine values.
            head = ArcFace(feat_dim, num_class, margin_arc, margin_am, scale)
        elif self.head_type == 'MagFace':
            feat_dim = self.head_param['feat_dim'] # dimension of the output features, e.g. 512
            num_class = self.head_param['num_class'] # number of classes in the training set.
            margin_am = self.head_param['margin_am'] # cos_theta - margin_am.
            scale = self.head_param['scale'] # the scaling factor for cosine values.
            l_a = self.head_param['l_a']
            u_a = self.head_param['u_a']
            l_margin = self.head_param['l_margin']
            u_margin = self.head_param['u_margin']
            lamda = self.head_param['lamda']
            head = MagFace(feat_dim, num_class, margin_am, scale, l_a, u_a, l_margin, u_margin, lamda)