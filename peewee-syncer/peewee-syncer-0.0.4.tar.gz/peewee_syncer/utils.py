import itertools
from .models import SyncManager


def chunks(iterable, n):
    try:
        while True:
            yield itertools.chain((next(iterable),), itertools.islice(iterable, n - 1))
    except StopIteration:
        return

def get_sync_manager(app, start, test=None):
    if test and start:
        raise Exception("start or test only. NOT BOTH!")

    if test:
        state = SyncManager()
        state.is_test_run = True
        state.set_last_offset(test, 0)

    else:
        with SyncManager.get_db().connection_context():
            state, created = SyncManager.get_or_create(app=app)

            if not created and start:
                raise Exception("cannot start with existing state. Clear it out first!")

            if created:
                if start is not None:
                    state.set_last_offset(start, 0)
                    state.save()
                else:
                    raise Exception("start required!")

            state.is_test_run = False

    return state


def test_bulk(it):
    import pprint
    for item in it:
        pprint.pprint(item)


def upsert_db_bulk(model, it, preserve=[], conflict_target=None):
    n = 0

    for items in chunks(it, 100):

        items = list(items)

        model.insert_many(items).on_conflict(
            action='UPDATE',
            preserve=preserve,
            conflict_target=conflict_target
        ).execute()

        n += 1

        if n % 50 == 0:
            print(".", end="", flush=True)
