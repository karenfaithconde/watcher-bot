"""
ui_modmenu.py

Everything behind the !m command's moderation menu:

- dm_target()        — helper to privately message a user, ignoring
                        the error if their DMs are closed
- ActionModal         — the popup form for entering mute minutes or a
                        warn reason
- UnbanModal          — the popup form for entering a username to unban
- ConfirmActionView   — the Confirm/Cancel step shown after picking an
                        action from the menu
- ModMenuView         — the actual menu with 5 buttons: Mute, Warn,
                        Clear, Ban, Unban

Only the moderator who opened the menu can click its buttons — every
handler checks interaction.user.id against the stored moderator id.
"""

import discord

from config import BAN_AT
from datetime import timedelta
from warnings_store import warning_counts, save_warnings


async def dm_target(target, text):
    """Try to DM the target privately. Silently ignore if their DMs are closed."""
    try:
        await target.send(text)
    except discord.Forbidden:
        pass


class ActionModal(discord.ui.Modal):
    def __init__(self, action, target: discord.Member):
        title = "Mute duration (minutes)" if action == "mute" else "Warn reason"
        super().__init__(title=title)
        self.action = action
        self.target = target
        self.input = discord.ui.TextInput(
            label="Minutes" if action == "mute" else "Reason",
            placeholder="10" if action == "mute" else "Being disruptive",
            required=True
        )
        self.add_item(self.input)

    async def on_submit(self, interaction: discord.Interaction):
        if self.action == "mute":
            try:
                minutes = int(self.input.value)
            except ValueError:
                await interaction.response.send_message("Please enter a whole number.", ephemeral=True)
                return

            until = discord.utils.utcnow() + timedelta(minutes=minutes)
            await self.target.timeout(until, reason=f"Muted via mod menu by {interaction.user}")
            await interaction.response.send_message(
                f"{self.target.mention} muted for {minutes} minute(s).", ephemeral=True
            )
            await dm_target(self.target, f"You've been muted in **{self.target.guild.name}** for {minutes} minute(s).")

        else:  # warn
            reason = self.input.value
            warning_counts[self.target.id] = warning_counts.get(self.target.id, 0) + 1
            count = warning_counts[self.target.id]
            save_warnings()

            await interaction.response.send_message(
                f"{self.target.mention} warned ({count}/{BAN_AT}).", ephemeral=True
            )
            await dm_target(
                self.target,
                f"You've been warned in **{self.target.guild.name}**. Reason: {reason} ({count}/{BAN_AT})"
            )


class UnbanModal(discord.ui.Modal, title="Unban a user"):
    username = discord.ui.TextInput(
        label="Username (exact)",
        placeholder="e.g. SomePerson or SomePerson#1234",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        banned_users = [entry async for entry in interaction.guild.bans()]

        target_entry = None
        for entry in banned_users:
            if str(entry.user) == self.username.value or entry.user.name == self.username.value:
                target_entry = entry
                break

        if target_entry is None:
            await interaction.response.send_message("Couldn't find that user in the ban list.", ephemeral=True)
            return

        await interaction.guild.unban(target_entry.user, reason=f"Unbanned by {interaction.user}")
        await interaction.response.send_message(f"{target_entry.user} has been unbanned.", ephemeral=True)


class ConfirmActionView(discord.ui.View):
    def __init__(self, action, target: discord.Member, moderator: discord.Member):
        super().__init__(timeout=60)
        self.action = action
        self.target = target
        self.moderator = moderator

    async def _check_moderator(self, interaction):
        if interaction.user.id != self.moderator.id:
            await interaction.response.send_message("Only the mod who opened this can use it.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_moderator(interaction):
            return

        if self.action == "clear":
            warning_counts.pop(self.target.id, None)
            save_warnings()
            try:
                await self.target.timeout(None, reason=f"Cleared by {interaction.user}")
            except discord.Forbidden:
                pass
            await interaction.response.edit_message(
                content=f"{self.target.mention}'s warnings and mute have been cleared.", view=None
            )
            await dm_target(self.target, f"Your warnings and mute in **{self.target.guild.name}** have been cleared.")

        elif self.action == "ban":
            await self.target.ban(reason=f"Banned via mod menu by {interaction.user}")
            await interaction.response.edit_message(
                content=f"{self.target.mention} has been banned.", view=None
            )

        else:  # mute or warn — needs extra input via modal
            await interaction.response.send_modal(ActionModal(self.action, self.target))

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_moderator(interaction):
            return
        await interaction.response.edit_message(content="Action cancelled.", view=None)


class ModMenuView(discord.ui.View):
    """Buttons are laid out in rows: row 0 = Mute/Warn/Clear/Ban, row 1 = Unban.
    This attaches to an embed message, so together it reads as one boxed card."""
    def __init__(self, target: discord.Member, moderator: discord.Member):
        super().__init__(timeout=30)
        self.target = target
        self.moderator = moderator

    async def _start(self, interaction, action):
        if interaction.user.id != self.moderator.id:
            await interaction.response.send_message("Only the mod who opened this menu can use it.", ephemeral=True)
            return
        view = ConfirmActionView(action, self.target, self.moderator)
        await interaction.response.send_message(
            f"Confirm **{action}** on {self.target.mention}?", view=view, ephemeral=True
        )

    @discord.ui.button(label="Mute", style=discord.ButtonStyle.blurple, row=0)
    async def mute_btn(self, interaction, button):
        await self._start(interaction, "mute")

    @discord.ui.button(label="Warn", style=discord.ButtonStyle.blurple, row=0)
    async def warn_btn(self, interaction, button):
        await self._start(interaction, "warn")

    @discord.ui.button(label="Clear", style=discord.ButtonStyle.green, row=0)
    async def clear_btn(self, interaction, button):
        await self._start(interaction, "clear")

    @discord.ui.button(label="Ban", style=discord.ButtonStyle.red, row=0)
    async def ban_btn(self, interaction, button):
        await self._start(interaction, "ban")

    @discord.ui.button(label="Unban", style=discord.ButtonStyle.grey, row=1)
    async def unban_btn(self, interaction, button):
        if interaction.user.id != self.moderator.id:
            await interaction.response.send_message("Only the mod who opened this menu can use it.", ephemeral=True)
            return
        await interaction.response.send_modal(UnbanModal())
