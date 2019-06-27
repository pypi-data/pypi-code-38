#---------------------------------
#
# Author: Caio Moraes
# Email: <caiomoraes.cesar@gmail.com>
# GitHub: MoraesCaio
#
# LAViD - Laboratório de Aplicações de Vídeo Digital
#
#---------------------------------

from .aelius_tagger import ClassificaSentencas
from .name_checking import NameChecking
from .lemma import Lemma
from .orthography import Orthography
from .char_preprocessing import CharPreprocessing
from .number import Number
import argparse
import re
import copy
import sys


class Translation():

    name_symbol = '"'
    num_symbol = '\''
    error_symbol = '#'

    def __init__(self):
        self.char_prep = CharPreprocessing()
        self.classifier = ClassificaSentencas()
        self.name_checking = NameChecking()
        self.orthography = Orthography()
        self.lemmatizer = Lemma()
        self.number = Number()

    def pipeline(self, phrase, save_names=False, save_typos=False, train_files=False, pp_pt=False, glosa=False, verbose=0):
        '''
        Many operations are common for both preprocessing and translation for libras, so this function do both on the same pipeline to avoid redundancy.
        The sentences are returned as follows:
            <tuple> (<str> portuguese_train_sentence, <str> libras_train_sentence, <str> portuguese_test_sentence, <str> libras_rule_translation)
        '''
        if not phrase.strip():
            # pp_pt_train, pp_glosa_train, pp_pt_test, rbmt_glosa
            return '', '', '', ''

        # remove useless chars and some applying some preprocessing for numbers
        phrase = self.char_prep.preprocess(phrase)

        tagged = self.classifier.iniciar_classificacao(phrase)[1]

        # redução de tags de números por extenso para cardinais
        tagged = self.number.simplificar_sentenca(tagged)
        # pontos decimais são substituídos por vírgulas
        tagged = self.char_prep.set_number_decimal_to_commas(tagged)
        # caixa baixa
        tagged = [[tag[0].lower(), tag[1]] for tag in tagged]

        test_or_glosa = pp_pt or glosa
        # copy for test_or_glosa file
        if test_or_glosa:
            test_tagged = copy.deepcopy(tagged)

        # SUBSTITUIÇÃO POR SÍMBOLOS
        # se é arquivo de teste, NÃO substitui NOMES, NÚMEROS e ERROS ORTOGRÁFICAOS por símbolos
        for tag in tagged:

            # NÚMERO
            if 'NUM' in tag[1] and not tag[0].isalpha():
                tag[0] = re.sub(r'\d+', self.num_symbol, tag[0])

            # NOME PRÓPRIO (DETECÇÃO DO AELIUS)
            elif 'NPR' in tag[1]:
                tag[0] = self.name_symbol

            # NOME PRÓPRIO (DETECÇÃO DO DICIONÁRIO DE NOMES)
            # não é verbo ser, estar, haver, ter ou outro verbo
            # PS.: encontrei muitos nomes homônimos de verbos;
            #       talvez não seja mais necessário verificar isso
            elif self.name_checking.is_tag_name(tag):
                tag[0] = self.name_symbol
                tag[1] = 'NPR'

            # ERRO ORTOGRÁFICO
            # 'não é pontuação, símbolo reservado, número ou nome e está errado'
            elif not tag[1].startswith('SPT') and\
                    not self.orthography.check(tag[0]):
                tag[0] = self.error_symbol

        # tags
        if verbose > 1:
            print_verbose('tagged (train):', tagged, verbose=verbose)
            if test_or_glosa:
                print_verbose('tagged (test):', test_tagged, verbose=verbose)

        # OUTPUTS
        pp_pt_train, pp_glosa_train = '', ''
        pp_pt_test, rbmt_glosa = '', ''

        # train files
        if train_files:
            pp_pt_train = self.pt_final_steps(tagged)
            pp_pt_train = self.char_prep.summarize_train_file(pp_pt_train)
            print_verbose('\nPT-BR (treino):\n' + pp_pt_train, verbose=verbose)
            pp_glosa_train = self.glosa_final_steps(tagged)
            pp_glosa_train = self.char_prep.summarize_train_file(pp_glosa_train)
            print_verbose('\nGLOSA (treino):\n' + pp_glosa_train, verbose=verbose)

        # test file
        if pp_pt:
            pp_pt_test = self.pt_final_steps(test_tagged)
            print_verbose('\nPT-BR (teste):\n' + pp_pt_test, verbose=verbose)

        # RBMT glosa
        if glosa:
            rbmt_glosa = self.glosa_final_steps(test_tagged)
            print_verbose('\nGLOSA (rule):\n' + rbmt_glosa, verbose=verbose)

        return pp_pt_train, pp_glosa_train, pp_pt_test, rbmt_glosa

    def pt_final_steps(self, tagged):
        # concatena sentença e desfazendo parsing de [ponto], [exclamação] e [interrogação]
        pt_sentence = ' '.join(tag[0] for tag in tagged)
        pt_sentence = self.char_prep.restore_punctuation(pt_sentence)

        return pt_sentence

    def glosa_final_steps(self, tagged):
        # substitui o símbolo de vírgula pela palavra 'vírgula' (apenas para números)
        tagged = self.char_prep.set_number_decimal_to_token(tagged)
        # lematiza, concatena sentença e apaga excesso de espaços
        glosa_sentence = [self.lemmatizer.lemmatize_aelius_tag(t)[0].upper() for t in tagged]
        glosa_sentence = ' '.join(glosa_sentence)
        glosa_sentence = self.char_prep.remove_multiple_spaces(glosa_sentence)

        return glosa_sentence

    def rule_translation(self, phrase):
        _, _, _, glosa_sentence = self.pipeline(phrase, glosa=True)

        return glosa_sentence

    def preprocess_pt(self, phrase):
        _, _, preprocessed_pt, _ = self.pipeline(phrase, pp_pt=True)

        return preprocessed_pt

    def preprocess_train_files(self, phrase):
        train_pt, train_glosa, _, _ = self.pipeline(phrase, train_files=True)

        return train_pt, train_glosa


def print_verbose(*objects, sep=' ', end='\n', file=sys.stdout, flush=False, verbose=0):
    if verbose > 0:
        print(*objects, sep=sep, end=end, file=file, flush=flush)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('phrase', help='Phrase')
    parser.add_argument('-n', '--save-names', action='store_true', help='Saves names.')
    parser.add_argument('-e', '--save-errors', action='store_true', help='Saves typos.')
    parser.add_argument('-t', '--train-files', action='store_true', help='Preprocessing for train files.')
    parser.add_argument('-p', '--preprocess-pt', action='store_true', help='Preprocessing for test file.')
    parser.add_argument('-r', '--rbmt-glosa', action='store_true', help='RBMT GLOSA.')
    parser.add_argument('-v', '--verbose', default=1, action='count', help='Verbose.')

    args, _ = parser.parse_known_args()

    Translation().pipeline(args.phrase, args.save_names, args.save_errors, train_files=args.train_files, pp_pt=args.preprocess_pt, glosa=args.rbmt_glosa, verbose=args.verbose)


if __name__ == '__main__':
    main()
