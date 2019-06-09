from zumi.util.screen import Screen
from zumi.zumi import Zumi
from random import uniform
import numpy as np
import cv2
import os

from sklearn.utils import shuffle
from sklearn.neighbors import KNeighborsClassifier

class Reaction():
    zumi = Zumi()
    eye = Screen()
    zumi.start_MPU()
    eye = Screen()
    emotions = ["sad1", "happy_1", "sleep", "none"]
    motions = ["forward", "backward", "left", "right", "circle", "triangle", "square", "none"]

    def __init__(self, emotion="", motion="", sound=""):
        self.emotion = emotion
        self.motion = motion
        self.sound = sound

    def print_info(self):
        print("Emotions [ " + ', '.join(Reaction.emotions) + "]")
        print("Motions [ " + ', '.join(Reaction.motions) + "]")
        print("Sounds [ type with in 0 - 60 , it's same as C2 - B6 notes  or  type '-1' to play nothing ]")

    def do_reaction(self):
        if self.emotion in Reaction.emotions:
            if self.emotion != "none":
                Reaction.eye.draw_image_by_name(self.emotion)

        if self.motion in Reaction.motions:
            if self.motion != "none":
                Reaction.zumi.command_drive(self.motion)

        if self.sound in range(0, 60):
            Reaction.zumi.play_note(self.sound)

