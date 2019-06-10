from fnmatch import fnmatch
from enum import Enum
from typing import Optional, Container, FrozenSet, Iterable, List, Dict, Union

from pydantic import BaseModel

__all__ = [
    "Feature",
    "FeatureProperties",
    "FeatureTask",
    "ManifestInfo",
    "Modpack",
    "ManifestIndex",
    "ModpackStatus",
    "PatternTestable",
    "RichManifest",
    "SimplePatternList",
    "SourceManifest",
    "TargetManifest",
    "Task",
    "UserFileTask",
]


class BaseManifest(BaseModel):
    name: str
    title: str
    version: str = "1.0"

    class Config:
        allow_mutation = False

    def __hash__(self):
        return hash((self.name, self.title, self.version))

    def __eq__(self, other):
        return hash(self) == hash(other)


class ManifestInfo(BaseManifest):
    location: str

    class Config:
        allow_mutation = False

    def __hash__(self):
        return hash((self.name, self.title, self.version, self.location))

    def __eq__(self, other):
        return hash(self) == hash(other)


class ManifestIndex(BaseModel):
    minimumVersion: int = 3
    packages: List[ManifestInfo] = []

    class Config:
        allow_mutation = False

    def __hash__(self):
        return hash((self.minimumVersion, frozenset(self.packages)))

    def __eq__(self, other):
        return hash(self) == hash(other)


class SimplePatternList(BaseModel):
    include: List[str] = []
    exclude: List[str] = []

    def __hash__(self):
        return hash(frozenset(self.include + self.exclude))

    def __eq__(self, other):
        return hash(self) == hash(other)

    class Config:
        allow_mutation = False


class FeatureProperties(BaseModel):
    name: str
    description: str
    recommendation: str = "starred"
    selected: bool = False

    def __hash__(self):
        return hash((self.name, self.description, self.recommendation, self.selected))

    def __eq__(self, other):
        return hash(self) == hash(other)

    class Config:
        allow_mutation = False


class Feature(BaseModel):
    properties: FeatureProperties
    files: SimplePatternList

    class Config:
        allow_mutation = False


class Task(BaseModel):
    type: str = "file"
    hash: str
    location: str
    to: str
    size: int

    def __hash__(self):
        return hash((
            self.type,
            self.hash,
            self.location,
            self.to,
            self.size,
        ))

    def __eq__(self, other):
        return hash(self) == hash(other)

    class Config:
        allow_mutation = False
        ignore_extra = False


class UserFileTask(BaseModel):
    type: str = "file"
    hash: str
    location: str
    to: str
    size: int

    userFile: bool = True

    def __hash__(self):
        return hash((
            self.type,
            self.hash,
            self.location,
            self.to,
            self.size,
            self.userFile,
        ))

    def __eq__(self, other):
        return hash(self) == hash(other)

    class Config:
        allow_mutation = False
        ignore_extra = False


class FeatureTask(BaseModel):
    type: str = "file"
    hash: str
    location: str
    to: str
    size: int

    when: Dict

    def __hash__(self):
        return hash((
            self.type,
            self.hash,
            self.location,
            self.to,
            self.size,
            self.when['if'],
            frozenset(self.when['features']),
        ))

    def __eq__(self, other):
        return hash(self) == hash(other)

    class Config:
        allow_mutation = False
        ignore_extra = False


class RichManifest(BaseManifest):
    gameVersion: str
    launch: Dict[str, List[str]] = {"flags": []}
    minimumVersion: int = 2
    librariesLocation: Optional[str] = None
    objectsLocation: str
    userFiles: SimplePatternList = SimplePatternList()

    class Config:
        allow_mutation = False


class SourceManifest(RichManifest):
    features: List[Feature] = []

    class Config:
        allow_mutation = False
        ignore_extra = False


class TargetManifest(RichManifest):
    features: List[FeatureProperties] = []
    tasks: List[Union[Task, UserFileTask, FeatureTask]] = []

    def __hash__(self):
        return hash((
            self.gameVersion,
            frozenset(self.launch['flags']),
            self.userFiles,
            self.minimumVersion,
            self.librariesLocation,
            self.objectsLocation,
            frozenset(self.features),
            frozenset(self.tasks),
        ))

    def __eq__(self, other):
        return hash(self) == hash(other)

    class Config:
        allow_mutation = False
        ignore_extra = False


class ModpackStatus(Enum):
    FRESH = "Fresh"
    OUTDATED = "Outdated"
    NOT_DEPLOYED = "Not deployed"
    ORPHANED = "Orphaned"
    BROKEN = "Broken"
    UNKNOWN = "Unknown"


class Modpack(BaseModel):
    name: str
    enabled: bool
    status: ModpackStatus
    source_manifest: Optional[SourceManifest] = None
    target_manifest: Optional[TargetManifest] = None

    class Config:
        allow_mutation = False
        ignore_extra = False


class PatternTestable(Container):
    __patterns: FrozenSet
    __slots__ = ('__patterns',)

    def __contains__(self, item: str) -> bool:
        return any(fnmatch(item, pattern) for pattern in self.__patterns)

    def __init__(self, patterns: Iterable[str]):
        self.__patterns = frozenset(patterns)

    def __len__(self) -> int:
        return len(self.__patterns)
