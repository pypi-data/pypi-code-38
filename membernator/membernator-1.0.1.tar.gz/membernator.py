#!/usr/bin/env python3
"""
membernator is a tool that can be used to scan membership cards and establish
if they're valid or not against a CSV database.

Usage:
    membernator [options] --database FILE
    membernator (-h | --help)
    membernator --version

Options:
    -h  --help       Shows the help screen
    --version        Outputs version information
    --database FILE  Path to the CSV database
    --id_col ID      "id" column in the CSV database. [default: ID]
    --name_col NAME  "name" column in the CSV database. [default: NAME]
    --time SEC       Delay in secs between scans. [default: 2.5]
    --width WIDTH    Width in pixels. Use 0 for fullscreen. [default: 800]
    --height HEIGHT  Height in pixels. Use 0 for fullscreen. [default: 480]
    --logfile LOG    Path to the logfile. [default: log.csv]
"""

import sys
import os
import csv

from datetime import datetime

try:
    from docopt import docopt  # Creating command-line interface
except ImportError:
    sys.stderr.write(
        "docopt is not installed: this program won't run correctly.")

# Make pygame import silent
from contextlib import redirect_stdout
with redirect_stdout(None):
    import pygame

# Only import the bits and pieces we need from pygame
pygame.font.init()
pygame.display.init()
pygame.display.set_caption('Membernator')

# Some initial variables
__version__ = "1.0.1"
TITLE_FONT = "Cantarell Extra Bold"
BODY_FONT = "Cantarell Bold"

# Set some colours
BLACK = 0, 0, 0
DARK_GREY = 40, 40, 40
GREY = 100, 100, 100
LIGHT_GREY = 200, 200, 200
RED = 180, 38, 34
GREEN = 37, 110, 51
CYAN = 40, 200, 200
PURP = 70, 10, 140
BLUE = 80, 80, 250
WHITE = 255, 255, 255


def display(width, height):
    """Set display options"""
    global screen, SCREEN_WIDTH, SCREEN_HEIGHT  # pylint:disable=invalid-name

    try:
        SCREEN_WIDTH = int(width)
        SCREEN_HEIGHT = int(height)
    except ValueError:
        sys.exit("Error: '--width' and '--height' must be integers")

    size = SCREEN_WIDTH, SCREEN_HEIGHT
    if size == (0, 0):
        screen = pygame.display.set_mode((size), pygame.FULLSCREEN)
        # Fullscreen needs those values to be recalculated
        SCREEN_WIDTH, SCREEN_HEIGHT = pygame.display.get_surface().get_size()
    else:
        screen = pygame.display.set_mode((size), pygame.NOFRAME)


def pannel_line(text, color, font, height):
    """Write a line of text on a pannel"""
    label = font.render(text, 1, color)
    text_rect = label.get_rect(center=(SCREEN_WIDTH/2, height))
    screen.blit(label, text_rect)


def wait(time):
    """Makes the program halt for 'time' seconds or until a key is pressed"""
    clock = pygame.time.Clock()
    waiting = True

    try:
        time = float(time)
    except ValueError:
        sys.exit("Error: '--time' must be a floating point number")

    while waiting:
        # Takes the time between each loop and convert to seconds
        delta = clock.tick(60) / 1000
        time -= delta
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("Escape pressed, exiting...")
                    sys.exit()
                else:
                    waiting = False

        if time <= 0:
            waiting = False


def drawpannel(title, titlebgcolour, bgcolour, time,
             line_1, line_2, line_3, line_4, line_5):
    """Draws a pannel with a title and 5 lines of text"""
    screen.fill(bgcolour)
    pygame.draw.rect(screen, (titlebgcolour), (50, 50, SCREEN_WIDTH-110, 110))
    titlefont = pygame.font.SysFont(TITLE_FONT, 120)
    label = titlefont.render(title, 1, WHITE)
    text_rect = label.get_rect(center=(SCREEN_WIDTH/2, 105))
    screen.blit(label, text_rect)

    textfont = pygame.font.SysFont(BODY_FONT, 50)

    pannel_line(line_1, LIGHT_GREY, textfont, SCREEN_HEIGHT/5)
    pannel_line(line_2, LIGHT_GREY, textfont, SCREEN_HEIGHT*2.5/5)
    pannel_line(line_3, LIGHT_GREY, textfont, SCREEN_HEIGHT*3.5/5)
    pannel_line(line_4, LIGHT_GREY, textfont, SCREEN_HEIGHT*4/5)
    pannel_line(line_5, LIGHT_GREY, textfont, SCREEN_HEIGHT)

    pygame.display.flip()
    # We need this for the pannel to switch back to "SCAN" automatically
    if time != 0:
        wait(time)
        press_return = pygame.event.Event(pygame.KEYDOWN,
                                          {'key':pygame.K_RETURN})
        pygame.event.post(press_return)


