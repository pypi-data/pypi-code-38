#!/usr/bin/env python3
#
# This file is part of Vocabulary Football (VocBall).
#
# Copyright (C) 2017-2019 - Thomas Dähnrich <develop@tdaehnrich.de>
#
# VocBall is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# VocBall is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with VocBall. If not, see <http://www.gnu.org/licenses/>.

import gi
import os
import random
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import Pango

from settings import PIXMAPS_DIR, SOUNDS_DIR, TEAMS_FILE, UI_DIR, VERSION
from settings import get_settings, setup_language


# get settings and setup language

fullscreen = get_settings()
_ = setup_language()


# define global variables

ballpos = 0
colorA = '#204a87'
colorB = '#a40000'
headerbar_color = "dark"
ingame = False
player_number = 0
players = []
scale_full = 1
scoreA = 0
scoreB = 0
space_full = 0
voc_active = []


# main functions of game

def setup_headerbar(self):

    global headerbar_color

    deco_old = Gtk.Settings.get_default().get_property("gtk-decoration-layout")
    deco_new = deco_old.replace(",maximize", "").replace(":maximize,", ":").replace("maximize", "")
    self.headGame.set_decoration_layout(deco_new)
    if "close" in deco_new.split(":")[0]:
        self.headGame.remove(self.btnMenu)
        self.headGame.remove(self.btnGame)
        self.headGame.pack_start(self.btnMenu)
        self.headGame.pack_end(self.btnGame)

    color = self.lblScore.get_style_context().get_property(Gtk.STYLE_PROPERTY_COLOR,
        Gtk.StateFlags.NORMAL)
    if color.blue < 0.5:
        headerbar_color = "light"
        scoreA_file = 'scoreoff_30x50_{}.png'.format(headerbar_color)
        scoreB_file = 'scoreoff_30x50_{}.png'.format(headerbar_color)
        self.imgScoreA.set_from_file(os.path.join(PIXMAPS_DIR, scoreA_file))
        self.imgScoreB.set_from_file(os.path.join(PIXMAPS_DIR, scoreB_file))
        markup = "<span foreground='#000000'>{}</span>".format(":")
    else:
        markup = "<span foreground='#ffffff'>{}</span>".format(":")
    self.lblScore.set_markup(markup)


def check_fullscreen(self):

    global scale_full, space_full

    if not Gtk.check_version(3,22,0):
        display = Gdk.Display.get_default()
        monitor = display.get_monitor_at_window(self.winGame.get_window())
        monitor_width = monitor.get_geometry().width
        monitor_height = monitor.get_geometry().height
    else:
        screen = Gdk.Screen.get_default()
        monitor = screen.get_monitor_at_window(self.winGame.get_window())
        monitor_width = screen.get_monitor_geometry(monitor).width
        monitor_height = screen.get_monitor_geometry(monitor).height
    headerbar_height = self.headGame.get_preferred_height()
    field_width_orig, field_height_orig = self.boxGame.get_size_request()
    field_height_full = monitor_height - headerbar_height[0]
    field_width_full = int(round(field_height_full * field_width_orig / field_height_orig))

    if field_width_full / field_width_orig < 1:
        from settings import deactivate_fullscreen
        deactivate_fullscreen()
    else:
        if fullscreen:
            scale_full = field_width_full / field_width_orig
            space_full = monitor_width - field_width_full
            setup_fullscreen(self, field_height_full, monitor_width)
            self.winGame.fullscreen()
        else:
            self.winGame.set_resizable(False)


