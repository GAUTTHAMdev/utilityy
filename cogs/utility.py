import discord
from discord.ext import commands
import asyncio
import aiohttp
import json
import re
import random
from datetime import datetime, timedelta
from typing import Optional
import math
from utils.embeds import *
from utils.helpers import *

class Utility(commands.Cog):
    """Utility commands for the bot"""

    def __init__(self, bot):
        self.bot = bot
        self.afk_check_enabled = True

        # Start reminder check task
        self.reminder_task = asyncio.create_task(self.check_reminders())

    def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.reminder_task.cancel()

    async def cog_before_invoke(self, ctx):
        """Log command before execution"""
        logging_cog = self.bot.get_cog('LoggingSystem')
        if logging_cog:
            args = ' '.join(str(arg) for arg in ctx.args[2:]) if len(ctx.args) > 2 else ""
            await logging_cog.log_command(ctx, ctx.command.name, args)

    async def check_reminders(self):
        """Background task to check for due reminders"""
        while not self.bot.is_closed():
            try:
                due_reminders = await self.bot.db.get_due_reminders()

                for reminder in due_reminders:
                    try:
                        user = await self.bot.fetch_user(reminder['user_id'])

                        embed = reminder_embed(
                            reminder['message'], 
                            datetime.fromisoformat(reminder['created_at'])
                        )

                        await user.send(embed=embed)
                        await self.bot.db.delete_reminder(reminder['id'])

                    except Exception as e:
                        print(f"Error sending reminder: {e}")
                        await self.bot.db.delete_reminder(reminder['id'])

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                print(f"Error in reminder check: {e}")
                await asyncio.sleep(60)

    async def check_afk(self, message):
        """Check for AFK mentions and removals"""
        if not self.afk_check_enabled or not message.guild:
            return

        try:
            # Check if user was AFK and remove it
            afk_data = await self.bot.db.get_afk(message.author.id, message.guild.id)
            if afk_data:
                await self.bot.db.remove_afk(message.author.id, message.guild.id)

                embed = afk_embed(message.author, "", "remove")
                embed.add_field(
                    name="Was AFK Since",
                    value=f"<t:{int(datetime.fromisoformat(afk_data['set_at']).timestamp())}:R>",
                    inline=False
                )

                await message.channel.send(embed=embed, delete_after=10)

            # Check for AFK mentions
            for mention in message.mentions:
                if mention.id == message.author.id:
                    continue

                afk_data = await self.bot.db.get_afk(mention.id, message.guild.id)
                if afk_data:
                    embed = discord.Embed(
                        title="💤 User is AFK",
                        description=f"{mention.mention} is currently AFK",
                        color=discord.Color.yellow()
                    )
                    embed.add_field(
                        name="Reason",
                        value=afk_data['reason'],
                        inline=False
                    )
                    embed.add_field(
                        name="Since",
                        value=f"<t:{int(datetime.fromisoformat(afk_data['set_at']).timestamp())}:R>",
                        inline=False
                    )

                    await message.channel.send(embed=embed, delete_after=15)

        except Exception as e:
            print(f"Error in AFK check: {e}")

    @commands.command(name='ping')
    async def ping(self, ctx):
        """Check bot's latency"""
        embed = ping_embed(self.bot.latency)
        await ctx.send(embed=embed)

    @commands.command(name='serverinfo')
    async def serverinfo(self, ctx):
        """Get information about the server"""
        if not ctx.guild:
            await ctx.send(embed=error_embed("Server Only", "This command can only be used in servers!"))
            return

        embed = guild_embed(ctx.guild)
        await ctx.send(embed=embed)

    @commands.command(name='userinfo')
    async def userinfo(self, ctx, member: discord.Member = None):
        """Get information about a user"""
        if member is None:
            member = ctx.author

        embed = user_embed(member)

        # Add roles if in guild
        if ctx.guild and hasattr(member, 'roles'):
            roles = [role.mention for role in member.roles[1:]]  # Skip @everyone
            if roles:
                embed.add_field(name="Roles", value=", ".join(roles), inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='avatar')
    async def avatar(self, ctx, member: discord.Member = None):
        """Get a user's avatar"""
        if member is None:
            member = ctx.author

        embed = avatar_embed(member)
        await ctx.send(embed=embed)

    @commands.command(name='servericon')
    async def servericon(self, ctx):
        """Get the server's icon"""
        if not ctx.guild:
            await ctx.send(embed=error_embed("Server Only", "This command can only be used in servers!"))
            return

        if not ctx.guild.icon:
            await ctx.send(embed=error_embed("No Icon", "This server doesn't have an icon!"))
            return

        embed = icon_embed(ctx.guild, "icon")
        await ctx.send(embed=embed)

    @commands.command(name='serverbanner')
    async def serverbanner(self, ctx):
        """Get the server's banner"""
        if not ctx.guild:
            await ctx.send(embed=error_embed("Server Only", "This command can only be used in servers!"))
            return

        if not ctx.guild.banner:
            await ctx.send(embed=error_embed("No Banner", "This server doesn't have a banner!"))
            return

        embed = icon_embed(ctx.guild, "banner")
        await ctx.send(embed=embed)

    @commands.command(name='serverowner')
    async def serverowner(self, ctx):
        """Get the server owner"""
        if not ctx.guild:
            await ctx.send(embed=error_embed("Server Only", "This command can only be used in servers!"))
            return

        embed = server_owner_embed(ctx.guild.owner)
        await ctx.send(embed=embed)

    @commands.command(name='servermembers')
    async def servermembers(self, ctx):
        """Get server member statistics"""
        if not ctx.guild:
            await ctx.send(embed=error_embed("Server Only", "This command can only be used in servers!"))
            return

        embed = member_count_embed(ctx.guild)
        await ctx.send(embed=embed)

    @commands.command(name='botinfo')
    async def botinfo(self, ctx):
        """Get information about the bot"""
        embed = bot_info_embed(self.bot)
        await ctx.send(embed=embed)

    @commands.command(name='membercount')
    async def membercount(self, ctx):
        """Get the server member count"""
        if not ctx.guild:
            await ctx.send(embed=error_embed("Server Only", "This command can only be used in servers!"))
            return

        embed = EmbedBuilder().title("👥 Member Count").description(f"**{ctx.guild.member_count}** members").color(discord.Color.blue()).build()
        await ctx.send(embed=embed)

    @commands.command(name='roleslist')
    async def roleslist(self, ctx):
        """List all server roles"""
        if not ctx.guild:
            await ctx.send(embed=error_embed("Server Only", "This command can only be used in servers!"))
            return

        roles = [role.mention for role in ctx.guild.roles[1:]]  # Skip @everyone

        if not roles:
            await ctx.send(embed=error_embed("No Roles", "No roles found!"))
            return

        # Split roles into chunks to avoid embed limits
        chunks = [roles[i:i+10] for i in range(0, len(roles), 10)]

        for i, chunk in enumerate(chunks):
            embed = EmbedBuilder().title(f"📋 Server Roles ({i+1}/{len(chunks)})").description("\n".join(chunk)).color(discord.Color.blue()).build()
            await ctx.send(embed=embed)

    @commands.command(name='emojislist')
    async def emojislist(self, ctx):
        """List all server emojis"""
        if not ctx.guild:
            await ctx.send(embed=error_embed("Server Only", "This command can only be used in servers!"))
            return

        emojis = [str(emoji) for emoji in ctx.guild.emojis]

        if not emojis:
            await ctx.send(embed=error_embed("No Emojis", "No custom emojis found!"))
            return

        # Split emojis into chunks
        chunks = [emojis[i:i+20] for i in range(0, len(emojis), 20)]

        for i, chunk in enumerate(chunks):
            embed = EmbedBuilder().title(f"😀 Server Emojis ({i+1}/{len(chunks)})").description(" ".join(chunk)).color(discord.Color.blue()).build()
            await ctx.send(embed=embed)

    @commands.command(name='channelinfo')
    async def channelinfo(self, ctx, channel: discord.TextChannel = None):
        """Get information about a channel"""
        if channel is None:
            channel = ctx.channel

        embed = channel_embed(channel)
        await ctx.send(embed=embed)

    @commands.command(name='invite')
    async def invite(self, ctx):
        """Generate a bot invite link"""
        permissions = discord.Permissions(
            read_messages=True,
            send_messages=True,
            embed_links=True,
            attach_files=True,
            read_message_history=True,
            add_reactions=True,
            use_external_emojis=True,
            manage_messages=True,
            manage_channels=True,
            manage_roles=True,
            ban_members=True,
            kick_members=True,
            use_slash_commands=True,
            moderate_members=True
        )

        invite_url = discord.utils.oauth_url(self.bot.user.id, permissions=permissions)

        embed = invite_embed(invite_url)
        await ctx.send(embed=embed)

    @commands.command(name='uptime')
    async def uptime(self, ctx):
        """Show bot uptime"""
        uptime = datetime.utcnow() - self.bot.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        uptime_str = f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
        embed = uptime_embed(uptime_str)
        await ctx.send(embed=embed)

    @commands.command(name='poll')
    async def poll(self, ctx, *, question):
        """Create a yes/no poll"""
        embed = poll_embed(question, ctx.author)

        message = await ctx.send(embed=embed)
        await message.add_reaction("✅")
        await message.add_reaction("❌")

    @commands.command(name='calculator', aliases=['calc'])
    async def calculator(self, ctx, *, expression):
        """Simple calculator"""
        try:
            # Only allow basic math operations
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                await ctx.send(embed=error_embed("Invalid Expression", "Invalid characters in expression!"))
                return

            # Evaluate the expression
            result = eval(expression)

            embed = calculation_embed(expression, str(result))
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(embed=error_embed("Calculation Error", f"Error: {str(e)}"))

