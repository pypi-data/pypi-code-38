#!python

import sys
import numpy as np
from sklearn.svm import SVC


if __name__ == '__main__':

    if len(sys.argv) < 2:

        print("--------------------------------")
        print("This script receives an embeddings csv file with rows in format: filename,emb1,emb2,... "
              "And outputs the class for each row and total accuracy")
        print("")
        print("Usage: ")
        print("python classifier_support_vector_simple.py 'embeddings_filename'")
        print("Or: ")
        print("python classifier_support_vector_simple.py 'embeddings_filename' min_nrof_images_per_class nrof_train_images_per_class")
        print("--------------------------------")

    else:

        seed = 666
        np.random.seed(seed=seed)

        embeddings_file = sys.argv[1]

        if len(sys.argv) >= 3:
            min_nrof_images_per_class = int(sys.argv[2])
        else:
            min_nrof_images_per_class = 30

        if len(sys.argv) >= 4:
            nrof_train_images_per_class = int(sys.argv[3])
        else:
            nrof_train_images_per_class = 10

        # Load all images
        classes = {}
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
        embedding_size = len(list(list(classes.values())[0].values())[0])

        # Remove class with less than 'min_nrof_images_per_class' images
        for class_name in list(classes.keys()):
            if len(classes[class_name]) < min_nrof_images_per_class:
                classes.pop(class_name)

        # Separate into TRAIN and TEST embeddings
        nrof_train_images = nrof_train_images_per_class * len(classes)
        train = np.zeros((nrof_train_images, embedding_size))
        labels_train = []
        train_index = 0

        nrof_test_images = sum(len(classes[k]) for k in classes) - nrof_train_images_per_class * len(classes)
        test = np.zeros((nrof_test_images, embedding_size))
        labels_test = []
        test_index = 0

        class_names = list(classes.keys())
        for i in range(len(classes)):
            class_name = class_names[i]

            images = list(classes[class_name].keys())
            np.random.shuffle(images)

            for image in images[:nrof_train_images_per_class]:
                train[train_index, :] = classes[class_name][image]
                train_index = train_index + 1
            labels_train += [i] * len(images[:nrof_train_images_per_class])

            for image in images[nrof_train_images_per_class:]:
                test[test_index, :] = classes[class_name][image]
                test_index = test_index + 1
            labels_test += [i] * len(images[nrof_train_images_per_class:])

        # Train classifier
        model = SVC(kernel='linear', probability=True)
        model.fit(train, labels_train)

        # Test classifier
        predictions = model.predict_proba(test)
        best_class_indices = np.argmax(predictions, axis=1)
        best_class_probabilities = predictions[np.arange(len(best_class_indices)), best_class_indices]

        for i in range(len(best_class_indices)):
            print('%4d  Real: %s, Predicted: %s, Prob: %.3f' % (i, class_names[labels_test[i]], class_names[best_class_indices[i]], best_class_probabilities[i]))

        accuracy = np.mean(np.equal(best_class_indices, labels_test))
        print('Accuracy: %.3f' % accuracy)