def setup_fullscreen(self, field_height_full, monitor_width):

    from gi.repository import GdkPixbuf

    self.winGame.move(0, 0)
    # workaround for headerbar in fullscreen mode
    self.winGame.remove(self.headGame)
    self.boxGame.pack_start(self.headGame, False, False, 0)
    self.boxGame.set_property("width-request", monitor_width)

    file_name = os.path.join(PIXMAPS_DIR, 'footballfield_1382x838.svg')
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(file_name, -1, field_height_full, True)
    self.imgFootballField.set_from_pixbuf(pixbuf)
    self.fix.move(self.imgFootballField, int(round(space_full / 2)), 0)

    self.drawA.set_property("width-request", int(round(31*scale_full)))
    self.drawA.set_property("height-request", int(round(88*scale_full)))
    self.drawB.set_property("width-request", int(round(31*scale_full)))
    self.drawB.set_property("height-request", int(round(88*scale_full)))
    self.fix.move(self.drawA,
        int(round(1344*scale_full + space_full/2)),
        int(round(375*scale_full)))
    self.fix.move(self.drawB,
        int(round(7*scale_full + space_full/2)),
        int(round(375*scale_full)))
    self.fix.move(self.lblGoalLeft,
        int(round(331*scale_full + 300*scale_full - 300 + space_full/2)),
        int(round(369*scale_full + 50*scale_full - 50)))
    self.fix.move(self.lblGoalRight,
        int(round(751*scale_full + space_full/2)),
        int(round(369*scale_full + 50*scale_full - 50)))
    self.fix.move(self.lblVocabulary,
        int(round(391*scale_full + 300*scale_full - 300 + space_full/2)),
        int(round(11*scale_full)))
    move_ball(self, ballpos)


def get_teams(self):

    global teams

    self.listTeamA.clear()
    self.listTeamB.clear()
    teams = []
    if os.path.exists(TEAMS_FILE):
        with open(TEAMS_FILE, 'r') as f:
            teams = list(filter(None, f.read().split("\n")))
    for team in teams:
        self.listTeamA.append([team])
        self.listTeamB.append([team])


def save_teams_file(teams):

    teams.sort()
    with open(TEAMS_FILE, 'w') as f:
        for team in teams:
            f.write(team + "\n")


def show_game_options(self):

    from list import get_vocabulary, get_vocabulary_error
    from settings import default_file
    global voc_unit

    if os.path.exists(default_file):
        secondary_text, voc_unit = get_vocabulary(self.listUnits, default_file)
        if secondary_text:
            get_vocabulary_error(default_file, self.winGame, secondary_text)
    get_teams(self)

    if not Gtk.check_version(3,22,0):
        self.popOptions.popup()
    else:
        self.popOptions.show_all()


def setup_game(self, teamA, teamB):

    global colorA, colorB, ingame, player_number, scoreA, scoreB

    # workaround for rendering issue in MS Windows
    self.drawA.hide()
    self.drawB.hide()

    rgbaA = Gtk.ColorChooser.get_rgba(self.colbtnTeamA)
    colorA = '#{:02x}{:02x}{:02x}'.format(round(rgbaA.red*255),
        round(rgbaA.green*255), round(rgbaA.blue*255))
    rgbaB = Gtk.ColorChooser.get_rgba(self.colbtnTeamB)
    colorB = '#{:02x}{:02x}{:02x}'.format(round(rgbaB.red*255),
        round(rgbaB.green*255), round(rgbaB.blue*255))
    if colorA[1] in "bcdef" or colorA[3] in "bcdef" or colorA[5] in "bcdef":
        markupA = "<span background='{}' foreground='#000000'>{}</span>".format(colorA, teamA)
    else:
        markupA = "<span background='{}' foreground='#ffffff'>{}</span>".format(colorA, teamA)
    if colorB[1] in "bcdef" or colorB[3] in "bcdef" or colorB[5] in "bcdef":
        markupB = "<span background='{}' foreground='#000000'>{}</span>".format(colorB, teamB)
    else:
        markupB = "<span background='{}' foreground='#ffffff'>{}</span>".format(colorB, teamB)
    self.lblTeamA.set_markup(markupA)
    self.lblTeamB.set_markup(markupB)
    self.lblVocabulary.set_text("")
    scoreA = self.cmbScoreA.get_active()
    scoreB = self.cmbScoreB.get_active()
    scoreA_file = 'score{}_30x50_{}.png'.format(str(scoreA), headerbar_color)
    scoreB_file = 'score{}_30x50_{}.png'.format(str(scoreB), headerbar_color)
    self.imgScoreA.set_from_file(os.path.join(PIXMAPS_DIR, scoreA_file))
    self.imgScoreB.set_from_file(os.path.join(PIXMAPS_DIR, scoreB_file))
    self.drawA.show()
    self.drawB.show()
    self.imgFootball.show()
    self.imgShirtA.hide()
    self.lblShirtA.hide()
    self.imgShirtB.hide()
    self.lblShirtB.hide()
    self.evntArrowLeft.hide()
    self.evntArrowRight.hide()
    self.lblGoalLeft.hide()
    self.lblGoalRight.hide()
    player_number = self.cmbPlayerNr.get_active()+5
    players.clear()
    for n in range(player_number):
        players.append(n)

    if not ingame:
        self.btnGame.set_label(_("Kick-off!"))
    ingame = True
    self.menuGameOptions.set_sensitive(True)

    if not Gtk.check_version(3,22,0):
        self.popOptions.popdown()
    else:
        self.popOptions.hide()