class KnnClassifier():
    upper = [180, 255, 255]

    def __init__(self, demo_name="",path=""):
        self.knn = KNeighborsClassifier()

        self.demo_name = demo_name

        self.label_names = []
        self.feature_names = []
        self.label_keys = []
        self.label_num = len(self.label_names)
        self.feature_num = len(self.feature_names)
        self.labels = []
        self.features = []

        self.divided_labels = []
        self.divided_features = []
        if path == "":
            self.path = os.getcwd()
        else:
            self.path = '/home/pi/robolink-zumi-demos/demos/machine-learning-demos/knn-classification'
        self.data_file_name = self.demo_name + "_KNN_data"
        self.current_image = ''
        self.current_hsv_value = ''
        self.current_label = ''

        self.reactions = []
        self.predicts = None

        self.label_cnt = -1
        if not (os.path.isdir("datas")):
            os.makedirs(os.path.join("datas"))
    
    def read_datas(self):
        while True :
            self.demo_name = input("What do you want to test? : ")

            if os.path.isdir("datas/" + self.demo_name):
                print("Okay, start ", self.demo_name)
                self.set_values_from_data()
                break
            else :
                print("There's no ", self.demo_name)        
            
    def set_values(self):
        if self.demo_name == "":
            self.demo_name = input("What is the name of this demo? : ")

        if os.path.isdir("datas/" + self.demo_name):
            if "y" == input("You already have this named data. Do you want to predict by the data? (y/n) : "):
                self.set_values_from_data()
                return False
            else:
                self.demo_name = ""
                return self.set_values()
        else:
            self.data_file_name = self.demo_name + "_KNN_data"
            while True:
                try:
                    self.label_num = int(input("What is the total number of labels? : "))
                except ValueError:
                    print("Type only integer, please.")
                else:
                    break

            for i in range(self.label_num):
                self.label_names.append(input("type label name (" + str(i + 1) + "/" + str(self.label_num) + ") : "))
                key = 'n'
                while key == 'n':
                    key = input(
                        "type keyboard command of this label (" + str(i + 1) + "/" + str(self.label_num) + ") : ")
                self.label_keys.append(key)

            while True:
                try:
                    self.feature_num = 3  # int(input("What is the total number of features? : "))
                except ValueError:
                    print("Type only integer, please.")
                else:
                    break

            # for i in range(self.feature_num):
            # input("type feature (" + str(i+1) + "/" + str(self.feature_num) + ") : "))
            self.feature_names.append('h')
            self.feature_names.append('s')
            self.feature_names.append('v')

            return True

    def set_values_from_data(self, demo_name=""):
        if demo_name == "":
            demo_name = self.demo_name
        else :
            self.demo_name = demo_name

        self.data_file_name = demo_name + "_KNN_data"
        file_path = self.path + "/datas/" + self.demo_name + "/" + self.data_file_name + ".txt"
        current_label = ""
        with open(file_path) as f:
            for line in f.readlines():
                line = line.split(' ')
                if line[0] == "Labels":
                    for cursor in line[2:-1]:
                        self.label_names.append(cursor)
                    self.label_num = len(self.label_names)

                elif line[0] == "Reactions":
                    reaction = []
                    for cursor in line[2:-1]:
                        if cursor == "(":
                            reaction = []
                        elif cursor == ")":
                            self.reactions.append(Reaction(reaction[0], reaction[1], int(reaction[2])))
                        else:
                            reaction.append(cursor)

                elif line[0] == "Features":
                    for cursor in line[2:-1]:
                        self.feature_names.append(cursor)
                    self.feature_num = len(self.feature_names)

                elif line[0] in self.label_names:
                    current_label = line[0]

                elif line[0] == ">":
                    feature = []
                    for cursor in line[1:-1]:
                        feature.append(int(cursor))
                    self.labels.append(current_label)
                    self.features.append(feature)

    def set_reactions(self):
        temp = Reaction()
        temp.print_info()

        print("If you don't want to select emotion/motion, type none")
        for label in self.label_names:
            while True:
                emotion = input("Which emotion for " + label + " : ")
                if emotion in temp.emotions:
                    break
                print("type again")
            while True:
                motion = input("Which motion for " + label + " : ")
                if motion in temp.motions:
                    break
                print("type again")
            while True:
                try:
                    sound = int(input("Which sound for " + label + " : "))
                    if sound in range(-1, 60):
                        break
                except ValueError:
                    print("type integer")

            self.reactions.append(Reaction(emotion, motion, sound))

    def add_data(self, label, feature):
        if label not in self.label_keys and label not in self.label_names:
            print("There's no " + label + ".")
            return

        label = self.label_names[self.label_keys.index(label)]
        self.current_label = label
        self.label_cnt += 1

        if not isinstance(feature, list):
            feature = self.get_hsv_data(feature)

        self.labels.append(label)
        self.features.append(feature)

    def get_hsv_data(self, image):
        image = cv2.flip(image, -1)
        height, width, channel = image.shape

        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        rgb = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        h, s, v = cv2.split(hsv)

        top = int(height / 2 - 2 * height / 10)
        bottom = int(height / 2)
        left = int(width / 2 - width / 10)
        right = int(width / 2 + width / 10)

        h = h[top:bottom, left:right]
        s = s[top:bottom, left:right]
        v = v[top:bottom, left:right]

        cv2.rectangle(rgb, (left, top), (right, bottom), (255, 0, 0), 2)

        mean_h = int(np.mean(h))
        mean_s = int(np.mean(s))
        mean_v = int(np.mean(v))

        print(mean_h, mean_s, mean_v)
        self.current_hsv_value = [mean_h, mean_s, mean_v]
        self.current_image = rgb

        return self.current_hsv_value

    def get_accuracy(self):
        X, Y = shuffle(self.features, self.labels, random_state=0)

        cut = int(len(X) / 10)
        if cut == 0:
            print("There are not enough Datas, add more.")
            return

        X_train = X[:-cut]
        Y_train = Y[:-cut]
        X_test = X[-cut:]
        Y_test = Y[-cut:]

        self.knn.fit(X_train, Y_train)

        print(self.knn.predict(X_test))
        print(Y_test)

        n = 0
        for i in range(0, len(self.knn.predict(X_test))):
            if self.knn.predict(X_test)[i] == Y_test[i]:
                n += 1
        accuracy = (n / len(Y_test)) * 100

        print("Accuracy : " + str(accuracy))

        return accuracy

    def predict(self, features):
        if not isinstance(features, list):
            features = self.get_hsv_data(features)

        pred_list = []
        pred_list.append(features)

        self.knn.fit(self.features, self.labels)
        self.predicts = self.knn.predict(pred_list)

        return self.predicts

    def is_in_labels(self, label):
        return label in self.label_names or label in self.label_keys

    def do_reaction(self):
        index = self.label_names.index(self.predicts[0])
        if len(self.reactions) > 0:
            self.reactions[index].do_reaction()

    def save_image(self):
        file_name = self.path + "/datas/" + self.demo_name + "/images/" + self.current_label + "." + str(
            self.label_cnt) + "[" + '_'.join(map(str, self.current_hsv_value)) + "].jpg"
        cv2.imwrite(file_name, self.current_image)

    def save_data_set(self):
        self.remove_outlier()

        try:
            dic = "datas/" + self.demo_name
            if not (os.path.isdir(dic)):
                os.makedirs(os.path.join(dic))
                os.makedirs(os.path.join(dic + "/images"))
        except OSError as e:
            if e.errno != errno.EEXIST:
                print("Failed to create directory!!!!!")
                raise

        f = open(self.path + "/datas/" + self.demo_name + "/" + self.data_file_name + ".txt", 'w')

        f.write('[' + self.data_file_name + ']\n')
        f.write("Labels : " + " ".join(self.label_names) + " \n")
        f.write("Reactions : ")
        for reaction in self.reactions:
            f.write("( " + reaction.emotion + " " + reaction.motion + " " + str(reaction.sound) + " ) ")
        f.write(" \n")
        f.write("Features : " + " ".join(self.feature_names) + " \n")

        current_label_name = ""
        for i in range(len(self.labels)):
            if current_label_name != self.labels[i]:
                f.write(self.labels[i] + " ---------- \n")
                current_label_name = self.labels[i]
            f.write("> " + ' '.join(map(str, self.features[i])) + ' \n')

        f.close()

    def divide_datas(self):
        self.labels, self.features = zip(*sorted(zip(self.labels, self.features)))

        divided_labels = [None] * (self.label_num)
        divided_features = [None] * (self.label_num)

        current_label_name = self.labels[0]
        prev_idx = 0
        for i in range(1, len(self.labels)):
            if current_label_name != self.labels[i] or i == len(self.labels) - 1:
                idx = self.label_names.index(self.labels[i - 1])
                if i == len(self.labels) - 1:
                    i = len(self.labels)
                else:
                    current_label_name = self.labels[i]
                divided_labels[idx] = self.labels[prev_idx:i]
                divided_features[idx] = self.features[prev_idx: i]
                prev_idx = i

        self.divided_labels = divided_labels
        self.divided_features = divided_features

    def remove_outlier(self):
        self.divide_datas()

        divided_features = []
        divided_labels = []
        for i in range(self.label_num):
            features = list(self.divided_features[i])
            labels = list(self.divided_labels[i])
            length = len(labels)
            features = features[int(length/5):int(length-length/5)]
            means = np.array(np.mean(features, axis=0))
            stds = np.array(np.std(features, axis=0))

            for j in range(length - len(features)):
                random_val = uniform(-2, 2)
                stds = np.array(random_val * stds)
                feature = []
                for k in range(self.feature_num):
                    temp = int(means[k] + stds[k])
                    if temp > KnnClassifier.upper[k]:
                        temp = KnnClassifier.upper[k]
                    elif temp < 0 :
                        temp = 0
                    feature.append(temp)

                features.append(feature)
            divided_features.append(features)
            divided_labels.append(labels)

        self.divided_features = divided_features
        self.divided_labels = divided_labels

        sorted_labels = []
        sorted_features = []

        for i in range(self.label_num):
            sorted_labels += self.divided_labels[i]
            sorted_features += self.divided_features[i]

        self.labels = sorted_labels
        self.features = sorted_features
