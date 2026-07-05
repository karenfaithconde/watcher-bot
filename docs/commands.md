# commands.py

This file holds everything a person has to **type** to trigger — as opposed to `events.py`, which runs automatically.

## `!p` — profile check
If used as a reply to someone's message, shows that person's profile immediately. If typed alone, posts a button that opens a pop-up form asking for a username. Requires `manage_messages` permission.

## `!setuphelp`
Posts the permanent dropdown help menu (from `ui_help.py`). Meant to be run exactly once.

## `!setupnotify`
Posts the permanent join-ping toggle button (from `ui_notify.py`). Also meant to be run once.

## `!m` — the mod menu
Only works as a reply to a message. Builds an embed showing the target's current warning count, attaches the 5-button `ModMenuView` (from `ui_modmenu.py`), and sends it. Requires `manage_messages` permission.

## `!purge` (aliases: `!clear`, `!clean`)
Deletes the last `<amount>` messages in the channel, plus the command message itself. Requires both the command's author *and* the bot itself to have `manage_messages` permission — that second check (`bot_has_permissions`) prevents a confusing silent failure if the bot's role doesn't have the right permission.

## Why this file stays simple

Notice this file barely contains any real logic — it mostly just builds an embed and hands off to a `View` class from one of the `ui_*.py` files. Keeping the "what button does what" logic inside those UI files, and the "which command triggers what" logic here, keeps each file focused on one job.
