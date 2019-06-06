from soyspacing.countbase import RuleDict, CountSpace
from SmiToText.util.util import Util
import os

class koSoySpacing(object):

    def __init__(self):
        self.util = Util()

    def train(self, filename):
        verbose = False
        mc = 10  # min_count
        ft = 0.3  # force_abs_threshold
        nt = -0.3  # nonspace_threshold
        st = 0.3  # space_threshold

        model = CountSpace()

        rootDirPath = self.util.getRootPath("SmiToText.SmiToText")
        corpus_fname = rootDirPath + os.path.sep + "data" +  os.path.sep + "koDetokenizerData" + os.path.sep + "ko_law_common_space.txt"
        model_fname = rootDirPath + os.path.sep + "kosoy-models" + os.path.sep + "soyspacing.model"

        ### 학습
        # model.train(corpus_fname)
        # model.save_model(model_fname, json_format=False)

        ## 모델 로드
        model.load_model(model_fname, json_format=False)

        #sent = '이건진짜좋은영화 라라랜드진짜좋은영화'
        # sent = '그일단그구성원인사람들과,,'
        sent = 'DAB는, 결정과 관련한 각 위원들의 모든 일당 수수료와 경비에 대한 청구금액이 완전하게 지급될 때 까지는, 결정문을 발급할 의무를 갖지 아니한다.'

        sent_input = sent.replace( " ", "")

        # with parameters
        setn_output_1, tags = model.correct(
            doc=sent_input,
            verbose=verbose,
            force_abs_threshold=ft,
            nonspace_threshold=nt,
            space_threshold=st,
            min_count=mc)

        # without parameters
        setn_output_2, tags = model.correct(sent_input)

        print(sent)
        print(setn_output_1)
        print(setn_output_2)


if __name__ == '__main__':
    ksc = koSoySpacing()
    ksc.train('ko_law_common_space.txt')
