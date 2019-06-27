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
from .translation import Translation
import os
from os.path import join
import traceback


class FileTranslation():

    def pipeline(self, *files, train_files=False, preprocess_pt=False, rbmt_glosa=False, verbose=False):

        preproc = Translation()

        for file in files:
            dirname = os.path.dirname(file)
            basename = os.path.basename(file)
            prep = join(dirname, 'prep')

            os.makedirs(prep, exist_ok=True)

            if train_files:
                pp_pt_train_file = open(join(prep, basename + '_train.pt'), 'w')
                pp_glosa_train_file = open(join(prep, basename + '_train.glosa'), 'w')

            if preprocess_pt:
                pp_pt_test_file = open(join(prep, basename + '_test.pt'), 'w')

            if rbmt_glosa:
                rbmt_glosa_file = open(join(prep, basename + '_rbmt.glosa'), 'w')

            with open(file, 'r') as f,\
                    open(join(prep, basename + '_log'), 'a') as log:

                for i, line in enumerate(f):

                    try:
                        result = preproc.pipeline(line, train_files=train_files, pp_pt=preprocess_pt, glosa=rbmt_glosa, verbose=verbose)
                    except KeyboardInterrupt:
                        return
                    except:
                        log.write('file: ' + file + ' line: ' + str(i) + '\n')
                        log.write(line + '\n')
                        log.write(traceback.format_exc() + '\n\n')
                        log.write(("-" * 50) + '\n')
                    else:
                        if result:
                            pp_pt_train, pp_glosa_train, pp_pt_test, rbmt_glosa = result

                            if train_files:
                                if pp_pt_train:
                                    pp_pt_train_file.write(pp_pt_train + '\n')

                                if pp_glosa_train:
                                    pp_glosa_train_file.write(pp_glosa_train + '\n')

                            if preprocess_pt:
                                pp_pt_test_file.write(pp_pt_test + '\n')

                            if rbmt_glosa:
                                rbmt_glosa_file.write(rbmt_glosa + '\n')

            if train_files:
                pp_pt_train_file.close()
                pp_glosa_train_file.close()

            if preprocess_pt:
                pp_pt_test_file.close()

            if rbmt_glosa:
                rbmt_glosa_file.close()

    def rule_translation(self, *files):
        self.pipeline(*files, rbmt_glosa=True)

    def preprocess_pt(self, *files):
        self.pipeline(*files, preprocess_pt=True)

    def preprocess_train_files(self, *files):
        self.pipeline(*files, train_files=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+', help='Raw text file')
    parser.add_argument('-t', '--train-files', action='store_true', help='Preprocessing for train files.')
    parser.add_argument('-p', '--preprocess-pt', action='store_true', help='Preprocessing for test file.')
    parser.add_argument('-r', '--rbmt-glosa', action='store_true', help='RBMT GLOSA.')
    parser.add_argument('-v', '--verbose', default=1, action='count', help='Verbose.')
    args, _ = parser.parse_known_args()

    fpp = FileTranslation()
    fpp.pipeline(*args.files, train_files=args.train_files, preprocess_pt=args.preprocess_pt, rbmt_glosa=args.rbmt_glosa, verbose=args.verbose)


if __name__ == '__main__':
    main()
