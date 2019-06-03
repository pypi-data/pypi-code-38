import logging
import sys
from sys import stdout

import click
from PyInquirer import prompt
from fxq.core.beans.factory.annotation import Autowired
from pyfiglet import Figlet

from fxq.geoffrey.config import ApplicationConfig
from fxq.geoffrey.exception import ConfigNotFoundException

try:
    from fxq.geoffrey.geoffreycli import GeoffreyCli, style
except ConfigNotFoundException as e:
    if not stdout.isatty():
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(exc_value)
        sys.exit()
    else:
        questions = [
            {
                'type': 'input',
                'name': 'yml_location',
                'message': 'We couldn\'t find a config, where would you like to pull your YML from',
            }
        ]
        answers = prompt(questions)
        config = Autowired(type=ApplicationConfig)
        config.create_new_config(answers["yml_location"])

from fxq.geoffrey.geoffreycli import GeoffreyCli, style

geoffrey = GeoffreyCli()


@click.command()
@click.option('--task', '-t', multiple=True, help="Provide tasks to be run with multiple -t flags")
@click.option('--no-banner', is_flag=True, help="Disable printing of the banner")
@click.option('--list-tasks', is_flag=True, help="Display a list of all the available tasks")
def main(task, no_banner, list_tasks):
    selected = []
    if not no_banner:
        f = Figlet(font='standard')
        print(f.renderText(' Geoffrey '))
        print('=== The Devops CLI provisioning Tool ===')

    if list_tasks:
        print("Available Tasks:")
        for section, tasks in geoffrey.list_available_tasks().items():
            print("## %s:## " % section)
            for task in tasks:
                print(" - %s" % task)
    elif not stdout.isatty() or len(task) > 0:
        for t in task:
            if geoffrey.task_exists(t):
                geoffrey.run_task(t)
            else:
                print("Ignoring Task \"%s\" as its not available" % t)
    else:
        questions = [
            {
                'type': 'checkbox',
                'message': 'Select Tasks to run',
                'name': 'items',
                'choices': geoffrey.get_choices()
            }
        ]
        try:
            for o in prompt(questions, style=style)["items"]:
                selected.append(o)
        except KeyError as e:
            sys.exit()

        print("Selected Options are:")
        for t in selected:
            print(" - %s" % t)

        questions = [
            {
                'type': 'confirm',
                'message': 'Do you want to continue?',
                'name': 'continue',
                'default': True,
            },
        ]

        try:
            confirm = prompt(questions, style=style)

            if confirm["continue"]:
                for task in selected:
                    geoffrey.run_task(task)
            else:
                main()
        except KeyError as e:
            sys.exit()


if __name__ == '__main__':
    logging.basicConfig(format="[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s", level=logging.INFO)
    main()
