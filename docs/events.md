# events.py

This one took me the longest to really get comfortable with, mostly because it is the biggest file, but once I broke it down function by function it made a lot more sense. Everything in here runs on its own, without anyone typing a command. Discord just calls these functions directly whenever something happens, which is why they are all named on_something.

## on_ready

```python
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Online in {len(bot.guilds)} server(s)")
    bot.add_view(NotifyButton())
    bot.add_view(HelpMenuView())
    bot.add_view(HelpDetailView())
```

This runs exactly once, the moment the bot successfully connects. The print lines are just there so I can glance at my terminal and confirm it actually logged in. The three bot.add_view(...) lines matter more than they look. Buttons and dropdowns that are supposed to work forever, like the notify toggle and the help menu, need to be re registered every time the bot restarts, or Discord forgets which code they are supposed to run.

## on_guild_join

```python
@bot.event
async def on_guild_join(guild):
    channel = next(
        (c for c in guild.text_channels
         if c.name.lower() == "general" and c.permissions_for(guild.me).send_messages),
        None
    )
    if channel is None:
        channel = next(
            (c for c in guild.text_channels if c.permissions_for(guild.me).send_messages),
            None
        )
    if channel is None:
        print(f"Joined {guild.name} but couldn't find a channel to post in.")
        return

    embed = discord.Embed(
        title="Thanks for adding Watcher",
        description=(
            "There are two quick things to set up, and you'll only need to do them once.\n\n"
            "**`!setuphelp`** — run this here\n"
            "This posts a menu that walks through everything Watcher does.\n\n"
            "**`!setupnotify`** — run this in whatever channel you want\n"
            "This adds a toggle button so people can turn join pings on or off for themselves.\n\n"
            "Once those are done, you're all set."
        ),
        color=0x5865F2
    )
    await channel.send(embed=embed)
```

This one fires the moment the bot gets added to a brand new server, and it took a bit of trial and error to get right. My first version tried to rely on Discord's system channel setting, but I could not find that setting reliably in every server, so I switched to a simpler plan instead.

The first next(...) call looks for a channel literally named general that the bot is actually allowed to post in. Most servers have a channel like that by default, so it felt like a safe first guess. If that search comes up empty, the second next(...) call just grabs the first text channel it can post in, no matter the name. If even that fails, which should basically never happen since the bot usually has Administrator, it prints a note to my own console instead of silently doing nothing, so I at least know it happened.

## on_member_join

```python
@bot.event
async def on_member_join(member):
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
```

This fires whenever someone new joins the server. The if not channel check is a small safety net, since if the welcome channel id in config.py ever points at a channel that got deleted, this just quietly does nothing instead of crashing the whole bot. The allowed_mentions part is something I did not expect to need. Without explicitly allowing role mentions, the ping to the notify role would just silently fail to notify anyone, even though the text would still show up.

## on_member_remove

```python
@bot.event
async def on_member_remove(member):
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
```

The quieter sibling of on_member_join. Same shape, just a shorter message and a grey color instead of blue, since it is meant to feel less exciting than a welcome.

## on_message, the big one

This is where most of the actual moderation happens, so let me slow down here.

```python
@bot.event
async def on_message(message):
    if message.author.bot:
        return
```

First thing it does is bail out immediately if the message came from a bot. Without this, the bot could end up reacting to its own messages, or to other bots, which gets messy fast.

```python
    if is_flagged(message.content):
        ...
    elif await is_dangerous_link(message.content):
        ...
    elif is_spamming(message.author.id):
        ...
```

These three checks run in order, and using elif instead of separate if statements was a deliberate choice. It means a message only ever gets punished for one reason at a time, even if it happens to match more than one check.

Inside each of those three blocks, the pattern repeats almost exactly the same way. Delete the message. Add one to that person's warning count. Save it to disk. Post an embed to the mod log channel explaining what happened. Then check the new count against BAN_AT and TIMEOUT_AT from config.py to decide whether this crosses into a ban, a timeout, or is still just a warning.

I originally wrote all three blocks slightly differently before realizing they really are the same shape with a different reason attached, which made we wish I had built a shared helper function sooner. Still on my list to clean up later.

```python
    await bot.process_commands(message)
```

This last line almost tripped me up early on. Once you define your own on_message, you are overriding the built in message handling discord.py normally does for you, which includes checking whether a message is a command. Without this exact line at the end, none of the ! commands would work at all, since the bot would never actually check for them.
