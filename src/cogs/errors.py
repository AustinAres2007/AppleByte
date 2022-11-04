from discord.ext import commands
import discord


class ErrorHandler(commands.Cog, name="errors"):
    def __init__(self, client: commands.Bot):
        print("Errors Loaded")
        self.client = client
        client.tree.error(self._handle_error)

    async def _handle_error(self, interaction: discord.Interaction, error: discord.ClientException):
        try:
        
            responce = self.client.command_errors[interaction.command.name][type(error.original) if hasattr(error, "original") else type(error)]
        except KeyError:
            responce = str(error)
        finally:
            await interaction.response.send_message(responce)
            print(error)

async def setup(client: commands.Bot):
    await client.add_cog(ErrorHandler(client))