def play_game(self):

    from settings import timer_length

    if len(players) == 1:
        players.clear()
        for n in range(player_number):
            players.append(n)
    player_current = random.randint(1, len(players)-1)
    if colorA[1] in "ef" and colorA[3] in "ef" and colorA[5] in "ef":
        markupA = "<span foreground='#000000'>{}</span>".format(str(players[player_current]))
    else:
        markupA = "<span foreground='{}'>{}</span>".format(colorA, str(players[player_current]))
    if colorB[1] in "ef" and colorB[3] in "ef" and colorB[5] in "ef":
        markupB = "<span foreground='#000000'>{}</span>".format(str(players[player_current]))
    else:
        markupB = "<span foreground='{}'>{}</span>".format(colorB, str(players[player_current]))
    self.lblShirtA.set_markup(markupA)
    self.lblShirtB.set_markup(markupB)
    self.lblShirtA.show()
    self.lblShirtB.show()
    self.imgShirtA.show()
    self.imgShirtB.show()
    players.remove(players[player_current])

    self.btnGame.set_label(_("Next"))
    self.btnGame.set_sensitive(False)
    self.evntArrowLeft.hide()
    self.evntArrowRight.hide()

    markup = "<span background='#ffdd00' foreground='#000000'>{}</span>".format(str(timer_length))
    self.lblVocabulary.set_markup(markup)
    self.btnMenu.set_sensitive(False)
    GObject.timeout_add(1000, select_vocable, self)


def select_vocable(self):

    count = int(self.lblVocabulary.get_text())
    count -= 1
    markup = "<span background='#ffdd00' foreground='#000000'>{}</span>".format(str(count))
    self.lblVocabulary.set_markup(markup)
    if count == 0:
        vocable = voc_active[random.randint(0, len(voc_active)-1)]
        markup = "<span background='#ffdd00' foreground='#000000'>{}</span>".format(vocable)
        self.lblVocabulary.set_markup(markup)
        self.btnGame.set_sensitive(True)
        self.btnGame.grab_focus()
        self.evntArrowLeft.show()
        self.evntArrowRight.show()
        self.btnMenu.set_sensitive(True)
        return False
    return True


