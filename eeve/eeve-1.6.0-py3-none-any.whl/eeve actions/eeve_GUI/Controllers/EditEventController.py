from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, Qt, QAbstractListModel  # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QWidget  # pylint: disable=no-name-in-module
from .EditTriggerController import EditTriggerController  # pylint: disable=relative-beyond-top-level
from .EditActionController import EditActionController  # pylint: disable=relative-beyond-top-level
from .. import GuiController, primary_color  # pylint: disable=relative-beyond-top-level

import eeve  # pylint: disable=import-error
from eeve.base_classes import Event, Trigger, Action, Task  # pylint: disable=import-error
from eeve import database


class EditEventController(GuiController):

    eventEditInitialized = pyqtSignal(str, arguments=['eventName'])

    def load_page(self, event: Event, database_ref: database.Event, clear=False):
        self.selected_event = event
        self.editing_trigger = None
        self.editing_action = None
        self.database_ref = database_ref

        root = self.main_controller.engine.rootObjects()[0]
        self.reload_actions(root)
        self.reload_triggers(root)
        self.eventEditInitialized.emit(self.selected_event.name)

    def reload_triggers(self, root):
        result = root.findChild(QAbstractListModel, "listmodeltriggers")

        self.invoke(result, 'clearItems', 0)

        for i, trigger in enumerate(self.selected_event.triggers):
            value = {"name": trigger.name, "colorCode": primary_color, "tag": i}
            self.invoke(result, 'addItem', value)

    def reload_actions(self, root):
        result = root.findChild(QAbstractListModel, "listmodelactions")

        self.invoke(result, 'clearItems', 0)

        for i, action in enumerate(self.selected_event.task.actions):
            value = {"name": action.name, "colorCode": primary_color, "tag": i}
            self.invoke(result, 'addItem', value)

    @pyqtSlot()
    def addTrigger(self):
        print('add trigger')

        t = Trigger.make(template=eeve.trigger_templates['on eeve startup'])
        self.selected_event.triggers.append(t)
        self.editing_trigger = len(self.selected_event.triggers) - 1

        dbt = database.Trigger(name=t.name)
        self.database_ref.triggers.append(dbt)

        self.load_controller(EditTriggerController, t, dbt)

    @pyqtSlot()
    def addAction(self):
        print('add action')

        a = Action(action_info=eeve.action_templates['start gui'])
        self.selected_event.task.actions.append(a)
        self.editing_action = len(self.selected_event.task.actions) - 1

        dba = database.Action(name=a.name)
        self.database_ref.task.actions.append(dba)

        self.load_controller(EditActionController, a, dba)

    @pyqtSlot(QObject, int, int)
    def clickedTrigger(self, r, index, data):
        #print('selected trigger:', self.selected_event.triggers[data])
        r.setProperty('color', '#ff0000')
        self.editing_trigger = data
        self.load_controller(EditTriggerController, self.selected_event.triggers[data],
                             self.database_ref.triggers[data])

    @pyqtSlot(QObject, int, int)
    def clickedAction(self, r, index, data):
        #print('selected action:', self.selected_event.task.actions[data])
        r.setProperty('color', '#ff0000')
        self.editing_action = data
        self.load_controller(EditActionController, self.selected_event.task.actions[data],
                             self.database_ref.task.actions[data])

    @pyqtSlot(int)
    def deleteAction(self, index):
        self.selected_event.task.actions.pop(index)
        self.selected_event.task.update_actions()

        i = self.database_ref.task.actions.pop(index)
        # delete i

        self.load_page(event=self.selected_event, database_ref=self.database_ref, clear=True)

    @pyqtSlot(int)
    def deleteTrigger(self, index):
        self.selected_event.triggers[index].unregister()
        self.selected_event.triggers.pop(index)

        i = self.database_ref.triggers.pop(index)
        # delete i

        self.load_page(event=self.selected_event, database_ref=self.database_ref, clear=True)

    @pyqtSlot(str)
    def nameChanged(self, name):
        self.selected_event.name = name
        self.database_ref.name = name

    def regain_focus(self, obj):
        obj, db_obj = obj
        if type(obj) is Trigger:
            trigger: Trigger = obj
            if self.editing_trigger is not None:
                self.selected_event.triggers[self.editing_trigger] = trigger
                # no need to change db here
            else:
                self.selected_event.triggers.append(trigger)
                self.database_ref.triggers.append(db_obj)

        elif type(obj) is Action:
            action: Action = obj
            if self.editing_action is not None:
                self.selected_event.task.actions[self.editing_action] = action
                # no need to change db here
            else:
                self.selected_event.task.actions.append(action)
                self.database_ref.task.actions.append(db_obj)

            self.selected_event.task.update_actions()

        self.load_page(event=self.selected_event, database_ref=self.database_ref, clear=True)

    def unload_page(self):
        return self.selected_event
