# ui_help.py

The dropdown-based help menu behind `!setuphelp`.

## `HELP_CONTENT`
One dictionary holding every dropdown option — label, short description, and the longer detail text. Adding a new feature to the help menu means adding one new entry here; nothing else in the file needs to change.

## `build_menu_embed()` / `build_detail_embed(key)`
Two small functions that turn `HELP_CONTENT` into actual Discord embeds. The menu embed is always the same intro text. The detail embed looks up one specific entry by its dictionary key.

## `HelpMenuView` — the dropdown itself
Built using a **list comprehension** — a compact loop that turns every entry in `HELP_CONTENT` into a `discord.SelectOption` in one line, instead of manually writing out each option. This means the dropdown automatically has as many options as `HELP_CONTENT` has entries.

When someone picks an option, `select_callback` runs. It checks if that option is one of the mod-only entries (`mod_only_keys`) — if the person clicking isn't a mod, they get a private "mods only" message instead of seeing the detail.

## `HelpDetailView` — the Back button
Just one button. Since "Back" always returns to the exact same starting menu, this view doesn't need to remember any state — clicking it just rebuilds `build_menu_embed()` and `HelpMenuView()` fresh.

## Why both views use `timeout=None` + `custom_id`
Same reasoning as `ui_notify.py` — this menu is posted once and needs to keep working forever after, so it needs the same "permanent button" setup, registered in `on_ready`.