def inputpannel(title, titlebgcolour, bgcolour, line_1, line_2, line_3):
    """Draws a pannel with a title, 3 lines of text and an input box"""
    text = ''
    done = False

    while not done:
        screen.fill(bgcolour)
        pygame.draw.rect(screen, (titlebgcolour), (50, 50, SCREEN_WIDTH-110,
                                                   110))
        titlefont = pygame.font.SysFont(TITLE_FONT, 120)
        label = titlefont.render(title, 1, WHITE)
        text_rect = label.get_rect(center=(SCREEN_WIDTH/2, 105))
        screen.blit(label, text_rect)

        textfont = pygame.font.SysFont(BODY_FONT, 50)

        pannel_line(line_1, LIGHT_GREY, textfont, SCREEN_HEIGHT*2.5/5)
        pannel_line(line_2, LIGHT_GREY, textfont, SCREEN_HEIGHT*3/5)
        pannel_line(line_3, LIGHT_GREY, textfont, SCREEN_HEIGHT*4/5)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("Escape pressed, exiting...")
                    sys.exit()
                elif event.key == pygame.K_RETURN:
                    done = True
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

        # Render the current text.
        txt_surface = textfont.render(text, True, GREY)
        # Resize the box if the text is too long.
        input_box = pygame.Rect((SCREEN_WIDTH-400)/2, SCREEN_HEIGHT*3.5/5, 140,
                                50)
        input_box.w = max(400, txt_surface.get_width()+10)
        # Blit
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, GREY, input_box, 2)

        pygame.display.flip()

    return text


def welcome():
    """Draw a welcome pannel"""
    drawpannel("WELCOME", GREY, DARK_GREY, 0,
             "",
             "To start, press any key",
             "Press <Escape> to quit at any time",
             "",
             "")


def validate(csvdict, logdict, id_col, name_col, text):
    """Validate the scanned card"""
    valid = False
    seen = False
    name = None
    for row in csvdict:
        if text == row[id_col]:
            valid = True
            name = row[name_col]
    for row in logdict:
        if text == row[id_col]:
            seen = True

    return valid, seen, name


def logger(logfile, logdict, valid, id_col, name_col, text, name):
    """Write scanned cards to the logfile"""
    scan_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Keep track of scanned cards
    logdict.append({"Scan Time":scan_time, "Valid":valid, id_col:text,
                    name_col:name})
    # Write to the logfile
    with open(logfile, 'a+', newline='') as log:
        log_write = csv.DictWriter(log, fieldnames=["Scan Time", "Valid",
                                                    id_col, name_col])
        if os.stat(logfile).st_size == 0:  # only write header for new files
            log_write.writeheader()
        log_write.writerow(logdict[len(logdict)-1])  # only write last entry

    return logdict


def showpannel(valid, seen, name, time):
    """The pannels shown to the user"""
    if (valid == True) and (seen == True):
        drawpannel("VALID", CYAN, DARK_GREY, float(time)*2,
                 "",
                 "This card has already be scanned",
                 "Name: " + name,
                 "",
                 "")
    elif (valid == True) and (seen == False):
        drawpannel("VALID", GREEN, DARK_GREY, time,
                 "",
                 "This card is valid",
                 "Name: " + name,
                 "",
                 "")
    else:
        drawpannel("INVALID", RED, DARK_GREY, time,
                 "",
                 "This card is invalid",
                 "",
                 "",
                 "")


def text_input(database, id_col, name_col, time, logfile):
    """Manage the  user's text input"""
    logdict = []
    with open(database, newline='') as csvfile:
        csvdict = csv.DictReader(csvfile)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        print("Escape pressed, exiting...")
                        sys.exit()
                    else:
                        text = inputpannel("READY TO SCAN", BLUE, DARK_GREY,
                                         "Scan a card or type the member's",
                                         "ID number and press <Enter>",
                                         "")
                        csvfile.seek(0) # Read the entire file each time
                        valid, seen, name = validate(csvdict, logdict, id_col,
                                                     name_col, text)
                        logdict = logger(logfile, logdict, valid, id_col,
                                         name_col, text, name)
                        showpannel(valid, seen, name, time)


def main():
    """Main function"""
    args = docopt(__doc__, version="membernator %s" % __version__)
    display(args["--width"], args["--height"])
    welcome()
    text_input(args["--database"], args["--id_col"], args["--name_col"],
               args["--time"], logfile = args["--logfile"])


if __name__ == "__main__":
    main()
