from api.model.MetaModelField import MetaModelField


class MetaModel:

    @property
    def dao(self):
        from factdatasource.dao.jdbc.JdbcDatasourceDao import JdbcDatasourceDao
        return JdbcDatasourceDao.instance()

    """
    模型
    """

    def __init__(self, id=None, site=None, project_code=None, code=None, name=None, description=None, fields=None):
        """
        数据模型
        :param id:
        :param site:
        :param project_code:
        :param code:
        :param name:
        :param description:
        :param fields: MetaModelField
        """
        self.id = id
        self.site = site
        self.projectCode = project_code
        self.code = code
        self.name = name
        self.description = description
        self.fields = fields

        if self.site is None and self.id is not None:
            # 说明只传入了一个ID,需要获取metamodel
            self.__init_model__(id)

    def __init_model__(self, id):
        sql = f"""SELECT id,site,projectCode,code,name,description FROM `sc_metamodel` WHERE id=:id"""
        code_dict = {'id': id}
        model = self.dao.select_one(sql, code_dict)

        if model is not None:
            self.site = model["site"]
            self.projectCode = model["projectCode"]
            self.code = model["code"]
            self.name = model["name"]
            self.description = model["description"]

            self.fields = self.__init_field__(id)

    def __init_field__(self, id):
        """
        构造 Fields
        :param id:
        :return:
        """
        sql = f"""SELECT id,modelId,fieldName,alias,description,dataType,primaryKey,minLength,maxLength,nullable,
        refModel,multiple,indexNames,fixItemId,params
         FROM `sc_metamodel_field` WHERE modelId=:id"""
        fields = self.dao.select_all(sql, {"id": id})

        if fields is not None and len(fields) > 0:
            result = []
            for field in fields:
                result.append(MetaModelField(**field))
            return result

        return None
