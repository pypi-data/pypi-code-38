import os
import math
import pickle
from enum import Enum
from collections import defaultdict
from data import load_model


class Lang(Enum):
    EN = 1
    # JA = 2


class TextTrans:
    """
    文字列の文字遷移パターンを学習し，生成遷移確率を計算する
    """

    mat = None
    non_pattern_prob = 0
    ngram = 1

    def __init__(self, lang: Lang = Lang.EN, model_path: str = None):
        if model_path is not None and os.path.exists(model_path) is True:
            self.load_model(model_path=model_path)
        elif lang is not None and lang == Lang.EN:
            self.load_model_data(load_model.model_en())

    def read_prob_mat(self, key0: str, key1: str):
        tmp_d = self.mat
        tmp_v = self.non_pattern_prob
        if self.mat:
            for key in [key0, key1]:
                tmp_v = tmp_d.get(key, self.non_pattern_prob)
                if isinstance(tmp_v, dict):
                    tmp_d = tmp_v
                else:
                    break
        return tmp_v

    def save_model(self, save_path: str = None):

        if save_path is None or len(save_path) == 0:
            print("[error] save_path {} is nothing".format(save_path))
            return

        if len(os.path.dirname(save_path)) > 0:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
        pickle.dump({"mat": self.mat,
                     "non_pattern_prob": self.non_pattern_prob,
                     "ngram": self.ngram},
                    open(save_path, "wb"))

    def load_model(self, model_path: str):
        if os.path.exists(model_path) is False:
            print("[error] save_path {} is not found".format(model_path))
            return
        try:
            model_data = pickle.load(open(model_path, "rb"))
            self.load_model_data(model_data=model_data)
        except Exception as e:
            print("e:", e)

    def load_model_data(self, model_data):
        try:
            self.mat = model_data["mat"]
            self.non_pattern_prob = model_data["non_pattern_prob"]
            self.ngram = model_data["ngram"]
        except Exception as e:
            print("e:", e)

    def train(self, train_path: str, save_path: str, ngram: int = 1):

        if os.path.exists(train_path) is False:
            print("[error] train_file {} is not found.".format(train_path))

        transition_mat = defaultdict(lambda: defaultdict(int))

        for line in open(train_path):
            tmp_line = line.rstrip("\r\n")
            for a, b in self.sublines_for_ngram(tmp_line, n=ngram):
                transition_mat[a][b] += 1

        # max normalization constant
        max_nc = 0
        for k, v in transition_mat.items():
            s = float(sum(v.values()))
            if max_nc < s:
                max_nc = s
        if max_nc == 0:
            max_nc = 50

        # to reduce data size, it calculates prob of patterns not in training data
        non_pattern_prob = math.log(1 / (max_nc * 2))

        # normalize
        for key0, dict0 in transition_mat.items():
            total = float(sum(dict0.values()))
            for key1, value1 in dict0.items():
                if value1 > 0:
                    dict0[key1] = math.log(float(value1)/ total)

        self.mat = dict(transition_mat)
        self.non_pattern_prob = non_pattern_prob
        self.ngram = ngram
        self.save_model(save_path=save_path)

    def prob(self, text: str):

        if self.mat is None:
            return 0

        log_prob = 0.0
        trans_ct = 0
        for a, b in self.sublines_for_ngram(text):
            p = self.read_prob_mat(a, b)
            log_prob += p
            trans_ct += 1
        prob = math.exp(log_prob / (trans_ct or 1))
        return prob

    def sublines_for_ngram(self, input_line: str, n=None):

        def subline_with_upper_limit(line, sub_index, sub_length):
            subline = line[sub_index:]
            if sub_length <= len(subline):
                subline = subline[:sub_length]
            return subline

        if n is None:
            n = self.ngram

        terminal_char = "\0"

        if terminal_char in input_line:
            line = input_line
        else:
            line = input_line + terminal_char

        char_list = [c for c in line]
        for index, c in enumerate(char_list):
            if c == terminal_char:
                continue

            sublines0 = subline_with_upper_limit(line, index, n)

            next_index = index + n
            if terminal_char in sublines0:
                sublines0 = sublines0.replace(terminal_char, "")
                next_index = index + len(sublines0)

            sublines1 = subline_with_upper_limit(line, next_index, n)

            yield sublines0, sublines1


if __name__ == "__main__":
    print("[demo] TestTrans")

    training_file = "./dataset/words_alpha.txt"
    model_file = "./dataset/en.pki"

    # tt = TextTrans()
    # tt.train(train_path=training_file, save_path=model_file)
    # print("p =", tt.prob("pen"))
    # print("p =", tt.prob("aaa"))

    tp2 = TextTrans()
    print("p =", tp2.prob("pen"))
    print("p =", tp2.prob("aaa"))
