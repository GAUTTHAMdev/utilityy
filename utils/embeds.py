import discord
from datetime import datetime
from typing import Optional, List, Dict, Any, Union

class EmbedBuilder:
    """Builder class for creating Discord embeds with common patterns"""
    
    def __init__(self):
        self.embed = discord.Embed()
        self.embed.timestamp = datetime.utcnow()
    
    def title(self, title: str) -> 'EmbedBuilder':
        """Set embed title"""
        self.embed.title = title
        return self
    
    def description(self, description: str) -> 'EmbedBuilder':
        """Set embed description"""
        self.embed.description = description
        return self
    
    def color(self, color: Union[discord.Color, int]) -> 'EmbedBuilder':
        """Set embed color"""
        if isinstance(color, int):
            self.embed.color = discord.Color(color)
        else:
            self.embed.color = color
        return self
    
    def field(self, name: str, value: str, inline: bool = False) -> 'EmbedBuilder':
        """Add a field to the embed"""
        self.embed.add_field(name=name, value=value, inline=inline)
        return self
    
    def thumbnail(self, url: str) -> 'EmbedBuilder':
        """Set embed thumbnail"""
        self.embed.set_thumbnail(url=url)
        return self
    
    def image(self, url: str) -> 'EmbedBuilder':
        """Set embed image"""
        self.embed.set_image(url=url)
        return self
    
    def footer(self, text: str, icon_url: str = None) -> 'EmbedBuilder':
        """Set embed footer"""
        self.embed.set_footer(text=text, icon_url=icon_url)
        return self
    
    def author(self, name: str, url: str = None, icon_url: str = None) -> 'EmbedBuilder':
        """Set embed author"""
        self.embed.set_author(name=name, url=url, icon_url=icon_url)
        return self
    
    def timestamp(self, timestamp: datetime = None) -> 'EmbedBuilder':
        """Set embed timestamp"""
        self.embed.timestamp = timestamp or datetime.utcnow()
        return self
    
    def build(self) -> discord.Embed:
        """Build and return the embed"""
        # Add footer to every embed
        self.embed.set_footer(text="made by Gautham B | powered by SparkHub")
        return self.embed

# Common embed functions
def success_embed(title: str, description: str = None) -> discord.Embed:
    """Create a success embed"""
    return EmbedBuilder().title(f"✅ {title}").description(description).color(discord.Color.green()).build()

def error_embed(title: str, description: str = None) -> discord.Embed:
    """Create an error embed"""
    return EmbedBuilder().title(f"❌ {title}").description(description).color(discord.Color.red()).build()

def warning_embed(title: str, description: str = None) -> discord.Embed:
    """Create a warning embed"""
    return EmbedBuilder().title(f"⚠️ {title}").description(description).color(discord.Color.orange()).build()

def info_embed(title: str, description: str = None) -> discord.Embed:
    """Create an info embed"""
    return EmbedBuilder().title(f"ℹ️ {title}").description(description).color(discord.Color.blue()).build()

def loading_embed(title: str = "Loading...", description: str = None) -> discord.Embed:
    """Create a loading embed"""
    return EmbedBuilder().title(f"⏳ {title}").description(description).color(discord.Color.yellow()).build()

def user_embed(user: discord.Member, additional_fields: List[Dict[str, Any]] = None) -> discord.Embed:
    """Create a user info embed"""
    embed = EmbedBuilder().title(f"👤 {user}").color(user.color)
    
    if user.avatar:
        embed.thumbnail(user.avatar.url)
    elif user.default_avatar:
        embed.thumbnail(user.default_avatar.url)
    
    embed.field("ID", str(user.id), True)
    embed.field("Created", f"<t:{int(user.created_at.timestamp())}:F>", True)
    
    if hasattr(user, 'joined_at') and user.joined_at:
        embed.field("Joined", f"<t:{int(user.joined_at.timestamp())}:F>", True)
    
    embed.field("Status", str(user.status).title(), True)
    embed.field("Bot", "Yes" if user.bot else "No", True)
    
    if hasattr(user, 'premium_since') and user.premium_since:
        embed.field("Boosting Since", f"<t:{int(user.premium_since.timestamp())}:F>", True)
    
    if additional_fields:
        for field in additional_fields:
            embed.field(field.get('name', ''), field.get('value', ''), field.get('inline', False))
    
    return embed.build()

