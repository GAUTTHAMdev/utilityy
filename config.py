import os
from typing import Optional

class Config:
    """Configuration management for the bot"""
    
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.owner_id = int(os.getenv('OWNER_ID', 0))
        self.prefix = os.getenv('PREFIX', '!')
        
        # API Keys with fallbacks
        self.tinyurl_api_key = os.getenv('TINYURL_API_KEY', 'default_key')
        self.reddit_client_id = os.getenv('REDDIT_CLIENT_ID', 'default_id')
        self.reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET', 'default_secret')
        self.translate_api_key = os.getenv('TRANSLATE_API_KEY', 'default_key')
        
        # Bot settings
        self.max_ticket_per_user = 3
        self.ticket_auto_archive_hours = 24
        self.max_poll_options = 10
        self.max_reminder_hours = 168  # 7 days
        
    def validate(self) -> bool:
        """Validate required configuration"""
        if not self.bot_token:
            return False
        if not self.owner_id:
            return False
        return True
    
    def get_log_channel_id(self, guild_id: int) -> Optional[int]:
        """Get log channel ID for a guild"""
        # This would typically come from database
        return None
    
    def get_ticket_category_id(self, guild_id: int) -> Optional[int]:
        """Get ticket category ID for a guild"""
        # This would typically come from database
        return None
    
    def get_staff_role_ids(self, guild_id: int) -> list:
        """Get staff role IDs for a guild"""
        # This would typically come from database
        return []
