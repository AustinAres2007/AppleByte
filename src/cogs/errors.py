from discord.ext import commands
import discord


class ErrorHandler(commands.Cog, name="errors"):
    def __init__(self, client: commands.Bot):
        self.client = client
        client.tree.error(self._handle_error)

    async def _handle_error(self, interaction: discord.Interaction, error: discord.ClientException):
        try:
            responce = self.client.command_errors[interaction.command.name][type(error)]
        except KeyError:
            responce = str(error)
        finally:
            await interaction.response.send_message(responce)

async def setup(client: commands.Bot):
    await client.add_cog(ErrorHandler(client))