async def setup(bot):
    await bot.add_cog(Utility(bot))

    @commands.command(name='shorten')
    async def shorten_url(self, ctx, url):
        """Shorten a URL using TinyURL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://tinyurl.com/api-create.php?url={url}") as response:
                    if response.status == 200:
                        short_url = await response.text()

                        embed = url_shorten_embed(url, short_url)
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send(embed=error_embed("URL Shortening Failed", "Failed to shorten URL!"))

        except Exception as e:
            await ctx.send(embed=error_embed("Error", f"Error shortening URL: {str(e)}"))

    @commands.command(name='quote')
    async def quote(self, ctx):
        """Get a random inspirational quote"""
        quotes = [
            "The only way to do great work is to love what you do. - Steve Jobs",
            "Innovation distinguishes between a leader and a follower. - Steve Jobs",
            "Life is what happens to you while you're busy making other plans. - John Lennon",
            "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
            "It is during our darkest moments that we must focus to see the light. - Aristotle",
            "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
            "The only impossible journey is the one you never begin. - Tony Robbins",
            "In the middle of difficulty lies opportunity. - Albert Einstein",
            "Be yourself; everyone else is already taken. - Oscar Wilde",
            "Two things are infinite: the universe and human stupidity; and I'm not sure about the universe. - Albert Einstein"
        ]

        quote = random.choice(quotes)
        embed = quote_embed(quote)
        await ctx.send(embed=embed)

    @commands.command(name='urban')
    async def urban_dictionary(self, ctx, *, term):
        """Search Urban Dictionary"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://api.urbandictionary.com/v0/define?term={term}") as response:
                    if response.status == 200:
                        data = await response.json()

                        if not data.get('list'):
                            await ctx.send(embed=error_embed("No Results", f"No definition found for '{term}'"))
                            return

                        definition = data['list'][0]

                        embed = EmbedBuilder().title(f"📚 Urban Dictionary: {term}").color(discord.Color.blue()).build()

                        # Truncate definition if too long
                        def_text = definition['definition']
                        if len(def_text) > 1000:
                            def_text = def_text[:1000] + "..."

                        embed.add_field(name="Definition", value=def_text, inline=False)

                        # Add example if available
                        if definition.get('example'):
                            example_text = definition['example']
                            if len(example_text) > 500:
                                example_text = example_text[:500] + "..."
                            embed.add_field(name="Example", value=example_text, inline=False)

                        embed.add_field(name="👍", value=definition.get('thumbs_up', 0), inline=True)
                        embed.add_field(name="👎", value=definition.get('thumbs_down', 0), inline=True)

                        await ctx.send(embed=embed)
                    else:
                        await ctx.send(embed=error_embed("API Error", "Failed to fetch definition"))

        except Exception as e:
            await ctx.send(embed=error_embed("Error", f"Error fetching definition: {str(e)}"))

    @commands.command(name='define')
    async def define_word(self, ctx, *, word):
        """Get dictionary definition of a word"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}") as response:
                    if response.status == 200:
                        data = await response.json()

                        if not data:
                            await ctx.send(embed=error_embed("No Results", f"No definition found for '{word}'"))
                            return

                        entry = data[0]

                        embed = EmbedBuilder().title(f"📖 Definition: {word}").color(discord.Color.blue()).build()

                        # Add pronunciation if available
                        if 'phonetic' in entry:
                            embed.add_field(name="Pronunciation", value=entry['phonetic'], inline=False)

                        # Add meanings
                        for i, meaning in enumerate(entry.get('meanings', [])[:3]):  # Limit to 3 meanings
                            part_of_speech = meaning.get('partOfSpeech', 'Unknown')
                            definitions = meaning.get('definitions', [])

                            if definitions:
                                definition_text = definitions[0].get('definition', 'No definition available')
                                if len(definition_text) > 500:
                                    definition_text = definition_text[:500] + "..."

                                embed.add_field(
                                    name=f"{part_of_speech.title()}",
                                    value=definition_text,
                                    inline=False
                                )

                        await ctx.send(embed=embed)
                    else:
                        await ctx.send(embed=error_embed("No Results", f"No definition found for '{word}'"))

        except Exception as e:
            await ctx.send(embed=error_embed("Error", f"Error fetching definition: {str(e)}"))

    @commands.command(name='translate')
    async def translate_text(self, ctx, target_lang: str, *, text):
        """Translate text to target language"""
        try:
            # Simple translation using Google Translate API (free tier)
            async with aiohttp.ClientSession() as session:
                url = "https://translate.googleapis.com/translate_a/single"
                params = {
                    'client': 'gtx',
                    'sl': 'auto',
                    'tl': target_lang,
                    'dt': 't',
                    'q': text
                }

                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        if data and data[0]:
                            translated_text = ''.join([sentence[0] for sentence in data[0]])
                            detected_lang = data[2] if len(data) > 2 else 'Unknown'

                            embed = EmbedBuilder().title("🌐 Translation").color(discord.Color.blue()).build()

                            embed.add_field(name="Original", value=text[:500], inline=False)
                            embed.add_field(name="Translated", value=translated_text[:500], inline=False)
                            embed.add_field(name="Detected Language", value=detected_lang, inline=True)
                            embed.add_field(name="Target Language", value=target_lang, inline=True)

                            await ctx.send(embed=embed)
                        else:
                            await ctx.send(embed=error_embed("Translation Failed", "Could not translate the text"))
                    else:
                        await ctx.send(embed=error_embed("API Error", "Translation service unavailable"))

        except Exception as e:
            await ctx.send(embed=error_embed("Error", f"Error translating text: {str(e)}"))

    @commands.command(name='timer')
    async def timer(self, ctx, duration: str):
        """Start a countdown timer"""
        try:
            # Parse duration
            duration_delta = parse_time(duration)
            if not duration_delta:
                await ctx.send(embed=error_embed("Invalid Duration", "Duration format: 1h30m, 2d, 45s, etc."))
                return

            if duration_delta.total_seconds() > 86400:  # 24 hours max
                await ctx.send(embed=error_embed("Duration Too Long", "Timer duration cannot exceed 24 hours"))
                return

            if duration_delta.total_seconds() < 5:  # 5 seconds min
                await ctx.send(embed=error_embed("Duration Too Short", "Timer duration must be at least 5 seconds"))
                return

            total_seconds = int(duration_delta.total_seconds())

            # Create timer embed
            embed = EmbedBuilder().title("⏲️ Timer Started").description(f"Timer set for {duration}").color(discord.Color.green()).build()

            message = await ctx.send(embed=embed)

            # Wait for the duration
            await asyncio.sleep(total_seconds)

            # Send completion message
            completion_embed = EmbedBuilder().title("⏰ Timer Completed").description(f"{ctx.author.mention} Your timer for {duration} has finished!").color(discord.Color.red()).build()

            await ctx.send(embed=completion_embed)

        except Exception as e:
            await ctx.send(embed=error_embed("Error", f"Error starting timer: {str(e)}"))

    @commands.command(name='meme')
    async def meme(self, ctx):
        """Get a random meme"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://meme-api.herokuapp.com/gimme") as response:
                    if response.status == 200:
                        data = await response.json()

                        if not data.get('url'):
                            await ctx.send(embed=error_embed("No Meme", "Could not fetch a meme"))
                            return

                        embed = EmbedBuilder().title("😂 Random Meme").description(data.get('title', 'Meme')).color(discord.Color.blue()).build()

                        embed.set_image(url=data['url'])
                        embed.add_field(name="Subreddit", value=f"r/{data.get('subreddit', 'Unknown')}", inline=True)
                        embed.add_field(name="Author", value=f"u/{data.get('author', 'Unknown')}", inline=True)

                        await ctx.send(embed=embed)
                    else:
                        await ctx.send(embed=error_embed("API Error", "Meme service unavailable"))

        except Exception as e:
            await ctx.send(embed=error_embed("Error", f"Error fetching meme: {str(e)}"))

    @commands.command(name='choose')
    async def choose(self, ctx, *, choices):
        """Choose randomly from given options"""
        options = [choice.strip() for choice in choices.split(',')]

        if len(options) < 2:
            await ctx.send(embed=error_embed("Not Enough Options", "Please provide at least 2 options separated by commas!"))
            return

        choice = random.choice(options)
        embed = choice_embed(choice)
        await ctx.send(embed=embed)

    @commands.command(name='eightball', aliases=['8ball'])
    async def eightball(self, ctx, *, question):
        """Ask the magic 8-ball a question"""
        responses = [
            "It is certain", "It is decidedly so", "Without a doubt", "Yes definitely",
            "You may rely on it", "As I see it, yes", "Most likely", "Outlook good",
            "Yes", "Signs point to yes", "Reply hazy, try again", "Ask again later",
            "Better not tell you now", "Cannot predict now", "Concentrate and ask again",
            "Don't count on it", "My reply is no", "My sources say no", "Outlook not so good",
            "Very doubtful"
        ]

        response = random.choice(responses)
        embed = eight_ball_embed(question, response)
        await ctx.send(embed=embed)

    @commands.command(name='afk')
    async def afk(self, ctx, *, reason="No reason provided"):
        """Set your AFK status"""
        if not ctx.guild:
            await ctx.send(embed=error_embed("Server Only", "This command can only be used in servers!"))
            return

        await self.bot.db.set_afk(ctx.author.id, ctx.guild.id, reason)

        embed = afk_embed(ctx.author, reason, "set")
        await ctx.send(embed=embed)

    @commands.command(name='remind')
    async def remind(self, ctx, time_str, *, message):
        """Set a reminder (e.g., 1h30m, 2d, 45s)"""
        try:
            # Parse time string
            time_delta = parse_time(time_str)
            if not time_delta:
                await ctx.send(embed=error_embed("Invalid Time", "Invalid time format! Use format like: 1h30m, 2d, 45s"))
                return

            total_seconds = int(time_delta.total_seconds())

            if total_seconds > 7 * 24 * 3600:  # 7 days max
                await ctx.send(embed=error_embed("Time Too Long", "Maximum reminder time is 7 days!"))
                return

            if total_seconds < 60:  # 1 minute min
                await ctx.send(embed=error_embed("Time Too Short", "Minimum reminder time is 1 minute!"))
                return

            remind_at = datetime.utcnow() + time_delta

            reminder_id = await self.bot.db.add_reminder(
                ctx.author.id, ctx.guild.id if ctx.guild else 0, 
                ctx.channel.id, message, remind_at
            )

            embed = success_embed("Reminder Set", f"I'll remind you in {time_str}")
            embed.add_field(name="Message", value=message, inline=False)
            embed.add_field(name="Remind At", value=f"<t:{int(remind_at.timestamp())}:F>", inline=False)

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(embed=error_embed("Error", f"Error setting reminder: {str(e)}"))

    @commands.command(name='report')
    async def report(self, ctx, member: discord.Member, *, reason):
        """Report a user"""
        if not ctx.guild:
            await ctx.send(embed=error_embed("Server Only", "This command can only be used in servers!"))
            return

        if member == ctx.author:
            await ctx.send(embed=error_embed("Cannot Report Self", "You cannot report yourself!"))
            return

        report_id = await self.bot.db.add_report(
            ctx.guild.id, ctx.author.id, member.id, reason
        )

        embed = report_embed(report_id, member, reason)
        await ctx.send(embed=embed)

        # Log to owner
        logging_cog = self.bot.get_cog('LoggingSystem')
        if logging_cog:
            await logging_cog.log_action(
                "User Report",
                guild=ctx.guild,
                user=ctx.author,
                details=f"Reported {member} for: {reason}"
            )

    @commands.command(name='suggestions', aliases=['suggest'])
    async def suggestions(self, ctx, *, suggestion):
        """Submit a suggestion"""
        if not ctx.guild:
            await ctx.send(embed=error_embed("Server Only", "This command can only be used in servers!"))
            return

        suggestion_id = await self.bot.db.add_suggestion(
            ctx.guild.id, ctx.author.id, suggestion
        )

        embed = suggestion_embed(suggestion_id, suggestion)
        await ctx.send(embed=embed)

    @commands.command(name='sayembed')
    @commands.has_permissions(manage_messages=True)
    async def sayembed(self, ctx, title, *, description):
        """Send a custom embed"""
        embed = EmbedBuilder().title(title).description(description).color(discord.Color.blue()).build()

        await ctx.send(embed=embed)

        # Delete the command message
        try:
            await ctx.message.delete()
        except:
            pass

async def setup(bot):
    bot.add_cog(Utility(bot))