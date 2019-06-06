
import sys
import pickle
import numpy as np
from sklearn.svm import SVC

class SVClassifier:

    def __init__(self):
        self.model = SVC(kernel='linear', probability=True)
        self.class_names = None

    def train(self, train_image_array, class_names, labels_train):
        self.class_names = class_names
        self.model.fit(train_image_array, labels_train)

    def save(self, output_filename="svclassifier.pkl"):
        with open(output_filename, "wb") as f:
            pickle.dump(self, f)

    def predict(self, test_image_array):

        predictions = self.model.predict_proba(test_image_array)
        best_class_indices = np.argmax(predictions, axis=1)
        best_class_probabilities = predictions[np.arange(len(best_class_indices)), best_class_indices]

        return best_class_indices, best_class_probabilities

    @staticmethod
    def load(save_file):
        with open(save_file, "rb") as f:
            return pickle.load(f)


def load_images(embeddings_file):

    # Load all images
    classes = {}
    nrof_images = 0
    with open(embeddings_file, 'r') as f:
        for line in f:
            tokens = line.split(",")
            filename = tokens[0]
            filename_no_ext = filename.split(".")[0]
            class_name = " ".join(filename_no_ext.split("_")[:-1])

            embedding = np.array([float(e) for e in tokens[1:]])
            if class_name not in classes:
                classes[class_name] = {}

            classes[class_name][filename_no_ext] = embedding
            nrof_images += 1
    embedding_size = len(list(list(classes.values())[0].values())[0])

    images_array = np.zeros((nrof_images, embedding_size))
    images_array_index = 0
    labels = []

    class_names = list(classes.keys())

    for i in range(len(classes)):
        class_name = class_names[i]

        images = list(classes[class_name].keys())
        np.random.shuffle(images)

        for image in images:
            images_array[images_array_index, :] = classes[class_name][image]
            images_array_index = images_array_index + 1
        labels += [i] * len(images)

    return class_names, images_array, labels

if __name__ == '__main__':

    if len(sys.argv) < 4:

        print("--------------------------------")
        print("This script receives an embeddings csv file with rows in format: filename,emb1,emb2,... ")
        print("If running TRAIN mode, it trains an SV classifier and saves the resulting object to the specified file")
        print("If running TEST mode, it tests each embedding against a trained model in the specified file and prints the results")
        print("")
        print("Usage: ")
        print("python classifier_support_vector.py TRAIN 'embeddings_file' 'picklefile'")
        print("Or: ")
        print("python classifier_support_vector.py TEST 'embeddings_file' 'picklefile'")
        print("--------------------------------")

    else:

        seed = 666
        np.random.seed(seed=seed)

        mode = sys.argv[1]
        embeddings_file = sys.argv[2]
        pickle_file = sys.argv[3]

        if mode == "TRAIN":

            class_names, train, labels_train = load_images(embeddings_file)

            # Train classifier
            classifier = SVClassifier()
            classifier.train(train, class_names, labels_train)

            # Save trained classifier
            classifier.save(pickle_file)

        elif mode == "TEST":

            class_names, test, labels_test = load_images(embeddings_file)

            # Load classifier
            classifier = SVClassifier.load(pickle_file)

            # Test classifier
            best_class_indices, best_class_probabilities = classifier.predict(test)

            for i in range(len(best_class_indices)):
                print('%4d  Real: %s, Predicted: %s, Prob: %.3f' % (i, class_names[labels_test[i]], class_names[best_class_indices[i]], best_class_probabilities[i]))

            accuracy = np.mean(np.equal(best_class_indices, labels_test))
            print('Accuracy: %.3f' % accuracy)

        else:

            print("Wrong mode, use 'TRAIN' or 'TEST'")