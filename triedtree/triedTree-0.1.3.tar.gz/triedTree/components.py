# create by fanfan on 2019/1/16 0016
import logging


logger = logging.getLogger(__name__)




class Component(object):
    name = ""
    def __init__(self,**kwargs):
        pass


    def process(self, **kwargs):
        pass

    def persist(self, model_dir):
        '''
        保存模型
        :param model_dir: 
        :return: 
        '''
        pass

    def restore(self,model_dir):
        """
        从指定目录加载模型
        :param model_dir: 
        :return: 
        """
        pass


