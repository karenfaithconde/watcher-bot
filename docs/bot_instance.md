# bot_instance.py

Honestly, this was one of the first things that confused me when I started splitting my bot into multiple files. If commands.py needs the bot, and events.py needs the bot, and main.py needs the bot... don't I need to create it three times?

Turns out, no. And once it clicked, it made a lot of sense.

## The problem I ran into

If every file made its own commands.Bot(...), I'd actually end up with multiple separate bots that have no idea about each other. events.py's bot wouldn't know about the commands registered in commands.py. It'd be like having three different phones and wondering why texting yourself doesn't work.

So instead, this tiny file has one job: create the bot once, and let every other file borrow it.

```python
from bot_instance import bot
```

That one line is doing a lot of quiet work. It's the reason events.py and commands.py can both attach things to the exact same bot, without ever needing to talk to each other directly.

## Walking through the code

```python
import discord
from discord.ext import commands
```
These are the two building blocks. discord is the main library: embeds, buttons, all the Discord specific stuff. commands is a smaller toolkit inside discord.py made specifically for handling typed commands like !m or !purge. I didn't realize at first these were two separate imports for a reason. commands is really its own mini framework built on top of the base library.

```python
intents = discord.Intents.default()
```
This part surprised me. Discord makes bots explicitly ask for permission to see certain kinds of data, even before a server owner adds them. Intents.default() is just the normal starting pack, the basic stuff every bot gets without asking.

```python
intents.message_content = True
```
This one is NOT included by default, and I learned that the hard way. Without this, message.content comes back empty, which quietly broke my profanity filter, spam checker, and link scanner all at once, since all three need to actually read what people typed.

```python
intents.members = True
```
Also opt in only. This is what lets the bot see the full member list and get notified when someone joins or leaves. Without it, my welcome and leave messages just never would have fired, and !p wouldn't be able to search for someone by name.

```python
bot = commands.Bot(command_prefix="!", intents=intents)
```
And here's the actual bot, the one single object that main.py, events.py, and commands.py all end up sharing. command_prefix="!" is what tells it "hey, if a message starts with this symbol, check if it's a command." The intents=intents part hands over everything configured just above.

## One thing worth remembering

This file never actually calls bot.run(). It just builds the bot and stops there. Starting it for real happens in main.py, after every other file has had a chance to attach its commands and events onto this same object first.
