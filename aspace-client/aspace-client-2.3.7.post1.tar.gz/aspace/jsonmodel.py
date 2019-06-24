"""
Contains functions and classes that can be used when construction common
components of ArchivesSpace's JsonModel objects.
"""

from aspace import enums


def _ref(ref: str):
    """
    ```
    {'ref': ref}
    ```
    """
    return {'ref': ref}


def ref(ref: str):
    """
    ```
    {'ref': ref}
    ```
    """
    return _ref(ref)


def instance_sub_container(instance_type: str, ref: str,
                           type_2: str = None, indicator_2: str = None,
                           type_3: str = None, indicator_3: str = None,
                           ) -> dict:
    """
    The type and indicator parameters apply to the 'sub_container' object.

    ```
    {
        'instance_type': instance_type,
        'sub_container': {'top_container': {'ref': ref}}
    }
    ```
    """
    
    sub_container = {
        'top_container': _ref(ref)
    }

    if type_2 is not None: sub_container['type_2']
    if indicator_2 is not None: sub_container['indicator_2']

    if type_3 is not None: sub_container['type_3']
    if indicator_3 is not None: sub_container['indicator_3']

    return {
        'instance_type': instance_type,
        'sub_container': sub_container
    }


def instance_digital_object(ref: str) -> dict:
    """
    ```
    {
        'instance_type': 'digital_object',
        'digital_object': {'ref': ref}
    }
    ```
    """

    return {
        'instance_type': 'digital_object',
        'digital_object': _ref(ref)
    }


def linked_agent(ref: str, role: enums.LinkedAgentRole, relator: str = None,
                 terms: list = None, title: str = None) -> dict:
    """
    ```
    {
        'ref': ref,
        'role': role.value or role,
        'relator': relator,
        'terms': terms,
        'title': title,        
    }
    ```
    """

    ref = _ref(ref)
    
    ref.update({
        'role': (
            role.value
            if isinstance(role, enums.LinkedAgentRole) else
            role
        ),
        'relator': relator,
        'terms': terms,
        'title': title,
    })

    return ref


def abstract_note(persistent_id: str = None, label: str = None, publish=True):
    """
    ```
    {
        'persistent_id': persistent_id,
        'label': label,
        'publish': publish,
    }
    ```
    """
    return {
        'persistent_id': persistent_id,
        'label': label,
        'publish': publish,
    }


def note_singlepart(note_type: str, content: list, persistent_id: str = None,
                    label: str = None, publish=True):
    """
    ```
    {
        # ...
        'jsonmodel_type': 'note_singlepart',
        'type': note_type,
        'content': content.copy(),
    }
    ```
    """

    note = abstract_note(
        persistent_id=persistent_id,
        label=label,
        publish=publish,
    )
    
    note.update({
        'type': note_type,
        'jsonmodel_type': 'note_singlepart',
        'content': content.copy(),
    })

    return note


def note_multipart(note_type: str, subnotes: list, persistent_id: str = None,
                   label: str = None, publish=True):
    """
    ```
    {
        'jsonmodel_type': 'note_multipart',
        'type': note_type,
        'subnotes': [note for note in subnotes],
        # ...
    }
    ```

    Note: If the contents of subnotes are not dicts, then each will be mapped
    using the `subnote_text` jsonmodel template.
    """
    
    note = abstract_note(
        persistent_id=persistent_id,
        label=label,
        publish=publish,
    )
    
    note.update({
        'type': note_type,
        'jsonmodel_type': 'note_multipart',
        'subnotes': list(map(
            lambda note: 
                note if isinstance(note, dict) else 
                subnote_text(note),
            subnotes,
        ))
    })
    
    return note


def subnote_text(content: str, publish=True):
    """
    ```
    {
        'jsonmodel_type': 'note_text',
        'content': content,
        'publish': publish
    }
    ```
    """
    return {
        'jsonmodel_type': 'note_text',
        'content': content,
        'publish': publish
    }


def subject(source: str, terms: list, vocabulary_uri: str = '/vocabularies/1',
            **kwargs) -> dict:
    """
    {
        'source': source,
        'terms': terms,
        'vocabulary': vocabulary_uri,
        # ...
    }
    """
    _subject = {
        'source': source,
        'terms': terms,
        'vocabulary': vocabulary_uri,
    }
    _subject.update(**kwargs)
    return _subject


def subject_term(term: str, term_type: enums.SubjectTermType,
                 vocabulary_uri: str = '/vocabularies/1') -> dict:
    """
    ```
    {
        'term': term,
        'term_type': term_type.value,
        'vocabulary': vocabulary_uri,
    }
    ```
    """
    return {
        'term': term,
        'term_type': (
            term_type.value
            if isinstance(term_type, enums.SubjectTermType) else
            term_type
        ),
        'vocabulary': vocabulary_uri,
    }


def external_document(title: str, location: str, publish=True) -> dict:
    """
    ```
    {
        'title': title,
        'location': location,
        'publish': publish,
    }
    ```
    """
    return {
        'title': title,
        'location': location,
        'publish': publish,
    }