def move_ball(self, ballpos):

    if -4 < ballpos < 4:
        if ballpos == -3:
            x = int(round(116*scale_full + 50*scale_full - 50 + space_full/2))
            y = int(round(544*scale_full + 50*scale_full - 50))
            self.fix.move(self.imgFootball, x, y)
            self.fix.move(self.imgShirtA, x-75, y+100)
            self.fix.move(self.lblShirtA, x-75, y+100)
            self.fix.move(self.imgShirtB, x+100, y+100)
            self.fix.move(self.lblShirtB, x+100, y+100)
            self.fix.move(self.evntArrowLeft, x-75, y-75)
            self.fix.move(self.evntArrowRight, x+100, y-75)
            self.imgArrowLeft.set_from_file(os.path.join(PIXMAPS_DIR, 'arrowupleft_75x75.png'))
            self.imgArrowRight.set_from_file(os.path.join(PIXMAPS_DIR, 'arrowupright_75x75.png'))
        if ballpos == -2:
            x = int(round(291*scale_full + 50*scale_full - 50 + space_full/2))
            y = int(round(369*scale_full + 50*scale_full - 50))
            self.fix.move(self.imgFootball, x, y)
            self.fix.move(self.imgShirtA, x+100, y+100)
            self.fix.move(self.lblShirtA, x+100, y+100)
            self.fix.move(self.imgShirtB, x-75, y-75)
            self.fix.move(self.lblShirtB, x-75, y-75)
            self.fix.move(self.evntArrowLeft, x-75, y+100)
            self.fix.move(self.evntArrowRight, x+100, y-75)
            self.imgArrowLeft.set_from_file(os.path.join(PIXMAPS_DIR, 'arrowdownleft_75x75.png'))
            self.imgArrowRight.set_from_file(os.path.join(PIXMAPS_DIR, 'arrowupright_75x75.png'))
        if ballpos == -1:
            x = int(round(466*scale_full + 50*scale_full - 50 + space_full/2))
            y = int(round(194*scale_full + 50*scale_full - 50))
            self.fix.move(self.imgFootball, x, y)
            self.fix.move(self.imgShirtA, x+100, y-75)
            self.fix.move(self.lblShirtA, x+100, y-75)
            self.fix.move(self.imgShirtB, x-75, y-75)
            self.fix.move(self.lblShirtB, x-75, y-75)
            self.fix.move(self.evntArrowLeft, x-75, y+100)
            self.fix.move(self.evntArrowRight, x+100, y+100)
            self.imgArrowLeft.set_from_file(os.path.join(PIXMAPS_DIR, 'arrowdownleft_75x75.png'))
            self.imgArrowRight.set_from_file(os.path.join(PIXMAPS_DIR, 'arrowdownright_75x75.png'))
        if ballpos == 0:
            move_ball_middle(self)
        if ballpos == 1:
            x = int(round(816*scale_full + 50*scale_full - 50 + space_full/2))
            y = int(round(544*scale_full + 50*scale_full - 50))
            self.fix.move(self.imgFootball, x, y)
            self.fix.move(self.imgShirtA, x+100, y+100)
            self.fix.move(self.lblShirtA, x+100, y+100)
            self.fix.move(self.imgShirtB, x-75, y+100)
            self.fix.move(self.lblShirtB, x-75, y+100)
            self.fix.move(self.evntArrowLeft, x-75, y-75)
            self.fix.move(self.evntArrowRight, x+100, y-75)
            self.imgArrowLeft.set_from_file(os.path.join(PIXMAPS_DIR, 'arrowupleft_75x75.png'))
            self.imgArrowRight.set_from_file(os.path.join(PIXMAPS_DIR, 'arrowupright_75x75.png'))
        if ballpos == 2:
            x = int(round(991*scale_full + 50*scale_full - 50 + space_full/2))
            y = int(round(369*scale_full + 50*scale_full - 50))
            self.fix.move(self.imgFootball, x, y)
            self.fix.move(self.imgShirtA, x+100, y+100)
            self.fix.move(self.lblShirtA, x+100, y+100)
            self.fix.move(self.imgShirtB, x-75, y-75)
            self.fix.move(self.lblShirtB, x-75, y-75)
            self.fix.move(self.evntArrowLeft, x-75, y+100)
            self.fix.move(self.evntArrowRight, x+100, y-75)
            self.imgArrowLeft.set_from_file(os.path.join(PIXMAPS_DIR, 'arrowdownleft_75x75.png'))
            self.imgArrowRight.set_from_file(os.path.join(PIXMAPS_DIR, 'arrowupright_75x75.png'))
        if ballpos == 3:
            x = int(round(1166*scale_full + 50*scale_full - 50 + space_full/2))
            y = int(round(194*scale_full + 50*scale_full - 50))
            self.fix.move(self.imgFootball, x, y)
            self.fix.move(self.imgShirtA, x+100, y-75)
            self.fix.move(self.lblShirtA, x+100, y-75)
            self.fix.move(self.imgShirtB, x-75, y-75)
            self.fix.move(self.lblShirtB, x-75, y-75)
            self.fix.move(self.evntArrowLeft, x-75, y+100)
            self.fix.move(self.evntArrowRight, x+100, y+100)
            self.imgArrowLeft.set_from_file(os.path.join(PIXMAPS_DIR, 'arrowdownleft_75x75.png'))
            self.imgArrowRight.set_from_file(os.path.join(PIXMAPS_DIR, 'arrowdownright_75x75.png'))
    else:
        goal(self, ballpos)


