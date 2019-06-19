# -*- coding: utf-8 -*-

###############################################
# - 导入
###############################################


###############################################
# - [关于MVC架构中的Repository模式](http://blog.csdn.net/syaguang2006/article/details/22111211)
# - [项目架构开发：数据访问层之Repository](https://www.cnblogs.com/lanxiaoke/p/6503022.html)
###############################################

class BaseRepo(object):
    ## 创建实例
    # @desc 不做插入动作, db中不应该产生实例
    @staticmethod
    def create():
        pass

    ## 插入实例
    #
    @staticmethod
    def insert(entity):
        pass

    ## 批量插入实例
    #
    @staticmethod
    def insert_batch(entitys):
        pass

    ## 更新实例
    #
    @staticmethod
    def update(entity):
        pass

    ## 删除实例
    #
    @staticmethod
    def delete(entity):
        pass

    ## 删除实例 通过 id
    #
    @staticmethod
    def delete_by_id(id):
        pass

    @staticmethod
    def delete_by_ids(ids):
        pass

    ## 删除实例 通过 uid, user identification 用户识别; user identifier 用户标识符; universal identifier 通用标识符; unique identifier 惟一标识符;
    #
    @staticmethod
    def delete_by_uid(uid):
        pass

    @staticmethod
    def delete_by_uids(uids):
        pass

    ## 查询所有
    #
    @staticmethod
    def query_all():
        pass

    ## 查询 按 id （一般为整型）
    #
    @staticmethod
    def query_by_id(id):
        pass

    @staticmethod
    def query_by_ids(ids):
        pass

    ## 查询 按 uid （一般为字符串标识符）
    #
    @staticmethod
    def query_by_uid(uid):
        pass

    ## 查询 按 匿名函数
    # @param exp: User.id=user_id
    # @return 实体对象数组
    @staticmethod
    def query_by(exp):
        pass

    ## 查询总数目
    #
    @staticmethod
    def count_all():
        pass

    ## 查询 按 匿名函数
    # @return 实体对象数组
    @staticmethod
    def count_by(exp):
        pass

    ## 实例是否存在
    #
    @staticmethod
    def exist_by_id(id):
        pass

    ## 实例是否存在
    #
    @staticmethod
    def exist_by_uid(uid):
        pass

    ## 实例是否存在 按 匿名函数
    # @return BOOL
    @staticmethod
    def exist_by(exp):
        pass



    ####### 基类提供实现的方法
    @staticmethod
    def strip():
        pass
