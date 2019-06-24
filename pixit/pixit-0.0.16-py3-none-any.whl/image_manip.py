import glob
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import Button
from matplotlib.widgets import LassoSelector as LS
from matplotlib.widgets import PolygonSelector as PS
from sklearn.utils import Bunch
from smartwidgets import EllipseSelector, RadioButtons, RectangleSelector


class ImageSet(Bunch):
    """Dataset of images"""
    def __init__(self, images, **kwargs):
        super().__init__(images=images, **kwargs)
        # do this to suppress errors
        if len(images) < 1:
            raise ValueError('images cannot be empty array-like.')
        self.images = images
        
    def label_images(self, label_names=None, label=None, random_order=False, random_state=None, fraction=1.0):
        """
        Display images for labeling in matplotlib figure. Results are saved to label.
        Numbers correspond to index of label_names. None indicated unlabeled.
        
        If random_order is False then images are displayed in order starting with the 
        first unlabeled image.
        
        fraction is a float between [0, 1] indicating how many images to label before
        automatically stopping (useful for semi-supervised learning purposes)
        """
        def draw_next_image():
            # check if enough have been done
            if np.sum(self.label==None) <= (1 - fraction) * len(self.label):
                plt.close(fig=fig)
            else:
                # allow for going from end back to beginning
                self.i = self.i % len(index_order)
                imgax.clear()
                imgax.imshow(self.images[index_order[self.i]])
                lab_num = self.label[index_order[self.i]] 
                lab = self.label_names[lab_num] if lab_num is not None else None
                imgax.set_title('Image: {}, Label: {}'.format(index_order[self.i], lab))
                fig.canvas.draw_idle()

        def on_next_handler(event):
            self.i += 1
            draw_next_image()

        def on_prev_handler(event):
            self.i -= 1
            draw_next_image()

        def on_save_handler(event):
            self.label[index_order[self.i]] = np.argwhere(self.label_names==rb.value_selected)[0][0]
            on_next_handler(event)

        def cleanup_handler(event):
            if hasattr(self, 'i'):
                self.pop('i')
            else:
                pass

        def handle_keys(event):
            if event.key == 'left':
                on_prev_handler(event)
            elif event.key == 'right':
                on_next_handler(event)
            elif event.key == 'enter':
                on_save_handler(event)
            elif event.key == 'up':
                ind = np.argwhere(self.label_names==rb.value_selected)[0][0]
                ind = (ind - 1) % len(self.label_names)
                rb.set_active(ind)
            elif event.key == 'down':
                ind = np.argwhere(self.label_names==rb.value_selected)[0][0]
                ind = (ind + 1) % len(self.label_names)
                rb.set_active(ind)
            elif event.key == 'q':
                cleanup_handler(event)

        # create label_names column if doesn't exist
        if label_names:
            self.label_names = np.array(label_names)
        else:
            # check if label_names already exists
            if not hasattr(self, 'label_names'):
                raise KeyError('label_names not found')
            else:
                self.label_names = np.array(self.label_names)

        # create label column if doesn't exist
        if label:
            # check if label is same length as images
            if label.shape[0] == len(self.images):
                self.label = np.array(label)
            else:
                raise ValueError('label must be the same length as images')
        else:
            if hasattr(self, 'label'):
                pass
            else:
                self.label = np.repeat(None, len(self.images))

        # check if fraction is between (0, 1]
        if not fraction >= 0 or not fraction <= 1:
            raise ValueError('fraction must be between [0, 1]')

        index_order = np.argwhere(self.label==None).reshape(-1)
        if index_order.size == 0:
            return
        if random_order is True:
            np.random.seed(random_state)
            index_order = np.random.choice(index_order, size=np.sum(self.label==None), replace=False)
        
        self.i = 0

        fig = plt.figure()
        size = 8
        grid = GridSpec(size, size, figure=fig)

        imgax = fig.add_subplot(grid[:, :-2])

        rbax = fig.add_subplot(grid[:-2, -2:])
        rb = RadioButtons(rbax, self.label_names)
        rb.set_active(0)

        nxax = fig.add_subplot(grid[-2, -1])
        nx = Button(nxax, '->')
        nx.on_clicked(on_next_handler)

        prevax = fig.add_subplot(grid[-2, -2])
        prev = Button(prevax, '<-')
        prev.on_clicked(on_prev_handler)

        saveax = fig.add_subplot(grid[-1, -2:])
        save = Button(saveax, 'Save')
        save.on_clicked(on_save_handler)

        imgax.set_title('Image: {}, Label: {}'.format(index_order[self.i], self.label[index_order[self.i]]))
        imgax.imshow(self.images[index_order[self.i]])

        fig.canvas.mpl_connect('close_event', cleanup_handler)
        fig.canvas.mpl_connect('key_press_event', handle_keys)
        
        plt.show()
        
    def annotate_images(self, annotation_names=None, annotation=None, selectors=None, random_order=False, fraction=1.0):
        """
        Display images for annotation
        """
        # create annotation_names column if doesn't exist
        if annotation_names:
            self.annotation_names = annotation_names
        else:
            # check if annotation_names already exists
            if not hasattr(self, 'annotation_names'):
                raise KeyError('annotation_names not found')

        if annotation:
            # check if annotation is same length as images
            if len(annotation) == len(self.images):
                self.annotation = annotation
            else:
                raise ValueError('annotation must be the same length as images')
        else:
            if hasattr(self, 'annotation'):
                pass
            else:
                self.annotation = [None for _ in range(len(self.images))]

    def append_images(self, other_images):
        """
        Function that will intelligently append images to self.images based on the format
        of self.images and will resize self.labe and self.annotation if they exist.
        """
        if isinstance(self.images, list):
            self.images.append(other_images)
        else: # np array
            try:
                self.images = np.stack(self.images, other_images)
            except:
                if isinstance(other_images, list):
                    self.images = self.images.tolist() + other_images
                else:
                    self.images = self.images.tolist() + other_images.tolist()

        if hasattr(self, 'label') and len(self.label) != len(self.images):
            self.label.append([None for _ in range(len(self.images) - len(self.label))])
        if hasattr(self, 'annotation') and len(self.annotation) != len(self.images):
            self.annotation.append([None for _ in range(len(self.images) - len(self.annotation))])
            
    @classmethod
    def load_images(cls, list_of_paths_or_folder, **kwargs):
        if isinstance(list_of_paths_or_folder, str):
            list_of_paths_or_folder = glob.glob(list_of_paths_or_folder)
        images = [plt.imread(f) for f in list_of_paths_or_folder]
        try:
            images = np.stack(images)
        except:
            print('Could not stack images due to varying sizes. This may not be ideal.')
            images = np.array(images)
        finally:
            return cls(images, **kwargs)

"""
To Do
    - make annotate_images method
    - create example scripts
    - find faces dataset
    - figure out licensing for images (check sklearn)
    - make other methods for ImageSet for saving/loading
    - check other libraries for loading images and csv files like cv2, csv
    - add all selectors as options for selecting
    - add better OOP to drawing (make labeling and annotating use the same functions???)
        # functions I would need to make both work together
        # - draw_image(self, i)
        # - save (label if there is one, annotation if there is one)
        # - _next
        # - _prev
        # - _quit

    - add way to add label/annotation in GUI
    - Button to make selectors work or not work/drop down menu
    - checks for empty images

"""

if __name__ == "__main__":
    from pixit import datasets
    animals = datasets.load_animals()
    print(animals)
    animals.label_images()