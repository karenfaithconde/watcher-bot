"""
commands.py

Registers every @bot.command:

- !setupnotify — posts the persistent join-ping toggle button (run once)
- !m           — reply to a message to bring up the mute/warn/clear/
                 ban/unban moderation menu
- !purge       — bulk-delete messages (aliases: !clear, !clean)

Like events.py, importing this module registers the commands as a
side effect — main.py imports it purely to trigger that registration.
"""

import discord
from discord.ext import commands

from bot_instance import bot
from config import BAN_AT
from warnings_store import warning_counts
from ui_notify import NotifyButton
from ui_modmenu import ModMenuView
from ui_help import HelpMenuView, build_menu_embed

@bot.command()
async def setuphelp(ctx):
    """Posts the permanent help menu. Only needs to be run once e.g. in your help channel."""
    await ctx.send(embed=build_menu_embed(), view=HelpMenuView())
    
@bot.command()
async def setupnotify(ctx):
    """Posts the persistent notify button. Only needs to be run once,
    e.g. in your roles-and-toggles channel."""
    await ctx.send("Click the button below to toggle join pings:", view=NotifyButton())


@bot.command(name="m")
@commands.has_permissions(manage_messages=True)
async def mod_menu(ctx):
    """Reply to someone's message with !m to bring up the moderation menu."""
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


@bot.command(name="purge", aliases=["clear", "clean"])
@commands.has_permissions(manage_messages=True)
@commands.bot_has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    """!purge <amount> (or !clear / !clean) — deletes the last `amount`
    messages plus the command message itself."""
    if amount <= 0:
        await ctx.send("Please provide a number greater than 0.", delete_after=5)
        return

    deleted = await ctx.channel.purge(limit=amount + 1)
    confirmation = await ctx.send(f"Deleted {len(deleted) - 1} message(s).")
    await confirmation.delete(delay=3)
