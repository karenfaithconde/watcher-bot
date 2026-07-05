import discord


def calculate_risk(member: discord.Member):
    # adds up a few warning signs, higher score = more suspicious
    score = 0
    now = discord.utils.utcnow()

    account_age_days = (now - member.created_at).days
    if account_age_days < 7:
        score += 2
    elif account_age_days < 30:
        score += 1

    if member.avatar is None:  # never set a profile picture
        score += 1

    if len(member.roles) <= 1:  # has no roles at all
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


def build_profile_embed(member: discord.Member):
    now = discord.utils.utcnow()
    score, label, color = calculate_risk(member)

    account_age_days = (now - member.created_at).days
    created_str = member.created_at.strftime("%b %d, %Y")

    embed = discord.Embed(title=str(member), color=color)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="Account created", value=f"{created_str} ({account_age_days} days ago)", inline=False)

    if member.joined_at:
        join_age_days = (now - member.joined_at).days
        joined_str = member.joined_at.strftime("%b %d, %Y")
        embed.add_field(name="Joined server", value=f"{joined_str} ({join_age_days} days ago)", inline=False)

    roles = [r.mention for r in member.roles if r.name != "@everyone"]
    embed.add_field(name="Roles", value=", ".join(roles) if roles else "None", inline=False)
    embed.add_field(name="Assessment", value=f"{label} ({score} points)", inline=False)
    embed.set_footer(text="Just a guess based on public info, not proof of anything.")

    return embed


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

        if target is None:
            await interaction.response.send_message("Couldn't find that member.", ephemeral=True)
            return

        if target.bot:
            await interaction.response.send_message("Can't check a bot.", ephemeral=True)
            return

        await interaction.response.send_message(embed=build_profile_embed(target), ephemeral=True)


class ProfileLookupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Check a Profile", style=discord.ButtonStyle.blurple)
    async def check_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("Mods only.", ephemeral=True)
            return
        await interaction.response.send_modal(ProfileLookupModal())