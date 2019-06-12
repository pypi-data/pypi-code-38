from Acquisition import aq_parent
from DateTime import DateTime
from plone import api
from Products.CMFCore.utils import getToolByName


def question_transition(question, event):
    if event.action in ['approve-question']:
        wf = getToolByName(question, 'portal_workflow')
        comment_id = wf.getInfoFor(question,
            'comments', wf_id='esd-question-review-workflow')
        comment = question.get(comment_id, None)
        if comment is not None:
            comment_state = api.content.get_state(obj=comment)
            comment.setEffectiveDate(DateTime())
            if comment_state in ['initial']:
                api.content.transition(obj=comment, transition='publish')

    if event.action in ['approve-question']:
        observation = aq_parent(question)
        if api.content.get_state(observation) == 'draft':
            api.content.transition(obj=observation, transition='open')

    if event.action in ['recall-question-lr']:
        wf = getToolByName(question, 'portal_workflow')
        comment_id = wf.getInfoFor(question,
            'comments', wf_id='esd-question-review-workflow')
        comment = question.get(comment_id, None)
        if comment is not None:
            comment_state = api.content.get_state(obj=comment)
            if comment_state in ['public']:
                api.content.transition(obj=comment, transition='retract')

    if event.action in ['answer-to-lr']:
        wf = getToolByName(question, 'portal_workflow')
        comment_id = wf.getInfoFor(question,
            'comments', wf_id='esd-question-review-workflow')
        comment = question.get(comment_id, None)
        if comment is not None:
            comment_state = api.content.get_state(obj=comment)
            comment.setEffectiveDate(DateTime())
            if comment_state in ['initial']:
                api.content.transition(obj=comment, transition='publish')

    if event.action in ['recall-msa']:
        wf = getToolByName(question, 'portal_workflow')
        comment_id = wf.getInfoFor(question,
            'comments', wf_id='esd-question-review-workflow')
        comment = question.get(comment_id, None)
        if comment is not None:
            comment_state = api.content.get_state(obj=comment)
            if comment_state in ['public']:
                api.content.transition(obj=comment, transition='retract')

    observation = aq_parent(question)
    observation.reindexObject()


def observation_transition(observation, event):
    if event.action == 'reopen-qa-chat':
        with api.env.adopt_roles(roles=['Manager']):
            qs = [q for q in observation.values() if q.portal_type == 'Question']
            if qs:
                q = qs[0]
                api.content.transition(obj=q, transition='reopen')

    elif event.action in ['request-comments']:
        with api.env.adopt_roles(roles=['Manager']):
            conclusions = [c for c in observation.values() if c.portal_type == 'Conclusions']
            if conclusions:
                conclusion = conclusions[0]
                api.content.transition(obj=conclusion,
                    transition='request-comments')

    elif event.action in ['finish-comments']:
        with api.env.adopt_roles(roles=['Manager']):
            conclusions = [c for c in observation.values() if c.portal_type == 'Conclusions']
            if conclusions:
                conclusion = conclusions[0]
                api.content.transition(obj=conclusion,
                    transition='redraft')

    elif event.action in ['finish-observation', 'recall-lr']:
        with api.env.adopt_roles(roles=['Manager']):
            conclusions = [c for c in observation.values() if c.portal_type == 'Conclusions']
            if conclusions:
                conclusion = conclusions[0]
                api.content.transition(obj=conclusion,
                    transition='ask-approval')

    elif event.action in ['confirm-finishing-observation']:
        with api.env.adopt_roles(roles=['Manager']):
            conclusions = [c for c in observation.values() if c.portal_type == 'Conclusions']
            if conclusions:
                conclusion = conclusions[0]
                api.content.transition(obj=conclusion,
                    transition='publish')

    elif event.action in ['deny-finishing-observation']:
        with api.env.adopt_roles(roles=['Manager']):
            conclusions = [c for c in observation.values() if c.portal_type == 'Conclusions']
            if conclusions:
                conclusion = conclusions[0]
                api.content.transition(obj=conclusion,
                    transition='redraft')

    elif event.action == 'draft-conclusions':
        with api.env.adopt_roles(roles=['Manager']):
            questions = [c for c in observation.values() if c.portal_type == 'Question']
            if questions:
                question = questions[0]
                if api.content.get_state(question) == 'draft':
                    api.content.transition(obj=question,
                        transition='close')
                elif api.content.get_state(question) in ['drafted', 'recalled-lr']:
                    api.content.transition(obj=question,
                        transition='close-lr')

    elif event.action == 'recall-from':
        with api.env.adopt_roles(roles=['Manager']):
            questions = [c for c in observation.values() if c.portal_type == 'Question']
            if questions:
                question = questions[0]
                api.content.transition(
                    obj=question,
                    transition='recall'
                )

    elif event.action == 'reopen-closed-observation':
        with api.env.adopt_roles(roles=['Manager']):
            conclusions = [c for c in observation.values() if c.portal_type == 'Conclusions']
            if conclusions:
                conclusion = conclusions[0]
                api.content.transition(
                    obj=conclusion,
                    transition='redraft'
                )
                api.content.transition(
                    obj=conclusion,
                    transition='ask-approval'
                )

    observation.reindexObject()
