"""
Modelling of PEP440-compliant versions and components
"""

import enum
import logging
import re
from datetime import datetime
from itertools import zip_longest


logger = logging.getLogger(__name__)


PEP440_EXPRESSION = re.compile(
    r'(?P<release>(?P<epoch>\d+!)?(?P<components>\d+(\.\d+)*))'
    r'((a(lpha)?(?P<alpha>\d+))|(b(?P<beta>\d+))|(rc(?P<candidate>\d+)))?'
    r'(\.post(?P<post>\d+))?'
    r'(\.dev(?P<dev>\d+))?'
    r'(\+(?P<local>[A-Za-z0-9.]*))?'
)


class Release:
    """
    A release version; e.g. 6.2.8
    """
    EXPRESSION = re.compile(r'(?P<epoch>\d+!)?(?P<components>\d+(\.\d+)*)')

    def __init__(self, components):
        """
        :param iterable components: An iterable of non-negative integers
        """
        try:
            iter(components)
        except TypeError:
            components = (components,)
        bad_values = []
        self.components = tuple(int(x) for x in components) 
        for index, component in enumerate(self.components):
            if component < 0:
                bad_values.append(f'{component!r} (index {index})')
        if bad_values:
            raise ValueError(
                'components must consist of non-negative integers;'
                f' bad values are {", ".join(bad_values)}')

    def __str__(self):
        return '.'.join(str(x) for x in self.components)

    def get_bumped(self, index=None, increment=1):
        """
        Obtain a new release version by bumping the component at the specified
        index by the specified increment. All following components will be set
        to zero.

        :param int index: Position of the component to bump.
        :param int increment: Amouny by which to increase specified component
        :return Release:
        """
        if index is None:
            index = len(self.components) - 1
        new_components = [
            x for x, _ in zip_longest(
                self.components[:index + 1], range(index + 1), fillvalue=0)
        ]
        new_components[index] += increment
        new_components.extend(
            0 for _ in range(len(self.components) - len(new_components)))
        return Release(components=new_components)

    @classmethod
    def from_datetime(cls, time=None):
        if time is None:
            time = datetime.utcnow()
        components = time.utctimetuple()[:3]
        return cls(components=components)

    @classmethod
    def from_str(cls, string):
        """
        Create a Release version from a PEP440-compliant release string

        :param str string: A PEP440-comliant release string
        :return Release:
        """
        match = cls.EXPRESSION.fullmatch(string.strip())
        return cls(components=match['components'].split('.'))


class Prerelease:
    """
    A prerelease version, e.g. rc1337
    """
    class Category(enum.IntEnum):
        """
        Types of prerelease versions
        """
        ALPHA = 1
        BETA = 2
        RELEASE_CANDIDATE = 3

    EXPRESSION = re.compile(
        r'('
            r'(?P<alpha>a(lpha)?)'
            r'|(?P<beta>b(eta)?)'
            r'|(?P<release_candidate>((r?c)|(pre(view)?)))'
        r')([.-_]?(?P<value>\d+))?',
        flags=re.IGNORECASE,
    )

    _PREFIXES = {
        Category.ALPHA: 'a',
        Category.BETA: 'b',
        Category.RELEASE_CANDIDATE: 'rc',
    }

    def __init__(self, category, value=0):
        """
        :param Prerelease.Category category: A prerelease category
        :param int value: A non-negative integer
        """
        self.category = category
        self.value = value

    def __str__(self):
        return f'{self._PREFIXES[self.category]}{self.value}'

    def get_bumped(self, increment=1):
        """
        Create a new prerelease version by bumping this one by the specified
        increment. The category will remain the same.

        :param int increment: The amount by which to increase the version
        :return Prerelease:
        """
        return Prerelease(category=self.category, value=self.value + increment)

    @classmethod
    def from_str(cls, string):
        """
        Create a Prerelease version from a PEP440-compliant prerelease version
        string.

        :param str string: A PEP440-compliant prerelease version string
        :return Prerelease:
        """
        match = cls.EXPRESSION.fullmatch(string.strip())
        for name in 'alpha', 'beta', 'release_candidate':
            if match[name]:
                category = Prerelease.Category[name.upper()]
                break
        else:
            raise ValueError(
                f'{string!r} does not contain a valid prerelease category')
        optionals = {}
        if match['value'] is not None:
            optionals['value'] = int(match['value'])
        return cls(category=category, **optionals)


