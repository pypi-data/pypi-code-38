from contextlib import ContextDecorator
import os
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL
from datetime import datetime
import socket
import getpass
from typing import List, Dict, Callable, Tuple
import humanize
import time
import pandas as pd
from validators import domain
from environments_utils import is_stdout_enabled
from tabulate import tabulate
from validate_email import validate_email
import sys
from traceback import format_tb
from userinput import userinput, set_validator, start


class Notipy(ContextDecorator):
    def __init__(self):
        """Create a new istance of Notipy."""
        super(Notipy, self).__init__()
        self._enabled = False
        self._setup()
        self._report = self._interrupt_txt = self._interrupt_html = None

    @start
    def _setup(self):
        self._enabled = True
        print("Let's setup your notipy!")
        print("Hit enter to use the default values.")
        self._always_use_default = userinput("always_use_default",
                                     label="Should I always use the defaults?",
                                     default="no",
                                     sanitizer="human_bool",
                                     validator=set_validator(["yes", "no"]))
        self._email = userinput("email", validator="email", always_use_default=self._always_use_default)
        self._password = getpass.getpass("Password: ")
        self._send_start_email = userinput("start_email",
                                     label="Should I send a start email too?",
                                     default="yes",
                                     sanitizer="human_bool",
                                     validator=set_validator(["yes", "no"]))
        self._task_name = userinput("task name", validator="non_empty", always_use_default=self._always_use_default)
        self._recipients = userinput("recipients", default=self._email,
                                     label="Please insert {name}, separated by a comma",
                                     validator=lambda x: all([
                                         validate_email(email) for email in x.split(",")
                                     ]),
                                     always_use_default=self._always_use_default
                                     ).split(",")
        timeouts = {
            "hours": 24,
            "minutes": 30,
            "seconds": 120
        }
        self._report_timeout_unit = userinput(
            "report_timeout_unit",
            label="Please insert {{name}}, choosing from {choices}".format(
                choices=", ".join(timeouts.keys())
            ),
            default="hours",
            validator=set_validator(timeouts.keys()),
            always_use_default=self._always_use_default
        )
        self._report_timeout = int(userinput(
            "report_timeout",
            label="Please insert {{name}} in {unit}".format(
                unit=self._report_timeout_unit
            ),
            default=timeouts[self._report_timeout_unit],
            validator="positive_integer",
            always_use_default=self._always_use_default
        ))
        self._port = int(userinput(
            "port",
            default=465,
            validator="positive_integer",
            always_use_default=self._always_use_default
        ))

        self._smtp_server = userinput(
            "smtp_server",
            default="smtp.{server}".format(server=".".join(
                self._email.split("@")[1].split(".")[-2:])),
            validator="hostname",
            always_use_default=self._always_use_default
        )

    def _notify(self, subject: str, txt: str, html: str):
        server_ssl = SMTP_SSL(self._smtp_server, self._port)
        server_ssl.login(self._email, self._password)
        msg = MIMEMultipart('alternative')
        msg["Subject"] = subject
        msg["To"] = ",".join(self._recipients)
        msg["From"] = self._email
        msg.attach(MIMEText(txt, 'plain'))
        msg.attach(MIMEText(html, 'html'))
        server_ssl.sendmail(msg["From"], msg["To"], msg.as_string())
        server_ssl.close()

    @property
    def _pwd(self):
        return os.path.dirname(os.path.realpath(__file__))

    def _load_model(self, name: str, ext: str):
        with open("{pwd}/models/{name}.{ext}".format(pwd=self._pwd, name=name, ext=ext), "r") as f:
            return f.read()

    def _json(self, name: str, ext: str)->Dict:
        common = json.loads(self._load_model("common", "json"))
        generic = json.loads(self._load_model(name, "json"))
        extension = json.loads(self._load_model(ext, "json"))
        return {**common, **generic, **extension}

    def _start(self):
        subject, txt, html = self._build_models("start")
        self._notify(subject, txt, html)

    def _completed(self):
        subject, txt, html = self._build_models("completed")
        self._notify(subject, txt, html)

    def _interruption(self):
        subject, txt, html = self._build_models("interruption")
        self._notify(subject, txt, html)

    def _send_report(self):
        subject, txt, html = self._build_models("report")
        self._notify(subject, txt, html)

    def _format_traceback(self, tb, value):
        self._interrupt_txt = "\n".join(format_tb(tb)) + str(value)
        self._interrupt_html = self._interrupt_txt.replace("\n", "<br>")

    def _info(self)->Dict:
        return {
            "hostname": socket.gethostname(),
            "username": getpass.getuser(),
            "pwd": os.getcwd(),
            "elapsed": humanize.naturaldelta(time.time() - self._start_time),
            "now": datetime.now().date(),
            "interrupt_txt": "" if self._interrupt_txt is None else self._interrupt_txt,
            "interrupt_html": "" if self._interrupt_html is None else self._interrupt_html,
            "report_html": "" if self._report is None else self._report.tail().to_html(),
            "report_txt": "" if self._report is None else tabulate(self._report.tail(), tablefmt="pipe", headers="keys"),
            "email": self._email,
            "task_name": self._task_name
        }

    def _build_models(self, name: str)->Tuple[str, str, str]:
        info = self._info()
        models = []
        for ext in ("txt", "html"):
            data = self._json(name, ext)
            model = self._load_model("basic", ext)
            for k, v in data.items():
                if isinstance(v, list):
                    if ext == "txt":
                        v = "\n".join(v)
                    if ext == "html":
                        v = "<br>".join(v)
                v = v.format(**info)
                model = model.replace(k, v)
                data[k] = v
            models.append(model)
        return (data["model_subject"], *models)

    def add_report(self, df: pd.DataFrame):
        if not self._enabled:
            return
        self._report = df if self._report is None else pd.concat([
            self._report, df
        ])
        if time.time() - self._last_report > self._report_timeout*{
            "hours": 60*60,
            "minutes": 60,
            "seconds": 1
        }[self._report_timeout_unit]:
            self._last_report = time.time()
            self._send_report()

    def __enter__(self):
        if self._enabled:
            self._start_time = time.time()
            self._last_report = time.time()
            if self._send_start_email:
                self._start()
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        if not self._enabled:
            return
        if exc_type is not None and exc_type is not KeyboardInterrupt:
            self._format_traceback(traceback, exc_val)
            self._interruption()
        elif exc_type is None:
            self._completed()