def guild_embed(guild: discord.Guild, additional_fields: List[Dict[str, Any]] = None) -> discord.Embed:
    """Create a guild info embed"""
    embed = EmbedBuilder().title(f"📊 {guild.name}").color(discord.Color.blue())
    
    if guild.icon:
        embed.thumbnail(guild.icon.url)
    
    embed.field("Owner", guild.owner.mention if guild.owner else "Unknown", True)
    embed.field("Created", f"<t:{int(guild.created_at.timestamp())}:F>", True)
    embed.field("Members", str(guild.member_count), True)
    embed.field("Channels", str(len(guild.channels)), True)
    embed.field("Roles", str(len(guild.roles)), True)
    embed.field("Emojis", str(len(guild.emojis)), True)
    embed.field("Boost Level", str(guild.premium_tier), True)
    embed.field("Boosts", str(guild.premium_subscription_count), True)
    embed.field("Verification Level", str(guild.verification_level).title(), True)
    
    if additional_fields:
        for field in additional_fields:
            embed.field(field.get('name', ''), field.get('value', ''), field.get('inline', False))
    
    return embed.build()

def channel_embed(channel: discord.TextChannel, additional_fields: List[Dict[str, Any]] = None) -> discord.Embed:
    """Create a channel info embed"""
    embed = EmbedBuilder().title(f"📝 #{channel.name}").color(discord.Color.blue())
    
    embed.field("ID", str(channel.id), True)
    embed.field("Created", f"<t:{int(channel.created_at.timestamp())}:F>", True)
    embed.field("Category", channel.category.name if channel.category else "None", True)
    embed.field("NSFW", "Yes" if channel.nsfw else "No", True)
    embed.field("Slowmode", f"{channel.slowmode_delay}s" if channel.slowmode_delay else "None", True)
    
    if channel.topic:
        embed.field("Topic", channel.topic, False)
    
    if additional_fields:
        for field in additional_fields:
            embed.field(field.get('name', ''), field.get('value', ''), field.get('inline', False))
    
    return embed.build()

def moderation_embed(action: str, user: discord.Member, moderator: discord.Member, reason: str = None) -> discord.Embed:
    """Create a moderation action embed"""
    embed = EmbedBuilder().title(f"🔨 {action}").color(discord.Color.red())
    
    embed.field("User", f"{user.mention} ({user})", True)
    embed.field("Moderator", f"{moderator.mention} ({moderator})", True)
    
    if reason:
        embed.field("Reason", reason, False)
    
    return embed.build()

def ticket_embed(ticket_id: int, category: str, user: discord.Member, status: str = "open") -> discord.Embed:
    """Create a ticket embed"""
    color = discord.Color.green() if status == "open" else discord.Color.red()
    
    embed = EmbedBuilder().title(f"🎫 Ticket #{ticket_id}").color(color)
    
    embed.field("Category", category, True)
    embed.field("User", f"{user.mention} ({user})", True)
    embed.field("Status", status.title(), True)
    
    return embed.build()

def poll_embed(question: str, author: discord.Member) -> discord.Embed:
    """Create a poll embed"""
    embed = EmbedBuilder().title("📊 Poll").description(question).color(discord.Color.blue())
    
    embed.footer(f"Poll by {author}", author.avatar.url if author.avatar else None)
    
    return embed.build()

def reminder_embed(message: str, created_at: datetime) -> discord.Embed:
    """Create a reminder embed"""
    embed = EmbedBuilder().title("⏰ Reminder").description(message).color(discord.Color.blue())
    
    embed.field("Set At", f"<t:{int(created_at.timestamp())}:F>", False)
    
    return embed.build()

