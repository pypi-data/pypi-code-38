# module to open alarm widget which appears and flashes and plays noise
from __future__ import print_function, unicode_literals, absolute_import, division
import six
import subprocess
import sys
from hcam_widgets.tkutils import addStyle, get_root

if not six.PY3:
    import Tkinter as tk
else:
    import tkinter as tk

alarm_file = '/home/observer/alarms/phat_alarm.mp3'
login = '/usr/bin/ssh observer@192.168.1.1'
alarm_cmd = '{} {} {}'.format(
    login,
    '/usr/bin/afplay' if sys.platform == 'darwin' else '/usr/bin/mpg123-portaudio',
    alarm_file
)

kill_alarm_cmd = '{} {}'.format(
    login,
    '/usr/bin/killall afplay' if sys.platform == 'darwin' else '/usr/bin/killall mpg123.bin'
)


class AlarmDialog(tk.Toplevel):
    """
    A widget that appears when an alarm is raised.

    A simple dialog widget that displays an alarm message.
    It also plays an alarm sound, and allows you to acknowledge
    the alarm, which silences the sound and destroys the widget.

    Arguments
    ----------
    widget : `hcam_drivers.hardware.HardwareDisplayWidget`
        calling hardware widget
    msg : string
        the alarm message
    play_sound : bool
        play alarm sound y/n?
    title : string, optional
        title for widget
    """
    alarm_playing = False

    def __init__(self, widget, msg, play_sound=True, title='Alarm'):
        parent = widget.parent
        tk.Toplevel.__init__(self, parent)
        self.transient(parent)
        self.title(title)
        self.parent = parent
        self.widget = widget
        self.result = None
        body = tk.Frame(self)
        tk.Label(body, text=msg).pack()
        body.pack(padx=5, pady=5)
        self.buttonbox()

        self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.ack)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        self.initial_focus.focus_set()
        if play_sound and not AlarmDialog.alarm_playing:
            self.alarm_proc = subprocess.Popen(alarm_cmd.split(), shell=False,
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE)
            AlarmDialog.alarm_playing = True
        else:
            self.alarm_proc = None
        addStyle(self)

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons
        box = tk.Frame(self)
        g = get_root(self).globals
        w = tk.Button(box, text="OK", width=10, bg=g.COL['start'],
                      command=self.cancel, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="ACK", width=10, bg=g.COL['warn'],
                      command=self.ack, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("<Return>", self.cancel)
        box.pack()

    #
    # standard button semantics
    def ack(self, event=None):
        # just stop the noise
        self.kill_alarm()
        self.widget.acknowledge_alarm()
        self.teardown()

    def teardown(self):
        self.withdraw()
        self.update_idletasks()
        self.parent.focus_set()
        self.destroy()

    def cancel(self, event=None):
        # cancel alarm
        self.kill_alarm()
        self.widget.cancel_alarm()
        self.teardown()

    def kill_alarm(self):
        proc = subprocess.Popen(kill_alarm_cmd.split(), shell=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if self.alarm_proc:
            self.kill_proc(self.alarm_proc)
        proc.wait()
        AlarmDialog.alarm_playing = False

    def kill_proc(self, proc):
        if proc.poll() is not None:
            return
        proc.terminate()

        # kill if it has not exited after countdown
        def kill_after(countdown):
            if proc.poll() is None:  # process hasn't quit yet
                countdown -= 1
                if countdown < 0:  # kill
                    proc.kill()
                else:
                    self.after(1000, kill_after, countdown)
                    return

            proc.stdout.close()
            proc.wait()

        kill_after(countdown=5)
