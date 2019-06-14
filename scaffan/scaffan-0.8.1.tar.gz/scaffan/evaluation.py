# /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Used to support algorithm evaluation. For every inserted annotation it looks for lobulus boundary
and lobulus central vein. The segmentation is compared then and evaluated.
"""

from loguru import logger

import scaffan.image
import scaffan.lobulus
import numpy as np
import matplotlib.pyplot as plt


class Evaluation:
    def __init__(self):
        self.report = None
        self.evaluation_history = []
        pass

    def set_input_data(self, anim: scaffan.image.AnnotatedImage, annotation_id, lobulus:scaffan.lobulus.Lobulus):
        data = {}
        # lobulus.view
        inner_ids = anim.select_inner_annotations(annotation_id, color="#000000")
        if len(inner_ids) > 1:
            logger.warning("More than one inner annotation find to annotation with ID %i", annotation_id)
        elif len(inner_ids) > 0:
            inner_id = inner_ids[0]
            seg_true = lobulus.view.get_annotation_region_raster(annotation_id=inner_id) > 0
            seg = lobulus.central_vein_mask > 0

            dice0 = np.sum((seg & seg_true)) * 2
            dice1 = np.sum(seg) + np.sum(seg_true)
            dice = dice0 / dice1
            data["Central Vein Dice"] = dice
            if self.report is not None:
                fig = plt.figure()
                plt.imshow(seg_true.astype(np.int8) + seg.astype(np.int8))
                self.report.savefig_and_show("evaluation_central_vein_{}.png".format(annotation_id), fig=fig)

        outer_ids = anim.select_outer_annotations(annotation_id, color="#000000")
        if len(outer_ids) > 1:
            logger.warning("More than one outer annotation find to annotation with ID %i", annotation_id)
        elif len(outer_ids) > 0:
            outer_id = outer_ids[0]
            seg_true = lobulus.view.get_annotation_region_raster(annotation_id=outer_id) > 0
            seg = (lobulus.lobulus_mask + lobulus.central_vein_mask) > 0
            if self.report is not None:
                fig = plt.figure()
                plt.imshow(seg_true.astype(np.int8) + seg.astype(np.int8))
                self.report.savefig_and_show("evaluation_lobulus_border_{}.png".format(annotation_id), fig=fig)

            dice0 = np.sum((seg & seg_true)) * 2
            dice1 = np.sum(seg) + np.sum(seg_true)
            dice = dice0 / dice1
            data["Lobulus Border Dice"] = dice
        # inner_ids = anim.select_inner_annotations(annotaion_id, color="#000000")
        self.report.add_cols_to_actual_row(data)
        self.evaluation_history.append(data)
        pass

    def run(self):
        # TODO evaluate
        pass
