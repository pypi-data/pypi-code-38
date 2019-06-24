
class GraphNode(dict):
    """
    图数据的节点对象
    """

    def __init__(self, guid: str, type: str, tags: dict = None) -> None:
        """
        图的节点对象
        :param guid: 节点唯一guid
        :param type: 节点类型
        :param tags: 辅助标签/属性
        """
        super().__init__()
        self.__setitem__("@type", "com.sobey.jcg.sobeycube.core.api.domain.graph.GraphNode")
        self.__setitem__("guid", guid)
        self.__setitem__("type", type)
        if tags is not None:
            self.__setitem__("tags", tags)

    @property
    def guid(self):
        return self.__getitem__("guid")

    @guid.setter
    def guid(self,value:str):
        self.__setitem__("guid", value)

    @property
    def type(self):
        return self.__getitem__("type")

    @type.setter
    def type(self, value: str):
        self.__setitem__("type", value)

    @property
    def tags(self):
        return self.__getitem__("tags") if "tags" in self else None

    @tags.setter
    def tags(self, value: dict):
        if value is not None:
            self.__setitem__("tags",value)
        else:
            self.__delitem__("tags")