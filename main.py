import os
import asyncio
import traceback
from datetime import datetime
import discord
from discord.ext import commands
import sqlite3
import logging

from config import Config
from database import Database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SparkUtilityBot(commands.Bot):
    def __init__(self):
        # Get prefix from environment
        prefix = os.getenv('PREFIX', '!')
        
        # Initialize bot with intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.reactions = True
        
        super().__init__(
            command_prefix=prefix,
            intents=intents,
            help_command=None,  # We'll use custom help
            case_insensitive=True
        )
        
        # Bot configuration
        self.config = Config()
        self.db = Database()
        self.start_time = datetime.utcnow()
        
        # Initialize database
        self.db.init_db()
        
    async def setup_hook(self):
        """Load all cogs and setup the bot"""
        logger.info("🔄 Starting setup_hook...")
        
        cogs_to_load = [
            'cogs.logging_system',
            'cogs.utility', 
            'cogs.moderation',
            'cogs.tickets',
            'cogs.help'
        ]
        
        logger.info(f"📦 Attempting to load {len(cogs_to_load)} cogs...")
        
        for cog in cogs_to_load:
            try:
                logger.info(f"🔄 Loading cog: {cog}")
                await self.load_extension(cog)
                logger.info(f"✅ Successfully loaded cog: {cog}")
            except Exception as e:
                logger.error(f"❌ Failed to load cog {cog}: {e}")
                traceback.print_exc()
        
        logger.info("🚀 Cog loading process completed")
        logger.info(f"📋 Final loaded cogs: {list(self.cogs.keys())}")
        logger.info(f"🔧 Final available commands: {[cmd.name for cmd in self.commands]}")
        
        # Sync slash commands (if needed)
        try:
            synced = await self.tree.sync()
            logger.info(f"🔄 Synced {len(synced)} slash commands")
        except Exception as e:
            logger.error(f"❌ Failed to sync slash commands: {e}")
            
    async def load_cogs_manually(self):
        """Alternative method to load cogs if setup_hook fails"""
        logger.info("🔄 Manually loading cogs...")
        
        cogs_to_load = [
            'cogs.logging_system',
            'cogs.utility', 
            'cogs.moderation',
            'cogs.tickets',
            'cogs.help'
        ]
        
        for cog in cogs_to_load:
            try:
                logger.info(f"🔄 Manually loading cog: {cog}")
                await self.load_extension(cog)
                logger.info(f"✅ Manually loaded cog: {cog}")
            except Exception as e:
                logger.error(f"❌ Failed to manually load cog {cog}: {e}")
                traceback.print_exc()
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"{self.user} has connected to Discord!")
        
        # Check if cogs are loaded, if not load them manually
        if not self.cogs:
            logger.warning("⚠️ No cogs loaded in setup_hook, attempting manual load...")
            await self.load_cogs_manually()
        
        # Set bot status
        prefix = os.getenv('PREFIX', '!')
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"Spark Utility | {prefix}help"
        )
        await self.change_presence(activity=activity)
        
        # Log loaded cogs
        logger.info(f"📋 Available cogs: {list(self.cogs.keys())}")
        logger.info(f"🔧 Available commands: {[cmd.name for cmd in self.commands]}")
        
        # Log to owner
        try:
            owner_id = int(os.getenv('OWNER_ID'))
            owner = await self.fetch_user(owner_id)
            
            embed = discord.Embed(
                title="🚀 Spark Utility Bot Online",
                description="Bot has successfully started and is ready to serve!",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Bot User", value=f"{self.user} ({self.user.id})", inline=False)
            embed.add_field(name="Guilds", value=len(self.guilds), inline=True)
            embed.add_field(name="Users", value=len(self.users), inline=True)
            embed.add_field(name="Prefix", value=prefix, inline=True)
            embed.add_field(name="Commands", value=len(self.commands), inline=True)
            embed.add_field(name="Cogs", value=len(self.cogs), inline=True)
            
            await owner.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Could not send startup message to owner: {e}")
    
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        # Log error to owner
        try:
            logging_cog = self.get_cog('LoggingSystem')
            if logging_cog:
                await logging_cog.log_error(ctx, error)
        except Exception as e:
            logger.error(f"Error in logging system: {e}")
        
        # Handle specific errors
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore command not found errors
        
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
            
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
            
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ I don't have the required permissions to execute this command.")
            
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ Command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
            
        else:
            # Log unexpected errors
            logger.error(f"Unexpected error in command {ctx.command}: {error}")
            await ctx.send("❌ An unexpected error occurred. The bot owner has been notified.")
    
    async def on_message(self, message):
        """Process messages"""
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Process AFK system
        try:
            utility_cog = self.get_cog('Utility')
            if utility_cog:
                await utility_cog.check_afk(message)
        except Exception as e:
            logger.error(f"Error in AFK system: {e}")
        
        # Process commands
        await self.process_commands(message)
    
    async def close(self):
        """Clean shutdown"""
        logger.info("Bot is shutting down...")
        await super().close()

async def main():
    """Main function to run the bot"""
    # Check required environment variables
    required_vars = ['BOT_TOKEN', 'OWNER_ID', 'PREFIX']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"✅ Spark Utility Discord Bot is ready to deploy!")
        print(f"📋 Missing environment variables: {', '.join(missing_vars)}")
        print("\n🔧 Bot Features:")
        print("   • Comprehensive utility commands (ping, serverinfo, userinfo, etc.)")
        print("   • Advanced ticket system with interactive panels")
        print("   • Moderation tools (ban, kick, clear, timeout)")
        print("   • Fun commands (poll, calculator, quotes, meme)")
        print("   • Complete logging system to owner DMs")
        print("   • Customizable prefix and settings")
        print("\n🚀 To start the bot:")
        print("   1. Set BOT_TOKEN environment variable with your Discord bot token")
        print("   2. Set OWNER_ID environment variable with your Discord user ID")
        print("   3. Set PREFIX environment variable with your desired command prefix")
        print("\n💡 All commands and actions are logged to the bot owner's DMs")
        print("   Use '!logs set' command to also log to a server channel")
        return
    
    # Create and run bot
    bot = SparkUtilityBot()
    
    try:
        await bot.start(os.getenv('BOT_TOKEN'))
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        traceback.print_exc()
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
