import discord
from discord.ext import commands
from discord import ui
import asyncio
import io
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import os
import json

class TicketCategorySelect(ui.Select):
    """Select menu for ticket categories"""

    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(
                label="Support", 
                description="General support and help",
                emoji="🛠️"
            ),
            discord.SelectOption(
                label="Sales", 
                description="Sales inquiries and questions",
                emoji="💰"
            ),
            discord.SelectOption(
                label="Appeals", 
                description="Ban appeals and punishments",
                emoji="⚖️"
            ),
            discord.SelectOption(
                label="Bug Report", 
                description="Report bugs and issues",
                emoji="🐛"
            ),
            discord.SelectOption(
                label="Other", 
                description="Other inquiries",
                emoji="❓"
            )
        ]

        super().__init__(
            placeholder="Select a ticket category...",
            options=options,
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]

        # Check if user already has tickets
        tickets_cog = self.bot.get_cog('Tickets')
        if tickets_cog:
            await tickets_cog.create_ticket(interaction, category)

class TicketCreateView(ui.View):
    """View for ticket creation panel"""

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.add_item(TicketCategorySelect(bot))

class TicketControlView(ui.View):
    """View for ticket control buttons"""

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="Close", style=discord.ButtonStyle.danger, emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        tickets_cog = self.bot.get_cog('Tickets')
        if tickets_cog:
            await tickets_cog.close_ticket(interaction)

    @ui.button(label="Claim", style=discord.ButtonStyle.primary, emoji="✋")
    async def claim_ticket(self, interaction: discord.Interaction, button: ui.Button):
        tickets_cog = self.bot.get_cog('Tickets')
        if tickets_cog:
            await tickets_cog.claim_ticket(interaction)

    @ui.button(label="Add User", style=discord.ButtonStyle.secondary, emoji="➕")
    async def add_user(self, interaction: discord.Interaction, button: ui.Button):
        tickets_cog = self.bot.get_cog('Tickets')
        if tickets_cog:
            await tickets_cog.add_user_modal(interaction)

    @ui.button(label="Remove User", style=discord.ButtonStyle.secondary, emoji="➖")
    async def remove_user(self, interaction: discord.Interaction, button: ui.Button):
        tickets_cog = self.bot.get_cog('Tickets')
        if tickets_cog:
            await tickets_cog.remove_user_modal(interaction)

class AddUserModal(ui.Modal):
    """Modal for adding users to tickets"""

    def __init__(self, bot):
        super().__init__(title="Add User to Ticket")
        self.bot = bot

        self.user_input = ui.TextInput(
            label="User ID or Username",
            placeholder="Enter user ID or username...",
            required=True
        )
        self.add_item(self.user_input)

    async def on_submit(self, interaction: discord.Interaction):
        tickets_cog = self.bot.get_cog('Tickets')
        if tickets_cog:
            await tickets_cog.add_user_to_ticket(interaction, self.user_input.value)

class RemoveUserModal(ui.Modal):
    """Modal for removing users from tickets"""

    def __init__(self, bot):
        super().__init__(title="Remove User from Ticket")
        self.bot = bot

        self.user_input = ui.TextInput(
            label="User ID or Username",
            placeholder="Enter user ID or username...",
            required=True
        )
        self.add_item(self.user_input)

    async def on_submit(self, interaction: discord.Interaction):
        tickets_cog = self.bot.get_cog('Tickets')
        if tickets_cog:
            await tickets_cog.remove_user_from_ticket(interaction, self.user_input.value)