def move_ball_middle(self):

    x = int(round(641*scale_full + 50*scale_full - 50 + space_full/2))
    y = int(round(369*scale_full + 50*scale_full - 50))
    self.fix.move(self.imgFootball, x, y)
    self.fix.move(self.imgShirtA, x+100, y-75)
    self.fix.move(self.lblShirtA, x+100, y-75)
    self.fix.move(self.imgShirtB, x-75, y+100)
    self.fix.move(self.lblShirtB, x-75, y+100)
    self.fix.move(self.evntArrowLeft, x-75, y-75)
    self.fix.move(self.evntArrowRight, x+100, y+100)
    self.imgArrowLeft.set_from_file(os.path.join(PIXMAPS_DIR, 'arrowupleft_75x75.png'))
    self.imgArrowRight.set_from_file(os.path.join(PIXMAPS_DIR, 'arrowdownright_75x75.png'))


def goal(self, ballpos):

    from settings import sound
    global scoreA, scoreB

    move_ball_middle(self)
    self.evntArrowLeft.hide()
    self.evntArrowRight.hide()
    self.btnGame.set_label(_("Kick-off!"))
    self.lblVocabulary.set_text("")

    if ballpos == -4:
        if scoreA == 9:
            scoreA = 0
        else:
            scoreA += 1
        scoreA_file = 'score{}_30x50_{}.png'.format(str(scoreA), headerbar_color)
        self.imgScoreA.set_from_file(os.path.join(PIXMAPS_DIR, scoreA_file))
        markupLeft = "<span foreground='{}'>{}</span>".format(colorA, _("G"))
        markupRight = "<span foreground='{}'>{}</span>".format(colorA, _("AL"))
        self.lblGoalLeft.set_markup(markupLeft)
        self.lblGoalRight.set_markup(markupRight)
    if ballpos == 4:
        if scoreB == 9:
            scoreB = 0
        else:
            scoreB += 1
        scoreB_file = 'score{}_30x50_{}.png'.format(str(scoreB), headerbar_color)
        self.imgScoreB.set_from_file(os.path.join(PIXMAPS_DIR, scoreB_file))
        markupLeft = "<span foreground='{}'>{}</span>".format(colorB, _("G"))
        markupRight = "<span foreground='{}'>{}</span>".format(colorB, _("AL"))
        self.lblGoalLeft.set_markup(markupLeft)
        self.lblGoalRight.set_markup(markupRight)
    self.lblGoalLeft.show()
    self.lblGoalRight.show()

    if sound:
        play_sound(self, 'crowd.wav')


def reset_game(self):

    global ballpos, ingame, players, scoreA, scoreB, voc_active

    ballpos = 0
    ingame = False
    self.imgFootball.hide()
    self.imgShirtA.hide()
    self.lblShirtA.hide()
    self.imgShirtB.hide()
    self.lblShirtB.hide()
    self.evntArrowLeft.hide()
    self.evntArrowRight.hide()
    self.drawA.hide()
    self.drawB.hide()
    self.lblGoalLeft.hide()
    self.lblGoalRight.hide()
    move_ball_middle(self)
    scoreA = 0
    scoreB = 0
    scoreA_file = 'scoreoff_30x50_{}.png'.format(headerbar_color)
    scoreB_file = 'scoreoff_30x50_{}.png'.format(headerbar_color)
    self.imgScoreA.set_from_file(os.path.join(PIXMAPS_DIR, scoreA_file))
    self.imgScoreB.set_from_file(os.path.join(PIXMAPS_DIR, scoreB_file))
    self.cmbScoreA.set_active(scoreA)
    self.cmbScoreB.set_active(scoreB)
    self.lblTeamA.set_text("")
    self.lblTeamB.set_text("")
    self.lblVocabulary.set_text("")
    players.clear()
    voc_active.clear()
    self.listUnits.clear()
    self.btnGame.set_label(_("New Game"))
    self.menuGameOptions.set_sensitive(False)


