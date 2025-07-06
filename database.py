import sqlite3
import asyncio
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
import aiosqlite

class Database:
    """Database management for the bot"""
    
    def __init__(self, db_path: str = "spark_utility.db"):
        self.db_path = db_path
    
    def init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Guild settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS guild_settings (
                    guild_id INTEGER PRIMARY KEY,
                    log_channel_id INTEGER,
                    ticket_category_id INTEGER,
                    staff_role_ids TEXT,
                    ticket_log_channel_id INTEGER,
                    auto_archive_hours INTEGER DEFAULT 24,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tickets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    channel_id INTEGER,
                    user_id INTEGER,
                    staff_id INTEGER,
                    category TEXT,
                    status TEXT DEFAULT 'open',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    closed_at TIMESTAMP,
                    messages_count INTEGER DEFAULT 0
                )
            ''')
            
            # AFK table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS afk_users (
                    user_id INTEGER PRIMARY KEY,
                    guild_id INTEGER,
                    reason TEXT,
                    set_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Reminders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    guild_id INTEGER,
                    channel_id INTEGER,
                    message TEXT,
                    remind_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Reports table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    reporter_id INTEGER,
                    reported_id INTEGER,
                    reason TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Suggestions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS suggestions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    suggestion TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    async def get_guild_settings(self, guild_id: int) -> Optional[Dict]:
        """Get guild settings"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                'SELECT * FROM guild_settings WHERE guild_id = ?',
                (guild_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        'guild_id': row[0],
                        'log_channel_id': row[1],
                        'ticket_category_id': row[2],
                        'staff_role_ids': json.loads(row[3]) if row[3] else [],
                        'ticket_log_channel_id': row[4],
                        'auto_archive_hours': row[5],
                        'created_at': row[6]
                    }
                return None
    
    async def set_guild_setting(self, guild_id: int, setting: str, value: Any):
        """Set a guild setting"""
        async with aiosqlite.connect(self.db_path) as db:
            # Check if guild exists
            async with db.execute(
                'SELECT 1 FROM guild_settings WHERE guild_id = ?',
                (guild_id,)
            ) as cursor:
                exists = await cursor.fetchone()
            
            if exists:
                await db.execute(
                    f'UPDATE guild_settings SET {setting} = ? WHERE guild_id = ?',
                    (value, guild_id)
                )
            else:
                await db.execute(
                    f'INSERT INTO guild_settings (guild_id, {setting}) VALUES (?, ?)',
                    (guild_id, value)
                )
            
            await db.commit()
    
    async def create_ticket(self, guild_id: int, channel_id: int, user_id: int, category: str) -> int:
        """Create a new ticket"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                'INSERT INTO tickets (guild_id, channel_id, user_id, category) VALUES (?, ?, ?, ?)',
                (guild_id, channel_id, user_id, category)
            ) as cursor:
                ticket_id = cursor.lastrowid
                await db.commit()
                return ticket_id
    
    async def get_ticket(self, channel_id: int) -> Optional[Dict]:
        """Get ticket by channel ID"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                'SELECT * FROM tickets WHERE channel_id = ?',
                (channel_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'guild_id': row[1],
                        'channel_id': row[2],
                        'user_id': row[3],
                        'staff_id': row[4],
                        'category': row[5],
                        'status': row[6],
                        'created_at': row[7],
                        'closed_at': row[8],
                        'messages_count': row[9]
                    }
                return None
    
    async def update_ticket(self, channel_id: int, **kwargs):
        """Update ticket information"""
        async with aiosqlite.connect(self.db_path) as db:
            for key, value in kwargs.items():
                await db.execute(
                    f'UPDATE tickets SET {key} = ? WHERE channel_id = ?',
                    (value, channel_id)
                )
            await db.commit()
    
    async def get_user_tickets(self, user_id: int, guild_id: int) -> List[Dict]:
        """Get all open tickets for a user"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                'SELECT * FROM tickets WHERE user_id = ? AND guild_id = ? AND status = "open"',
                (user_id, guild_id)
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        'id': row[0],
                        'guild_id': row[1],
                        'channel_id': row[2],
                        'user_id': row[3],
                        'staff_id': row[4],
                        'category': row[5],
                        'status': row[6],
                        'created_at': row[7],
                        'closed_at': row[8],
                        'messages_count': row[9]
                    }
                    for row in rows
                ]
    
    async def get_ticket_stats(self, guild_id: int) -> Dict:
        """Get ticket statistics for a guild"""
        async with aiosqlite.connect(self.db_path) as db:
            # Total tickets
            async with db.execute(
                'SELECT COUNT(*) FROM tickets WHERE guild_id = ?',
                (guild_id,)
            ) as cursor:
                total_tickets = (await cursor.fetchone())[0]
            
            # Open tickets
            async with db.execute(
                'SELECT COUNT(*) FROM tickets WHERE guild_id = ? AND status = "open"',
                (guild_id,)
            ) as cursor:
                open_tickets = (await cursor.fetchone())[0]
            
            # Closed tickets
            async with db.execute(
                'SELECT COUNT(*) FROM tickets WHERE guild_id = ? AND status = "closed"',
                (guild_id,)
            ) as cursor:
                closed_tickets = (await cursor.fetchone())[0]
            
            return {
                'total': total_tickets,
                'open': open_tickets,
                'closed': closed_tickets
            }
    
    async def set_afk(self, user_id: int, guild_id: int, reason: str):
        """Set user as AFK"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'INSERT OR REPLACE INTO afk_users (user_id, guild_id, reason) VALUES (?, ?, ?)',
                (user_id, guild_id, reason)
            )
            await db.commit()
    
    async def get_afk(self, user_id: int, guild_id: int) -> Optional[Dict]:
        """Get AFK status for user"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                'SELECT * FROM afk_users WHERE user_id = ? AND guild_id = ?',
                (user_id, guild_id)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        'user_id': row[0],
                        'guild_id': row[1],
                        'reason': row[2],
                        'set_at': row[3]
                    }
                return None
    
    async def remove_afk(self, user_id: int, guild_id: int):
        """Remove AFK status"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'DELETE FROM afk_users WHERE user_id = ? AND guild_id = ?',
                (user_id, guild_id)
            )
            await db.commit()
    
    async def add_reminder(self, user_id: int, guild_id: int, channel_id: int, message: str, remind_at: datetime) -> int:
        """Add a reminder"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                'INSERT INTO reminders (user_id, guild_id, channel_id, message, remind_at) VALUES (?, ?, ?, ?, ?)',
                (user_id, guild_id, channel_id, message, remind_at)
            ) as cursor:
                reminder_id = cursor.lastrowid
                await db.commit()
                return reminder_id
    
    async def get_due_reminders(self) -> List[Dict]:
        """Get all due reminders"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                'SELECT * FROM reminders WHERE remind_at <= ?',
                (datetime.utcnow(),)
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        'id': row[0],
                        'user_id': row[1],
                        'guild_id': row[2],
                        'channel_id': row[3],
                        'message': row[4],
                        'remind_at': row[5],
                        'created_at': row[6]
                    }
                    for row in rows
                ]
    
    async def delete_reminder(self, reminder_id: int):
        """Delete a reminder"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'DELETE FROM reminders WHERE id = ?',
                (reminder_id,)
            )
            await db.commit()
    
    async def add_report(self, guild_id: int, reporter_id: int, reported_id: int, reason: str) -> int:
        """Add a report"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                'INSERT INTO reports (guild_id, reporter_id, reported_id, reason) VALUES (?, ?, ?, ?)',
                (guild_id, reporter_id, reported_id, reason)
            ) as cursor:
                report_id = cursor.lastrowid
                await db.commit()
                return report_id
    
    async def add_suggestion(self, guild_id: int, user_id: int, suggestion: str) -> int:
        """Add a suggestion"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                'INSERT INTO suggestions (guild_id, user_id, suggestion) VALUES (?, ?, ?)',
                (guild_id, user_id, suggestion)
            ) as cursor:
                suggestion_id = cursor.lastrowid
                await db.commit()
                return suggestion_id
