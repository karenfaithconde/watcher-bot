import discord

from config import NOTIFY_ROLE_ID


class NotifyButton(discord.ui.View):
    # persistent button, needs timeout=None + custom_id + bot.add_view() in on_ready
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