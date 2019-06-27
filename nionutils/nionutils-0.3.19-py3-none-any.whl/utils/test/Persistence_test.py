# standard libraries
import unittest
import uuid

# third party libraries
# None

# local libraries
from nion.utils import Persistence


class ObjectWithUUID(object):

    def __init__(self):
        self.uuid = uuid.uuid4()


class TestPersistentObjectContextClass(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_persistent_object_context_calls_register_on_already_registered_object(self):
        global was_registered
        persistent_object_context = Persistence.PersistentObjectContext()
        object1 = ObjectWithUUID()
        persistent_object_context.register(object1)
        was_registered = False
        def registered(object):
            global was_registered
            was_registered = True
        persistent_object_context.subscribe(object1.uuid, registered, None)
        self.assertTrue(was_registered)

    def test_persistent_object_context_calls_register_when_object_becomes_registered(self):
        global was_registered
        persistent_object_context = Persistence.PersistentObjectContext()
        object1 = ObjectWithUUID()
        was_registered = False
        def registered(object):
            global was_registered
            was_registered = True
        persistent_object_context.subscribe(object1.uuid, registered, None)
        persistent_object_context.register(object1)
        self.assertTrue(was_registered)

    def test_persistent_object_context_calls_unregister_when_object_becomes_unregistered(self):
        global was_registered
        persistent_object_context = Persistence.PersistentObjectContext()
        object1 = ObjectWithUUID()
        was_registered = False
        def registered(object):
            global was_registered
            was_registered = True
        def unregistered(object):
            global was_registered
            was_registered = False
        persistent_object_context.subscribe(object1.uuid, registered, unregistered)
        persistent_object_context.register(object1)
        self.assertTrue(was_registered)
        persistent_object_context.unregister(object1)
        self.assertFalse(was_registered)

    def test_persistent_object_context_unregister_without_subscription_works(self):
        # this test will only generate extra output in the failure case, which has been fixed
        persistent_object_context = Persistence.PersistentObjectContext()
        object1 = ObjectWithUUID()
        persistent_object_context.register(object1)
        object1 = None
