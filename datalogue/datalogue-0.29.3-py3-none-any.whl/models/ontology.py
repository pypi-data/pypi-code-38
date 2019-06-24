from abc import ABC, abstractmethod
from typing import Dict, List, Set, Optional, Union
from uuid import UUID
import itertools

from datalogue.errors import _enum_parse_error, DtlError
from datalogue.utils import _parse_list, _parse_string_list, SerializableStringEnum


class OntologyNode:
    def __init__(self,
                 name: str,
                 description: Optional[str] = None,
                 children: List['OntologyNode'] = [],
                 node_id: Optional[UUID] = None):

        if not isinstance(name, str):
            raise DtlError("name should be string in OntologyNode")

        if description is not None and not isinstance(description, str):
            raise DtlError("description should be string in OntologyNode")

        if not isinstance(children, List):
            raise DtlError("children should be list in OntologyNode")

        if node_id is not None and not isinstance(node_id, UUID):
            raise DtlError("node_id should be uuid in OntologyNode")

        self.name = name
        self.description = description
        self.children = children
        self.node_id = node_id

    def __eq__(self, other: 'OntologyNode'):
        if isinstance(self, other.__class__):
            return (self.name == other.name and
                    self.description == other.description and
                    self.children == other.children and
                    self.node_id == other.node_id)
        return False

    @staticmethod
    def as_payload(ontology_node: 'OntologyNode') -> Union[DtlError, dict]:
        payload = {
            "name": ontology_node.name,
            "children": list(map(lambda n: OntologyNode.as_payload(n), ontology_node.children))
        }

        if ontology_node.description is not None:
            payload["description"] = ontology_node.description

        return payload

    @staticmethod
    def from_payload(payload: dict) -> Union[DtlError, 'OntologyNode']:
        node_id = UUID(payload.get("id"))
        name = payload.get("name")
        description = payload.get("description")
        children = payload.get("children")
        if children is None:
            children = []
        else:
            children = _parse_list(OntologyNode.from_payload)(children)
        return OntologyNode(name, description, children, node_id=node_id)


class Ontology:
    def __init__(self,
                 name: str,
                 description: Optional[str] = None,
                 tree: List[OntologyNode] = [],
                 ontology_id: Optional[UUID] = None):

        if not isinstance(name, str):
            raise DtlError("name should be string in Ontology")

        if description is not None and not isinstance(description, str):
            raise DtlError("description should be string in Ontology")

        if not isinstance(tree, List):
            raise DtlError("tree should be list in Ontology")

        if ontology_id is not None and not isinstance(ontology_id, UUID):
            raise DtlError("ontology_id should be uuid in Ontology")

        self.name = name
        self.description = description
        self.tree = tree
        self.ontology_id = ontology_id



    def __eq__(self, other: 'Ontology'):
        if isinstance(self, other.__class__):
            return (self.name == other.name and
                    self.description == other.description and
                    self.tree == other.tree and
                    self.ontology_id == other.ontology_id)
        return False

    def __repr__(self):
        def print_nodes(tree, output=[], level=0):
            for n in tree:
                padding = '   ' * level
                if level == 0:
                    output.append(padding + n.name)
                else:
                    output.append(padding + '|___' + n.name)
                for c in n.children:
                    print_nodes([c], output, level=level+1)
            return output

        first_line = f'Ontology(id: {self.ontology_id}, name: {self.name!r}, description: {self.description!r})' + '\n'
        return '\n'.join(print_nodes(self.tree, [first_line]))

    def leaves(self) -> List[OntologyNode]:
        def iterate(node: OntologyNode) -> List[OntologyNode]:
            if not node.children:
                return [ node ]
            else:
                return list(itertools.chain(*map(lambda n: iterate(n), node.children)))

        return list(itertools.chain(*map(lambda n: iterate(n), self.tree)))

    @staticmethod
    def as_payload(ontology: 'Ontology') -> Union[DtlError, dict]:
        payload = {
            "name": ontology.name,
            "children": list(map(lambda n: OntologyNode.as_payload(n), ontology.tree))
        }

        if ontology.description is not None:
            payload["description"] = ontology.description

        return payload

    @staticmethod
    def from_payload(payload: dict) -> Union[DtlError, 'Ontology']:
        ontology_id = UUID(payload.get("id"))
        name = payload.get("name")
        description = payload.get("description")
        tree = payload.get("tree")
        if tree is None:
            tree = []
        else:
            tree = _parse_list(OntologyNode.from_payload)(payload["tree"])
        return Ontology(name, description, tree, ontology_id=ontology_id)


class DataRef:
    def __init__(self, node: OntologyNode, path_list: List[List[str]]):
        self.node = node
        self.path_list = path_list
