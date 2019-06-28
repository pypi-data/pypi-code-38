# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import Interface, Invalid, invariant
from plone import api
from imio.actionspanel import ActionsPanelMessageFactory as _


class IImioActionsPanelConfig(Interface):
    """
        Configuration schema
    """

    transitions = schema.List(
        title=_(u'Transitions to confirm'),
        description=_(u'Define for each object transition the optional corresponding view'),
        required=False,
        value_type=schema.BytesLine(
            title=_("Transition value"),
            description=_('Formatted like "portal_type" "." "transition name" "|" "view", '
                          'like "Document.publish|" . The view can be empty'),
        )
    )

    @invariant
    def validateSettings(data):
        uniques = []
        states = {}
        if not data._Data_data___:
            return
        if 'value' not in data._Data_data___:
            raise Invalid(_(u"Internal validation error"))
        values = data._Data_data___['value']
        if values is None:
            return
        i = 0
        portal = api.portal.getSite()

        def transitions_for(typ):
            if typ not in states:
                states[typ] = []
                for wf_name in portal.portal_workflow.getChainFor(typ):
                    workflow = portal.portal_workflow[wf_name]
                    for tid in workflow.transitions.objectIds():
                        if tid not in states[typ]:
                            states[typ].append(tid)
            return states[typ]

        for value in values:
            i += 1
            val = value.strip()
            if ' ' in val:
                raise Invalid(_("The value cannot contain space: line ${i}, '${val}'", mapping={'i': i, 'val': value}))
            if val.find('|') <= 0:
                val += '|'
            values[i - 1] = val
            (typ_trans, view) = val.split('|')
            if typ_trans in uniques:
                raise Invalid(_("The transition value '${val}' is set multiple times.", mapping={'val': typ_trans}))
            uniques.append(typ_trans)
            if typ_trans.find('.') <= 0:
                raise Invalid(_("The first part must contain one dot to separate the type and the transition: "
                                "line ${i}, '${val}'", mapping={'i': i, 'val': value}))
            parts = typ_trans.split('.')
            if len(parts) != 2:
                raise Invalid(_("The first part must contain one dot to separate the type and the transition: "
                                "line ${i}, '${val}'", mapping={'i': i, 'val': value}))
            (typ, transition) = typ_trans.split('.')
            if typ not in portal.portal_types.listContentTypes():
                raise Invalid(_("This portal_type doesn't exist: line ${i}, '${val}'", mapping={'i': i, 'val': value}))
            if transition not in transitions_for(typ):
                raise Invalid(_("This transition id isn't valid for the portal_type: line ${i}, '${val}'",
                                mapping={'i': i, 'val': value}))
        data._Data_data___['value'] = values
