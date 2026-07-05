# main.py

This is the file you actually run: `python main.py`. It doesn't do much on its own — its whole job is to wake everything else up in the right order.

## What it does, step by step

1. Imports `bot` from `bot_instance.py` — the shared bot object everything else plugs into
2. Imports `TOKEN` from `config.py` — the secret key that lets the bot log into Discord
3. Imports `events` and `commands` — just importing these two modules is enough to register every `@bot.event` and `@bot.command` in them, since those decorators run the moment the file is loaded
4. Calls `bot.run(TOKEN)` — this actually connects to Discord and keeps the bot alive

## Why it's this short

All the real logic lives in other files. `main.py` exists purely to pull everything together in one place and start it up — think of it as flipping the light switch, not wiring the house.

## One thing to know

`bot.run(TOKEN)` is a blocking call — it doesn't return until the bot shuts down. Anything placed after it in the file would never actually run.
