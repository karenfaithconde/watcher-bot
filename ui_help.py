"""
ui_help.py

The permanent, README-style help menu posted once via !setuphelp.

- HELP_CONTENT   — all dropdown option text + detail text in one place,
                   so adding/editing a feature only means editing this dict
- HelpMenuView   — the dropdown (select menu) shown first
- HelpDetailView — shown after picking an option: the detail text + a
                   Back button that returns to HelpMenuView

Both views use timeout=None and a fixed custom_id so they keep working
across bot restarts, as long as bot.add_view() registers them in
on_ready (same pattern as NotifyButton).
"""

import discord

# Each entry: label shown in dropdown (numbered instead of using an
# emoji), one-line description shown in dropdown, and the longer detail
# text shown after it's picked.
HELP_CONTENT = {
    "profanity": {
        "label": "1. Language Filter",
        "desc": "Deletes offensive language automatically",
        "detail": "Scans every message for offensive language and deletes it. "
                   "A whitelist allows casual words like 'fuck'/'bitch' through."
    },
    "spam": {
        "label": "2. Spam Protection",
        "desc": "Stops message flooding",
        "detail": "If someone sends too many messages too fast, their messages "
                   "get deleted and they receive a warning."
    },
    "links": {
        "label": "3. Link Safety",
        "desc": "Scans links for malware/phishing",
        "detail": "Any link posted is checked against Google Safe Browsing. "
                   "Flagged links are deleted automatically."
    },
    "modmenu": {
        "label": "4. Mod Menu (!m)",
        "desc": "Mute, warn, clear, ban, unban",
        "detail": "Reply to any message with `!m` to open a private menu with "
                   "Mute, Warn, Clear, Ban, and Unban buttons."
    },
    "purge": {
        "label": "5. Purge (!purge)",
        "desc": "Bulk delete messages",
        "detail": "`!purge <amount>` deletes that many recent messages in the "
                   "channel. Aliases: !clear, !clean."
    },
    "welcome": {
        "label": "6. Welcome/Leave",
        "desc": "Greets new members, notes when they leave",
        "detail": "Posts a welcome message when someone joins, and a short "
                   "note when they leave — both in your welcome channel."
    },
    "pings": {
        "label": "7. Join Pings",
        "desc": "Get notified when someone new joins",
        "detail": "Click the Notify button (posted via !setupnotify) to opt "
                   "in or out of being pinged when a new member joins."
    },
    "setupnotify": {
        "label": "8. Setup: !setupnotify",
        "desc": "Posts the join-ping toggle button",
        "detail": "Run `!setupnotify` once in your toggles channel. It posts "
                   "a permanent button — no need to run it again."
    },
    "setuphelp": {
        "label": "9. Setup: !setuphelp",
        "desc": "Posts this help menu",
        "detail": "Run `!setuphelp` once in your help channel. It posts this "
                   "permanent dropdown menu — no need to run it again."
    },
}


def build_menu_embed():
    return discord.Embed(
        title="Watcher",
        description=(
            "Watcher keeps this server safe from spam, scams, and harassment, "
            "so people can actually enjoy being here.\n\n"
            "Pick something below to see how it works."
        ),
        color=0x5865F2
    )


def build_detail_embed(key):
    entry = HELP_CONTENT[key]
    return discord.Embed(
        title=entry["label"],
        description=entry["detail"],
        color=0x5865F2
    )


class HelpDetailView(discord.ui.View):
    """Shown after picking a dropdown option. Just a Back button — it
    doesn't need to remember which option was picked, since Back always
    returns to the same starting menu."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.grey, custom_id="help_back_button")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=build_menu_embed(), view=HelpMenuView())


class HelpMenuView(discord.ui.View):
    """The starting dropdown. Selecting an option edits the message in
    place to show that feature's detail + a Back button."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Choose a feature or setup command...",
        custom_id="help_select_menu",
        options=[
            discord.SelectOption(
                label=entry["label"],
                description=entry["desc"],
                value=key
            )
            for key, entry in HELP_CONTENT.items()
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        key = select.values[0]

        mod_only_keys = ("modmenu", "purge", "setupnotify", "setuphelp")

        if key in mod_only_keys and not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "That option is for mods only.", ephemeral=True
            )
            return

        await interaction.response.edit_message(embed=build_detail_embed(key), view=HelpDetailView())