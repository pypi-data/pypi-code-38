from api.model.GraphNode import GraphNode


class GraphRelation(dict):

    """
        图数据的关系对象
        """

    def __init__(self, from_: GraphNode,to:GraphNode, type: str,guid:str, tags: dict = None) -> None:
        """
        图关系节点
        :param from_: 关系开始节点唯一guid
        :param to: 关系结束节点唯一guid
        :param type: 关系类型
        :param guid: 关系的唯一guid
        :param tags: 辅助标签/属性
        """
        super().__init__()
        self.__setitem__("@type", "com.sobey.jcg.sobeycube.core.api.domain.graph.GraphRelation")
        self.__setitem__("from", from_)
        self.__setitem__("to", to)
        self.__setitem__("guid", guid)
        self.__setitem__("type", type)
        if tags is not None:
            self.__setitem__("tags", tags)

    @property
    def from_(self):
        return self.__getitem__("from")

    @from_.setter
    def from_(self, value: GraphNode):
        self.__setitem__("from", value)

    @property
    def to(self):
        return self.__getitem__("to")

    @to.setter
    def to(self, value: str):
        self.__setitem__("to", value)

    @property
    def guid(self):
        return self.__getitem__("guid")

    @guid.setter
    def guid(self, value: str):
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
            self.__setitem__("tags", value)
        else:
            self.__delitem__("tags")