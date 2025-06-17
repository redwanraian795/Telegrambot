import asyncio
import random
from typing import List, Dict, Any
from telegram import Update, Bot
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import logging

logger = logging.getLogger(__name__)

class AnimationService:
    def __init__(self):
        self.mascot_name = "BotBuddy"
        self.loading_animations = {
            'dots': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
            'clock': ['🕐', '🕑', '🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚', '🕛'],
            'moon': ['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘'],
            'weather': ['☀️', '⛅', '☁️', '🌧️', '⛈️', '🌩️', '🌨️'],
            'growth': ['🌱', '🌿', '🌳', '🌲'],
            'magic': ['✨', '🌟', '⭐', '💫', '🔮'],
            'animals': ['🐱', '🐶', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼'],
            'tech': ['💻', '⚙️', '🔧', '🛠️', '🔍', '📡', '🤖'],
            'food': ['🍎', '🍌', '🍓', '🥕', '🌽', '🥖', '🧀', '🍕']
        }
        
        self.mascot_states = {
            'thinking': [
                f"🤖 {self.mascot_name} is thinking...",
                f"🧠 {self.mascot_name} is processing your request...",
                f"💭 {self.mascot_name} is analyzing...",
                f"🔍 {self.mascot_name} is searching for answers...",
                f"⚡ {self.mascot_name} is charging up the brain cells..."
            ],
            'working': [
                f"🔨 {self.mascot_name} is hard at work!",
                f"⚙️ {self.mascot_name} is spinning the gears...",
                f"🏗️ {self.mascot_name} is building your response...",
                f"🎨 {self.mascot_name} is crafting something special...",
                f"🔧 {self.mascot_name} is fine-tuning the results..."
            ],
            'downloading': [
                f"📥 {self.mascot_name} is fetching your file...",
                f"🌐 {self.mascot_name} is surfing the web...",
                f"📡 {self.mascot_name} is beaming down data...",
                f"🚀 {self.mascot_name} is launching download rockets...",
                f"🎯 {self.mascot_name} is targeting the perfect download..."
            ],
            'translating': [
                f"🌍 {self.mascot_name} is speaking all languages...",
                f"📚 {self.mascot_name} is consulting the dictionary...",
                f"🔤 {self.mascot_name} is juggling words...",
                f"🗣️ {self.mascot_name} is practicing pronunciation...",
                f"🌐 {self.mascot_name} is bridging language barriers..."
            ],
            'searching': [
                f"🔍 {self.mascot_name} is on a treasure hunt...",
                f"🕵️ Detective {self.mascot_name} is on the case...",
                f"📖 {self.mascot_name} is flipping through pages...",
                f"🎯 {self.mascot_name} is zeroing in on answers...",
                f"🗺️ {self.mascot_name} is exploring knowledge maps..."
            ],
            'analyzing': [
                f"🧪 {self.mascot_name} is mixing data potions...",
                f"🔬 {self.mascot_name} is under the microscope...",
                f"📊 {self.mascot_name} is crunching numbers...",
                f"🎲 {self.mascot_name} is rolling the dice of logic...",
                f"🧩 {self.mascot_name} is solving the puzzle..."
            ]
        }
        
        self.success_animations = [
            "🎉 Ta-da! Mission accomplished!",
            "✨ Voilà! Magic happened!",
            "🚀 Success achieved at light speed!",
            "🎯 Bullseye! Perfect hit!",
            "🌟 Stellar performance complete!",
            "🏆 Victory achieved!",
            "💫 Dream come true!",
            "🎊 Party time - it's done!"
        ]
        
        self.error_animations = [
            "😅 Oops! That didn't go as planned...",
            "🤔 Hmm, that's puzzling...",
            "🔧 Time for some troubleshooting!",
            "🎭 Plot twist! Let's try again...",
            "🌪️ Encountered a small tornado...",
            "🚧 Under construction - please wait!",
            "🔄 Rebooting the magic circuits...",
            "🎪 The circus got a bit chaotic..."
        ]
    
    async def show_loading_animation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                   animation_type: str = 'thinking', duration: int = 3) -> int:
        """Show animated loading with mascot interactions"""
        try:
            # Choose animation style based on type
            if animation_type in self.loading_animations:
                frames = self.loading_animations[animation_type]
            else:
                frames = self.loading_animations['dots']
            
            # Get mascot message
            mascot_messages = self.mascot_states.get(animation_type, self.mascot_states['thinking'])
            mascot_msg = random.choice(mascot_messages)
            
            # Send initial message
            message = await update.message.reply_text(f"{mascot_msg}\n{frames[0]}")
            message_id = message.message_id
            
            # Animate for specified duration
            frame_count = 0
            animation_cycles = duration * 2  # 2 cycles per second
            
            for i in range(animation_cycles):
                frame = frames[frame_count % len(frames)]
                progress_bar = self._create_progress_bar(i, animation_cycles)
                
                # Occasionally change mascot message for variety
                if i % 8 == 0 and i > 0:
                    mascot_msg = random.choice(mascot_messages)
                
                animated_text = f"{mascot_msg}\n{frame} {progress_bar}"
                
                try:
                    await context.bot.edit_message_text(
                        chat_id=update.effective_chat.id,
                        message_id=message_id,
                        text=animated_text
                    )
                except Exception:
                    # If edit fails, continue animation
                    pass
                
                frame_count += 1
                await asyncio.sleep(0.5)
            
            return message_id
            
        except Exception as e:
            logger.error(f"Animation error: {e}")
            return None
    
    def _create_progress_bar(self, current: int, total: int, length: int = 10) -> str:
        """Create animated progress bar"""
        progress = current / total
        filled = int(progress * length)
        bar = "█" * filled + "░" * (length - filled)
        percentage = int(progress * 100)
        return f"[{bar}] {percentage}%"
    
    async def show_typewriter_effect(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                   text: str, delay: float = 0.1) -> None:
        """Show typewriter effect for text"""
        try:
            message = await update.message.reply_text("✍️ Preparing your message...")
            message_id = message.message_id
            
            displayed_text = ""
            for i, char in enumerate(text):
                displayed_text += char
                
                # Add blinking cursor
                cursor_text = displayed_text + "▌"
                
                try:
                    await context.bot.edit_message_text(
                        chat_id=update.effective_chat.id,
                        message_id=message_id,
                        text=cursor_text,
                        parse_mode=ParseMode.MARKDOWN
                    )
                except Exception:
                    pass
                
                await asyncio.sleep(delay)
            
            # Final message without cursor
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=message_id,
                text=displayed_text,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Typewriter error: {e}")
    
    async def show_success_animation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                   message_id: int = None) -> None:
        """Show success animation"""
        try:
            success_msg = random.choice(self.success_animations)
            celebration = random.choice(['🎉🎊🎉', '✨🌟✨', '🚀🎯🚀', '🏆👑🏆'])
            
            final_text = f"{celebration}\n{success_msg}\n{celebration}"
            
            if message_id:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=message_id,
                    text=final_text
                )
            else:
                await update.message.reply_text(final_text)
                
        except Exception as e:
            logger.error(f"Success animation error: {e}")
    
    async def show_error_animation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                 message_id: int = None, error_msg: str = None) -> None:
        """Show error animation with mascot reaction"""
        try:
            error_animation = random.choice(self.error_animations)
            sad_face = random.choice(['😔', '😅', '🤕', '😵‍💫', '🥴'])
            
            if error_msg:
                final_text = f"{sad_face} {error_animation}\n\n❌ {error_msg}"
            else:
                final_text = f"{sad_face} {error_animation}"
            
            if message_id:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=message_id,
                    text=final_text
                )
            else:
                await update.message.reply_text(final_text)
                
        except Exception as e:
            logger.error(f"Error animation error: {e}")
    
    async def show_mascot_greeting(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show animated mascot greeting"""
        try:
            greetings = [
                f"👋 Hi there! I'm {self.mascot_name}, your friendly bot assistant!",
                f"🌟 Welcome! {self.mascot_name} at your service!",
                f"🎉 Hey! {self.mascot_name} is excited to help you!",
                f"🚀 Greetings! {self.mascot_name} ready for action!",
                f"✨ Hello! {self.mascot_name} here to make magic happen!"
            ]
            
            greeting = random.choice(greetings)
            
            # Animated entrance
            frames = ['🌟', '✨', '💫', '⭐', '🌟']
            message = await update.message.reply_text(frames[0])
            message_id = message.message_id
            
            for frame in frames:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=message_id,
                    text=f"{frame} Loading {self.mascot_name}... {frame}"
                )
                await asyncio.sleep(0.3)
            
            # Final greeting
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=message_id,
                text=greeting
            )
            
        except Exception as e:
            logger.error(f"Greeting animation error: {e}")
    
    async def show_random_mascot_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show random mascot interaction"""
        try:
            actions = [
                f"🎪 {self.mascot_name} is juggling data packets!",
                f"🎭 {self.mascot_name} is performing digital magic!",
                f"🎨 {self.mascot_name} is painting with pixels!",
                f"🎵 {self.mascot_name} is humming binary tunes!",
                f"🏃‍♂️ {self.mascot_name} is racing through algorithms!",
                f"🧘‍♂️ {self.mascot_name} is meditating on code!",
                f"🕺 {self.mascot_name} is dancing with databases!",
                f"🎯 {self.mascot_name} is targeting the perfect answer!"
            ]
            
            action = random.choice(actions)
            await update.message.reply_text(action)
            
        except Exception as e:
            logger.error(f"Random action error: {e}")
    
    def get_random_emoji_sequence(self, category: str = 'magic', count: int = 3) -> str:
        """Get random emoji sequence for animations"""
        if category in self.loading_animations:
            emojis = self.loading_animations[category]
            return ' '.join(random.choices(emojis, k=count))
        return '✨ 🌟 ✨'
    
    async def show_countdown_animation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                     seconds: int = 5, action: str = "magic") -> int:
        """Show countdown animation with mascot"""
        try:
            message = await update.message.reply_text(f"⏰ {self.mascot_name} starting countdown...")
            message_id = message.message_id
            
            for i in range(seconds, 0, -1):
                emoji = random.choice(['🔥', '💥', '⚡', '🚀', '🎯'])
                countdown_text = f"{emoji} {self.mascot_name} says: {i} seconds until {action}! {emoji}"
                
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=message_id,
                    text=countdown_text
                )
                await asyncio.sleep(1)
            
            # Final blast off
            blast_text = f"🚀💥 {action.upper()} TIME! 💥🚀"
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=message_id,
                text=blast_text
            )
            
            return message_id
            
        except Exception as e:
            logger.error(f"Countdown error: {e}")
            return None

# Global instance
animation_service = AnimationService()