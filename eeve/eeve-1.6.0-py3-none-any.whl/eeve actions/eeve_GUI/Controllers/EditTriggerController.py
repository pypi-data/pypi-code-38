from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QAbstractListModel  # pylint: disable=no-name-in-module

import eeve
from eeve.base_classes import Event, Trigger, Task, Action
from .. import GuiController  # pylint: disable=relative-beyond-top-level
from eeve import database


class EditTriggerController(GuiController):
    def load_page(self, trigger: Trigger, database_ref: database.Trigger):

        self.trigger = trigger
        self.database_ref = database_ref

        if self.trigger is None:
            self.trigger = Trigger.make(template=eeve.trigger_templates['on eeve startup'])

        root = self.main_controller.engine.rootObjects()
        root = root[0]
        result = root.findChild(QAbstractListModel, "tlm")
        self.invoke(result, 'clearItems', None)
        index = 0
        for i, trigger_name in enumerate(eeve.trigger_templates):
            self.invoke(result, 'addItem', str(trigger_name))
            if trigger_name == self.trigger.name:
                index = i

        result = root.findChild(QObject, "triggersComboBox")
        result.setProperty("currentIndex", index)

        result = root.findChild(QAbstractListModel, "listmodelargs")
        for i, trigger_arg in enumerate(self.trigger.args):
            value = {"value": str(trigger_arg), 'tag': i}
            self.invoke(result, 'addItem', value)

    def unload_page(self):
        print('unloading page')
        return self.trigger, self.database_ref

    @pyqtSlot(str)
    def triggerChanged(self, trigger_name):
        t = self.trigger
        self.trigger = Trigger.make(*t.args, template=eeve.trigger_templates[trigger_name], **t.kwargs)
        t = None
        print(self.trigger)
        self.database_ref.name = trigger_name

    @pyqtSlot(int, str)
    def argsChanged(self, index, value):
        print(index, value)
        #if '=' in value:


        self.trigger.args = list(self.trigger.args)
        self.trigger.args[index] = value
        self.database_ref.arguments[index].value = value

    @pyqtSlot()
    def addTriggerArgument(self):
        root = self.main_controller.engine.rootObjects()
        root = root[0]
        result = root.findChild(QAbstractListModel, "listmodelargs")

        i = len(self.trigger.args)
        self.trigger.args = list(self.trigger.args)
        self.trigger.args.append(f'arg {i}')
        self.database_ref.arguments.append(database.TriggerArgument(value=f'arg {i}'))

        self.invoke(result, "addItem", {'value': self.trigger.args[i], 'tag': i})

    @pyqtSlot(int)
    def deleteArg(self, index):
        root = self.main_controller.engine.rootObjects()
        root = root[0]
        result = root.findChild(QAbstractListModel, "listmodelargs")
        self.invoke(result, "clearItems", None)

        self.trigger.args: list = list(self.trigger.args)
        self.trigger.args.pop(index)
        i = self.database_ref.arguments.pop(index)
        #delete i

        self.load_page(trigger=self.trigger, database_ref=self.database_ref)


def print_child(obj, i=0):
    print('-' * 4 * i, obj.property("objectName"), obj)
    for dp in QObject.dynamicPropertyNames(obj):
        print('-' * 4 * i, 'prop:', dp, obj.property(dp))

    for c in obj.children():
        print_child(c, i + 1)
