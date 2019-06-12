from j5basic import ObjTracker

def test_objtracker():
    ot = ObjTracker.ObjTracker()
    new_objects = []
    for i in range(10):
        new_objects.append({})

    ot.print_changes()