# ui_profile.py

This is the file behind !p, and it is probably the one I am proudest of, since it started as just a question I was not sure I could even answer. Can a bot tell if an account looks suspicious. Turns out, sort of, but only using information that is genuinely public.

## calculate_risk, the scoring logic

```python
def calculate_risk(member: discord.Member):
    score = 0
    now = discord.utils.utcnow()

    account_age_days = (now - member.created_at).days
    if account_age_days < 7:
        score += 2
    elif account_age_days < 30:
        score += 1

    if member.avatar is None:
        score += 1

    if len(member.roles) <= 1:
        score += 1

    if member.joined_at:
        join_age_days = (now - member.joined_at).days
        if join_age_days < 1:
            score += 1

    if score >= 4:
        return score, "Looks suspicious, worth checking", discord.Color.red()
    elif score >= 2:
        return score, "A little new/unusual", discord.Color.orange()
    else:
        return score, "Looks normal", discord.Color.green()
```

This function is just adding up points based on a handful of signals that, on their own, do not prove anything, but together start to paint a picture. A brand new account adds points. Never setting a profile picture adds a point. Having no roles at all adds a point. Joining the server less than a day ago adds a point.

I want to be honest about what this is not. This is not detecting alt accounts, and it cannot, since Discord genuinely does not give bots access to that kind of information. This is just pattern matching against things spam accounts commonly have in common, nothing more certain than that.

The very last part returns three separate values at once, the numeric score, a short label, and a color. I did not realize at first that Python lets you return multiple things like this in one line, and unpack them just as easily wherever the function gets called.

## build_profile_embed, turning the score into something visible

```python
def build_profile_embed(member: discord.Member):
    now = discord.utils.utcnow()
    score, label, color = calculate_risk(member)
    ...
    embed = discord.Embed(title=str(member), color=color)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="Account created", value=f"{created_str} ({account_age_days} days ago)", inline=False)
    ...
    embed.add_field(name="Assessment", value=f"{label} ({score} points)", inline=False)
    embed.set_footer(text="Just a guess based on public info, not proof of anything.")
    return embed
```

score, label, color = calculate_risk(member) is unpacking those three values from the function above into three separate variables in one line. From there, this function just lays everything out, account age, join date, roles, and the final assessment, using the color to tint the whole embed red, orange, or green depending on how many signals came up.

That footer line at the bottom was important to me to include on purpose. I do not want anyone treating this as more certain than it actually is.

## ProfileLookupModal, the search form

```python
class ProfileLookupModal(discord.ui.Modal, title="Check a member's profile"):
    identifier = discord.ui.TextInput(
        label="Username, display name, or user ID",
        placeholder="e.g. SomePerson or 123456789012345678",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        query = self.identifier.value
        guild = interaction.guild
        target = None

        if query.isdigit():
            target = guild.get_member(int(query))

        if target is None:
            query_lower = query.lower()
            for m in guild.members:
                if m.name.lower() == query_lower or m.display_name.lower() == query_lower:
                    target = m
                    break
        ...
```

This only shows up when !p is typed with no reply attached, since at that point there is no obvious target yet. It tries the most reliable method first, checking if what was typed is a plain number and treating it as a user id. If that does not find anyone, it falls back to looping through every member in the server and comparing names, which is slower but works for people who do not have the id handy.

## ProfileLookupView, the one button that starts it all

```python
class ProfileLookupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Check a Profile", style=discord.ButtonStyle.blurple)
    async def check_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("Mods only.", ephemeral=True)
            return
        await interaction.response.send_modal(ProfileLookupModal())
```

This one exists purely because of a rule I did not know about until I hit it directly. Discord will not let a modal, meaning a pop up form, open straight from someone typing a command. It has to open from an interaction like a button click instead. So this small button is really just a required middle step between typing !p and actually seeing the lookup form pop up.
