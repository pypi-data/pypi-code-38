from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, Qt, QAbstractListModel  # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QWidget  # pylint: disable=no-name-in-module
from .EditEventController import EditEventController  # pylint: disable=relative-beyond-top-level
from .. import GuiController, primary_color  # pylint: disable=relative-beyond-top-level

import eeve
import os
import travel_backpack
from eeve.base_classes import Event, Trigger, Action, Task
from eeve import database


class EventsController(GuiController):
    def load_page(self):
        self.session = database.Session()
        root = self.main_controller.engine.rootObjects()[0]
        result = root.findChild(QAbstractListModel, "listmodel")
        self.invoke(result, 'clearItems', None)
        for i, event in enumerate(eeve.events):
            value = {"name": event.name, "colorCode": primary_color, 'tag': i, 'isEventEnabled': event.enabled}
            self.invoke(result, 'addItem', value)

    @pyqtSlot()
    def addEvent(self):
        event = Event(
            triggers=[Trigger.make(template=eeve.trigger_templates['on eeve startup'])],
            task=Task([Action('notepad', action_info=eeve.action_templates['run'])]),
            name='Novo evento',
            enabled=False)
        eeve.events.append(event)

        # create whole event chain
        ev = database.Event(
            name=event.name,
            triggers=[database.Trigger(name='on eeve startup')],
            task=database.Task(
                actions=[database.Action(name='run', arguments=[database.ActionArgument(value='notepad')])]))

        self.session.add(ev)
        self.session.commit() # commit here so that the id property is updated to use in line below
        event.tag = ev.id
        self.load_controller(EditEventController, event, ev)

    @pyqtSlot(QObject, int, int)
    def clickedEvent(self, r, index, data):
        #print('selected event:', eeve.events[data])
        eeve.events[data].enabled = False
        ev = self.session.query(database.Event).filter(database.Event.id == eeve.events[data].tag).one()
        print(ev)
        self.load_controller(EditEventController, eeve.events[data], ev)

    @pyqtSlot(int)
    def deleteEvent(self, i):
        deleted_event = eeve.events.pop(i)
        deleted_event.unregister()

        self.session.delete(self.session.query(database.Event).filter(database.Event.id == deleted_event.tag).one())
        self.session.commit()

        #delete whole event chain
        self.load_page()

    @pyqtSlot(int, bool)
    def eventStateChanged(self, index:int, value:bool):
        eeve.events[index].enabled = value
        ev = self.session.query(database.Event).filter(database.Event.id == eeve.events[index].tag).one()
        ev.enabled = value
        self.session.commit()


    def regain_focus(self, event: Event):
        print('event updated')
        event.reinitialize_triggers()
        event.enabled = True
        self.session.commit()
        self.load_page()

    @pyqtSlot()
    def importFile(self):
        from ..Views import FileDialog  # pylint: disable=relative-beyond-top-level
        filedialog = FileDialog.openFileNamesDialog()

        destination_path = os.path.join(eeve.script_root, 'eeve plugins')

        if filedialog:
            for file_name in filedialog:
                travel_backpack.copy(file_name, destination_path, dst_is_file=False)

            eeve.load_triggers_from_path(destination_path)
            eeve.load_actions_from_path(destination_path)
            print()