import unittest
from atman_kg_nlp.stanford_nlp.client import *


class TestClientMethods(unittest.TestCase):

    def _test_phrase_extraction(self, client, text, phrases, language):
        doc = client.annotate(text, annotators=['parse'], language=language)
        result = {x.text for x in doc.phrases if
                  x.tag in ('NR', 'NN', 'NNS', 'NP', 'JJ', 'ADJP', 'VV', 'VA')}
        for phrase in phrases:
            self.assertIn(phrase, result)

    def test_en_phrase_extraction(self):
        client = LanguageCoreNLPClient()
        text1 = 'Naloxone reverses the antihypertensive effect of clonid' \
                'ine. In unanesthetized, spontaneously hypertensive rats' \
                ' the decrease in blood pressure and heart rate produced' \
                ' by intravenous clonidine, 5 to 20 micrograms/kg, was i' \
                'nhibited or reversed by nalozone, 0.2 to 2 mg/kg. The h' \
                'ypotensive effect of 100 mg/kg alpha-methyldopa was als' \
                'o partially reversed by naloxone. Naloxone alone did no' \
                't affect either blood pressure or heart rate. In brain ' \
                'membranes from spontaneously hypertensive rats clonidin' \
                'e, 10(-8) to 10(-5) M, did not influence stereoselectiv' \
                'e binding of [3H]-naloxone (8 nM), and naloxone, 10(-8)' \
                ' to 10(-4) M, did not influence clonidine-suppressible ' \
                'binding of [3H]-dihydroergocryptine (1 nM). These findi' \
                'ngs indicate that in spontaneously hypertensive rats th' \
                'e effects of central alpha-adrenoceptor stimulation inv' \
                'olve activation of opiate receptors.'
        target1 = ['naloxone', 'clonidine', 'hypertensive', 'nalozone',
                   'blood pressure', 'heart rate', 'intravenous',
                   'brain membranes', 'alpha-adrenoceptor',
                   'opiate', 'alpha-methyldopa',
                   'dihydroergocryptine',
                   # '[3H]-naloxone',
                   # '[3H]-dihydroergocryptine'
                   ]
        self._test_phrase_extraction(client, text1, target1, 'en')

        text2 = 'Lidocaine-induced cardiac asystole. Intravenous admini' \
                'stration of a single 50-mg bolus of lidocaine in a 67-' \
                'year-old man resulted in profound depression of the ac' \
                'tivity of the sinoatrial and atrioventricular nodal pa' \
                'cemakers. The patient had no apparent associated condi' \
                'tions which might have predisposed him to the developm' \
                'ent of bradyarrhythmias; and, thus, this probably repr' \
                'esented a true idiosyncrasy to lidocaine.'
        target2 = ['lidocaine',
                   # 'Lidocaine',
                   # 'cardiac asystole',
                   'bradyarrhythmias']
        self._test_phrase_extraction(client, text2, target2, 'en')

        text3 = 'Suxamethonium infusion rate and observed fasciculations' \
                '. A dose-response study. Suxamethonium chloride (Sch) w' \
                'as administered i.v. to 36 adult males at six rates: 0.' \
                '25 mg s-1 to 20 mg s-1. The infusion was discontinued e' \
                'ither when there was no muscular response to tetanic st' \
                'imulation of the ulnar nerve or when Sch 120 mg was exc' \
                'eeded. Six additional patients received a 30-mg i.v. bo' \
                'lus dose. Fasciculations in six areas of the body were ' \
                'scored from 0 to 3 and summated as a total fasciculatio' \
                'n score. The times to first fasciculation, twitch suppr' \
                'ession and tetanus suppression were inversely related t' \
                'o the infusion rates. Fasciculations in the six areas a' \
                'nd the total fasciculation score were related directly ' \
                'to the rate of infusion. Total fasciculation scores in ' \
                'the 30-mg bolus group and the 5-mg s-1 and 20-mg s-1 in' \
                'fusion groups were not significantly different.'
        target3 = ['Suxamethonium', 'fasciculations', 'Suxamethonium chloride',
                   'Sch', 'fasciculation']
        self._test_phrase_extraction(client, text3, target3, 'en')
        client.stop()

    def test_zh_phrase_extraction(self):
        client = LanguageCoreNLPClient()
        text1 = '新藤黄酸诱导LP-1人多发性骨髓瘤细胞凋亡及抑制血管生成作用的实验研究。' \
                '目的:研究新藤黄酸对于多发性骨髓瘤LP-1细胞凋亡的诱导作用及血管生成抑' \
                '制作用.方法:通过采用CCK-8细胞活力检测法研究了新藤黄酸对LP-1多发性' \
                '骨髓瘤细胞体外增殖的影响;采用Annexin V-EGFP荧光染色法定性检测及' \
                '流式细胞术定量检测了新藤黄酸对LP-1多发性骨髓瘤细胞凋亡的诱导作用;' \
                '采用级联酶底物显色法检测了新藤黄酸对LP-1多发性骨髓瘤细胞caspase-' \
                '3酶原活化状态的影响;划痕法检测了新藤黄酸对血管内皮细胞体外血管生成' \
                '能力的影响.结果:新藤黄酸能明显抑制LP-1多发性骨髓瘤细胞体外增殖,其I' \
                'C50为7.765 μM.新藤黄酸可诱导LP-1细胞发生细胞凋亡,此效应具有剂量' \
                '依赖性,新藤黄酸60μM作用于LP-1细胞24h细胞凋亡百分率达到59.8％.进' \
                '一步的研究表明,新藤黄酸可引起LP-I细胞caspase-3酶原活化,提示新藤' \
                '黄酸引起的LP-1细胞凋亡过程中caspase-3酶原活化发挥了重要作用.新藤' \
                '黄酸能剂量依赖性地抑制人血管内皮细胞划痕修复,提示新藤黄酸能抑制人脐' \
                '静脉血管内皮细胞体外血管生成能力.结论:新藤黄酸对于多发性骨髓瘤细胞' \
                '具有抑制细胞增殖、诱导细胞凋亡的作用,此作用机制部分是通过级联酶原活' \
                '化的途径实现,新藤黄酸亦可抑制血管内皮细胞体外血管生成的能力.'
        target1 = ['新藤黄酸', 'LP-1', '多发性骨髓瘤',
                   # 'Annexin V - EGFP荧光染色法',
                   # '流式细胞术',
                   # '级联酶底物显色法',
                   'caspase-3',
                   '划痕法',
                   'LP-I细胞'
                   ]
        self._test_phrase_extraction(client, text1, target1, 'zh')

        text2 = '桑白皮水煎总提物对肾阴虚水肿模型的影响。 目的：研究桑白皮水煎总提物对' \
                '肾阴虚水肿模型的影响,为桑白皮的药性研究提供支撑. 方法：采用两次尾静' \
                '脉注射阿霉素同时灌胃给予甲状腺片21天的方法建立大鼠肾阴虚水肿模型,造' \
                '模完成后连续给药4周.实验结束后,检测尿蛋白、环磷酸腺苷(cAMP)、环磷' \
                '酸鸟苷(cGMP)、睾酮(T)、雌二醇(E2)、甲状腺素(T4)、三碘甲状腺原氨' \
                '酸(T3)等指标. 结果：与正常组相比,模型组尿蛋白、cAMP、E2、T3、T4' \
                '的水平显著升高(P＜0.05或P＜0.01),cGMP、T的水平显著降低(P＜0.0' \
                'l);与模型组相比,桑白皮水煎总提物能显著降低尿蛋白、cAMP、E2、T3、' \
                'T4的水平(P＜0.05或P＜0.01),升高cGMP、T的水平(P＜0.05或P＜0.0' \
                '1). 结论：桑白皮水煎总提物能显著改善肾阴虚水肿模型大鼠的病理状况,' \
                '其中低剂量234mg·kg-1为最佳有效剂量,且这种改善可能与桑白皮归肺经,' \
                '味甘,性寒的药性有关.'
        target2 = ['桑白皮水煎总提物', '肾阴虚水肿模型', '桑白皮',
                   '阿霉素', '甲状腺片',
                   # '尿蛋白',
                   # '环磷酸腺苷',
                   # '环磷酸鸟苷',
                   '睾酮', '雌二醇',
                   '甲状腺素',
                   # '三碘甲状腺原氨酸'
                   ]
        self._test_phrase_extraction(client, text2, target2, 'zh')

        client.stop()

    if __name__ == '__main__':
        unittest.main()
