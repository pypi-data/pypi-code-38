from dotenv import load_dotenv
from discord.ext import commands
from quotly.Quote import Quote
from quotly.Quoty import Quoty

load_dotenv()
quoty = Quoty()
quoty_bot = commands.Bot(command_prefix='!')

cmds = {
    'add_quote': 'quotly-add',
    'get_quote': 'quotly-get'
}


@quoty_bot.command(name=cmds['add_quote'])
async def create(ctx, q, *targets):
    quoty.quotes.append(Quote(q, targets))
    quoty.write_quotes()

    await ctx.send('New quote: \'{0}\'. Targets: {1}'.format(q, targets))


@quoty_bot.command(name=cmds['get_quote'])
async def quote(ctx, *targets):
    if not targets:
        await ctx.send(quoty.get_random().quote)