class LocalVersion:
    """
    A PEP440-compliant local version specification
    """
    EXPRESSION = re.compile(r'[a-z0-9]+([.\-_][a-z0-9]+)*', flags=re.IGNORECASE)
    _SEPARATOR_EXPRESSION = re.compile(r'[.\-_]')

    def __init__(self, segments):
        """
        :param iterable segments: An iterable of local version segments
            comprising non-negative integers or alphanumeric character strings.
        """
        self.segments = tuple(segments)

    def __str__(self):
        return '.'.join(str(x) for x in self.segments)

    @classmethod
    def from_str(cls, string):
        """
        Create a local version specifier from a PEP440-compliant local version
        string.

        :param str string: A PEP440-compliant local version string
        """
        if not cls.EXPRESSION.fullmatch(string):
            raise ValueError(
                f'{string!r} is not a valid local version specifier')
        segments = []
        for segment in cls._SEPARATOR_EXPRESSION.split(string.strip()):
            try:
                segments.append(int(segment))
            except ValueError:
                segments.append(segment)
        return cls(segments=segments)


class Version:
    """
    A PEP440-compliant version
    """
    EXPRESSION = re.compile(
        r'v?(?P<release>' + Release.EXPRESSION.pattern + r')' + r'('
            r'[.-_]?(?P<prerelease>' + Prerelease.EXPRESSION.pattern + r'))?'
            r'((([.-_]?(post|r(ev)?)(?P<post>\d+)?)|-(?P<implicit_post>\d+)))?'
            r'([.-_]?dev(?P<dev>\d+))?'
            r'(\+(?P<local>' + LocalVersion.EXPRESSION.pattern + r'))?',
        flags=re.IGNORECASE,
    )

    def __init__(
            self,
            *,
            release,
            epoch=0,
            prerelease=None,
            post=None,
            dev=None,
            local=None,
    ):
        """
        :param Release release: The release version
        :param int epoch: The epoch
        :param Prerelease prerelease: The prerelease version
        :param int post: The postrelease version
        :param int dev: The development version
        :param str local: The local version string
        """
        if epoch < 0:
            raise ValueError
        if isinstance(release, str):
            release = Release.from_str(release)
        if isinstance(prerelease, str):
            prerelease = Prerelease.from_str(prerelease)
        if post is not None and post < 0:
            raise ValueError('post must be a non-negative integer')
        if dev is not None and dev < 0:
            raise ValueError('dev must be a non-negative integer')
        if isinstance(local, str):
            local = LocalVersion.from_str(local)
        self.release = release
        self.prerelease = prerelease
        self.post = post
        self.dev = dev
        self.local = local

    def __repr__(self):
        return f'{self.__class__.__name__}.from_str({str(self)!r})'

    def __str__(self):
        strings = [str(self.release)]
        if self.prerelease:
            strings.append(str(self.prerelease))
        if self.post:
            strings.append(f'.post{self.post}')
        if self.dev:
            strings.append(f'.dev{self.dev}')
        if self.local:
            strings.append(f'+{self.local}')
        return ''.join(strings)

    def get_bumped(self, release_index=None, field='release', increment=1):
        """
        Get the Version corresponding to this Version bumped according to the
        specified parameters.

        :param int release_index: The index of the release version to bump
        :param str field: The Version segment to bump
        :param int increment: The amount by which to bump the specified segment
        :return Version:
        """
        if field == 'release':
            release = self.release.get_bumped(
                index=release_index, increment=increment)
            return self.__class__(release=release)
        if release_index is not None:
            raise ValueError(
                "release index can only be specified for a 'release' bump")
        if field == 'prerelease':
            prerelease = self.prerelease.get_bumped(increment=increment)
            return self.__class__(release=self.release, prerelease=prerelease)
        optionals = {'prerelease': self.prerelease}
        if field == 'post':
            optionals['post'] = self.post + increment
            return self.__class__(release=release, **optionals)
        optionals['post'] = self.post
        if field == 'dev':
            optionals['dev'] = self.dev + increment
            return self.__class__(release=self.release, **optionals)
        raise ValueError(f'{field!r} is not a bumpable version field')

    @classmethod
    def from_datetime(cls, time=None, **kwargs):
        return cls(release=Release.from_datetime(time), **kwargs)

    @classmethod
    def from_str(cls, string):
        """
        Construct a Version from a string

        :param str string: A PEP44-compliant version string
        :return Version:
        """
        match = cls.EXPRESSION.fullmatch(string)
        if not match:
            raise ValueError(
                f'{string!r} is not a PEP440-compliant public version string')
        release = Release.from_str(match['release'])
        optionals = {}
        if match['prerelease']:
            optionals['prerelease'] = Prerelease.from_str(match['prerelease'])
        if match['post']:
            optionals['post'] = int(match['post'])
        elif match['implicit_post']:
            optionals['post'] = int(match['implicit_post'])
        if match['dev']:
            optionals['dev'] = int(match['dev'])
        if match['local']:
            optionals['local'] = LocalVersion.from_str(match['local'])
        return cls(release=release, **optionals)

