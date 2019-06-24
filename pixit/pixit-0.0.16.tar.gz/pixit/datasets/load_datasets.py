import os
import matplotlib.pyplot as plt
import pixit


def load_animals():
    animals_folder = os.path.join(os.path.dirname(__file__), 'images/animals')
    files = [os.path.join(animals_folder, filename) for filename in sorted(os.listdir(animals_folder))]
    images = [plt.imread(img) for img in files]
    label_names = ['elephant', 'giraffe', 'tiger', 'zebra']

    return pixit.ImageSet(images, label_names=label_names)

# def load_faces():
#     faces_folder = os.path.join(os.path.dirname(__file__), 'images/faces', '*.jpg')
#     files = glob.glob(faces_folder)
#     images = [plt.imread(img) for img in files]
#     # label_names = ['elephant', 'giraffe', 'tiger', 'zebra']

#     return pixit.ImageSet(images)
