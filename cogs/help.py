import discord
from discord.ext import commands
from discord import ui
import os

class HelpView(ui.View):
    """View for help command with category selection"""
    
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
    
    @ui.select(
        placeholder="Select a category...",
        options=[
            discord.SelectOption(label="Utility", description="Utility commands", emoji="🔧"),
            discord.SelectOption(label="Tickets", description="Ticket system commands", emoji="🎫"),
            discord.SelectOption(label="Moderation", description="Moderation commands", emoji="🛡️"),
            discord.SelectOption(label="Fun", description="Fun commands", emoji="🎉"),
            discord.SelectOption(label="Other", description="Other commands", emoji="📋")
        ]
    )
    async def select_category(self, interaction: discord.Interaction, select):
        category = interaction.data['values'][0]
        
        if category == "Utility":
            embed = self.get_utility_embed()
        elif category == "Tickets":
            embed = self.get_tickets_embed()
        elif category == "Moderation":
            embed = self.get_moderation_embed()
        elif category == "Fun":
            embed = self.get_fun_embed()
        else:
            embed = self.get_other_embed()
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    def get_utility_embed(self):
        """Get utility commands embed"""
        prefix = os.getenv('PREFIX', '!')
        
        embed = discord.Embed(
            title="🔧 Utility Commands",
            description="General utility commands for server information and management",
            color=discord.Color.blue()
        )
        
        commands_text = f"""
        **{prefix}ping** - Check bot latency
        **{prefix}serverinfo** - Get server information
        **{prefix}userinfo [user]** - Get user information
        **{prefix}avatar [user]** - Get user's avatar
        **{prefix}servericon** - Get server icon
        **{prefix}serverbanner** - Get server banner
        **{prefix}serverowner** - Get server owner info
        **{prefix}servermembers** - Get member statistics
        **{prefix}botinfo** - Get bot information
        **{prefix}membercount** - Get member count
        **{prefix}roleslist** - List all server roles
        **{prefix}emojislist** - List all server emojis
        **{prefix}channelinfo [channel]** - Get channel info
        **{prefix}invite** - Get bot invite link
        **{prefix}uptime** - Show bot uptime
        """
        
        embed.add_field(name="Commands", value=commands_text, inline=False)
        
        return embed
    
    def get_tickets_embed(self):
        """Get ticket commands embed"""
        prefix = os.getenv('PREFIX', '!')
        
        embed = discord.Embed(
            title="🎫 Ticket System",
            description="Advanced ticket system with interactive panels and comprehensive management",
            color=discord.Color.green()
        )
        
        commands_text = f"""
        **{prefix}ticket setup interactive** - Setup interactive ticket panel
        **{prefix}ticket setup normal** - Setup normal ticket panel
        **{prefix}ticket stats** - View ticket statistics
        **{prefix}ticket config** - Configure ticket settings
        """
        
        embed.add_field(name="Commands", value=commands_text, inline=False)
        
        features_text = """
        • Interactive category selection
        • Automatic channel creation
        • Staff claiming system
        • User management (add/remove)
        • Automatic transcripts
        • Anti-spam protection
        • Auto-archive inactive tickets
        • Comprehensive logging
        """
        
        embed.add_field(name="Features", value=features_text, inline=False)
        
        return embed
    
    def get_moderation_embed(self):
        """Get moderation commands embed"""
        prefix = os.getenv('PREFIX', '!')
        
        embed = discord.Embed(
            title="🛡️ Moderation Commands",
            description="Moderation tools for server management",
            color=discord.Color.red()
        )
        
        commands_text = f"""
        **{prefix}clear [amount]** - Clear messages (bulk delete)
        **{prefix}ban [user] [reason]** - Ban a user
        **{prefix}unban [user]** - Unban a user
        **{prefix}kick [user] [reason]** - Kick a user
        **{prefix}slowmode [seconds]** - Set channel slowmode
        **{prefix}logs [channel]** - Set log channel
        """
        
        embed.add_field(name="Commands", value=commands_text, inline=False)
        
        embed.add_field(
            name="⚠️ Note",
            value="All moderation commands require appropriate permissions and include permission checks.",
            inline=False
        )
        
        return embed
    
    def get_fun_embed(self):
        """Get fun commands embed"""
        prefix = os.getenv('PREFIX', '!')
        
        embed = discord.Embed(
            title="🎉 Fun Commands",
            description="Entertainment and utility commands for users",
            color=discord.Color.purple()
        )
        
        commands_text = f"""
        **{prefix}poll [question]** - Create a yes/no poll
        **{prefix}calculator [expression]** - Calculate math expressions
        **{prefix}shorten [url]** - Shorten URLs using TinyURL
        **{prefix}quote** - Get a random inspirational quote
        **{prefix}urban [term]** - Search Urban Dictionary
        **{prefix}define [word]** - Get dictionary definition
        **{prefix}translate [text]** - Translate text
        **{prefix}remind [time] [message]** - Set a reminder
        **{prefix}timer [time]** - Start a countdown timer
        **{prefix}afk [reason]** - Set AFK status
        **{prefix}choose [options]** - Choose randomly from options
        **{prefix}eightball [question]** - Ask the magic 8-ball
        **{prefix}meme** - Get a random meme
        """
        
        embed.add_field(name="Commands", value=commands_text, inline=False)
        
        return embed
    
    def get_other_embed(self):
        """Get other commands embed"""
        prefix = os.getenv('PREFIX', '!')
        
        embed = discord.Embed(
            title="📋 Other Commands",
            description="Additional utility and management commands",
            color=discord.Color.orange()
        )
        
        commands_text = f"""
        **{prefix}report [user] [reason]** - Report a user
        **{prefix}suggestions [suggestion]** - Submit a suggestion
        **{prefix}sayembed [title] [description]** - Send custom embed
        **{prefix}help** - Show this help menu
        """
        
        embed.add_field(name="Commands", value=commands_text, inline=False)
        
        embed.add_field(
            name="🤖 Bot Information",
            value="Spark Utility is an advanced Discord bot with comprehensive utility features and an advanced ticket system. All commands are logged to the bot owner for monitoring and debugging purposes.",
            inline=False
        )
        
        return embed

