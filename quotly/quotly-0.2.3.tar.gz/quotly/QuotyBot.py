from discord import DMChannel
from dotenv import load_dotenv, find_dotenv
from discord.ext import commands
from quotly.Quotly import Quotly

quotly = Quotly()
quoty_bot = commands.Bot(command_prefix='!')

cmds = {
    'add_quote': 'quotly-add',
    'get_quote': 'quotly-get'
}


@quoty_bot.command(name=cmds['add_quote'])
async def create(ctx, q, *targets):
    # keep the channel clean
    if not isinstance(ctx.channel, DMChannel):
        await ctx.message.delete()

    # message user that his quote is stored
    await ctx.author.send('Quote added: {0}'.format((quotly.store_quote(q, targets))))


@quoty_bot.command(name=cmds['get_quote'])
async def quote(ctx, *targets):
    if len(targets) > 0:
        await ctx.send(quotly.fetch_quote_with_targets(targets))
    else:
        await ctx.send(quotly.fetch_quote())
