"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from sklearn.svm import SVC

from pyjamas.rimage.rimclassifier.rimclassifier import rimclassifier
from pyjamas.rutils import RUtils


class svm(rimclassifier):
    KERNEL_TYPES = ('linear', )

    DEFAULT_KERNEL_TYPE: int = 0

    # Missed class penalty: small values (0.05) result in some additional nuclei detected and others
    # not. Large values (100) do not seem to change the result with respect to 1.0.
    DEFAULT_C: float = 1.0

    # Should featurecalculator be a class attribute?
    def __init__(self, parameters: dict = None):
        super().__init__(parameters)

        # SVM-specific parameters.
        self.misclass_penalty_C: float = parameters.get('C', svm.DEFAULT_C)
        self.kernel_type: int = parameters.get('kernel_type', svm.DEFAULT_KERNEL_TYPE)
        self.classifier = parameters.get('classifier', SVC(kernel=svm.KERNEL_TYPES[self.kernel_type], C=self.misclass_penalty_C,
                                       random_state=1, probability=True))

    def save_classifier(self, filename: str) -> bool:
        theclassifier = {
            'positive_training_folder': self.positive_training_folder,
            'negative_training_folder': self.negative_training_folder,
            'hard_negative_training_folder': self.hard_negative_training_folder,
            'train_image_size': self.train_image_size,
            'fc': self.fc,
            'step_sz': self.step_sz,
            'C': self.misclass_penalty_C,
            'kernel_type': self.kernel_type,
            'iou_threshold': self.iou_threshold,
            'prob_threshold': self.prob_threshold,
            'max_num_objects_dial': self.max_num_objects,
            'classifier': self.classifier,
            'features_positive_array': self.features_positive_array,
            'features_negative_array': self.features_negative_array,
        }

        return RUtils.pickle_this(theclassifier, RUtils.set_extension(filename, rimclassifier.CLASSIFIER_EXTENSION))
