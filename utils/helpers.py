import discord
import re
import asyncio
from datetime import datetime, timedelta
from typing import Union, Optional, List

def parse_time(time_str: str) -> Optional[timedelta]:
    """Parse time string into timedelta object"""
    try:
        time_regex = re.compile(r'(\d+)([dhms])')
        matches = time_regex.findall(time_str.lower())
        
        if not matches:
            return None
        
        total_seconds = 0
        for amount, unit in matches:
            amount = int(amount)
            if unit == 's':
                total_seconds += amount
            elif unit == 'm':
                total_seconds += amount * 60
            elif unit == 'h':
                total_seconds += amount * 3600
            elif unit == 'd':
                total_seconds += amount * 86400
        
        return timedelta(seconds=total_seconds)
    except:
        return None

def format_time(seconds: int) -> str:
    """Format seconds into human readable time"""
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds:
        parts.append(f"{seconds}s")
    
    return " ".join(parts) if parts else "0s"

async def safe_send(channel: discord.abc.Messageable, content: str = None, **kwargs) -> Optional[discord.Message]:
    """Safely send a message to a channel"""
    try:
        return await channel.send(content, **kwargs)
    except discord.Forbidden:
        print(f"Missing permissions to send message to {channel}")
        return None
    except discord.NotFound:
        print(f"Channel {channel} not found")
        return None
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

async def safe_delete(message: discord.Message) -> bool:
    """Safely delete a message"""
    try:
        await message.delete()
        return True
    except discord.Forbidden:
        print(f"Missing permissions to delete message {message.id}")
        return False
    except discord.NotFound:
        print(f"Message {message.id} not found")
        return False
    except Exception as e:
        print(f"Error deleting message: {e}")
        return False

def get_member_from_string(guild: discord.Guild, user_str: str) -> Optional[discord.Member]:
    """Get member from string (ID, mention, or username)"""
    # Try ID first
    if user_str.isdigit():
        return guild.get_member(int(user_str))
    
    # Try mention
    if user_str.startswith('<@') and user_str.endswith('>'):
        user_id = re.sub(r'[<@!>]', '', user_str)
        if user_id.isdigit():
            return guild.get_member(int(user_id))
    
    # Try username
    member = discord.utils.get(guild.members, name=user_str)
    if member:
        return member
    
    # Try display name
    member = discord.utils.get(guild.members, display_name=user_str)
    if member:
        return member
    
    return None

def get_role_from_string(guild: discord.Guild, role_str: str) -> Optional[discord.Role]:
    """Get role from string (ID, mention, or name)"""
    # Try ID first
    if role_str.isdigit():
        return guild.get_role(int(role_str))
    
    # Try mention
    if role_str.startswith('<@&') and role_str.endswith('>'):
        role_id = re.sub(r'[<@&>]', '', role_str)
        if role_id.isdigit():
            return guild.get_role(int(role_id))
    
    # Try name
    role = discord.utils.get(guild.roles, name=role_str)
    if role:
        return role
    
    return None

def get_channel_from_string(guild: discord.Guild, channel_str: str) -> Optional[discord.TextChannel]:
    """Get channel from string (ID, mention, or name)"""
    # Try ID first
    if channel_str.isdigit():
        channel = guild.get_channel(int(channel_str))
        if isinstance(channel, discord.TextChannel):
            return channel
    
    # Try mention
    if channel_str.startswith('<#') and channel_str.endswith('>'):
        channel_id = re.sub(r'[<#>]', '', channel_str)
        if channel_id.isdigit():
            channel = guild.get_channel(int(channel_id))
            if isinstance(channel, discord.TextChannel):
                return channel
    
    # Try name
    channel = discord.utils.get(guild.text_channels, name=channel_str)
    if channel:
        return channel
    
    return None

