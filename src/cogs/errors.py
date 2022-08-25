import discord
from discord.ext import commands
from discord import errors

class ErrorHandlers(commands.Bot):
    def __init__(self, client: commands.Bot):
        self.client = client
        print("Error handlers ready.")

    @commands.Cog.listener("on_command_error")
    async def on_command_error(self, context, exception: errors.CommandError, /) -> None:
        print(exception)

async def setup(client: commands.Bot):
