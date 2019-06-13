from IPython.core import magic_arguments
from IPython.core.magic import cell_magic, magics_class
from IPython.core.magics import ExecutionMagics
from twilio.rest import Client
import time
import os

def txt_self(message):
    twilio_sid = os.environ["TWILIO_SID"]
    twilio_token = os.environ["TWILIO_TOKEN"]
    sending_number = os.environ["TWILIO_NUMBER"]
    receiving_number = os.environ["MY_NUMBER"]

    client = Client(twilio_sid, twilio_token)

    txt = client.messages \
                .create(
                    body=message,
                    from_=sending_number,
                    to=receiving_number
                )

def construct_time_mess(elapsed):
    day = elapsed // (24 * 3600)
    elapsed = elapsed % (24 * 3600)
    hour = elapsed // 3600
    elapsed %= 3600
    minutes = elapsed // 60
    elapsed %= 60
    seconds = round(elapsed, 1)
    time_mess = ""
    if day > 0:
        time_mess += " {} days".format(day)
    if hour > 0:
        time_mess += " {} hours ".format(hour)
    if minutes > 0:
        time_mess += " {} minutes".format(minutes)
    if seconds > 0:
        time_mess += " {} seconds".format(seconds)
    return time_mess

@magics_class
class TxtWhenDoneMagics(ExecutionMagics):

    def __init__(self, shell):
        super().__init__(shell)
    
    @cell_magic
    @magic_arguments.magic_arguments()
    @magic_arguments.argument("message", type=str)
    @magic_arguments.argument("--time", "-t", action="store_true")
    def txt_when_done(self, line='', cell=None):
        args = magic_arguments.parse_argstring(self.txt_when_done, line)
        mess = args.message.replace("\"", "")
        start = time.time()
        try:
            self.shell.ex(cell)
            if args.time:
                elapsed = time.time() - start
                time_mess = construct_time_mess(elapsed)
                mess += " in" + time_mess
            txt_self("Finished {}".format(mess))
        except BaseException as e:
            txt_self("Error in cell")
            raise e