from __future__ import division  # You don't need this in Python3
import curses
from math import ceil


def DisplayList(strings):
    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.start_color()
    screen.keypad(1)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    highlightText = curses.color_pair(1)
    normalText = curses.A_NORMAL
    screen.border(0)
    curses.curs_set(0)
    max_row = 20  # max number of rows
    box = curses.newwin(max_row + 2, 130, 1, 1)
    box.box()
    row_num = len(strings)

    pages = int(ceil(row_num / max_row))
    position = 1
    page = 1
    for i in range(1, max_row + 1):
        if row_num == 0:
            box.addstr(1, 1, "There aren't strings", highlightText)
        else:
            name = strings[i - 1]["Name"]
            if (i == position):
                box.addstr(i, 2, str(i) + " - " + name, highlightText)
            else:
                box.addstr(i, 2, str(i) + " - " + name, normalText)
            if i == row_num:
                break

    screen.refresh()
    box.refresh()

    x = screen.getch()
    try:
        while x != 27:
            if x == curses.KEY_DOWN:
                if page == 1:
                    if position < i:
                        position = position + 1
                    else:
                        if pages > 1:
                            page = page + 1
                            position = 1 + (max_row * (page - 1))
                elif page == pages:
                    if position < row_num:
                        position = position + 1
                else:
                    if position < max_row + (max_row * (page - 1)):
                        position = position + 1
                    else:
                        page = page + 1
                        position = 1 + (max_row * (page - 1))
            if x == curses.KEY_UP:
                if page == 1:
                    if position > 1:
                        position = position - 1
                else:
                    if position > (1 + (max_row * (page - 1))):
                        position = position - 1
                    else:
                        page = page - 1
                        position = max_row + (max_row * (page - 1))
            if x == curses.KEY_LEFT:
                if page > 1:
                    page = page - 1
                    position = 1 + (max_row * (page - 1))

            if x == curses.KEY_RIGHT:
                if page < pages:
                    page = page + 1
                    position = (1 + (max_row * (page - 1)))
            if x == ord("\n") and row_num != 0:
                screen.erase()
                screen.border(0)
                name = strings[position - 1]["Name"]
                screen.addstr(14, 3, "YOU HAVE PRESSED '" + name +
                            "' ON POSITION " + str(position))
                curses.endwin()
                return(strings[position - 1])

            box.erase()
            screen.border(0)
            box.border(0)
            my_max_row = max_row * (page - 1)
            height, breath = 1 + (my_max_row), max_row + 1 + (my_max_row)
            for i in range(height, breath):
                if row_num == 0:
                    box.addstr(1, 1, "There aren't strings",  highlightText)
                else:
                    if (i + (my_max_row) == position + (my_max_row)):
                        box.addstr(i - (my_max_row), 2, str(i) +
                                " - " + strings[i - 1]["Name"], highlightText)
                    else:
                        box.addstr(i - (my_max_row), 2, str(i) +
                                " - " + strings[i - 1]["Name"], normalText)
                    if i == row_num:
                        break

            screen.refresh()
            box.refresh()
            x = screen.getch()
        curses.endwin()
        return("lol")
    except Exception as identifier:
        print(identifier)
        curses.endwin()


if __name__ == "__main__":
    pass
    # s= CloudWatchlogs.GetCloudWatchLogs()
    # s.ListLogs('us-west-2')
    # data  = s.ledger

    # a = DisplayList(data)
    # print(a)
    # # curses.endwin()
    # exit()
