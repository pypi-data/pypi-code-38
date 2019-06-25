"""
Curses-menu
"""
import sys
import logging
from xlines import __version__
from xlines.configure import display_exclusions

try:
    from cursesmenu import CursesMenu, SelectionMenu
    from cursesmenu.items import FunctionItem, SubmenuItem, CommandItem
except Exception as e:
    print('Errors when importing module cursesmenu: %s' % str(e))


logger = logging.getLogger(__version__)
logger.setLevel(logging.INFO)


def submenu_backup(menu_obj):
    submenu = CursesMenu("Access Key Backup")
    q1_item = FunctionItem("Do you want to retain a copy of newly created access keys?", input, ["yes"])
    q2_item = FunctionItem("Enter the directory where a backup copy of the access keys should be stored", input, ["~/Backup"])
    submenu.append_item(q1_item)
    submenu.append_item(q2_item)
    submenu_item = SubmenuItem("Show a submenu", submenu, menu=menu_obj)
    return submenu_item


def submenu_logging(menu_obj):
    submenu = CursesMenu("Logging Configuration")
    q1_item = FunctionItem("Do you want to turn enable logging?", input, ['yes'])
    q2_item = FunctionItem("If yes, do you want logging to stdout or a log file?", input, ['FILE'])
    submenu.append_item(q1_item)
    submenu.append_item(q2_item)
    submenu_item = SubmenuItem("Show a submenu", submenu, menu=menu_obj)
    return submenu_item


def selection_menu_example():
    bool_list = ['~/logs', '~/Backup']
    submenu2 = SelectionMenu(bool_list, "What directory location?")
    submenu2.show()
    submenu2.join()
    selection = submenu2.selected_option
    print('\nselection is: %s\n' % str(selection))


def main():
    """ Builds main menu, branches to submenus """

    # parent menu
    menu = CursesMenu("Local Configuration Menu", "keyup Project")

    try:
        submenu_backup = submenu_backup(menu)
        submenu_logging = submenu_logging(menu)

        # assemble main menu
        menu.append_item(submenu_backup)
        menu.append_item(submenu_logging)

        menu.show()
        user_selection = menu.selected_option
    except Exception as e:
        print('Unknown Exception: %s. Exit' % str(e))
        return False
    return True


if __name__ == '__main__':
    menu = CursesMenu("Local Configuration Menu", "xlines Project")
    # backup
    submenu = CursesMenu("Exclusions", 'Do you want to add a new file type exclusion?')
    q1_item1 = FunctionItem("Yes", input, ["yes"])
    q1_item2 = FunctionItem("No", print('Exit'), ["no"])
    submenu.append_item(q1_item1)
    submenu.append_item(q1_item2)
    submenu_exclusions = SubmenuItem("Configure Exclusion List", submenu, menu=menu)
    menu.append_item(submenu_exclusions)
    if q1_item1 == "yes":
        display_exclusions()
        submenu = CursesMenu("Access Key Backup", 'Enter the directory where a backup copy of the access keys should be stored')
        q2_item1 = FunctionItem("~/Backup/", input, ["~/Backup"])
        submenu.append(q2_item1)
        submenu.show()

    # logging
    submenu2 = CursesMenu("Logging Configuration", "Do you want to enable logging?")
    q2_item1 = FunctionItem("Yes", selection_menu_example(), ['yes'])
    q2_item2 = FunctionItem("No", input, ['No'])
    print('\nsubmenu_selection is: %s\n' % str(selection_menu_example()))
    submenu2.append_item(q2_item1)
    submenu2.append_item(q2_item2)

    submenu_logging = SubmenuItem("Configure Logging", submenu2, menu=menu)
    menu.append_item(submenu_logging)
    menu.show()
    user_selection = menu.selected_option
    print('\nuser_selection is: %s\n' % str(user_selection))
    sys.exit(0)
