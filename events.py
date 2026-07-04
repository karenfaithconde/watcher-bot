"""
events.py

Registers every @bot.event handler:

- on_ready         — startup log + re-registers the persistent NotifyButton
- on_member_join   — welcome embed + Notify role ping
- on_member_remove — "someone just left" embed
- on_message       — runs every message through the profanity, dangerous
                     link, and spam checks (in that order), escalating
                     warnings into a timeout or ban as needed, then
                     always hands off to process_commands so ! commands
                     still work

Importing this module is what actually registers the handlers with the
bot — main.py imports it purely for that side effect.
"""

import discord

from bot_instance import bot
from config import MOD_LOG_CHANNEL_ID, WELCOME_CHANNEL_ID, NOTIFY_ROLE_ID, TIMEOUT_AT, BAN_AT, TIMEOUT_DURATION
from datetime import timedelta
from filters import is_flagged, is_spamming, is_dangerous_link
from warnings_store import warning_counts, save_warnings
from ui_notify import NotifyButton


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Online in {len(bot.guilds)} server(s)")
    bot.add_view(NotifyButton())


@bot.event
async def on_member_join(member):
    """Sends a welcome embed + pings the Notify role when someone joins."""
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if not channel:
        return

    embed = discord.Embed(
        title="Welcome to the server.",
        description=(
            f"Hey {member.mention}, welcome to **{member.guild.name}**.\n\n"
            "It's great to have you here. Take a look around, introduce yourself if you'd like, "
            "and enjoy your stay."
        ),
        color=0x5865F2,
        timestamp=discord.utils.utcnow()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"{member.guild.member_count} members")

    await channel.send(
        content=f"Welcome {member.mention}! Everyone give them a warm welcome! <@&{NOTIFY_ROLE_ID}>",
        embed=embed,
        allowed_mentions=discord.AllowedMentions(roles=True, users=True)
    )


@bot.event
async def on_member_remove(member):
    """Sends a 'someone left' embed when a member leaves/is removed."""
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if not channel:
        return

    embed = discord.Embed(
        title="Someone just left.",
        description=f"Looks like **{member}** has left the server.\n\nWe'll miss having them around. Take care!",
        color=0x95A5A6,
        timestamp=discord.utils.utcnow()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"{member.guild.member_count} members")

    await channel.send(embed=embed)


@bot.event
async def on_message(message):
    """Filters every message for profanity, dangerous links, or spam
    (checked in that order — only one violation type applies per
    message), escalates warnings into a timeout/ban, then always hands
    off to process_commands so ! commands still work."""
    if message.author.bot:
        return

    if is_flagged(message.content):
        await message.delete()

        user_id = message.author.id
        warning_counts[user_id] = warning_counts.get(user_id, 0) + 1
        count = warning_counts[user_id]
        save_warnings()

        log_channel = bot.get_channel(MOD_LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="Flagged Message",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="User", value=f"{message.author.mention} ({message.author})", inline=False)
            embed.add_field(name="Channel", value=message.channel.mention, inline=False)
            embed.add_field(name="Message", value=message.content or "*(empty/embed content)*", inline=False)
            embed.add_field(name="Warning count", value=str(count), inline=False)
            await log_channel.send(embed=embed)

        if count >= BAN_AT:
            await message.channel.send(f"{message.author.mention} has been banned for repeated violations.")
            await message.author.ban(reason="Repeated language violations")
            warning_counts.pop(user_id, None)
            save_warnings()

        elif count >= TIMEOUT_AT:
            until = discord.utils.utcnow() + timedelta(seconds=TIMEOUT_DURATION)
            await message.author.timeout(until, reason="Repeated language violations")
            await message.channel.send(f"{message.author.mention} has been timed out for 10 minutes (warning {count}/{BAN_AT}).")

        else:
            await message.channel.send(f"{message.author.mention}, watch the language. ({count}/{BAN_AT} warnings)")

    elif await is_dangerous_link(message.content):
        await message.delete()

        user_id = message.author.id
        warning_counts[user_id] = warning_counts.get(user_id, 0) + 1
        count = warning_counts[user_id]
        save_warnings()

        log_channel = bot.get_channel(MOD_LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="Dangerous Link Detected",
                color=discord.Color.dark_red(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="User", value=f"{message.author.mention} ({message.author})", inline=False)
            embed.add_field(name="Channel", value=message.channel.mention, inline=False)
            embed.add_field(name="Message", value=message.content, inline=False)
            embed.add_field(name="Warning count", value=str(count), inline=False)
            await log_channel.send(embed=embed)

        if count >= BAN_AT:
            await message.channel.send(f"{message.author.mention} has been banned for repeated violations.")
            await message.author.ban(reason="Posted dangerous link / repeated violations")
            warning_counts.pop(user_id, None)
            save_warnings()

        elif count >= TIMEOUT_AT:
            until = discord.utils.utcnow() + timedelta(seconds=TIMEOUT_DURATION)
            await message.author.timeout(until, reason="Posted dangerous link / repeated violations")
            await message.channel.send(f"{message.author.mention} has been timed out for posting a dangerous link ({count}/{BAN_AT}).")

        else:
            await message.channel.send(f"{message.author.mention}, that link was flagged as dangerous and has been removed. ({count}/{BAN_AT} warnings)")

    elif is_spamming(message.author.id):
        await message.delete()

        user_id = message.author.id
        warning_counts[user_id] = warning_counts.get(user_id, 0) + 1
        count = warning_counts[user_id]
        save_warnings()

        log_channel = bot.get_channel(MOD_LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="Spam Detected",
                color=discord.Color.orange(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="User", value=f"{message.author.mention} ({message.author})", inline=False)
            embed.add_field(name="Channel", value=message.channel.mention, inline=False)
            embed.add_field(name="Warning count", value=str(count), inline=False)
            await log_channel.send(embed=embed)

        if count >= BAN_AT:
            await message.channel.send(f"{message.author.mention} has been banned for repeated violations.")
            await message.author.ban(reason="Spam / repeated violations")
            warning_counts.pop(user_id, None)
            save_warnings()

        elif count >= TIMEOUT_AT:
            until = discord.utils.utcnow() + timedelta(seconds=TIMEOUT_DURATION)
            await message.author.timeout(until, reason="Spam / repeated violations")
            await message.channel.send(f"{message.author.mention} has been timed out for spamming ({count}/{BAN_AT}).")

        else:
            await message.channel.send(f"{message.author.mention}, slow down — you're sending messages too fast. ({count}/{BAN_AT} warnings)")

    await bot.process_commands(message)
