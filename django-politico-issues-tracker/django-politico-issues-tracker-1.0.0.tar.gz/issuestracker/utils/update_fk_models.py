from issuestracker.utils.diff_relative_complement import diff
import logging


logger = logging.getLogger("serializer")


def update_fk_models(instance, data, model, serializer, context_keys=[]):
    """
    Given a model with instance names, array of dictionaries, a model,
    and a serializer: use the serializer's save method to update, create,
    or delete an entry.
    """
    # Delete models
    model_name = model.__name__.lower()
    old_model_ids = [
        m.id for m in getattr(instance, "{}_set".format(model_name)).all()
    ]
    new_model_ids = [m["id"] for m in data if "id" in m]
    for id in diff(old_model_ids, new_model_ids):
        model.objects.get(pk=id).delete()

    # Update/create models
    for row in data:
        id = row.pop("id", None)

        kwargs = {}
        for key in context_keys:
            kwargs[key] = row.pop(key)

        if id:
            m = model.objects.get(pk=id)
            s = serializer(m, data=row)
        else:
            s = serializer(data=row)

        if not s.is_valid():
            logger.error(s.errors)

        s.is_valid(raise_exception=True)

        s.save(**kwargs)
