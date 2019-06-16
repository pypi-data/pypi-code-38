"""MAM config object."""

from __future__ import annotations

import functools
from typing import (
    Any, Dict, Iterator, List, NamedTuple, Optional, Tuple, Union,
)

from ..find import find
from ..objects import NULL
from ..typings import (ConfigObject, Mutation, MutationTree, Path)

__all__ = [
    'MutationInfo',
    'Config',
    'NULL',
]


@functools.lru_cache()
def load_mutation(mutation: Union[str, Mutation]) -> Mutation:
    """Load a mutation from the specified location."""
    if isinstance(mutation, str):
        mutation = find(mutation).obj
    return mutation


# nosa: pylint[:Undefined variable 'Config'],pyflakes[:undefined name 'Config']
class Config:
    """Config object."""

    MUTATIONS = '_mutations'

    orig: ConfigObject
    parent: Optional[Config]
    output: ConfigObject
    p_node: Optional[Config]

    def __init__(self, orig: ConfigObject, p_node: Optional[Config] = None):
        """Build Config object."""
        self.orig = orig
        self.parent = None
        self.output = {}

        self.p_node = p_node

    def _get_keys(self, key: Optional[str]) -> List[str]:
        """Get config and inherited keys to merge together."""
        if key is not None:
            keys = [key]
        else:
            keys_ = set(self.orig.keys())
            if self.parent is not None:
                keys_ |= set(self.parent.output) - set(self.output)
            keys = list(keys_)
        return keys

    def _get_mutations(self) -> MutationTree:
        """Get all possible mutations from config."""
        return (
            self.output.get(self.MUTATIONS)
            or (
                self.parent.output.get(self.MUTATIONS)
                if self.parent is not None else
                None
            )
        )

    def _traverse_mutations(self, mutation: Union[MutationTree, str],
                            path: Path, multi: bool = False,
                            star: bool = True,
                            ) -> Iterator[Union[str, MutationTree]]:
        """Get all mutations for specified path."""
        if not path:
            if multi and isinstance(mutation, dict) and '**' in mutation:
                yield mutation['**']
            else:
                yield mutation
            return

        if isinstance(mutation, dict):
            if path[0] in mutation:
                yield from self._traverse_mutations(
                    mutation[path[0]],
                    path[1:],
                    multi=False,
                )
            if '*' in mutation:
                yield from self._traverse_mutations(
                    mutation['*'],
                    path[1:],
                    multi=False,
                )
            if multi:
                if path[0] in mutation:
                    yield from self._traverse_mutations(
                        mutation[path[0]],
                        path[1:],
                        multi=True,
                    )
                if '*' in mutation:
                    yield from self._traverse_mutations(
                        mutation['*'],
                        path[1:],
                        multi=True,
                    )
                if star and '**' in mutation:
                    for i in range(len(path) + 1):
                        yield from self._traverse_mutations(
                            mutation['**'],
                            path[i:],
                            multi=True,
                            star=bool(i),
                        )

    def _get_mutation(self, path: Path) -> Mutation:
        """Get mutation to merge the values at the path."""
        mutations = self._get_mutations()
        for mutation in self._traverse_mutations(mutations, path, True):
            mutation_: Union[str, MutationTree, None] = mutation
            if isinstance(mutation_, dict):
                mutation_ = mutation_.get('$')
            if mutation_ is not None:
                return load_mutation(mutation_)
        raise ValueError(
            "Can't find mutation for config path {key}"
            .format(key='.'.join(path)),
        )

    def merge(self, orig: Any, parent: Any,
              path: Path, *, root: bool, leaf: bool,
              ) -> Any:
        """Merge config value and it's inherited value."""
        mutation = self._get_mutation(path)
        return mutation(
            orig,
            parent,
            info=MutationInfo(
                path=path,
                root=root,
                leaf=leaf,
                config=self,
            ),
        )

    def _merge(self, orig: Dict[str, Any], parent: Optional[Dict[str, Any]],
               mutations: MutationTree, key: str, *, root: bool,
               leaf: bool) -> Any:
        """Merge config value and it's inherited value."""
        # bootstrap mutations
        if mutations is None and parent is None:
            return orig.pop(key, NULL)

        return self.merge(
            orig.pop(key, NULL),
            (parent or {}).get(key, NULL),
            (key,),
            root=root,
            leaf=leaf,
        )

    def _reduce(self, key: Optional[str] = None, root: bool = False) -> None:
        """Merge this config and the configs it inherits."""
        orig = self.orig
        if self.parent is None:
            parent = None
            leaf = True
        else:
            self.parent._reduce(key)
            parent = self.parent.output
            leaf = False

        mutations = self._get_mutations()
        for key_ in self._get_keys(key):
            if key_ in self.output:
                raise ValueError(
                    'key, {0}, already in output {1}'
                    .format(key_, self),
                )
            output = self._merge(
                orig, parent, mutations,
                key_, root=root, leaf=leaf,
            )
            if output is not NULL:
                self.output[key_] = output

    def reduce(self, key: Optional[str] = None) -> None:
        """Merge this config and the configs it inherits."""
        self._reduce(key, root=True)

    def walk(self) -> Iterator[Config]:
        """Walk the configs, returns itself and its children."""
        node: Optional[Config] = self
        while node is not None:
            yield node
            node = node.parent

    def leaves(self) -> List[Config]:
        """Get leaf configs."""
        node = self
        while node.parent is not None:
            node = node.parent
        return [node]

    def root(self) -> Config:
        """Get root config."""
        node = self
        while node.p_node is not None:
            node = node.p_node
        return node


class MutationInfo(NamedTuple(
    'MutationInfo',
    [
        ('config', Config),
        ('path', Tuple[str, ...]),
        ('root', bool),
        ('leaf', bool),
    ],
)):
    """Hold information about config mutation."""

    def merge(self, orig: Any, parent: Any, key: str):
        """Wrap `Config.merge`."""
        return self.config.merge(
            orig,
            parent,
            self.path + (key,),
            leaf=self.leaf,
            root=self.root,
        )
