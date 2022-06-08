import yaml

from train.MobileFaceNets import MobileFaceNet


class BackboneFactory:
    """Factory to produce backbone according the backbone_conf.yaml.

    Attributes:
        backbone_type(str): which backbone will produce.
        backbone_param(dict):  parsed params and it's value.
    """

    def __init__(self, backbone_type, backbone_conf_file):
        self.backbone_type = backbone_type
        with open(backbone_conf_file) as f:
            backbone_conf = yaml.load(f, Loader=yaml.FullLoader)
            self.backbone_param = backbone_conf[backbone_type]
        print('backbone param:')
        print(self.backbone_param)

    def get_backbone(self):
        if self.backbone_type == 'MobileFaceNet':
            feat_dim = self.backbone_param['feat_dim'] # dimension of the output features, e.g. 512.
            out_h = self.backbone_param['out_h'] # height of the feature map before the final features.
            out_w = self.backbone_param['out_w'] # width of the feature map before the final features.
            backbone = MobileFaceNet(feat_dim, out_h, out_w)