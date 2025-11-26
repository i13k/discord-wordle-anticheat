import discord
from discord import app_commands
from unidecode import unidecode
import yaml
import asyncio
import re

import database
from wordle_api import update_answer_cache
from guild_functions import get_guild_settings, change_guild_settings
from strings import STRINGS

from __version__ import __version__

CONFIG_PATH = "config.yaml"

def load_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f) or {}

class Client(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.answer_cache = (None, None)

    async def on_ready(self) -> None:
        await self.wait_until_ready()
        await self.tree.sync()
        print(f"{self.user} has connected to Discord!")

class SettingsEmbed(discord.Embed):
    def __init__(self, settings: dict) -> None:
        super().__init__(title=STRINGS["en"]["settings"]["title"], color=0x0000dd)

        for key, value in settings.items():
            self.add_field(
                name=STRINGS["en"]["settings"]["setting_names"][key],
                value=":white_check_mark: " + STRINGS["en"]["settings"]["enabled"] if value else ":negative_squared_cross_mark: " + STRINGS["en"]["settings"]["disabled"],
                inline=False
            )

class SettingsButtonsView(discord.ui.View):
    def __init__(self, settings: dict, timeout: int = 180) -> None:
        super().__init__(timeout=timeout)

        self.buttons = {}
        for key, value in settings.items():
            self.buttons[key] = discord.ui.Button(
                label=(STRINGS["en"]["settings"]["disable"] if value else STRINGS["en"]["settings"]["enable"]) \
                      + " " + STRINGS["en"]["settings"]["toggle_setting_names"][key],
                style=discord.ButtonStyle.red if value else discord.ButtonStyle.green,
                disabled=not settings["anticheat"] and key != "anticheat"
            )
            self.buttons[key].callback = lambda interaction, key=key, value=not value: self.toggle_setting(interaction, key, value)
            self.add_item(self.buttons[key])

    async def toggle_setting(self, interaction: discord.Interaction, setting_key: str, new_value: bool) -> None:
        if not interaction.user.guild_permissions.administrator:
            return
        await change_guild_settings(interaction.guild.id, {setting_key: new_value})
        new_settings = await get_guild_settings(interaction.guild.id)
        embed = SettingsEmbed(settings=new_settings)
        view = SettingsButtonsView(settings=new_settings)
        await interaction.response.edit_message(embed=embed, view=view)

client = Client()

############################################################################### <- to remove

# @client.tree.command(name="enable", description="Enable Wordle anti-cheat")
# async def enable_anticheat(interaction: discord.Interaction) -> None:
#     await interaction.response.defer(ephemeral=True)
#     if not interaction.user.guild_permissions.administrator:
#         await interaction.followup.send(":lock: **Access denied!** This command is only for server administrators.")
#         return
#     guild = await get_guild(interaction.guild.id)
#     if guild.enabled:
#         await interaction.followup.send(":information_source: Wordle anti-cheat is already **enabled** in this server.")
#         return
#     await change_enabled(guild, True)
#     await interaction.followup.send(":white_check_mark: Wordle anti-cheat **successfully enabled**.")

# @client.tree.command(name="disable", description="Disable Wordle anti-cheat")
# async def disable_anticheat(interaction: discord.Interaction) -> None:
#     await interaction.response.defer(ephemeral=True)
#     if not interaction.user.guild_permissions.administrator:
#         await interaction.followup.send(":lock: **Access denied!** This command is only for server administrators.")
#         return
#     guild = await get_guild(interaction.guild.id)
#     if not guild.enabled:
#         await interaction.followup.send(":information_source: Wordle anti-cheat is already **disabled** in this server.")
#         return
#     await change_enabled(guild, False)
#     await interaction.followup.send(":negative_squared_cross_mark: Wordle anti-cheat **successfully disabled**.")

# @client.tree.command(name="status", description="Get status of Wordle anti-cheat")
# async def anticheat_status(interaction: discord.Interaction) -> None:
#     await interaction.response.defer(ephemeral=True)
#     guild = await get_guild(interaction.guild.id)
#     message = f"Wordle anti-cheat is currently **{':white_check_mark: enabled' if guild.enabled else ':negative_squared_cross_mark: disabled'}** in this server.\n"
#     message += f"Use `{'/enable' if not guild.enabled else '/disable'}` to {'enable' if not guild.enabled else 'disable'} it."
#     await interaction.followup.send(message)

############################################################################### ->

############################################################################### <- change strings
@client.tree.command(name="about", description="About the bot")
async def about_bot(interaction: discord.Interaction) -> None:
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(
        title="Wordle Anti-cheat",
        description="**Anti-cheat** bot for Wordle activity in Discord.\nBot deletes messages that contain Wordle answers.",
        color=0x0000dd
    )
    embed.add_field(name="Version", value=f"`{__version__}`", inline=False)
    embed.add_field(name="Source code", value="[GitHub Repository](https://github.com/bartekl1/discord-wordle-anticheat)", inline=False)
    embed.add_field(name="License", value="GNU Affero General Public License v3.0", inline=False)
    await interaction.followup.send(embed=embed)
############################################################################### ->

@client.tree.command(name="settings", description="Bot settings for this server")
async def bot_settings(interaction: discord.Interaction) -> None:
    await interaction.response.defer(ephemeral=True)
    current_settings = await get_guild_settings(interaction.guild.id)
    embed = SettingsEmbed(settings=current_settings)
    if interaction.user.guild_permissions.administrator:
        view = SettingsButtonsView(settings=current_settings)
    else:
        view = discord.ui.View()
        embed.set_footer(text=STRINGS["en"]["settings_only_admin"])
    await interaction.followup.send(embed=embed, view=view)

############################################################################### <- to review
@client.event
async def on_message(message: discord.Message) -> None:
    client.answer_cache = await update_answer_cache(client.answer_cache)
    if message.author == client.user:
        return
    guild = await get_guild_settings(message.guild.id)
    if not guild["anticheat"]:
        return

    message_text = message.content.lower()
    message_text = unidecode(message_text) if guild["replace_diacritics"] else message_text
    message_text = re.sub(r"[^A-Za-z]", "", message_text).lower() if guild["remove_not_letters"] else message_text

    if client.answer_cache[1] in message_text or \
       (client.answer_cache[1][::-1] in message_text and guild["reversed_detection"]):
        await message.delete()
        if guild["send_messages"]:
            await message.channel.send(f":warning: {message.author.mention}, your message has been deleted because it contained today's Wordle answer.", silent=True)
############################################################################### ->

def main() -> None:
    config = load_config()
    asyncio.run(database.init_db(config.get("database_url", "sqlite+aiosqlite:///./wordle_anticheat.db")))
    client.run(config.get("bot_token"))

if __name__ == "__main__":
    main()
