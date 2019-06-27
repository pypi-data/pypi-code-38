#---------------------------------
#
# Author: Caio Moraes
# Email: <caiomoraes.cesar@gmail.com>
# GitHub: MoraesCaio
#
# LAViD - Laboratório de Aplicações de Vídeo Digital
#
#---------------------------------

import argparse
import re


class CharPreprocessing:

    def preprocess(self, sentence):
        sentence = self._fix_decimals(sentence)
        # some ordinal numbers use '°' which can raise an exception on nltk
        sentence = sentence.replace('°', 'º')
        sentence = self.remove_useless_chars(sentence)
        return sentence

    def _fix_decimals(self, sentence):
        sentence = self._remove_useless_commas(sentence)
        # .0 or ,0 -> 0.0
        sentence = re.sub(r'^[\.,](?=\d)|(?<=\s)[\.,](?=\d)', '0,', sentence)
        sentence = self._replace_number_commas_dots(sentence)

        return sentence

    # for non numbers
    def _remove_useless_commas(self, sentence):
        sentence = re.sub(r'(,(?=\D)|,$)', '', sentence)
        return sentence

    # inside numbers (FIX for NLTK parsing)
    def _replace_number_commas_dots(self, sentence):

        for match in re.finditer(r'\d+[\.\,\d]+\d+', sentence):
            match_found = match.group()
            replacement = self._keep_only_decimal_separator(match_found)
            sentence = re.sub(match_found, replacement, sentence, count=1)

        return sentence

    def _keep_only_decimal_separator(self, number):
        if '.' in number and ',' in number:
            commas = number.count(',') - 1
            x0 = number.replace('.', '')  # .replace(',', '.')
            # remove all comma but the last
            x0 = ''.join(x0.rsplit(',', commas))
        elif ',' in number:
            x0 = number.replace(',', '.')
        elif number.count('.') > 1:
            x0 = number.replace('.', '')
        else:
            x0 = number
        return x0

    def _remove_chars(self, sentence, chars):
        # remove chars efficiently
        return sentence.translate(str.maketrans(dict.fromkeys(chars)))

    def remove_useless_chars(self, sentence):
        wout_symbol = self._remove_chars(sentence, '\\/{}()[]*"\':;@¹²³£#$%¢¨¬&_+§|“”«»–’‘')

        wout_dup_hyphen = re.sub(r'\-{2,}', '-', wout_symbol)

        # keep only 'word-word' cases
        wout_hyphen = re.sub(r'((^|\b|\s+)[\-\s]+(\-\b|\s+|$))', ' ', wout_dup_hyphen)
        wout_hyphen = re.sub(r'(?<=\d)-(?=\d)', '', wout_hyphen)

        return wout_hyphen

    def remove_multiple_spaces(self, sentence):
        return re.sub(r'\s{2,}', ' ', sentence).strip()

    def set_number_decimal_to_commas(self, sequence):
        for postag in sequence:
            if postag[1].startswith('NUM'):
                postag[0] = re.sub(r'[\,\.]|vírgula', ' , ', postag[0])
        return sequence

    def set_number_decimal_to_token(self, sequence):
        for postag in sequence:
            if postag[1].startswith('NUM'):
                postag[0] = re.sub(r'[\,\.]|vírgula', ' vírgula ', postag[0])
        return sequence

    def restore_punctuation(self, sentence):
        sentence = sentence.replace('[ponto]', '.')
        sentence = sentence.replace('[interrogação]', '?')
        sentence = sentence.replace('[exclamação]', '!')
        return sentence

    def is_single_letter(self, token):
        return token.isalpha() and len(token) == 1

    def summarize_train_file(self, sentence):
        # remove múltiplos símbolos sequenciais
        sentence = re.sub(r'\"( \")+( ?)', '\" ', sentence)
        sentence = re.sub(r"'( ')+( ?)", "' ", sentence)
        sentence = re.sub(r'#( #)+( ?)', '# ', sentence)
        # remove linhas que não contenham palavras
        sentence = re.sub(r'^[\"\'\#(\[ponto\])(\[interrogação\])(\[exclamação\])\.\?\! ]+$', '', sentence)

        return sentence


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('sentence', help='sentence')
    args, _ = parser.parse_known_args()

    print(CharPreprocessing().preprocess(args.sentence))


if __name__ == '__main__':
    main()
