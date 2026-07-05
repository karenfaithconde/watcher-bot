# events.py

This file holds everything the bot does **automatically**, without anyone typing a command. Each function is named after the Discord "event" it responds to — Discord calls these functions itself, at the right moment.

## `on_ready()`
Runs once, right when the bot successfully logs in. Prints a couple of status lines to your console, and re-registers the persistent buttons/dropdowns (`NotifyButton`, `HelpMenuView`, `HelpDetailView`) so they keep working even after a restart.

## `on_guild_join(guild)`
Runs the moment the bot joins a new server. Looks for the first text channel it has permission to post in, and sends a short message pointing to `!setuphelp` and `!setupnotify`.

## `on_member_join(member)` / `on_member_remove(member)`
Post a welcome embed when someone joins, and a short "someone left" embed when they go — both to your configured welcome channel.

## `on_message(message)` — the big one
Runs on **every single message** sent in the server. It checks, in order:

1. **Profanity** (`is_flagged`) — if true, delete the message, add a warning
2. **Dangerous links** (`is_dangerous_link`) — only checked if profanity didn't already trigger
3. **Spam** (`is_spamming`) — only checked if neither of the above triggered

Using `elif` instead of separate `if` statements means a single message only ever gets flagged for **one** reason, even if it happens to trigger multiple checks.

For whichever one triggers, the same pattern repeats: delete the message, bump that user's warning count, log it to your mod-log channel as an embed, then check the count against `BAN_AT` and `TIMEOUT_AT` from `config.py` to decide whether to ban, timeout, or just warn.

The very last line, `await bot.process_commands(message)`, is critical — without it, none of your `!` commands (`!m`, `!purge`, etc.) would work, since defining `on_message` yourself overrides Discord's default command-processing behavior unless you explicitly call this.