class Help(commands.Cog):
    """Custom help command system"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_before_invoke(self, ctx):
        """Log command before execution"""
        logging_cog = self.bot.get_cog('LoggingSystem')
        if logging_cog:
            args = ' '.join(ctx.args[2:]) if len(ctx.args) > 2 else ""
            await logging_cog.log_command(ctx, ctx.command.name, args)
    
    @commands.command(name='help')
    async def help_command(self, ctx, *, command: str = None):
        """Show help for commands"""
        if command is None:
            # Show main help menu
            prefix = os.getenv('PREFIX', '!')
            
            embed = discord.Embed(
                title="🚀 Spark Utility Bot",
                description="Advanced Discord utility bot with comprehensive features",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📋 Categories",
                value="Select a category below to view commands in that category",
                inline=False
            )
            
            embed.add_field(
                name="🔧 Quick Info",
                value=f"**Prefix:** `{prefix}`\n"
                      f"**Total Commands:** {len(self.bot.commands)}\n"
                      f"**Servers:** {len(self.bot.guilds)}\n"
                      f"**Users:** {len(self.bot.users)}",
                inline=True
            )
            
            embed.add_field(
                name="🎫 Ticket System",
                value="Advanced ticket system with interactive panels, staff management, and comprehensive logging",
                inline=True
            )
            
            embed.add_field(
                name="📊 Logging",
                value="All commands and actions are logged to the bot owner for monitoring and debugging",
                inline=True
            )
            
            embed.set_footer(text=f"Use {prefix}help [command] for detailed help on a specific command")
            
            view = HelpView(self.bot)
            await ctx.send(embed=embed, view=view)
            
        else:
            # Show help for specific command
            cmd = self.bot.get_command(command)
            if cmd is None:
                await ctx.send(f"❌ Command `{command}` not found!")
                return
            
            embed = discord.Embed(
                title=f"❓ Help: {cmd.name}",
                description=cmd.help or "No description available",
                color=discord.Color.blue()
            )
            
            # Add usage info
            prefix = os.getenv('PREFIX', '!')
            usage = f"{prefix}{cmd.name}"
            
            if cmd.signature:
                usage += f" {cmd.signature}"
            
            embed.add_field(name="Usage", value=f"`{usage}`", inline=False)
            
            # Add aliases if any
            if cmd.aliases:
                embed.add_field(name="Aliases", value=", ".join(f"`{alias}`" for alias in cmd.aliases), inline=False)
            
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
