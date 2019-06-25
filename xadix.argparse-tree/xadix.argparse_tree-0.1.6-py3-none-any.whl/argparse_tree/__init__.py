# vim: set filetype=python sts=4 ts=4 sw=4 expandtab tw=100 cc=+1:
"""
This package provides a class :py:class:`ArgParseNode` which makes it easier to create complex
nested subcommands with argparse.
"""
import argparse
import re

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

# pydoc3 argparse._SubParsersAction
# pydoc3

class ArgParseNode:
    # pylint: disable=too-many-instance-attributes,too-many-arguments
    """
    This class is a node in a tree of various subcommands.

    :param dict options: passed to :py:class:`argparse.ArgumentParser` constructor if this
        is the root node or the :py:meth:`argparse._SubParsersAction.add_parser` method.
    :param dict default_options: options to use when calling
        :py:meth:`argparse._SubParsersAction.add_parser` if none is supplied.
    :param dict subparser_options: options to pass to
        :py:meth:`argparse.ArgumentParser.add_subparsers`.
    :param str name: name of this node.
    :param ArgParseNode parent: parent of this node.
    """
    __subparser_regex = re.compile("^subparser_(.*)$")
    def __init__(self, options, default_options=None,
        subparser_options=None, name=None, parent=None):
        self.children = {}
        self.__subparsers = None
        if parent:
            self.name = name
            self.parent = parent
            self.root = parent.root
            self.default_options = parent.default_options
            self.subparser_options = subparser_options or parent.subparser_options or {}
            self.__parser = parent.subparsers.add_parser(name, **(options or self.default_options))
        else:
            self.root = self
            self.default_options = default_options or {}
            self.subparser_options = subparser_options or {}
            self.__parser = argparse.ArgumentParser(**(options or self.default_options))
            self.parent = None
            self.name = None

    def get(self, name, options=None, no_create=None):
        """
        Retrieve or create a child of this node which has the specified `name`.

        :param str name: The name of the child node to retrieve or create.
        :param dict options: the options to pass to :py:meth:`argparse._SubParsersAction.add_parser`
            when creating the new node.
        :param bool no_create: Whether or not a new node may be created. If failse this method will
            throw if the node does not exist.
        :return: The child node.
        :rtype: ArgParseNode
        :raises KeyError: if `no_create` is set and there is no node named `name`
        """
        if name not in self.children:
            if no_create:
                raise KeyError("Node with name {} does not exist on {}".format(name, self.name))
            self.children[name] = ArgParseNode(parent=self, name=name, options=options)
        return self.children[name]

    @property
    def parser(self):
        """
        The actual :py:class:`argparse.ArgumentParser` object associated with this node.
        """
        #print("ArgParseNode: parser: type(self.__parser).__name__ = {}\n"
        #    .format(type(self.__parser).__name__))
        return self.__parser

    @property
    def level(self):
        """
        The level index of this node (root is 0).
        """
        if self.parent is not None:
            return self.parent.level + 1
        return 0

    @property
    def subparsers(self):
        """
        The :py:class:`argparse._SubParsersAction` associated with this node as returned
        by :py:meth:`argparse.ArgumentParser.add_subparsers`
        """
        #print("subparsers: entry: self.__subparsers = {}\n".format(self.__subparsers))
        if self.__subparsers is None:
            self.__subparsers = self.parser.add_subparsers(dest="subparser_{:d}".format(self.level),
            **self.subparser_options)
        #print("subparsers: entry: type(self.__subparsers).__name__ = {}\n"
        #    .format(type(self.__subparsers).__name__))
        #print("ArgParseNode: subparsers: type(self.__subparsers).__name__ = {}\n"
        #    .format(type(self.__subparsers).__name__))
        return self.__subparsers

    @property
    def path_list(self):
        """
        The path to the current `ArgParseNode` as a list of strings that consist
        of each of the :py:attr:`ArgParseNode.name` values of the nodes (except for the root).
        """
        if self.parent is not None:
            tmp = self.parent.path_list
            tmp.append(self.name)
            return tmp
        return []

    @property
    def path(self):
        """
        The path to the current `ArgParseNode` as `/` seperated list of strings that consist
        of each of the :py:attr:`ArgParseNode.name` values of the nodes (except for the root).
        """
        return "/".join(self.path_list)

    @classmethod
    def get_selected_path_list(cls, parse_result):
        """
        This method returns the path to the selected node as a list of name strings.

        :param argparse.Namespace parse_result: A namespace object returned by
            :py:meth:`argparse.ArgumentParser.parse_args`.
        :rtype: list
        """
        parts = []
        pdict = parse_result.__dict__
        #print("get_selected_path_list: pdict = {}".format(pdict))
        for key, value in pdict.items():
            #print("get_selected_path_list: key = {}, value = {}".format(key, value))
            if value is None:
                continue
            re_result = cls.__subparser_regex.match(key)
            if re_result:
                index = int(re_result.group(1))
                #print("get_selected_path_list: index = {}".format(index))
                parts.insert(index, value)
        #print("get_selected_path_list: parts = {}".format(parts))
        return parts

    @classmethod
    def get_selected_path(cls, parse_result):
        """
        This method returns the path to the selected node as a `/` seperated string.

        :param argparse.Namespace parse_result: A namespace object returned by
            :py:meth:`argparse.ArgumentParser.parse_args`.
        :rtype: str
        """
        path_list = cls.get_selected_path_list(parse_result)
        return "/".join(path_list)

    def get_selected_node(self, parse_result):
        """
        This method returns the selected node.

        :param argparse.Namespace parse_result: A namespace object returned by
            :py:meth:`argparse.ArgumentParser.parse_args`.
        :rtype: ArgParseNode
        """
        if self is not self.root:
            return self.root.get_selected_node(parse_result)
        selected_path_list = self.get_selected_path_list(parse_result)
        if not selected_path_list:
            return self
        selected_node = self
        for part in selected_path_list:
            selected_node = selected_node.get(part, None, True)
        return selected_node
