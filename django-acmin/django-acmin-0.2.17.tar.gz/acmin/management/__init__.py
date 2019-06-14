inited = False


def init_models(sender, **kwargs):
    global inited
    if not inited:
        inited = True
        from acmin.models.field import init_fields
        from acmin.models.contenttype import init_contenttype
        from acmin.models.choice import init_choices
        type_map = init_contenttype()
        init_fields(type_map)
        init_choices()
