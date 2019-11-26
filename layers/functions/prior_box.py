#-*- coding:utf-8 -*-

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import torch
from itertools import product as product
from math import sqrt as sqrt


class PriorBox(object):
    """Compute priorbox coordinates in center-offset form for each source
    feature map.
    """

    def __init__(self, input_size, cfg):
        super(PriorBox, self).__init__()
        self.imh = input_size[0]
        self.imw = input_size[1]

        # number of priors for feature map location (either 4 or 6)
        self.variance = cfg.VARIANCE or [0.1]
        self.feature_maps = cfg.FEATURE_MAPS
        self.min_sizes = cfg.ANCHOR_SIZES
        self.asp_ratios =cfg.ASP_RATIOS
        self.steps = cfg.STEPS
        self.clip = cfg.CLIP
        for v in self.variance:
            if v <= 0:
                raise ValueError('Variances must be greater than 0')

    def forward(self):
        mean = []
        for k in range(len(self.feature_maps)):
            feath = self.feature_maps[k][0]
            featw = self.feature_maps[k][1]
            for i, j in product(range(feath), range(featw)):
                f_kw = self.imw / self.steps[k]
                f_kh = self.imh / self.steps[k]

                cx = (j + 0.5) / f_kw
                cy = (i + 0.5) / f_kh

                s_kw = self.min_sizes[k] / self.imw
                s_kh = self.min_sizes[k] / self.imh
                asp = self.asp_ratios[k]

                mean += [cx, cy, s_kw/sqrt(asp), s_kh*sqrt(asp)]

        output = torch.Tensor(mean).view(-1, 4)
        if self.clip:
            output.clamp_(max=1, min=0)
        return output
