from typing import List, Union
import gc


class Resource(object):
    """
    Resource class holder.
    """

    def __init__(self, entry: object):
        self.entry = entry


class ResourceProvider(object):
    """
    Simple Singleton Factory Provider
    """

    def __init__(self):
        self.collection: List[Resource] = []

    def is_in(self, entry: type) -> bool:
        """
        Checks if required class already present in resource collection.
        :param entry: target class.
        :return: result flag.
        """
        result = False
        for member in self.collection:
            if type(member.entry) is entry:
                result = True
        return result

    def delete(self, entry: type) -> None:
        """
        Removes provided class exemplar from collection. And force garbage collection in order to clear memory.
        :param entry: target class.
        :return: Nothing.
        """
        for member in self.collection:
            if type(member.entry) is entry:
                self.collection.remove(member)
                gc.collect()

    def add(self, exemplar: object) -> None:
        """
        Adds exemplar to collection. In case if collection already contains exemplar of same class, deletes previous and adds new one.
        :param exemplar: object to store.
        :return: Nothing.
        """
        if self.is_in(type(exemplar)):
            self.delete(type(exemplar))
        self.collection.append(Resource(entry=exemplar))

    def get(self, entry: type) -> [Union, None]:
        """
        Searches for exemplar of provided class in collection and returns it, or in case if nothing was found returns None.
        :param entry: target class.
        :return: object from collection or nothing.
        """
        target = None
        for member in self.collection:
            if type(member.entry) is entry:
                target = member.entry
        return target
