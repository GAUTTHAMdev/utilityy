import discord
from discord.ext import commands
import asyncio
from datetime import datetime
from typing import Optional, Union
from utils.embeds import *
from utils.helpers import *

class Moderation(commands.Cog):
    """Moderation commands for server management"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_before_invoke(self, ctx):
        """Log command before execution"""
        logging_cog = self.bot.get_cog('LoggingSystem')
        if logging_cog:
            args = ' '.join(str(arg) for arg in ctx.args[2:]) if len(ctx.args) > 2 else ""
            await logging_cog.log_command(ctx, ctx.command.name, args)

    @commands.command(name='clear', aliases=['purge'])
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, amount: int = 10):
        """Clear messages in the current channel"""
        if amount <= 0:
            await ctx.send(embed=error_embed("Invalid Amount", "Amount must be greater than 0"))
            return

        if amount > 100:
            await ctx.send(embed=error_embed("Amount Too Large", "Cannot clear more than 100 messages at once"))
            return

        try:
            # Delete the command message first
            await ctx.message.delete()

            # Delete the specified number of messages
            deleted = await ctx.channel.purge(limit=amount)

            # Send confirmation message
            embed = success_embed("Messages Cleared", f"Successfully cleared {len(deleted)} messages")
            confirmation = await ctx.send(embed=embed)

            # Delete confirmation after 5 seconds
            await asyncio.sleep(5)
            await confirmation.delete()

        except discord.Forbidden:
            await ctx.send(embed=error_embed("Missing Permissions", "I don't have permission to delete messages"))
        except Exception as e:
            await ctx.send(embed=error_embed("Error", f"Failed to clear messages: {str(e)}"))

    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban_user(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Ban a user from the server"""
        if member == ctx.author:
            await ctx.send(embed=error_embed("Cannot Ban Self", "You cannot ban yourself"))
            return

        if member == ctx.guild.owner:
            await ctx.send(embed=error_embed("Cannot Ban Owner", "You cannot ban the server owner"))
            return

        if member.top_role >= ctx.author.top_role:
            await ctx.send(embed=error_embed("Insufficient Permissions", "You cannot ban someone with a higher or equal role"))
            return

        if member.top_role >= ctx.guild.me.top_role:
            await ctx.send(embed=error_embed("Bot Insufficient Permissions", "I cannot ban someone with a higher or equal role"))
            return

        try:
            # Send DM to user before banning
            try:
                dm_embed = moderation_embed("Banned", member, ctx.author, reason)
                dm_embed.add_field(name="Server", value=ctx.guild.name, inline=False)
                await member.send(embed=dm_embed)
            except:
                pass  # User has DMs disabled

            # Ban the user
            await member.ban(reason=f"Banned by {ctx.author} | {reason}")

            # Send confirmation
            embed = moderation_embed("User Banned", member, ctx.author, reason)
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send(embed=error_embed("Missing Permissions", "I don't have permission to ban this user"))
        except Exception as e:
            await ctx.send(embed=error_embed("Error", f"Failed to ban user: {str(e)}"))

    @commands.command(name='unban')
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban_user(self, ctx, user: Union[discord.User, str], *, reason: str = "No reason provided"):
        """Unban a user from the server"""
        if isinstance(user, str):
            # Try to find the user by ID or username
            try:
                if user.isdigit():
                    user = await self.bot.fetch_user(int(user))
                else:
                    # Search through ban list
                    bans = [ban async for ban in ctx.guild.bans()]
                    for ban in bans:
                        if ban.user.name.lower() == user.lower():
                            user = ban.user
                            break
                    else:
                        await ctx.send(embed=error_embed("User Not Found", "Could not find a banned user with that name"))
                        return
            except:
                await ctx.send(embed=error_embed("User Not Found", "Could not find the specified user"))
                return

        try:
            # Check if user is actually banned
            try:
                await ctx.guild.fetch_ban(user)
            except discord.NotFound:
                await ctx.send(embed=error_embed("User Not Banned", "This user is not banned"))
                return

            # Unban the user
            await ctx.guild.unban(user, reason=f"Unbanned by {ctx.author} | {reason}")

            # Send confirmation
            embed = success_embed("User Unbanned", f"Successfully unbanned {user}")
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send(embed=error_embed("Missing Permissions", "I don't have permission to unban users"))
        except Exception as e:
            await ctx.send(embed=error_embed("Error", f"Failed to unban user: {str(e)}"))

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick_user(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Kick a user from the server"""
        if member == ctx.author:
            await ctx.send(embed=error_embed("Cannot Kick Self", "You cannot kick yourself"))
            return

        if member == ctx.guild.owner:
            await ctx.send(embed=error_embed("Cannot Kick Owner", "You cannot kick the server owner"))
            return

        if member.top_role >= ctx.author.top_role:
            await ctx.send(embed=error_embed("Insufficient Permissions", "You cannot kick someone with a higher or equal role"))
            return

        if member.top_role >= ctx.guild.me.top_role:
            await ctx.send(embed=error_embed("Bot Insufficient Permissions", "I cannot kick someone with a higher or equal role"))
            return

        try:
            # Send DM to user before kicking
            try:
                dm_embed = moderation_embed("Kicked", member, ctx.author, reason)
                dm_embed.add_field(name="Server", value=ctx.guild.name, inline=False)
                await member.send(embed=dm_embed)
            except:
                pass  # User has DMs disabled

            # Kick the user
            await member.kick(reason=f"Kicked by {ctx.author} | {reason}")

            # Send confirmation
            embed = moderation_embed("User Kicked", member, ctx.author, reason)
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send(embed=error_embed("Missing Permissions", "I don't have permission to kick this user"))
        except Exception as e:
            await ctx.send(embed=error_embed("Error", f"Failed to kick user: {str(e)}"))

    @commands.command(name='slowmode')
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int = 0):
        """Set slowmode for the current channel"""
        if seconds < 0:
            await ctx.send(embed=error_embed("Invalid Duration", "Slowmode duration cannot be negative"))
            return

        if seconds > 21600:  # 6 hours max
            await ctx.send(embed=error_embed("Duration Too Long", "Slowmode duration cannot exceed 6 hours (21600 seconds)"))
            return

        try:
            await ctx.channel.edit(slowmode_delay=seconds)

            if seconds == 0:
                embed = success_embed("Slowmode Disabled", "Slowmode has been disabled for this channel")
            else:
                embed = success_embed("Slowmode Set", f"Slowmode set to {seconds} seconds for this channel")

            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send(embed=error_embed("Missing Permissions", "I don't have permission to manage this channel"))
        except Exception as e:
            await ctx.send(embed=error_embed("Error", f"Failed to set slowmode: {str(e)}"))

    @commands.command(name='timeout', aliases=['mute'])
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def timeout_user(self, ctx, member: discord.Member, duration: str, *, reason: str = "No reason provided"):
        """Timeout a user for a specified duration"""
        if member == ctx.author:
            await ctx.send(embed=error_embed("Cannot Timeout Self", "You cannot timeout yourself"))
            return

        if member == ctx.guild.owner:
            await ctx.send(embed=error_embed("Cannot Timeout Owner", "You cannot timeout the server owner"))
            return

        if member.top_role >= ctx.author.top_role:
            await ctx.send(embed=error_embed("Insufficient Permissions", "You cannot timeout someone with a higher or equal role"))
            return

        if member.top_role >= ctx.guild.me.top_role:
            await ctx.send(embed=error_embed("Bot Insufficient Permissions", "I cannot timeout someone with a higher or equal role"))
            return

        # Parse duration
        duration_delta = parse_time(duration)
        if not duration_delta:
            await ctx.send(embed=error_embed("Invalid Duration", "Duration format: 1h30m, 2d, 45s, etc."))
            return

        if duration_delta.total_seconds() > 2419200:  # 28 days max
            await ctx.send(embed=error_embed("Duration Too Long", "Timeout duration cannot exceed 28 days"))
            return

        try:
            # Calculate timeout end time
            timeout_until = datetime.utcnow() + duration_delta

            # Apply timeout
            await member.timeout(timeout_until, reason=f"Timed out by {ctx.author} | {reason}")

            # Send confirmation
            embed = moderation_embed("User Timed Out", member, ctx.author, reason)
            embed.add_field(name="Duration", value=duration, inline=True)
            embed.add_field(name="Until", value=f"<t:{int(timeout_until.timestamp())}:F>", inline=True)
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send(embed=error_embed("Missing Permissions", "I don't have permission to timeout this user"))
        except Exception as e:
            await ctx.send(embed=error_embed("Error", f"Failed to timeout user: {str(e)}"))

    @commands.command(name='untimeout', aliases=['unmute'])
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def untimeout_user(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Remove timeout from a user"""
        if not member.is_timed_out():
            await ctx.send(embed=error_embed("User Not Timed Out", "This user is not currently timed out"))
            return

        try:
            # Remove timeout
            await member.timeout(None, reason=f"Timeout removed by {ctx.author} | {reason}")

            # Send confirmation
            embed = success_embed("Timeout Removed", f"Timeout removed from {member.mention}")
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send(embed=error_embed("Missing Permissions", "I don't have permission to remove timeouts"))
        except Exception as e:
            await ctx.send(embed=error_embed("Error", f"Failed to remove timeout: {str(e)}"))

    @commands.command(name='warn')
    @commands.has_permissions(manage_messages=True)
    async def warn_user(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Warn a user"""
        if member == ctx.author:
            await ctx.send(embed=error_embed("Cannot Warn Self", "You cannot warn yourself"))
            return

        if member == ctx.guild.owner:
            await ctx.send(embed=error_embed("Cannot Warn Owner", "You cannot warn the server owner"))
            return

        try:
            # Send DM to user
            try:
                dm_embed = warning_embed("Warning", f"You have been warned in {ctx.guild.name}")
                dm_embed.add_field(name="Moderator", value=str(ctx.author), inline=True)
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                await member.send(embed=dm_embed)
            except:
                pass  # User has DMs disabled

            # Send confirmation
            embed = warning_embed("User Warned", f"{member.mention} has been warned")
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(embed=error_embed("Error", f"Failed to warn user: {str(e)}"))

async def setup(bot):
    await bot.add_cog(Moderation(bot))