def play_sound(self, file_name):

    sound_file = os.path.join(SOUNDS_DIR, file_name)
    if os.name == 'posix':
        from simpleaudio.simpleaudio import WaveObject
        WaveObject.from_wave_file(sound_file).play()
    else:
        from winsound import PlaySound, SND_FILENAME, SND_ASYNC
        PlaySound(sound_file, SND_FILENAME | SND_ASYNC)


# initialize game window and manage widgets

class Game(Gtk.Application):

    def __init__(self):

        Gtk.Application.__init__(self)

        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(UI_DIR, 'game.ui'))
        self.builder.connect_signals(self)

        for obj in self.builder.get_objects():
            if issubclass(type(obj), Gtk.Buildable):
                name = Gtk.Buildable.get_name(obj)
                setattr(self, name, obj)

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(os.path.join(UI_DIR, 'vocball.css'))
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),
            css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


    def do_startup(self):

        Gtk.Application.do_startup(self)

        setup_headerbar(self)
        check_fullscreen(self)

        self.abtdlg.set_version(VERSION)


    def do_activate(self):

        self.add_window(self.winGame)
        self.winGame.present()


    # menus

    def on_menuNew_clicked(self, widget):

        if ingame:
            message_text = _("Do you want to quit the current game?")
            dialog = Gtk.MessageDialog(self.winGame, 0,
                Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, message_text)
            response = dialog.run()
            if response == Gtk.ResponseType.YES:
                reset_game(self)
                show_game_options(self)
            dialog.destroy()
        else:
            show_game_options(self)


    def on_menuGameOptions_clicked(self, widget):

        get_teams(self)
        self.cmbScoreA.set_active(scoreA)
        self.cmbScoreB.set_active(scoreB)

        if not Gtk.check_version(3,22,0):
            self.popOptions.popup()
        else:
            self.popOptions.show_all()


    def on_menuSettings_clicked(self, widget):

        from settings import Settings

        Settings(self.winGame)


    def on_menuEditor_clicked(self, widget):

        from editor import Editor

        Editor(self.winGame)


    def on_menuHelp_clicked(self, widget):

        import webbrowser

        webbrowser.open_new_tab("https://vocball.readthedocs.io/en/latest/")


    def on_menuAbout_clicked(self, widget):

        self.abtdlg.run()
        self.abtdlg.hide()


    def on_menuQuit_clicked(self, widget):

        if ingame:
            message_text = _("Do you want to quit the application?")
            dialog = Gtk.MessageDialog(self.winGame, 0,
                Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, message_text)
            response = dialog.run()
            if response == Gtk.ResponseType.YES:
                self.quit()
            dialog.destroy()
        else:
            self.quit()


    # game button

    def on_btnGame_clicked(self, widget):

        if ingame:
            self.lblGoalLeft.hide()
            self.lblGoalRight.hide()
            from settings import sound
            if widget.get_label() == _("Kick-off!") and sound:
                play_sound(self, 'kickoff.wav')
            play_game(self)
        else:
            show_game_options(self)


    def on_btnGame_key_release_event(self, widget, event):

        from settings import keyboard

        if keyboard and widget.get_label() == _("Next"):
            keyval = event.get_keyval()
            # left arrow cursor pressed
            if keyval == (True, 65361):
                self.on_evntArrowLeft_button_press_event(widget, None)
            # right arrow cursor pressed
            if keyval == (True, 65363):
                self.on_evntArrowRight_button_press_event(widget, None)


    # option popover window

    def on_btnVocabulary_clicked(self, widget):

        from list import load_vocabulary_list, get_vocabulary, get_vocabulary_error
        global voc_unit

        dialog = load_vocabulary_list(self.winGame)

        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            voc_file_path = dialog.get_filename()
            dialog.destroy()
            secondary_text, voc_unit = get_vocabulary(self.listUnits, voc_file_path)
            if secondary_text:
                get_vocabulary_error(voc_file_path, self.winGame, secondary_text)
        else:
            dialog.destroy()


    def on_treeUnits_row_activated(self, widget, path, column):

        self.listUnits[path][0] = not self.listUnits[path][0]


    def on_entTeam_icon_press(self, widget, GTK_ENTRY_ICON_SECONDARY, event):

        widget.set_text("")


    def on_btnOptionsApply_clicked(self, widget):

        global teams, voc_active

        message_text = ""

        teamA = self.entTeamA.get_text()
        teamB = self.entTeamB.get_text()
        if not teamA or not teamB or teamA == teamB:
            message_text = _("Please type in two different team names!")
            dialog = Gtk.MessageDialog(self.winGame, 0,
                Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, message_text)
            dialog.run()
            dialog.destroy()
        else:
            if not teamA in teams:
                teams.append(teamA)
            if not teamB in teams:
                teams.append(teamB)
            save_teams_file(teams)
            unit_chosen = False
            for i in range(len(self.listUnits)):
                if self.listUnits[i][0]:
                    unit_chosen = True
                    break
            if not unit_chosen:
                message_text = _("You have to choose one unit at least.")
                dialog = Gtk.MessageDialog(self.winGame, 0,
                    Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, message_text)
                dialog.run()
                dialog.destroy()

        if not message_text:
            voc_active.clear()
            for i in range(len(self.listUnits)):
                if self.listUnits[i][0]:
                    for n in range(1,100):
                        if n == self.listUnits[i][2]:
                            voc_active.extend(voc_unit[n])
            setup_game(self, teamA, teamB)


    def on_btnOptionsCancel_clicked(self, widget):

        if not Gtk.check_version(3,22,0):
            self.popOptions.popdown()
        else:
            self.popOptions.hide()


    # drawing areas within goals

    def on_drawA_draw(self, widget, areaA):

        areaA.set_source_rgba(int(colorA[1:3], 16)/255, int(colorA[3:5], 16)/255,
            int(colorA[5:7], 16)/255, 1)
        x = int(round(31*scale_full))
        y = int(round(88*scale_full))
        areaA.rectangle(0, 0, x, y)
        areaA.fill()


    def on_drawB_draw(self, widget, areaB):

        areaB.set_source_rgba(int(colorB[1:3], 16)/255, int(colorB[3:5], 16)/255,
            int(colorB[5:7], 16)/255, 1)
        x = int(round(31*scale_full))
        y = int(round(88*scale_full))
        areaB.rectangle(0, 0 , x, y)
        areaB.fill()


    # arrows

    def on_evntArrowLeft_button_press_event(self, widget, BUTTON_PRESS):

        global ballpos

        self.imgShirtA.hide()
        self.lblShirtA.hide()
        self.imgShirtB.hide()
        self.lblShirtB.hide()

        if ballpos == 4 or ballpos == -4:
            ballpos = 0
        ballpos -= 1
        if ballpos == 2:
            from settings import sound
            if sound:
                play_sound(self, 'lostchance.wav')
        move_ball(self, ballpos)


    def on_evntArrowRight_button_press_event(self, widget, BUTTON_PRESS):

        global ballpos

        self.imgShirtA.hide()
        self.lblShirtA.hide()
        self.imgShirtB.hide()
        self.lblShirtB.hide()

        if ballpos == 4 or ballpos == -4:
            ballpos = 0
        ballpos += 1
        if ballpos == -2:
            from settings import sound
            if sound:
                play_sound(self, 'lostchance.wav')
        move_ball(self, ballpos)


    # quit game

    def on_winGame_delete_event(self, widget, event):

        if ingame:
            message_text = _("Do you want to quit the application?")
            dialog = Gtk.MessageDialog(self.winGame, 0,
                Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, message_text)
            response = dialog.run()
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                return False
            else:
                return True
        else:
            return False


    def on_winGame_destroy(self, widget):

        self.quit()