class Tickets(commands.Cog):
    """Advanced ticket system"""

    def __init__(self, bot):
        self.bot = bot
        self.ticket_panels = {}  # Store ticket panel message IDs

        # Start auto-archive task
        self.auto_archive_task = asyncio.create_task(self.auto_archive_tickets())

    def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.auto_archive_task.cancel()

    async def cog_before_invoke(self, ctx):
        """Log command before execution"""
        logging_cog = self.bot.get_cog('LoggingSystem')
        if logging_cog:
            args = ' '.join(ctx.args[2:]) if len(ctx.args) > 2 else ""
            await logging_cog.log_command(ctx, ctx.command.name, args)

    async def auto_archive_tickets(self):
        """Auto-archive inactive tickets"""
        while not self.bot.is_closed():
            try:
                # This would check for inactive tickets and archive them
                # Implementation depends on your specific requirements
                await asyncio.sleep(3600)  # Check every hour
            except Exception as e:
                print(f"Error in auto-archive: {e}")
                await asyncio.sleep(3600)

    async def create_ticket(self, interaction: discord.Interaction, category: str):
        """Create a new ticket"""
        try:
            # Check if user already has tickets
            user_tickets = await self.bot.db.get_user_tickets(interaction.user.id, interaction.guild.id)

            if len(user_tickets) >= 3:  # Max 3 tickets per user
                await interaction.response.send_message(
                    "❌ You already have the maximum number of tickets open (3)!",
                    ephemeral=True
                )
                return

            # Get guild settings
            settings = await self.bot.db.get_guild_settings(interaction.guild.id)

            # Create ticket channel
            category_channel = None
            if settings and settings.get('ticket_category_id'):
                category_channel = self.bot.get_channel(settings['ticket_category_id'])

            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(
                    read_messages=True, 
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),
                interaction.guild.me: discord.PermissionOverwrite(
                    read_messages=True, 
                    send_messages=True,
                    manage_messages=True,
                    embed_links=True,
                    attach_files=True
                )
            }

            # Add staff roles if configured
            if settings and settings.get('staff_role_ids'):
                for role_id in settings['staff_role_ids']:
                    role = interaction.guild.get_role(role_id)
                    if role:
                        overwrites[role] = discord.PermissionOverwrite(
                            read_messages=True,
                            send_messages=True,
                            manage_messages=True
                        )

            channel = await interaction.guild.create_text_channel(
                f"ticket-{interaction.user.name}",
                category=category_channel,
                overwrites=overwrites
            )

            # Create ticket in database
            ticket_id = await self.bot.db.create_ticket(
                interaction.guild.id,
                channel.id,
                interaction.user.id,
                category
            )

            # Send ticket created message
            embed = discord.Embed(
                title=f"🎫 Ticket #{ticket_id}",
                description=f"**Category:** {category}\n**Created by:** {interaction.user.mention}",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )

            embed.add_field(
                name="📝 How to use this ticket:",
                value="• Describe your issue in detail\n• Wait for staff to respond\n• Use the buttons below to manage the ticket",
                inline=False
            )

            view = TicketControlView(self.bot)
            ticket_message = await channel.send(embed=embed, view=view)

            # Pin the ticket message
            await ticket_message.pin()

            # Respond to interaction
            await interaction.response.send_message(
                f"✅ Ticket created! {channel.mention}",
                ephemeral=True
            )

            # Log ticket creation
            logging_cog = self.bot.get_cog('LoggingSystem')
            if logging_cog:
                await logging_cog.log_action(
                    "Ticket Created",
                    guild=interaction.guild,
                    user=interaction.user,
                    channel=channel,
                    details=f"Category: {category}, ID: {ticket_id}"
                )

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error creating ticket: {str(e)}",
                ephemeral=True
            )

    async def close_ticket(self, interaction: discord.Interaction):
        """Close a ticket"""
        try:
            ticket = await self.bot.db.get_ticket(interaction.channel.id)

            if not ticket:
                await interaction.response.send_message(
                    "❌ This is not a ticket channel!",
                    ephemeral=True
                )
                return

            # Check permissions
            if not (interaction.user.guild_permissions.manage_channels or 
                   interaction.user.id == ticket['user_id']):
                await interaction.response.send_message(
                    "❌ You don't have permission to close this ticket!",
                    ephemeral=True
                )
                return

            # Generate transcript
            transcript = await self.generate_transcript(interaction.channel)

            # Update ticket in database
            await self.bot.db.update_ticket(
                interaction.channel.id,
                status='closed',
                closed_at=datetime.utcnow()
            )

            # Send closing message
            embed = discord.Embed(
                title="🔒 Ticket Closed",
                description=f"Ticket closed by {interaction.user.mention}",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )

            await interaction.response.send_message(embed=embed)

            # Send transcript to owner and log channel
            if transcript:
                file = discord.File(io.StringIO(transcript), f"ticket-{ticket['id']}-transcript.txt")

                # Send to owner
                try:
                    owner = await self.bot.fetch_user(int(os.getenv('OWNER_ID')))
                    await owner.send(
                        f"Transcript for ticket #{ticket['id']} in {interaction.guild.name}",
                        file=file
                    )
                except:
                    pass

                # Send to log channel
                settings = await self.bot.db.get_guild_settings(interaction.guild.id)
                if settings and settings.get('ticket_log_channel_id'):
                    log_channel = self.bot.get_channel(settings['ticket_log_channel_id'])
                    if log_channel:
                        try:
                            file = discord.File(io.StringIO(transcript), f"ticket-{ticket['id']}-transcript.txt")
                            await log_channel.send(
                                f"Transcript for ticket #{ticket['id']}",
                                file=file
                            )
                        except:
                            pass

            # Delete channel after 10 seconds
            await asyncio.sleep(10)
            await interaction.channel.delete()

            # Log ticket closure
            logging_cog = self.bot.get_cog('LoggingSystem')
            if logging_cog:
                await logging_cog.log_action(
                    "Ticket Closed",
                    guild=interaction.guild,
                    user=interaction.user,
                    details=f"Ticket ID: {ticket['id']}"
                )

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error closing ticket: {str(e)}",
                ephemeral=True
            )

    async def claim_ticket(self, interaction: discord.Interaction):
        """Claim a ticket"""
        try:
            ticket = await self.bot.db.get_ticket(interaction.channel.id)

            if not ticket:
                await interaction.response.send_message(
                    "❌ This is not a ticket channel!",
                    ephemeral=True
                )
                return

            # Check if user has manage_channels permission
            if not interaction.user.guild_permissions.manage_channels:
                await interaction.response.send_message(
                    "❌ You don't have permission to claim tickets!",
                    ephemeral=True
                )
                return

            # Update ticket
            await self.bot.db.update_ticket(
                interaction.channel.id,
                staff_id=interaction.user.id
            )

            # Update channel name
            await interaction.channel.edit(name=f"ticket-{interaction.user.name}")

            # Send claim message
            embed = discord.Embed(
                title="✋ Ticket Claimed",
                description=f"This ticket has been claimed by {interaction.user.mention}",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )

            await interaction.response.send_message(embed=embed)

            # Log ticket claim
            logging_cog = self.bot.get_cog('LoggingSystem')
            if logging_cog:
                await logging_cog.log_action(
                    "Ticket Claimed",
                    guild=interaction.guild,
                    user=interaction.user,
                    channel=interaction.channel,
                    details=f"Ticket ID: {ticket['id']}"
                )

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error claiming ticket: {str(e)}",
                ephemeral=True
            )

    async def add_user_modal(self, interaction: discord.Interaction):
        """Show add user modal"""
        await interaction.response.send_modal(AddUserModal(self.bot))

    async def remove_user_modal(self, interaction: discord.Interaction):
        """Show remove user modal"""
        await interaction.response.send_modal(RemoveUserModal(self.bot))

    async def add_user_to_ticket(self, interaction: discord.Interaction, user_input: str):
        """Add user to ticket"""
        try:
            ticket = await self.bot.db.get_ticket(interaction.channel.id)

            if not ticket:
                await interaction.response.send_message(
                    "❌ This is not a ticket channel!",
                    ephemeral=True
                )
                return

            # Check permissions
            if not interaction.user.guild_permissions.manage_channels:
                await interaction.response.send_message(
                    "❌ You don't have permission to add users to tickets!",
                    ephemeral=True
                )
                return

            # Try to get user
            user = None
            if user_input.isdigit():
                user = interaction.guild.get_member(int(user_input))
            else:
                user = discord.utils.get(interaction.guild.members, name=user_input)

            if not user:
                await interaction.response.send_message(
                    "❌ User not found!",
                    ephemeral=True
                )
                return

            # Add user to channel
            await interaction.channel.set_permissions(
                user,
                read_messages=True,
                send_messages=True,
                attach_files=True,
                embed_links=True
            )

            embed = discord.Embed(
                title="➕ User Added",
                description=f"{user.mention} has been added to this ticket",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error adding user: {str(e)}",
                ephemeral=True
            )

    async def remove_user_from_ticket(self, interaction: discord.Interaction, user_input: str):
        """Remove user from ticket"""
        try:
            ticket = await self.bot.db.get_ticket(interaction.channel.id)

            if not ticket:
                await interaction.response.send_message(
                    "❌ This is not a ticket channel!",
                    ephemeral=True
                )
                return

            # Check permissions
            if not interaction.user.guild_permissions.manage_channels:
                await interaction.response.send_message(
                    "❌ You don't have permission to remove users from tickets!",
                    ephemeral=True
                )
                return

            # Try to get user
            user = None
            if user_input.isdigit():
                user = interaction.guild.get_member(int(user_input))
            else:
                user = discord.utils.get(interaction.guild.members, name=user_input)

            if not user:
                await interaction.response.send_message(
                    "❌ User not found!",
                    ephemeral=True
                )
                return

            # Don't remove ticket creator
            if user.id == ticket['user_id']:
                await interaction.response.send_message(
                    "❌ Cannot remove the ticket creator!",
                    ephemeral=True
                )
                return

            # Remove user from channel
            await interaction.channel.set_permissions(
                user,
                read_messages=False,
                send_messages=False
            )

            embed = discord.Embed(
                title="➖ User Removed",
                description=f"{user.mention} has been removed from this ticket",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error removing user: {str(e)}",
                ephemeral=True
            )

    async def generate_transcript(self, channel: discord.TextChannel) -> str:
        """Generate a transcript of the ticket"""
        try:
            messages = []
            async for message in channel.history(limit=None, oldest_first=True):
                timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
                content = message.content or "[No content]"

                # Handle embeds
                if message.embeds:
                    for embed in message.embeds:
                        if embed.title:
                            content += f"\n[EMBED TITLE: {embed.title}]"
                        if embed.description:
                            content += f"\n[EMBED DESCRIPTION: {embed.description}]"

                # Handle attachments
                if message.attachments:
                    for attachment in message.attachments:
                        content += f"\n[ATTACHMENT: {attachment.filename}]"

                messages.append(f"[{timestamp}] {message.author}: {content}")

            return "\n".join(messages)

        except Exception as e:
            print(f"Error generating transcript: {e}")
            return ""

    @commands.group(name='ticket', invoke_without_command=True)
    @commands.has_permissions(manage_channels=True)
    async def ticket(self, ctx):
        """Ticket system commands"""
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="🎫 Ticket System",
                description="Use subcommands to manage the ticket system",
                color=discord.Color.blue()
            )

            embed.add_field(
                name="Commands",
                value="`ticket setup interactive` - Setup interactive ticket panel\n"
                      "`ticket setup normal` - Setup normal ticket panel\n"
                      "`ticket stats` - View ticket statistics\n"
                      "`ticket config` - Configure ticket settings",
                inline=False
            )

            await ctx.send(embed=embed)

    @ticket.command(name='setup')
    @commands.has_permissions(manage_channels=True)
    async def setup_ticket(self, ctx, panel_type: str = "interactive"):
        """Setup ticket panel"""
        if panel_type.lower() == "interactive":
            embed = discord.Embed(
                title="🎫 Create a Ticket",
                description="Select a category below to create a ticket. Our staff will assist you as soon as possible!",
                color=discord.Color.blue()
            )

            embed.add_field(
                name="📋 Instructions",
                value="1. Select a category from the dropdown\n"
                      "2. Wait for your ticket channel to be created\n"
                      "3. Describe your issue in detail\n"
                      "4. Wait for staff to respond",
                inline=False
            )

            view = TicketCreateView(self.bot)
            await ctx.send(embed=embed, view=view)

        elif panel_type.lower() == "normal":
            embed = discord.Embed(
                title="🎫 Create a Ticket",
                description="React with 🎫 to create a ticket. Our staff will assist you as soon as possible!",
                color=discord.Color.blue()
            )

            embed.add_field(
                name="📋 Instructions",
                value="1. React with 🎫 below\n"
                      "2. Wait for your ticket channel to be created\n"
                      "3. Describe your issue in detail\n"
                      "4. Wait for staff to respond",
                inline=False
            )

            message = await ctx.send(embed=embed)
            await message.add_reaction("🎫")

        else:
            await ctx.send("❌ Invalid panel type! Use 'interactive' or 'normal'")

    @ticket.command(name='stats')
    @commands.has_permissions(manage_channels=True)
    async def ticket_stats(self, ctx):
        """View ticket statistics"""
        stats = await self.bot.db.get_ticket_stats(ctx.guild.id)

        embed = discord.Embed(
            title="📊 Ticket Statistics",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )

        embed.add_field(name="Total Tickets", value=stats['total'], inline=True)
        embed.add_field(name="Open Tickets", value=stats['open'], inline=True)
        embed.add_field(name="Closed Tickets", value=stats['closed'], inline=True)

        await ctx.send(embed=embed)

    @ticket.command(name='config')
    @commands.has_permissions(administrator=True)
    async def config_ticket(self, ctx, setting: str = None, *, value: str = None):
        """Configure ticket settings"""
        if setting is None:
            embed = discord.Embed(
                title="⚙️ Ticket Configuration",
                description="Configure ticket system settings",
                color=discord.Color.blue()
            )

            embed.add_field(
                name="Available Settings",
                value="`category` - Set ticket category\n"
                      "`logchannel` - Set ticket log channel\n"
                      "`staffroles` - Set staff roles (comma separated)",
                inline=False
            )

            await ctx.send(embed=embed)
            return

        if setting.lower() == "category":
            if value is None:
                await ctx.send("❌ Please specify a category ID!")
                return

            try:
                category_id = int(value)
                category = ctx.guild.get_channel(category_id)

                if not category or not isinstance(category, discord.CategoryChannel):
                    await ctx.send("❌ Invalid category ID!")
                    return

                await self.bot.db.set_guild_setting(ctx.guild.id, 'ticket_category_id', category_id)
                await ctx.send(f"✅ Ticket category set to {category.name}")

            except ValueError:
                await ctx.send("❌ Invalid category ID!")

        elif setting.lower() == "logchannel":
            if value is None:
                await ctx.send("❌ Please specify a channel ID!")
                return

            try:
                channel_id = int(value)
                channel = ctx.guild.get_channel(channel_id)

                if not channel or not isinstance(channel, discord.TextChannel):
                    await ctx.send("❌ Invalid channel ID!")
                    return

                await self.bot.db.set_guild_setting(ctx.guild.id, 'ticket_log_channel_id', channel_id)
                await ctx.send(f"✅ Ticket log channel set to {channel.mention}")

            except ValueError:
                await ctx.send("❌ Invalid channel ID!")

        elif setting.lower() == "staffroles":
            if value is None:
                await ctx.send("❌ Please specify role IDs (comma separated)!")
                return

            try:
                role_ids = [int(role_id.strip()) for role_id in value.split(",")]

                # Validate roles
                valid_roles = []
                for role_id in role_ids:
                    role = ctx.guild.get_role(role_id)
                    if role:
                        valid_roles.append(role_id)

                if not valid_roles:
                    await ctx.send("❌ No valid roles found!")
                    return

                await self.bot.db.set_guild_setting(ctx.guild.id, 'staff_role_ids', json.dumps(valid_roles))
                await ctx.send(f"✅ Staff roles set! ({len(valid_roles)} roles)")

            except ValueError:
                await ctx.send("❌ Invalid role IDs!")

        else:
            await ctx.send("❌ Invalid setting! Use `category`, `logchannel`, or `staffroles`")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Handle ticket creation via reactions"""
        if user.bot:
            return

        if str(reaction.emoji) == "🎫":
            # Check if this is a ticket panel
            if reaction.message.embeds:
                embed = reaction.message.embeds[0]
                if "Create a Ticket" in embed.title:
                    # Create ticket with "General" category
                    try:
                        # Create a fake interaction for compatibility
                        class FakeInteraction:
                            def __init__(self, user, guild, channel):
                                self.user = user
                                self.guild = guild
                                self.channel = channel

                            async def response(self):
                                pass

                        fake_interaction = FakeInteraction(user, reaction.message.guild, reaction.message.channel)
                        await self.create_ticket(fake_interaction, "General")

                    except Exception as e:
                        print(f"Error creating ticket from reaction: {e}")

async def setup(bot):
    await bot.add_cog(Tickets(bot))