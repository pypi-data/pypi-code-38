from pypeeper.pypeeper import Observable, Observer


# Make whichever class wanted to be observed subclass of Observable
class AnyClass(Observable):

    def __init__(self):
        self.attribute_a = False
        self.whatever_attr = 0

    def set_attribute(self, value):
        self.attribute_a = value


# Implement an observer class
class ObserverClass(Observer):

    # Override notify method within the class context to perform desired action
    # on notify events received by any Observable subclass.
    def notify(self, class_name, object_id, attribute_name, old, new):
        print(class_name, object_id, attribute_name, old, new)


# Instantiates both Observable and Observer
my_observable = AnyClass()
my_observer = ObserverClass()

# Since Observable's 'pattern' class attribute have no been overwritten,
# changes on every attribute will notify all Observer classes.
my_observable.set_attribute(True)
my_observable.attribute_a = 10
my_observable.whatever_attr = None

# Console output
# >>> AnyClass 2448221506696 attribute_a False True
# >>> AnyClass 2448221506696 attribute_a True 10
# >>> AnyClass 2448221506696 whatever_attr 0 None
