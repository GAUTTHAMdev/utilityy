import discord
from discord.ext import commands
import os
import traceback
from datetime import datetime
from typing import Optional

class LoggingSystem(commands.Cog):
    """Comprehensive logging system for the bot"""

    def __init__(self, bot):
        self.bot = bot
        self.owner_id = int(os.getenv('OWNER_ID', 0))

    async def get_log_channel(self, guild_id: int) -> Optional[discord.TextChannel]:
        """Get the log channel for a guild"""
        try:
            settings = await self.bot.db.get_guild_settings(guild_id)
            if settings and settings.get('log_channel_id'):
                channel = self.bot.get_channel(settings['log_channel_id'])
                return channel
        except Exception as e:
            print(f"Error getting log channel: {e}")
        return None

    async def log_command(self, ctx, command_name: str, args: str = "", success: bool = True, error: str = ""):
        """Log a command execution"""
        try:
            embed = discord.Embed(
                title="📝 Command Executed" if success else "❌ Command Failed",
                color=discord.Color.green() if success else discord.Color.red(),
                timestamp=datetime.utcnow()
            )

            # Command info
            embed.add_field(
                name="Command",
                value=f"`{command_name}`",
                inline=True
            )

            # User info
            embed.add_field(
                name="User",
                value=f"{ctx.author} ({ctx.author.id})",
                inline=True
            )

            # Server info
            embed.add_field(
                name="Server",
                value=f"{ctx.guild.name} ({ctx.guild.id})" if ctx.guild else "DM",
                inline=True
            )

            # Channel info
            embed.add_field(
                name="Channel",
                value=f"{ctx.channel.name} ({ctx.channel.id})" if hasattr(ctx.channel, 'name') else f"DM ({ctx.channel.id})",
                inline=True
            )

            # Arguments
            if args:
                embed.add_field(
                    name="Arguments",
                    value=f"```{args}```",
                    inline=False
                )

            # Error details
            if error:
                embed.add_field(
                    name="Error Details",
                    value=f"```{error[:1000]}```",
                    inline=False
                )

            # Send to owner
            await self.send_to_owner(embed)

            # Send to log channel if configured
            if ctx.guild:
                log_channel = await self.get_log_channel(ctx.guild.id)
                if log_channel:
                    try:
                        await log_channel.send(embed=embed)
                    except Exception as e:
                        print(f"Error sending to log channel: {e}")

        except Exception as e:
            print(f"Error in log_command: {e}")
            traceback.print_exc()

    async def log_action(self, action: str, guild: discord.Guild = None, user: discord.User = None, 
                        channel: discord.TextChannel = None, details: str = "", success: bool = True):
        """Log a bot action"""
        try:
            embed = discord.Embed(
                title="🔧 Bot Action" if success else "❌ Action Failed",
                color=discord.Color.blue() if success else discord.Color.red(),
                timestamp=datetime.utcnow()
            )

            embed.add_field(
                name="Action",
                value=f"`{action}`",
                inline=True
            )

            if user:
                embed.add_field(
                    name="User",
                    value=f"{user} ({user.id})",
                    inline=True
                )

            if guild:
                embed.add_field(
                    name="Server",
                    value=f"{guild.name} ({guild.id})",
                    inline=True
                )

            if channel:
                embed.add_field(
                    name="Channel",
                    value=f"{channel.name} ({channel.id})",
                    inline=True
                )

            if details:
                embed.add_field(
                    name="Details",
                    value=f"```{details[:1000]}```",
                    inline=False
                )

            await self.send_to_owner(embed)

            # Send to log channel if configured
            if guild:
                log_channel = await self.get_log_channel(guild.id)
                if log_channel:
                    try:
                        await log_channel.send(embed=embed)
                    except Exception as e:
                        print(f"Error sending to log channel: {e}")

        except Exception as e:
            print(f"Error in log_action: {e}")
            traceback.print_exc()

    async def log_error(self, ctx, error):
        """Log an error that occurred"""
        try:
            error_msg = str(error)
            stack_trace = ''.join(traceback.format_exception(type(error), error, error.__traceback__))

            embed = discord.Embed(
                title="🚨 Error Occurred",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )

            if ctx.command:
                embed.add_field(
                    name="Command",
                    value=f"`{ctx.command.name}`",
                    inline=True
                )

            embed.add_field(
                name="User",
                value=f"{ctx.author} ({ctx.author.id})",
                inline=True
            )

            embed.add_field(
                name="Server",
                value=f"{ctx.guild.name} ({ctx.guild.id})" if ctx.guild else "DM",
                inline=True
            )

            embed.add_field(
                name="Channel",
                value=f"{ctx.channel.name} ({ctx.channel.id})" if hasattr(ctx.channel, 'name') else f"DM ({ctx.channel.id})",
                inline=True
            )

            embed.add_field(
                name="Error",
                value=f"```{error_msg[:500]}```",
                inline=False
            )

            embed.add_field(
                name="Stack Trace",
                value=f"```{stack_trace[:1000]}```",
                inline=False
            )

            await self.send_to_owner(embed)

        except Exception as e:
            print(f"Error in log_error: {e}")
            traceback.print_exc()

    async def send_to_owner(self, embed: discord.Embed):
        """Send an embed to the bot owner"""
        try:
            owner = await self.bot.fetch_user(self.owner_id)
            await owner.send(embed=embed)
        except discord.Forbidden:
            print("Cannot send DM to owner - DMs are closed")
        except discord.NotFound:
            print("Owner user not found")
        except Exception as e:
            print(f"Error sending to owner: {e}")

    @commands.command(name='logs')
    @commands.has_permissions(administrator=True)
    async def set_log_channel(self, ctx, channel: discord.TextChannel = None):
        """Set the log channel for this server"""
        if channel is None:
            channel = ctx.channel

        await self.bot.db.set_guild_setting(ctx.guild.id, 'log_channel_id', channel.id)

        embed = discord.Embed(
            title="✅ Log Channel Set",
            description=f"Log channel has been set to {channel.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

        # Log this action
        await self.log_action(
            "Set Log Channel",
            guild=ctx.guild,
            user=ctx.author,
            channel=channel,
            details=f"Log channel set to {channel.name}"
        )

async def setup(bot):
    await bot.add_cog(LoggingSystem(bot))