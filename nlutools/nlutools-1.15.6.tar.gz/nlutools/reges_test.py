import tools as nlu


def run():
    print('测试分词')
    #print(nlu.cut('这是一个能够输出名词短语的分词器，欢迎试用！',pos=True,cut_all=False,mode='fast'))
    print(nlu.cut('这是一个能够输出名词短语的分词器，欢迎试用！',mode='fast'))
    print('测试分词完成')

    print('测试分句')
    print(nlu.getSubSentences('我喜欢在春天去观赏桃花，在夏天去欣赏荷花，在秋天去观赏红叶，但更喜欢在冬天去欣赏雪景。',mode=1))
    print('测试分句完成')
    #print('测试下载词向量')
    #nlu.getW2VFile('v1.0','~:')
    #print('词向量下载完成')

    print('测试句向量')
    print(nlu.getSentenceVec(['主要负责机器学习算法的研究以及搭建神经网络、训练模型、编写代码，以及其他的一些工作','机器学习算法的研究以及搭建神经网络，训练模型']))
    print('测试句向量完成')


    print('测试情感分析')
    print(nlu.predictEmotion(['这家公司很棒!','这家公司不咋地','这家公司还可以']))
    print(nlu.predictEmotion(['这家公司很棒!','这家公司不咋地','这家公司还可以'],prob=True))
    print('测试情感分析完成')


    print('测试词向量')
    print(nlu.getWordVec('深度学习'))
    print(nlu.getWordVec(['深度学习']))
    print(nlu.getMostSimiWords('深度学习',10))
    print(nlu.getMostSimiWords(['深度学习','神经网络'],10))
    print('测试词向量完成')

    print('测试bert句向量')
    print(nlu.getBertSentenceVec(['机器学习模型牛逼'],'char'))
    print(nlu.getBertSentenceVec(['机器学习模型牛逼'],'sent'))
    print('测试bert句向量完成')

    print('测试关键字提取')
    print(nlu.getKeywords('主要负责机器学习算法的研究以及搭建神经网络，训练模型，编写代码，以及其他的一些工作',4,True))
    print('测试关键字提取完成')

    print('测试句子相似度')
    print(nlu.getSentenceSimi('你家住地址是多少','你住哪里啊',10000))
    print('测试句子相似度完成')

    print('测试动宾提取')
    print(nlu.getVOB('要负责机器学习算法的研究以及搭建神经网络，训练模型，编写代码','fast'))
    print(nlu.getVOB('要负责机器学习算法的研究以及搭建神经网络，训练模型，编写代码，以及其他的一些工作','accurate'))
    print('测试动宾提取完成')

    print('测试句子合理性判定')
    print(nlu.getSentenceRationality(['床前明月光，疑是地上霜', '床前星星光，疑是地上霜', '床前白月光，疑是地上霜'],'true'))
    print(nlu.getSentenceRationality(['床前明月光，疑是地上霜', '床前星星光，疑是地上霜', '床前白月光，疑是地上霜'],'false'))
    print('测试句子合理性判定完成')

    print('测试实体转发服务')
    test_entity_str_list = ['我毕业于北京大学']
    print('测试实体序列标注服务')
    print(nlu.doEntityTask(test_entity_str_list,'ner'))
    print('测试实体信息抽取服务')
    print(nlu.doEntityTask(["我带5人团队","我有2年团队领导经验, 从2007年到2009年任总经理"],'ie'))
    print('测试实体面试bot信息抽取服务')
    print(nlu.doEntityTask(['我毕业于北京大学，我负责带5人团队，我有2年团队领导经验'],'interview_bot'))
    print('测试实体转发服务完成')

def press_run():
    nlu.cut('这是一个能够输出名词短语的分词器，欢迎试用！',mode='fast')
    nlu.getSubSentences('我喜欢在春天去观赏桃花，在夏天去欣赏荷花，在秋天去观赏红叶，但更喜欢在冬天去欣赏雪景。',mode=1)
    nlu.getSentenceVec(['主要负责机器学习算法的研究以及搭建神经网络、训练模型、编写代码，以及其他的一些工作',\
                    '机器学习算法的研究以及搭建神经网络，训练模型'])
    nlu.predictEmotion(['这家公司很棒!','这家公司不咋地','这家公司还可以'])
    nlu.predictEmotion(['这家公司很棒!','这家公司不咋地','这家公司还可以'],prob=True)
    nlu.getWordVec('深度学习')
    nlu.getWordVec(['深度学习'])
    nlu.getMostSimiWords('深度学习',10)
    nlu.getMostSimiWords(['深度学习','神经网络'],10)
    nlu.getKeywords('主要负责机器学习算法的研究以及搭建神经网络，训练模型，编写代码，以及其他的一些工作',4,True)
    nlu.getBertSentenceVec(['机器学习模型牛逼'],'char')
    nlu.getBertSentenceVec(['机器学习模型牛逼'],'sent')
    nlu.getSentenceSimi('你家住地址是多少','你住哪里啊',10000)
    nlu.getVOB('要负责机器学习算法的研究以及搭建神经网络，训练模型，编写代码，以及其他的一些工作','fast')
    nlu.getVOB('要负责机器学习算法的研究以及搭建神经网络，训练模型，编写代码，以及其他的一些工作','accurate')
    nlu.getSentenceRationality(['床前明月光，疑是地上霜', '床前星星光，疑是地上霜', '床前白月光，疑是地上霜'],'true')
    nlu.getSentenceRationality(['床前明月光，疑是地上霜', '床前星星光，疑是地上霜', '床前白月光，疑是地上霜'],'false')
    test_entity_str_list = ['我毕业于北京大学']
    nlu.doEntityTask(test_entity_str_list,'ner')
    nlu.doEntityTask(test_entity_str_list,'ie')
    nlu.doEntityTask(test_entity_str_list,'interview_bot')

if __name__=='__main__':
    run()
    '''
    i = 0
    try:
        while True:
            i += 1
            press_run()
            #nlu.predictEmotion('这家公司很棒')
            if i % 10 == 0:
                print(i)
    except Exception as e:
        print(i)
        raise e
    '''

