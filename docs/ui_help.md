# ui_help.py

This one grew on me the more I built it. It started as just a plain text list of features, but turning it into an actual clickable dropdown made it feel like a real part of the bot instead of an afterthought.

## HELP_CONTENT

```python
HELP_CONTENT = {
    "profanity": {
        "label": "1. Language Filter",
        "desc": "Deletes offensive language automatically",
        "detail": "Scans every message for offensive language and deletes it. "
                   "A whitelist allows casual words like 'fuck'/'bitch' through."
    },
    ...
}
```

This dictionary is really the heart of the whole file. Every single option in the dropdown, and everything shown after clicking it, comes from here. The nice part is that if I ever want to add a new feature to the help menu later, I only ever touch this one dictionary. Nothing else in the file needs to change at all.

Each entry has three things. label is what shows up as the option name in the dropdown. desc is the short one line description shown right underneath it. detail is the longer explanation shown after someone actually picks that option.

## build_menu_embed and build_detail_embed

```python
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
```

Two small functions that turn plain data into something Discord can actually display. build_menu_embed always returns the exact same intro screen. build_detail_embed takes one specific key, like profile, looks it up in HELP_CONTENT, and builds an embed just for that one entry.

## HelpDetailView, the simpler one first

```python
class HelpDetailView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.grey, custom_id="help_back_button")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=build_menu_embed(), view=HelpMenuView())
```

I actually built this one before the dropdown itself, since it is simpler. Just one button. Clicking Back does not need to remember anything about what was picked before, since it always goes back to the exact same starting menu no matter what. edit_message is doing the real work here, swapping out the current embed and view in place, rather than sending a whole new message underneath.

## HelpMenuView, the dropdown

```python
class HelpMenuView(discord.ui.View):
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

        mod_only_keys = ("modmenu", "purge", "setupnotify", "setuphelp", "profile")

        if key in mod_only_keys and not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "That option is for mods only.", ephemeral=True
            )
            return

        await interaction.response.edit_message(embed=build_detail_embed(key), view=HelpDetailView())
```

The options list is built using a list comprehension, which took me a while to feel comfortable reading. Instead of manually writing out nine separate SelectOption lines by hand, this loops through every entry in HELP_CONTENT and builds one option per entry automatically. If I add a tenth entry to the dictionary later, this dropdown grows to ten options on its own, without me touching this part at all.

Inside select_callback, key is whichever option the person just picked. Before showing anything, I check mod_only_keys first. A handful of these options, like the mod menu or the setup commands, really should not be visible to regular members, so if someone without manage_messages permission tries to open one of those specifically, they just get a quiet private message telling them it is mods only, and the shared dropdown message itself never changes for everyone else watching.

## Why both views need timeout None and a custom_id

This part confused me until I connected it back to what I learned building the notify button. Since !setuphelp is meant to be run exactly once, ever, both of these views need to survive a bot restart. timeout=None tells Discord this view never expires on its own. custom_id gives each interactive piece a fixed name Discord can recognize again later. And back in events.py, bot.add_view(HelpMenuView()) and bot.add_view(HelpDetailView()) inside on_ready are what actually remind the bot, every time it starts up, which code belongs to which button.
