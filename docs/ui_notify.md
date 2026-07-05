# ui_notify.py

The smallest UI file — just one button, the "Toggle Join Pings" button members click to opt in or out of being pinged when someone new joins.

## Why it needs to be "persistent"

Normally, Discord buttons only work for a limited time after being created — great for something temporary like a confirmation prompt, bad for a button that's supposed to work forever after being posted once via `!setupnotify`.

Three things make this button permanent:

1. **`timeout=None`** in `__init__` — tells Discord this view never expires on its own
2. **`custom_id="notify_button"`** — gives the button a fixed identifier Discord can recognize even after the bot restarts
3. **`bot.add_view(NotifyButton())`** in `on_ready` (in `events.py`) — tells the bot, every time it starts up, "remember that this `custom_id` belongs to this button's code"

Without all three together, the button would stop responding the next time the bot restarts.

## What happens when it's clicked

Checks if the person already has the Notify role. If yes, removes it and tells them privately ("ephemeral" — only they see the reply). If no, adds it and confirms the same way.
