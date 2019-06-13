"""
This module describes internalization features for SQLAlchemy models.

Provides new i18-aware string column type. Needs special initialization procedure before usage.
please refer to README.rst of the package for more information.

public functions: initialize i18n_column, i18n_relation.
"""
import collections

from sqlalchemy import Column, Integer, ForeignKey, UnicodeText, event
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import relationship, mapper
from sqlalchemy.orm.base import NO_VALUE, NEVER_SET
from sqlalchemy.orm.properties import RelationshipProperty
from sqlalchemy.sql import operators as oper, or_

from traduki import config
from traduki import helpers

# Tuple class describing the return value of the initialization function
Attributes = collections.namedtuple('Attributes', ['Translation', 'i18n_column', 'i18n_relation'])


class TranslationMixin(object):
    """Helper for future translation class which is created during initialization."""

    __tablename__ = 'traduki_translation'

    id = Column(Integer, primary_key=True)

    def get_dict(self):
        """Get language dictionary.
        The key is the language code and the value is the corresponding localized text.
        """
        return dict(
            (language, getattr(self, language))
            for language in helpers.get_supported_languages()
            if getattr(self, language)
        )

    def get_text(self, code=None, chain=None):
        """Get the text for specified language code.
        Delegates to :py:func:`LocalizedString.get_text_from_dict`, with all the given arguments and
        a dictionary, representing this :py:class:`Translation`.
        The dictionary is created using :py:func:`get_dict`.

        :param code: Language code.
        :param chain: Language code resolution chain.

        :returns: Unicode value if found or None.
        """
        return helpers.get_text_from_dict(self.get_dict(), code=code, chain=chain)

    def __unicode__(self):
        return self.get_text() or u''

    def __nonzero__(self):
        return bool(unicode(self))


def initialize(base, languages, get_current_language_callback, get_language_chain_callback, attributes=None):
    """Initialize using given declarative base.

    :param base: SQLAlchemy declarative base class
    :param languages: `iterable` of supported language codes
    :param get_current_language_callback: function which returns current language code
    :param get_language_chain_callback: function which returns language chain `dict`
        in format: {'<selector>': '<language code>'}
    :param attributes: `dict` of future Translation class additional attributes or overrides.
    For example: {'__tablename__': 'some_other_table'
    :return: `Attributes` object which contains:
        * Translation class
        * i18n_column helper to create i18n-aware columns on user models
        * i18n_relation helper to create i18n-aware relationships on user models

    """

    config.LANGUAGE_CALLBACK = get_current_language_callback
    config.LANGUAGE_CHAIN_CALLBACK = get_language_chain_callback
    config.LANGUAGES = languages

    if attributes is None:
        attributes = {}

    attributes.update(dict(((lang, Column(UnicodeText, nullable=True)) for lang in languages)))

    Translation = type('Translation', (TranslationMixin, base), attributes)

    class TranslationComparator(RelationshipProperty.Comparator):
        """
        RelationshipProperty.Comparator modification to enable the use of like, startswith, endswith and contains
        directly on the relationship. Each of the comparators compares against the first non-null item in the list of
        columns (languages) available, in order of preference (see ordered_languages() in this module).

        Raises NotImplementedError exception when using not with like, contains or startswith.
        All the `like` operations will look into next language if the specified language is not filled in.
        """

        LIKE_OPS = {oper.like_op, oper.contains_op, oper.startswith_op, oper.endswith_op}

        # Only the operators in LIKE_OPS are allowed on this relationship
        def operate(self, op, *other, **kw):
            if op in self.LIKE_OPS:
                return self._do_compare(op, *other, **kw)
            else:
                raise NotImplementedError()

        # contains is redefined in RelationshipProperty.Comparator, so we need to override it
        def contains(self, other, escape=None):
            return self.operate(oper.contains_op, other, escape=escape)

        def _do_compare(self, op, other, escape):
            """Perform comparison operations to the columns of the Translation model.
            Looking into all languages using the OR operator.
            """
            related = self.property.mapper.class_
            ops = [
                op(getattr(related, lang), other, escape=escape)
                for lang in helpers.get_ordered_languages()
                if hasattr(related, lang)
            ]
            return self.has(or_(*ops))

    def translation_attribute_set_hook(state, value, oldvalue, initiator):
        """Set accessor for the `Translation` object.

        :note: The value is copied using dict to avoid 2 objects
            referring to the same Translation. Also the oldvalue should
            wipe the values for the languages that are not in the value.

        :param state: SQLAlchemy instance state.
        :param value: The value that is being assigned.
        :param oldvalue: The current value.
        :param initiator: SQLAlchemy initiator (accessor).
        """
        # Need to check also against SQLAlchemy symbols:
        # https://github.com/sqlalchemy/sqlalchemy/issues/4691#issuecomment-495269727
        if value is None or value in (NO_VALUE, NEVER_SET):
            return None

        if isinstance(value, dict):
            value_dict = value
        else:
            value_dict = value.get_dict()

        if oldvalue is None:
            return Translation(**value_dict)
        else:
            for lang in helpers.get_ordered_languages():
                setattr(oldvalue, lang, value_dict.get(lang))

        return oldvalue

    def i18n_column(*args, **kwargs):
        """Create Column which is a ForeignKey to Translation class generated during initialization of the package.
        :param *args, **kwargs: parameters normally passed to SQLAlchemy `Column`
        return: `Column`
        """
        kw = dict(index=True, nullable=False, unique=True)
        kw.update(**kwargs)
        return Column(Integer, ForeignKey(Translation.id), *args, **kw)

    def i18n_relation(column=None, comparator_factory=TranslationComparator, lazy=True, **kwargs):
        """Convenience function for a relationship to i18n.Translation.

        :param column: The column that stores ID of localized text,
                       which should be result of the ``i18n_column``.
                       You need to provide it if there is more than one
                       localized field in the model class
        """
        if column is not None:
            if 'primaryjoin' in kwargs:
                raise ArgumentError("You cannot supply 'primaryjoin' argument to 'i18n_relation'")
            kwargs['primaryjoin'] = column == Translation.id

        res = relationship(
            Translation,
            comparator_factory=comparator_factory,
            lazy=lazy,
            # This required only for sqlalchemy < 1.3.4. See https://github.com/sqlalchemy/sqlalchemy/issues/4691
            active_history=True,
            **kwargs
        )

        # We must attach the event on before_configured. If we use after_configured, we're too late
        # as other hooks will already be installed by SQLAlchemy.
        @event.listens_for(mapper, 'before_configured')
        def setup_translation_set():
            event.listen(
                res,
                'set',
                translation_attribute_set_hook,
                retval=True,
                active_history=True,
                propagate=True,
            )

        return res

    return Attributes(Translation=Translation, i18n_column=i18n_column, i18n_relation=i18n_relation)