def quote_embed(quote: str) -> discord.Embed:
    """Create a quote embed"""
    return EmbedBuilder().title("💭 Inspirational Quote").description(quote).color(discord.Color.blue()).build()

def calculation_embed(expression: str, result: str) -> discord.Embed:
    """Create a calculation embed"""
    embed = EmbedBuilder().title("🧮 Calculator").color(discord.Color.blue())
    
    embed.field("Expression", f"```{expression}```", False)
    embed.field("Result", f"```{result}```", False)
    
    return embed.build()

def url_shorten_embed(original_url: str, short_url: str) -> discord.Embed:
    """Create a URL shortening embed"""
    embed = EmbedBuilder().title("🔗 URL Shortened").color(discord.Color.blue())
    
    embed.field("Original", original_url, False)
    embed.field("Shortened", short_url, False)
    
    return embed.build()

def help_embed(title: str, description: str, commands: List[str] = None) -> discord.Embed:
    """Create a help embed"""
    embed = EmbedBuilder().title(title).description(description).color(discord.Color.blue())
    
    if commands:
        embed.field("Commands", "\n".join(commands), False)
    
    return embed.build()

def stats_embed(title: str, stats: Dict[str, Any]) -> discord.Embed:
    """Create a statistics embed"""
    embed = EmbedBuilder().title(title).color(discord.Color.blue())
    
    for key, value in stats.items():
        embed.field(key, str(value), True)
    
    return embed.build()

def uptime_embed(uptime_str: str) -> discord.Embed:
    """Create an uptime embed"""
    return EmbedBuilder().title("⏰ Bot Uptime").description(f"**{uptime_str}**").color(discord.Color.blue()).build()

def ping_embed(latency: float) -> discord.Embed:
    """Create a ping embed"""
    return EmbedBuilder().title("🏓 Pong!").description(f"Latency: {round(latency * 1000)}ms").color(discord.Color.blue()).build()

def avatar_embed(user: discord.Member) -> discord.Embed:
    """Create an avatar embed"""
    embed = EmbedBuilder().title(f"🖼️ {user}'s Avatar").color(user.color)
    
    avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
    embed.image(avatar_url)
    embed.field("Download", f"[Click here]({avatar_url})", False)
    
    return embed.build()

def icon_embed(guild: discord.Guild, icon_type: str = "icon") -> discord.Embed:
    """Create a server icon/banner embed"""
    embed = EmbedBuilder().title(f"🖼️ {guild.name}'s {icon_type.title()}").color(discord.Color.blue())
    
    if icon_type == "icon" and guild.icon:
        embed.image(guild.icon.url)
        embed.field("Download", f"[Click here]({guild.icon.url})", False)
    elif icon_type == "banner" and guild.banner:
        embed.image(guild.banner.url)
        embed.field("Download", f"[Click here]({guild.banner.url})", False)
    
    return embed.build()

def bot_info_embed(bot) -> discord.Embed:
    """Create a bot info embed"""
    embed = EmbedBuilder().title("🤖 Spark Utility Bot").description("Advanced Discord utility bot with ticketing system").color(discord.Color.blue())
    
    if bot.user.avatar:
        embed.thumbnail(bot.user.avatar.url)
    elif bot.user.default_avatar:
        embed.thumbnail(bot.user.default_avatar.url)
    
    embed.field("Bot ID", str(bot.user.id), True)
    embed.field("Created", f"<t:{int(bot.user.created_at.timestamp())}:F>", True)
    embed.field("Servers", str(len(bot.guilds)), True)
    embed.field("Users", str(len(bot.users)), True)
    embed.field("Commands", str(len(bot.commands)), True)
    embed.field("Latency", f"{round(bot.latency * 1000)}ms", True)
    
    uptime = datetime.utcnow() - bot.start_time
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    embed.field("Uptime", f"{days}d {hours}h {minutes}m {seconds}s", True)
    
    return embed.build()

