from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
from datetime import datetime

import click
import dateparser as parser
import yaml
from colorclass import Color
from terminaltables import SingleTable

from .klass_path import Path

click.disable_unicode_literals_warning = True

DAYS = {
    0: "Lundi",
    1: "Mardi",
    2: "Mercredi",
    3: "Jeudi",
    4: "Vendredi",
    5: "Samedi",
    6: "Dimanche",
}

TODO_FILE = os.path.join(Path.home(), '.dyvz', 'todo.yml')
Path.touch(TODO_FILE)


class Tools:
    def set_color(self, txt, obj, level=2):
        if obj and isinstance(obj, Todo):
            level = obj.priority
            if obj.due and datetime.today().date() >= obj.due and not obj.done:
                level = 1
        if not level or level > 2:
            c = 'autoblue'
        elif level == 2:
            return txt
        else:
            c = 'autored'
        return Color('{%s}%s{/%s}' % (c, txt, c))


class Collection(object):
    def __init__(self, yml_file, tools):
        self.current_id = 0
        self.todos = []
        self.tools = tools
        self.yml_file = yml_file
        self.load()

    def load(self):
        with open(self.yml_file) as yd:
            data = yaml.load(yd.read())
        if data:
            self.current_id = data.get('current_id', 1)
            for item in data.get('data', []):
                todo = Todo()
                todo.load(item)
                self.todos.append(todo)

    def dump(self):
        data = {'data': [], 'current_id': self.current_id}
        for todo in self.todos:
            data['data'].append(todo.dump())
        with open(self.yml_file, 'w+') as yd:
            yd.write(yaml.dump(data))

    def add(self, todo):
        self.current_id += 1
        todo.id = self.current_id
        self.todos.append(todo)

    def show(self, todos=None, priority=None, done=None, new=None, due=None):
        if due:
            due = parser.parse(due).date() if parser.parse(due) else None
        tbl_data = [["ID", "CREATE DATE", "PRIORITY", "NAME", "DUE DATE", "DAY", "DONE"]]
        for todo in sorted(todos or self.todos, key=lambda todo: todo.due or datetime(2030, 1, 1).date()):
            if not todos:
                if priority is not None and todo.priority != priority: continue
                if not (done and new):
                    if done and todo.done == False: continue
                    if new and todo.done == True: continue
                if due and todo.due != due: continue
            tbl_data.append([
                self.tools.set_color(todo.id, todo),
                self.tools.set_color(todo.create, todo),
                self.tools.set_color(todo.priority, todo),
                self.tools.set_color(todo.name, todo),
                self.tools.set_color(todo.due or '', todo),
                self.tools.set_color(DAYS[todo.due.weekday()] if todo.due else '', todo),
                self.tools.set_color(todo.done and 'x' or '', todo),
            ])
        table_instance = SingleTable(tbl_data)
        table_instance.inner_heading_row_border = True
        table_instance.inner_column_border = False
        table_instance.outer_border = True
        click.echo(table_instance.table)
        click.echo('Total: %s' % (len(tbl_data) - 1))

    def find(self, param):
        found = []
        for item in param:
            for todo in self.todos:
                if str(item).isdigit():
                    item = int(item)
                if item in [todo.id, todo.name]:
                    found.append(todo)
        return found

    def apply(self, todos, delete=None, done=None, due=None, priority=None, name=None):
        for todo in todos:
            if todo in self.todos:
                if priority is not None:
                    todo.set_priority(priority)
                if done == True:
                    todo.set_done()
                if done == False:
                    todo.set_new()
                if due:
                    todo.set_due(due)
                if name:
                    todo.set_name(name)
                if delete:
                    self.todos.remove(todo)

    def reset(self):
        self.todos = []
        self.current_id = 0


class Todo(object):
    def __init__(self, name=None, priority=2):
        self.name = name
        self.priority = priority
        self.id = None
        self.done = False
        self.due = None
        self.create = datetime.today().date()

    def load(self, data):
        self.name = data.get('name', None)
        self.priority = data.get('priority', 2)
        self.id = data.get('id', 1)
        self.done = data.get('done', False)
        self.due = data.get('due', None)
        self.create = data.get('create', datetime.today().date())

    def set_name(self, name):
        self.name = name

    def set_new(self):
        self.done = False

    def set_done(self):
        self.done = True

    def set_priority(self, priority):
        self.priority = priority

    def set_due(self, due):
        if due:
            self.due = parser.parse(due).date() if parser.parse(due) else None
        else:
            self.due = None

    def dump(self):
        return {
            'name': self.name,
            'priority': self.priority,
            'id': self.id,
            'done': self.done,
            'due': self.due,
            'create': self.create,
        }


@click.command()
@click.argument('tasks', nargs=-1)
@click.option('--select', '-s', type=click.STRING, multiple=True, help="Select todos with ids")
@click.option('--add', '-a', type=click.STRING, multiple=True, help="Add todos")
@click.option('--delete', is_flag=True, default=False, help="delete todos with ids")
@click.option('--delete-all', is_flag=True, default=False, help="delete all todos")
@click.option('--set-done', is_flag=True, default=False, help="Set todos as done")
@click.option('--set-new', is_flag=True, default=False, help="Set todos as new")
@click.option('--set-name', type=click.STRING, help="Rename a todo")
@click.option('--set-due', type=click.STRING, help="Set a due date for todos")
@click.option('--set-priority', type=click.INT, help="Set a priority for todos")
@click.option('--list', '-l', 'r_list', is_flag=True, default=False, help="List todos")
@click.option('--new', is_flag=True, default=None, help="Filter todos by state=new")
@click.option('--done', is_flag=True, default=None, help="Filter todos by state=done")
@click.option('--due', type=click.STRING, help="filter by due date")
@click.option('--priority', type=click.INT, help="filter by the priority")
def cli_todo(
        tasks,
        select,
        add,
        delete,
        delete_all,
        set_done,
        set_new,
        set_name,
        set_due,
        set_priority,
        r_list,
        new,
        done,
        due,
        priority):
    """Create a todo list using: todo "Task A" "Task B" """
    add = list(add) + list(tasks)
    new = new or (not done and not new)
    collection = Collection(TODO_FILE, Tools())
    todos = collection.find(select)
    if delete_all:
        collection.reset()
    for todo_name in add:
        todo = Todo(name=todo_name)
        todos.append(todo)
        collection.add(todo)
    if set_done:
        collection.apply(todos, done=True)
    if set_new:
        collection.apply(todos, done=False)
    if set_due:
        collection.apply(todos, due=set_due)
    if set_name:
        collection.apply(todos, name=set_name)
    if set_priority:
        collection.apply(todos, priority=set_priority)
    if delete:
        collection.apply(todos, delete=True)
        old_todos = todos[:]
        for todo in todos:
            old_todos.remove(todo)
        todos = old_todos
    r_list = r_list or select or add or (priority or done or new or due)
    r_list = r_list or (not select and not add)
    if r_list:
        collection.show(todos=todos, priority=priority, done=done, new=new, due=due)
    collection.dump()
