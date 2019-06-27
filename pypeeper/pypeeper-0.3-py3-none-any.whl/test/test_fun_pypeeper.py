import unittest

from pypeeper.pypeeper import Observable, Observer


class DummyObservableA(Observable):

    def __init__(self):
        self.attribute_a = False
        self.attribute_b = False

    def set_attr_a(self, value):
        self.attribute_a = value

    def set_attr_b(self, value):
        self.attribute_b = value

    def set_all_attributes(self, value):
        self.attribute_a = value
        self.attribute_b = value


class DummyObservableB(Observable):
    pattern = r'^.*\_state$'

    def __init__(self):
        self.a_state = False
        self.attribute_b = False

    def set_a_state(self, value):
        self.a_state = value

    def set_attr_b(self, value):
        self.attribute_b = value


class DummyObserver(Observer):

    def __init__(self):
        self.notify_log = []

    def notify(self, cls, object_id, attribute_name, old, new):
        self.notify_log.append(
            (cls, object_id, attribute_name, old, new)
        )


class DummyObserverB(Observer):

    def __init__(self):
        self.notify_log = []

    def notify(self, class_name, object_id, attribute_name, old, new):
        self.notify_log.append(
            (class_name, object_id, attribute_name, old, new)
        )


class TestPyPeeper(unittest.TestCase):

    def test_changing_value_via_method(self):
        my_observable = DummyObservableA()
        my_observer = DummyObserver()

        my_observable.set_attr_a(True)
        change_event = my_observer.notify_log[-1]

        self.assertEqual(
            my_observable.__class__.__name__,
            change_event[0].__class__.__name__
        )
        self.assertEqual(id(my_observable), change_event[1])
        self.assertEqual('attribute_a', change_event[2])
        self.assertEqual(False, change_event[3])
        self.assertEqual(True, change_event[4])

    def test_changing_value_direct_access(self):
        my_observable = DummyObservableA()
        my_observer = DummyObserver()
        my_observable.set_attr_a(True)
        change_event = my_observer.notify_log[-1]

        self.assertEqual(
            my_observable.__class__.__name__,
            change_event[0].__class__.__name__
        )
        self.assertEqual(id(my_observable), change_event[1])
        self.assertEqual('attribute_a', change_event[2])
        self.assertEqual(False, change_event[3])
        self.assertEqual(True, change_event[4])

    def test_set_same_value(self):
        my_observable = DummyObservableA()
        my_observer = DummyObserver()
        my_observable.set_attr_a(False)

        self.assertFalse(my_observer.notify_log)

    def test_different_instances_same_observable(self):
        my_observable = DummyObservableA()
        my_observable_2 = DummyObservableA()
        my_observer = DummyObserver()
        my_observable.set_attr_a(True)
        my_observable_2.set_attr_a(True)
        change_event = my_observer.notify_log[-2]
        change_event_2 = my_observer.notify_log[-1]

        self.assertEqual(
            change_event[0].__class__.__name__,
            change_event_2[0].__class__.__name__
        )
        self.assertNotEqual(change_event[1], change_event_2[1])
        self.assertEqual(change_event[2], change_event_2[2])
        self.assertEqual(change_event[3], change_event_2[3])

    def test_same_observer_receive_from_different_observables(self):
        my_observable = DummyObservableA()
        my_observable_b = DummyObservableB()
        my_observer = DummyObserver()
        my_observable.set_attr_a(True)
        my_observable_b.set_a_state(True)
        change_event = my_observer.notify_log[-2]
        change_event_2 = my_observer.notify_log[-1]

        self.assertNotEqual(change_event[0], change_event_2[0])
        self.assertNotEqual(change_event[1], change_event_2[1])

    def test_different_observers_receive_same_events(self):
        my_observable = DummyObservableA()
        my_observer = DummyObserver()
        my_observer_b = DummyObserverB()

        my_observable.set_attr_a(True)
        change_event = my_observer.notify_log[-1]
        change_event_b = my_observer_b.notify_log[-1]

        self.assertEqual(change_event, change_event_b)

    def test_observable_custom_pattern(self):
        my_observable_b = DummyObservableB()
        my_observer = DummyObserver()

        my_observable_b.set_attr_b(True)
        self.assertFalse(my_observer.notify_log)

        my_observable_b.attribute_b = 1
        self.assertFalse(my_observer.notify_log)

        my_observable_b.set_a_state(True)
        self.assertTrue(my_observer.notify_log)
