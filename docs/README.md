# Watcher — Code Docs

This folder explains how each file in the bot actually works — what it's responsible for, how its pieces fit together, and why certain things are built the way they are. The code itself stays short and to the point; the "why" and "how" live here instead.

Each file below matches one `.py` file in the main project.

| File | What it covers |
|---|---|
| [main.md](main.md) | The entry point — what runs when you start the bot |
| [bot_instance.md](bot_instance.md) | The shared bot object every other file plugs into |
| [config.md](config.md) | Where settings/secrets come from, and what each one controls |
| [filters.md](filters.md) | The profanity, spam, and dangerous-link detection logic |
| [warnings_store.md](warnings_store.md) | How warning counts get saved and loaded so they survive a restart |
| [events.md](events.md) | Everything the bot does automatically — joins, messages, leaves |
| [commands.md](commands.md) | Every command someone has to type, like `!m` and `!purge` |
| [ui_notify.md](ui_notify.md) | The join-ping toggle button |
| [ui_modmenu.md](ui_modmenu.md) | The full mute/warn/clear/ban/unban menu behind `!m` |
| [ui_help.md](ui_help.md) | The dropdown help menu behind `!setuphelp` |
| [ui_profile.md](ui_profile.md) | The account risk check behind `!p` |

## Reading order, if you're new to the codebase

If you're trying to understand the whole project rather than just one piece, this order tends to make the most sense:

1. `main.md` and `bot_instance.md` — how the bot actually starts
2. `config.md` — what settings exist and where they come from
3. `filters.md` and `warnings_store.md` — the core detection and data logic, with no Discord UI involved yet
4. `events.md` — how detection turns into an actual action (delete, warn, timeout, ban)
5. `commands.md` — everything a person can type
6. The `ui_*.md` files — the buttons, menus, and pop-up forms tied to those commands
