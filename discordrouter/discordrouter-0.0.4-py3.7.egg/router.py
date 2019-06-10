from functools import wraps
from chatbottokenizer import Tokenizer


def message(router: 'Router', template: str, help: str = ""):
    def decorator(func):
        router.add(template, func, help)

        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            await func(self, *args, **kwargs)

        return wrapper

    return decorator


def guide(router: 'Router'):
    def decorator(func):
        router.set_guide(func)

        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            await func(self, *args, **kwargs)

        return wrapper

    return decorator


class Router:
    commands = []
    guide = None

    def __init__(self, name: str, auto_help=False):
        self.name = name
        self.auto_help = auto_help

    def add(self, template, func, hlp):
        self.commands.append((template, func, hlp))

    def set_guide(self, func):
        self.guide = func

    def set_name(self, name: str) -> None:
        self.name = name

    def _create_help(self):
        output = [
            f'{self.name} {tmpl} - {hlp}' for (tmpl, _, hlp) in self.commands
        ]
        output = '\n'.join(output)
        output = f'```{output}```'
        return output

    async def __call__(self, _self, message: 'discord.Message'):
        tokens = Tokenizer(self.name, message.content)

        if not tokens.to_bot():
            return

        for (tmpl, func, _) in self.commands:
            if tokens.match(tmpl):
                await func(
                    _self,
                    items=tokens.items(),
                    message=message,
                    send=message.channel.send)
                return

        if self.auto_help:
            await message.channel.send(self._create_help())
        elif self.guide != None:
            await self.guide(_self, message=message, send=message.channel.send)
