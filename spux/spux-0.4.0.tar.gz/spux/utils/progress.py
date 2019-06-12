# # # # # # # # # # # # # # # # # # # # # # # # # #
# Class for update'able progress bar for the command line
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #


class Progress(object):
    """Class for update'able progress bar for the command line."""

    def __init__(self, prefix, steps, length=20, caption="Progress: "):

        self.prefix = prefix
        self.length = length
        self.steps = steps
        self.percent = None
        self.caption = caption
        self.line = ""

        from sys import stdout

        self.stdout = stdout

    def init(self):
        self.update(0)
        return self.line

    def update(self, step):
        self.step = step
        fraction = float(step) / self.steps if self.steps != 0 else 1.0
        percent = int(round(100 * fraction))
        fraction = min(1.0, fraction)
        if percent == self.percent:
            return self.line
        self.percent = percent
        self.line = self.prefix + self.caption
        self.line += (
            "[" +
            "#" * int(round(fraction * self.length)) +
            " " * int((self.length - round(fraction * self.length))) +
            "]"
        )
        self.line += " " + ("%3d" % percent) + "%"
        self.stdout.write("\r" + self.line)
        self.stdout.flush()
        return self.line

    def increment(self, diff=1):
        self.update(self.step + diff)

    def message(self, message):
        self.reset()
        self.line = self.prefix + message
        self.stdout.write("\r" + self.line)
        self.stdout.flush()
        return self.line

    def reset(self):
        self.stdout.write("\r")
        self.stdout.write(" " * len(self.line))
        self.stdout.flush()
        self.line = ""
        self.stdout.write("\r")
        self.stdout.flush()
        return self.line

    def finalize(self):
        self.stdout.write("\n")
        self.stdout.flush()
        return self.line
