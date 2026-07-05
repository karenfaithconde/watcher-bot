# ui_profile.py

Backs the `!p` command — shows a member's account age, join date, roles, and a rough "risk" read.

## `calculate_risk(member)`
Adds up points based on a few legitimate, publicly-visible signals:
- Account under 7 days old → +2, under 30 days → +1
- Still using the default avatar → +1
- No roles beyond the automatic `@everyone` → +1
- Joined the server less than a day ago → +1

The total score maps to a label and a color (green/orange/red), returned together as one tuple: `return score, label, color`.

## `build_profile_embed(member)`
Calls `calculate_risk`, then builds an embed showing account creation date, join date, roles, and the risk assessment — using the color from `calculate_risk` to tint the whole embed.

## `ProfileLookupModal`
The pop-up form shown when `!p` is used with no reply. Takes a typed username/ID and searches the server's member list for a match — first by exact ID (most reliable), then by name/display name as a fallback.

## `ProfileLookupView`
Just the one button that opens `ProfileLookupModal`. Discord only allows pop-up forms (modals) to open from a button click or similar interaction — not directly from a typed `!` command — which is why this extra button step exists at all.

## An important limitation, on purpose
This file does **not** and cannot detect alt/multiple accounts — Discord's bot API simply doesn't expose that information to anyone, including server owners. Everything here is built only from data that's genuinely public and available, clearly labeled as a heuristic guess, not a determination.
