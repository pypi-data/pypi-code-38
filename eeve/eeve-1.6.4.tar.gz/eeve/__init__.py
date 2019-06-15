"""eeve - A flexible, powerfull and simple event trigger"""

__version__ = '1.6.4'
__author__ = 'Victor Marcelino <victor.fmarcelino@gmail.com>'
__all__ = []

import travel_backpack
import os

from . import helpers
from .importer import import_from_folder
from .wrapper import action_wrapper
from .base_classes import Action, ActionTemplate, Trigger, TriggerTemplate, Event, Task
from . import mappings
from . import database

from typing import Union, Any, Dict, List, Callable
from sqlalchemy import func
#from .ts import test_sampler_decorator

trigger_templates: Dict[str, TriggerTemplate] = {}
action_templates: Dict[str, ActionTemplate] = {}
events: List[Event] = []
script_root: str = ''


def main():
    global script_root
    print()

    load_default_templates()

    from pathlib import Path
    conf_root = os.path.join(Path.home(), 'Documents', 'eeve')
    conf_file = os.path.join(conf_root, 'eeve events.txt')
    conf_db_file = os.path.join(conf_root, 'eeve.db')

    #database.open_db_file(None)
    database.open_db_file(conf_db_file)

    if os.path.isfile(conf_file):
        with open(conf_file) as f:
            _all_events = f.read().replace('|||\n', '').split('\n')

        load_events_from_str_list(_all_events)

        new_name_ext = '.done.' + travel_backpack.time_now_to_string(
            separators=['.', '.', ' - ', '.', '.', '.']) + '.txt'
        new_name = os.path.splitext(conf_file)[0] + new_name_ext
        os.rename(src=conf_file, dst=new_name)
    else:
        print('no conf file at', conf_file)

    load_events_from_db()


def load_default_templates():
    """Loads default trigger and actions templates from scripts
    """

    script_root = os.path.dirname(os.path.realpath(__file__))
    load_triggers_from_path(os.path.join(script_root, 'eeve triggers'))
    load_actions_from_path(os.path.join(script_root, 'eeve actions'))

    load_triggers_from_path(os.path.join(script_root, 'eeve plugins'))
    load_actions_from_path(os.path.join(script_root, 'eeve plugins'))


def add_trigger_template(name: str, trigger: Union[Trigger, TriggerTemplate, dict, Callable]):
    """Adds a TriggerTemplate that can be used as base to a Trigger instance
    
    Arguments:
        name {str} -- the name of the TriggerTemplate

        trigger {Union[Trigger, TriggerTemplate, dict, Callable]} -- The trigger information.
        It can be a class where init will be used as register and attribute unregister as
        the unregister function,
        a dict with keys `register` and `unregister` with callables as value, a Trigger or
        another TriggerTemplate. Only the name given on the argument will be used.
    
    Raises:
        AttributeError: when a class passed as "trigger" argument has no "unregister" attribute
    """
    if type(trigger) is Trigger:
        tt = TriggerTemplate(name=name, register=trigger.register, unregister=trigger._unregister)
        trigger_templates[name] = tt

    elif type(trigger) is TriggerTemplate:

        tt = TriggerTemplate(name=name, register=trigger.register, unregister=trigger.unregister)
        trigger_templates[name] = tt

    elif type(trigger) is dict:
        trigger_templates[name] = TriggerTemplate(name=name,
                                                  register=trigger['register'],
                                                  unregister=trigger['unregister'])

    else:
        travel_backpack.check_and_raise(hasattr(trigger, 'unregister'),
                                        'trigger object must have "unregister" attribute', AttributeError)
        add_trigger_template(name=name, trigger={'register': trigger, 'unregister': trigger.unregister})


def remove_trigger_template(name: str, unregister=False):
    """Removes a TriggerTemplate from eeve

    Warning: only the template will be removed from eeve's system,
    but any trigger created from it will still function.\n
    In some cases the unregister function can be called to stop the instance running.
    This is, however, up to the trigger developer to implement.
    
    Arguments:
        name {str} -- Name of TriggerTemplate to remove
    
    Keyword Arguments:
        unregister {bool} -- if True, will call the unregister function from trigger (default: {False})
    """
    if name in trigger_templates:
        if unregister:
            trigger_templates[name].unregister()

        del trigger_templates[name]


def add_action_template(name: str, action_info: Union[Action, ActionTemplate, dict, Callable], *action_init_args,
                        **action_init_kwargs):
    """Adds an ActionTemplate that can be used as base to an Action instance
    
    Arguments:
        name {str} -- The name of the ActionTemplate

        action_info {Union[Action, ActionTemplate, dict, Callable]} -- The action information.
        It can be a class where init will be used as initialization and attribute "run" as
        the action function,
        a dict where key `run` has value of the action function, an optional `init` key with the initialization function as value, 
        an Action or another ActionTemplate. Only the name given on the argument will be used.
    """
    if type(action_info) in [Action, ActionTemplate]:
        at = ActionTemplate.copy_from(action_info)
        at.reinitialize_with_args(*action_init_args, **action_init_kwargs)
        action_templates[name] = at

    else:
        action_templates[name] = ActionTemplate.make(name=name,
                                                     action_info=action_info,
                                                     *action_init_args,
                                                     **action_init_kwargs)