def truncate_text(text: str, max_length: int = 2000) -> str:
    """Truncate text to fit Discord's character limits"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."

def format_permissions(permissions: discord.Permissions) -> List[str]:
    """Format permissions into a readable list"""
    perm_list = []
    
    if permissions.administrator:
        perm_list.append("Administrator")
    else:
        perm_mapping = {
            'manage_guild': 'Manage Server',
            'manage_channels': 'Manage Channels',
            'manage_roles': 'Manage Roles',
            'manage_messages': 'Manage Messages',
            'manage_webhooks': 'Manage Webhooks',
            'manage_nicknames': 'Manage Nicknames',
            'manage_emojis': 'Manage Emojis',
            'ban_members': 'Ban Members',
            'kick_members': 'Kick Members',
            'moderate_members': 'Moderate Members',
            'view_audit_log': 'View Audit Log',
            'priority_speaker': 'Priority Speaker',
            'stream': 'Stream',
            'connect': 'Connect',
            'speak': 'Speak',
            'mute_members': 'Mute Members',
            'deafen_members': 'Deafen Members',
            'move_members': 'Move Members',
            'use_voice_activation': 'Use Voice Activity',
            'change_nickname': 'Change Nickname',
            'create_instant_invite': 'Create Invite',
            'add_reactions': 'Add Reactions',
            'view_channel': 'View Channels',
            'send_messages': 'Send Messages',
            'send_tts_messages': 'Send TTS Messages',
            'embed_links': 'Embed Links',
            'attach_files': 'Attach Files',
            'read_message_history': 'Read Message History',
            'mention_everyone': 'Mention Everyone',
            'use_external_emojis': 'Use External Emojis',
            'use_slash_commands': 'Use Slash Commands',
            'use_external_stickers': 'Use External Stickers'
        }
        
        for perm, value in permissions:
            if value and perm in perm_mapping:
                perm_list.append(perm_mapping[perm])
    
    return perm_list

async def confirm_action(ctx, message: str, timeout: int = 30) -> bool:
    """Ask for confirmation before proceeding with an action"""
    embed = discord.Embed(
        title="⚠️ Confirmation Required",
        description=message,
        color=discord.Color.orange()
    )
    
    embed.add_field(
        name="Actions",
        value="React with ✅ to confirm or ❌ to cancel",
        inline=False
    )
    
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")
    
    def check(reaction, user):
        return (
            user == ctx.author and
            str(reaction.emoji) in ["✅", "❌"] and
            reaction.message.id == msg.id
        )
    
    try:
        reaction, user = await ctx.bot.wait_for('reaction_add', timeout=timeout, check=check)
        await msg.delete()
        return str(reaction.emoji) == "✅"
    except asyncio.TimeoutError:
        await msg.delete()
        await ctx.send("❌ Confirmation timed out.", delete_after=5)
        return False

def create_progress_bar(current: int, total: int, length: int = 20) -> str:
    """Create a progress bar string"""
    if total == 0:
        return "█" * length
    
    filled = int(length * current / total)
    bar = "█" * filled + "░" * (length - filled)
    percentage = round(100 * current / total, 1)
    
    return f"{bar} {percentage}%"

def format_bytes(bytes_count: int) -> str:
    """Format bytes into human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f}{unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f}PB"

def escape_markdown(text: str) -> str:
    """Escape Discord markdown characters"""
    markdown_chars = ['*', '_', '`', '~', '|', '\\']
    for char in markdown_chars:
        text = text.replace(char, f'\\{char}')
    return text

async def paginate_embeds(ctx, embeds: List[discord.Embed], timeout: int = 60):
    """Paginate through multiple embeds"""
    if not embeds:
        return
    
    if len(embeds) == 1:
        await ctx.send(embed=embeds[0])
        return
    
    current_page = 0
    message = await ctx.send(embed=embeds[current_page])
    
    # Add reactions
    await message.add_reaction("⬅️")
    await message.add_reaction("➡️")
    await message.add_reaction("❌")
    
    def check(reaction, user):
        return (
            user == ctx.author and
            str(reaction.emoji) in ["⬅️", "➡️", "❌"] and
            reaction.message.id == message.id
        )
    
    while True:
        try:
            reaction, user = await ctx.bot.wait_for('reaction_add', timeout=timeout, check=check)
            
            if str(reaction.emoji) == "⬅️":
                current_page = (current_page - 1) % len(embeds)
            elif str(reaction.emoji) == "➡️":
                current_page = (current_page + 1) % len(embeds)
            elif str(reaction.emoji) == "❌":
                await message.delete()
                return
            
            await message.edit(embed=embeds[current_page])
            await message.remove_reaction(reaction, user)
            
        except asyncio.TimeoutError:
            await message.clear_reactions()
            return