def member_count_embed(guild: discord.Guild) -> discord.Embed:
    """Create a member count embed"""
    total = guild.member_count
    humans = sum(1 for member in guild.members if not member.bot)
    bots = total - humans
    
    embed = EmbedBuilder().title(f"👥 {guild.name} Members").color(discord.Color.blue())
    
    embed.field("Total", str(total), True)
    embed.field("Humans", str(humans), True)
    embed.field("Bots", str(bots), True)
    
    return embed.build()

def server_owner_embed(owner: discord.Member) -> discord.Embed:
    """Create a server owner embed"""
    embed = EmbedBuilder().title("👑 Server Owner").description(f"{owner.mention} ({owner})").color(discord.Color.gold())
    
    if owner.avatar:
        embed.thumbnail(owner.avatar.url)
    elif owner.default_avatar:
        embed.thumbnail(owner.default_avatar.url)
    
    embed.field("ID", str(owner.id), True)
    embed.field("Created", f"<t:{int(owner.created_at.timestamp())}:F>", True)
    
    return embed.build()

def invite_embed(invite_url: str) -> discord.Embed:
    """Create an invite embed"""
    embed = EmbedBuilder().title("🔗 Invite Spark Utility").description(f"[Click here to invite the bot]({invite_url})").color(discord.Color.blue())
    
    return embed.build()

def eight_ball_embed(question: str, answer: str) -> discord.Embed:
    """Create an 8-ball embed"""
    embed = EmbedBuilder().title("🎱 Magic 8-Ball").color(discord.Color.blue())
    
    embed.field("Question", question, False)
    embed.field("Answer", answer, False)
    
    return embed.build()

def choice_embed(choice: str) -> discord.Embed:
    """Create a random choice embed"""
    return EmbedBuilder().title("🎲 Random Choice").description(f"I choose: **{choice}**").color(discord.Color.blue()).build()

def afk_embed(user: discord.Member, reason: str, action: str = "set") -> discord.Embed:
    """Create an AFK embed"""
    if action == "set":
        embed = EmbedBuilder().title("💤 AFK Set").description(f"{user.mention} is now AFK: {reason}").color(discord.Color.yellow())
    else:
        embed = EmbedBuilder().title("👋 Welcome Back!").description(f"{user.mention} is no longer AFK").color(discord.Color.green())
    
    return embed.build()

def report_embed(report_id: int, reported_user: discord.Member, reason: str) -> discord.Embed:
    """Create a report embed"""
    embed = EmbedBuilder().title("📋 Report Submitted").description(f"Report #{report_id} has been submitted").color(discord.Color.orange())
    
    embed.field("Reported User", reported_user.mention, True)
    embed.field("Reason", reason, False)
    
    return embed.build()

def suggestion_embed(suggestion_id: int, suggestion: str) -> discord.Embed:
    """Create a suggestion embed"""
    embed = EmbedBuilder().title("💡 Suggestion Submitted").description(f"Suggestion #{suggestion_id} has been submitted").color(discord.Color.green())
    
    embed.field("Suggestion", suggestion, False)
    
    return embed.build()

def log_embed(title: str, description: str, color: discord.Color = discord.Color.blue()) -> discord.Embed:
    """Create a log embed"""
    return EmbedBuilder().title(title).description(description).color(color).build()

def error_log_embed(error: str, command: str = None, user: discord.Member = None) -> discord.Embed:
    """Create an error log embed"""
    embed = EmbedBuilder().title("🚨 Error Occurred").color(discord.Color.red())
    
    if command:
        embed.field("Command", f"`{command}`", True)
    
    if user:
        embed.field("User", f"{user} ({user.id})", True)
    
    embed.field("Error", f"```{error[:500]}```", False)
    
    return embed.build()

def startup_embed(bot) -> discord.Embed:
    """Create a startup embed"""
    embed = EmbedBuilder().title("🚀 Spark Utility Bot Online").description("Bot has successfully started and is ready to serve!").color(discord.Color.green())
    
    embed.field("Bot User", f"{bot.user} ({bot.user.id})", False)
    embed.field("Guilds", str(len(bot.guilds)), True)
    embed.field("Users", str(len(bot.users)), True)
    
    return embed.build()
