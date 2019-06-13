import click
import datetime

class DurationParamType(click.ParamType):
    name = 'duration'

    def convert(self, value, param, ctx):
        """Accepts dd:hh:mm:ss or a sub portion like mm:ss or just ss"""
        try:
            parts = value.split(':')
            parts.reverse()

            total_seconds = 0
            
            multiplier = 1
            for part in parts:
                total_seconds += int(part) * multiplier
                multiplier *= 60

            return datetime.timedelta(seconds=total_seconds)
        except ValueError:
            self.fail('%s is not a valid duration' % value, param, ctx)

DURATION = DurationParamType()