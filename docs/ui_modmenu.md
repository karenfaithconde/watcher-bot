# ui_modmenu.py

Everything behind the `!m` command. This is the most complex file in the project, so here's the flow in order.

## The pieces

**`dm_target(target, text)`** — a small helper that tries to DM someone, and just quietly does nothing if their DMs are closed (instead of crashing).

**`ActionModal`** — the pop-up form used for Mute (asks for minutes) and Warn (asks for a reason). One class handles both, since they're nearly identical — the `action` passed in decides which label/placeholder text shows.

**`UnbanModal`** — a separate pop-up form asking for a username, since unbanning doesn't have a "target member" to work from (the person's not in the server anymore).

**`ConfirmActionView`** — the "Confirm / Cancel" step shown after picking an action. This exists so a misclick doesn't immediately mute or ban someone — there's always one more step to actually commit.

**`ModMenuView`** — the actual menu with 5 buttons (Mute, Warn, Clear, Ban, Unban), shown after running `!m`.

## How a click actually flows through the code

1. Mod runs `!m` as a reply → `ModMenuView` gets created and sent, targeting whoever was replied to
2. Mod clicks a button (say, "Mute") → `_start()` runs, which creates a `ConfirmActionView` and shows it privately
3. Mod clicks "Confirm" → if the action needs more info (mute/warn), it opens `ActionModal`; if not (clear/ban), it just executes right there
4. Filling out the modal and submitting runs `on_submit`, which actually applies the timeout/warning and DMs the target

## The permission check pattern

Almost every button handler starts with a check like:
```python
if interaction.user.id != self.moderator.id:
```
This makes sure only the mod who originally ran `!m` can click these buttons — not just anyone who happens to see the message.
