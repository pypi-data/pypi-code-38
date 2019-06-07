from __future__ import print_function
from abc import ABCMeta, abstractmethod
from wargame.gameuniterror import HealthMeterException
"""
RUNNING THE PROGRAM:
--------------------
- Python 3.5.x must be installed on your system.
- It is assumed that you have Python 3.5 available in your environment
  variable PATH. It will be typically available as 'python' or 'python3'.
- Here is the command to execute this code from command prompt

        $ python ch01_ex03.py     ( OR $ python3 ch01_ex03.py)

- See the README file for more information. Or visit python.org for OS
  specific instructions on executing Python from a command prompt.

.. todo::

1. The code comments and function descriptions in this file are
   intentionally kept to a minimum! See a later chapter of the book to
   learn about the code documentation and best practices!
   Feel free to add documentation after reading that chapter.
   Description of the code can be found in the book.
2. Split the code into smaller modules
3. Make GameUnit to an abstract base class
4. See the other TODO comments..things you can try fixing as an exercise!

:copyright: 2019, JinXingw
"""

import random

def print_bold(msg, end='\n'):
    print("\033[1m" + msg + "\033[0m", end=end);

def weighted_random_selection(obj1, obj2):
    """Randomly select between two objects based on assigned 'weght"""
    weighted_list = 3 * [id(obj1)] + 7 * [id(obj2)]
    selection = random.choice(weighted_list)

    if selection == id(obj1):
        return obj1

    return obj2

class AbstractGameUnit(metaclass=ABCMeta):
    """base class og game"""
    def __init__(self, name = ''):
        self.max_hp = 0
        self.health_meter = 0
        self.name = name
        self.enemy = None
        self.unit_type = None

    @abstractmethod
    def info(self):
        pass

    def attack(self, enemy):
        """The main logic to determine injured unit and amount of injury

        .. todo:: Check if enemy exists!
        """
        injured_unit = weighted_random_selection(self, enemy)
        injury = random.randint(10, 15)
        injured_unit.health_meter = max(injured_unit.health_meter - injury, 0)
        print("ATTACK!", end=' ')
        self.show_health(end='  ')
        enemy.show_health(end='  ')

    def heal(self, heal_by=2, full_healing=True):
        """Heal the unit replenishing all the hit points"""
        if self.health_meter == self.max_hp:
            return
        if full_healing:
            self.health_meter = self.max_hp
        else:
            self.health_meter += heal_by

        if self.health_meter > self.max_hp:
            raise HealthMeterException("health_meter > max_hp!");

        print_bold("You are HEALED", end='  ')
        self.show_health(bold=True)

    def reset_health_meter(self):
        """Reset the `health_meter` (assign default hit points)"""
        self.health_meter = self.max_hp

    def show_health(self, bold=False, end='\n'):

        msg = "Health: %s %d" % (self.name, self.health_meter)

        if bold:
            print_bold(msg, end=end)
        else:
            print(msg, end=end)
