"""
ui_notify.py

The "Toggle Join Pings" button members click in the roles/toggles
channel to opt in or out of being pinged when someone new joins.
Uses a fixed custom_id + timeout=None so it keeps working across bot
restarts, as long as bot.add_view(NotifyButton()) runs in on_ready.
"""

import discord

from config import NOTIFY_ROLE_ID


class NotifyButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Toggle Join Pings", style=discord.ButtonStyle.blurple, custom_id="notify_button")
    async def toggle(self, interaction, button):
        role = interaction.guild.get_role(NOTIFY_ROLE_ID)

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("Turned off join pings.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("Turned on join pings.", ephemeral=True)
