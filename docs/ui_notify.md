# ui_notify.py

This was the very first button I ever got working, and it is still one of my favorites since it taught me most of what I now know about buttons that need to survive a restart.

## The whole file

```python
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
```

## Why this button needed extra setup

My first version of this button worked fine right after I posted it, then completely stopped responding the next time I restarted the bot, and I could not figure out why for a while. Turns out Discord buttons normally only last a limited amount of time before they are considered expired, which is perfect for something temporary but not for a button that is supposed to work forever after being posted once through !setupnotify.

Three things fix that, and this file only handles part of it.

timeout=None right here tells the view itself to never expire on its own.

custom_id="notify_button" gives this specific button a fixed name, so Discord can recognize it again later even after the bot restarts.

The third piece actually lives outside this file, in events.py, where bot.add_view(NotifyButton()) runs inside on_ready. That line is what tells the bot, every single time it starts up, that this custom_id belongs to this exact class and code.

## What actually happens when someone clicks it

```python
role = interaction.guild.get_role(NOTIFY_ROLE_ID)

if role in interaction.user.roles:
    await interaction.user.remove_roles(role)
    ...
else:
    await interaction.user.add_roles(role)
    ...
```

It is really just a toggle. First it grabs the actual Notify role object using the id stored in config.py. Then it checks whether the person who clicked already has that role. If they do, it takes it away. If they do not, it gives it to them. Either way, the reply uses ephemeral=True, meaning only the person who clicked sees the confirmation message, nobody else in the channel notices anything happening.
