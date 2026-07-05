# commands.py

This file is where every typed command lives. If someone has to actually type something starting with ! for it to happen, it's in here. That's different from events.py, where things just happen on their own without anyone asking.

Once I had a few commands built, I noticed they all followed roughly the same shape, so let me walk through each one and point out what's actually going on.

## The imports at the top

```python
import discord
from discord.ext import commands
from bot_instance import bot
from config import BAN_AT
from warnings_store import warning_counts
from ui_notify import NotifyButton
from ui_modmenu import ModMenuView
from ui_help import HelpMenuView, build_menu_embed
from ui_profile import ProfileLookupView, build_profile_embed
```

This is basically the file introducing itself to everyone else it depends on. bot comes from bot_instance.py, since every command decorator needs that shared bot object. Everything else here is a class or function borrowed from one of the ui_ files, since this file mostly just builds an embed and hands off to those.

## !p, the profile check

```python
@bot.command(name="p")
@commands.has_permissions(manage_messages=True)
async def profile_check(ctx):
    if ctx.message.reference:
        replied = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        target = replied.author
        if target.bot:
            await ctx.send("Can't check a bot.", delete_after=6)
            return
        await ctx.send(embed=build_profile_embed(target))
    else:
        await ctx.send("Click below to check a member's profile:", view=ProfileLookupView())
```

The part I like about this one is the branching logic near the top. ctx.message.reference checks whether the person typed !p as a reply to someone else's message. If they did, I already know exactly who they mean, so I can skip straight to showing the profile. If they didn't reply to anyone, there's no target yet, so instead I post a button that opens a form asking who to look up.

@commands.has_permissions(manage_messages=True) sits above the function as a decorator, which quietly stops anyone without that permission from even running the command at all.

## !setuphelp and !setupnotify

```python
@bot.command()
async def setuphelp(ctx):
    await ctx.send(embed=build_menu_embed(), view=HelpMenuView())


@bot.command()
async def setupnotify(ctx):
    await ctx.send("Click the button below to toggle join pings:", view=NotifyButton())
```

These two are almost identical in shape, and that's on purpose. Both are meant to be run exactly once, ever, in whatever channel you want that feature to live in. They just post one message with a permanent view attached, and from then on the view itself (not this command) handles everything.

## !m, the moderation menu

```python
@bot.command(name="m")
@commands.has_permissions(manage_messages=True)
async def mod_menu(ctx):
    if not ctx.message.reference:
        await ctx.send("Reply to the message you want to act on, with !m.", delete_after=6)
        return

    replied = await ctx.channel.fetch_message(ctx.message.reference.message_id)
    target = replied.author

    if target.bot:
        await ctx.send("You can't moderate a bot.", delete_after=6)
        return

    embed = discord.Embed(
        title="Moderation Menu",
        description=f"Choose an action for {target.mention}.\n\nOnly {ctx.author.mention} can use these buttons.",
        color=0x5865F2
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="Target", value=str(target), inline=True)
    embed.add_field(name="Current warnings", value=f"{warning_counts.get(target.id, 0)}/{BAN_AT}", inline=True)

    view = ModMenuView(target, ctx.author)
    await ctx.send(embed=embed, view=view)
```

Unlike !p, this one only works as a reply. There's no fallback lookup form here, since moderating someone really should mean pointing at an actual message they sent, not searching a name from memory.

warning_counts.get(target.id, 0) is a small detail I appreciate now that I understand it. Instead of crashing if that person has never been warned before, .get with a default of 0 just quietly returns zero, which is exactly what you'd want to show.

## !purge

```python
@bot.command(name="purge", aliases=["clear", "clean"])
@commands.has_permissions(manage_messages=True)
@commands.bot_has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    if amount <= 0:
        await ctx.send("Please provide a number greater than 0.", delete_after=5)
        return

    deleted = await ctx.channel.purge(limit=amount + 1)
    confirmation = await ctx.send(f"Deleted {len(deleted) - 1} message(s).")
    await confirmation.delete(delay=3)
```

Two permission checks stacked on top of each other here, and I almost missed why both matter. has_permissions checks the person typing the command. bot_has_permissions checks the bot itself. Without that second one, if the bot's own role somehow lost Manage Messages, this command would fail with a confusing error instead of a clear one.

The +1 in limit=amount + 1 catches the command message itself too, so if you ask for 5 messages deleted, it actually removes your !purge message plus the 5 before it, not 5 plus your own message left behind looking odd.

## Why this file stays so thin

Almost nothing in here is real logic. It is mostly just: check permission, figure out the target, build a small embed, and hand off to a view class from one of the ui_ files. I ended up liking that split a lot, since it means if I ever want to change how the mod menu behaves, I only ever touch ui_modmenu.py, never this file.
