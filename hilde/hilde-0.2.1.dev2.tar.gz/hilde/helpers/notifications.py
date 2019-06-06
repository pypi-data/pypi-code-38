""" Notifications via, e.g., email """


def send_simple_mail(message, to_addr, extra_message=""):
    import os

    log = os.system(
        'echo "{}" | mailx -s "[hilde] {:s}" {:s}'.format(
            extra_message, message, to_addr
        )
    )

    if log:
        print("Sending the Mail returned error code {:s}".format(str(log)))