def remove_action_template(name: str):
    """Removes an ActionTemplate from eeve
    
    Arguments:
        name {str} -- Name o ActionTemplate to remove
    """
    if name in action_templates:
        del action_templates[name]


def load_triggers_from_path(path):
    print('--loading triggers--')
    modules = import_from_folder(path)
    for module in modules:
        try:
            triggers = getattr(module, 'triggers', dict())
            for trigger_name, trigger in triggers.items():
                print('loading', trigger_name)
                add_trigger_template(name=trigger_name, trigger=trigger)
        except Exception as ex:
            print('invalid trigger module:', ex)
    print('--triggers loaded--')
    print()
    print()


def load_actions_from_path(path):
    print('--loading actions--')
    modules = import_from_folder(path)
    for module in modules:
        try:
            actions = getattr(module, 'actions', dict())
            for action_name, action in actions.items():
                print('loading', action_name)
                add_action_template(name=action_name, action_info=action)
        except Exception as ex:
            print('invalid action module:', ex)
    print('--actions loaded--')
    print()
    print()


def load_events_from_db():
    session = database.Session()
    r = session.query(func.count(database.Event.id)).scalar()
    print(r)
    if r == 0:
        database.add_default_event()

    for event in session.query(database.Event):
        try:
            print(event.name)
            triggers = []
            for trigger in event.triggers:
                print(trigger.name)
                trigger_args = []
                trigger_kwargs = {}
                for arg in trigger.arguments:
                    if arg.key is not None:
                        trigger_kwargs[arg.key] = arg.value
                    else:
                        trigger_args.append(arg.value)

                triggers.append(Trigger.make(*trigger_args, template=trigger_templates[trigger.name], **trigger_kwargs))

            actions = []
            for action in event.task.actions:
                print(action.name)
                action_args = []
                action_kwargs = {}
                for arg in action.arguments:
                    if arg.key is not None:
                        action_kwargs[arg.key] = arg.value
                    else:
                        action_args.append(arg.value)

                actions.append(Action(*action_args, action_info=action_templates[action.name], **action_kwargs))

            task = Task(actions=actions)
            events.append(Event(triggers=triggers, task=task, name=event.name, tag=event.id, enabled=event.enabled))

        except Exception as ex:
            print('failed to add event', ex)

    print()
    session.close()


def load_events_from_str_list(_all_events: list):
    print('--loading events--')
    session = database.Session()
    for event in _all_events:
        if event and not event.startswith('#'):
            show_traceback = False
            verbose = 1
            print(f'loading [{event}]')
            while event.startswith('['):
                if event.startswith('[test]'):
                    show_traceback = True
                    event = event[len('[test]'):]
                elif event.startswith('[no verbose]'):
                    verbose = 0
                    event = event[len('[no verbose]'):]
            try:
                event = mappings.remap(event)
                trigger, raw_actions = helpers.strip_split(event, mappings.char_map['->'], maxsplit=1)

                trigger, trigger_args, trigger_kwargs = helpers.process_args(trigger, return_init_args=False)

                raw_actions = helpers.strip_split(raw_actions, mappings.char_map[';'])
                actions = []
                actions_db = []
                for action in raw_actions:
                    action_name, action_init_args, action_init_kwargs, action_run_args, action_run_kwargs = helpers.process_args(
                        action, return_init_args=True)

                    _action_template = ActionTemplate.copy_from(action_templates[action_name])
                    if _action_template.init_func:
                        _action_template.reinitialize_with_args(*action_init_args, **action_init_kwargs)
                    _action = Action(*action_run_args, action_info=_action_template, **action_run_kwargs)

                    arg_list_db = []
                    for arg in action_run_args:
                        arg_list_db.append(database.ActionArgument(value=arg))

                    for k, v in action_run_kwargs.items():
                        arg_list_db.append(database.ActionArgument(key=k, value=v))

                    _action_db = database.Action(name=action_name, arguments=arg_list_db)

                    actions.append(_action)
                    actions_db.append(_action_db)

                task = Task(actions, debug=show_traceback, verbose=verbose)
                task_db = database.Task(actions=actions_db)
                trigger_db = database.Trigger(
                    name=trigger,
                    arguments=[database.TriggerArgument(value=v) for v in trigger_args] +
                    [database.TriggerArgument(key=k, value=v) for k, v in trigger_kwargs.items()])
                trigger = Trigger.make(*trigger_args, template=trigger_templates[trigger],
                                       **trigger_kwargs)  # pre-initializes the trigger
                print('Starting trigger')
                event = Event(triggers=[trigger], task=task)  # starts the trigger
                print('Trigger started')
                event_db = database.Event(name=event.name, enabled=event.enabled, task=task_db, triggers=[trigger_db])
                session.add(event_db)
                session.commit()  # to generate id in event_db
                event.tag = event_db.id
                events.append(event)

            except Exception as ex:
                show_traceback = True
                print('invalid event:', (ex if not show_traceback else travel_backpack.format_exception_string(ex)))
                session.rollback()

    print('--events loaded--')
    print()
    print()