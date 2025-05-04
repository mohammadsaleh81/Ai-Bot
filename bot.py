from telethon import TelegramClient, events, Button
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import User, MessageEntityUrl
import os
from dotenv import load_dotenv
import asyncio
import signal
import sys
from datetime import datetime
import re
import aiohttp
from insta import get_insta_data, get_insta_posts

# Load environment variables
load_dotenv()

# Telegram API credentials
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Initialize the client
client = None

# Store registered users with their registration date, coins, and history
registered_users = {}

# Define coin costs for Instagram profile analysis
INSTAGRAM_COST = 5  # Cost to analyze an Instagram profile

# Initial coins for new users
INITIAL_COINS = 50

# Maximum history items to store per user
MAX_HISTORY = 10

# Coin recharge amounts
RECHARGE_AMOUNTS = {
    'small': 100,    # 100 coins
    'medium': 500,   # 500 coins
    'large': 1000    # 1000 coins
}

async def get_instagram_profile_url(username):
    """Get Instagram profile URL from username"""
    return f"https://www.instagram.com/{username}/"

@events.register(events.NewMessage(pattern='/start'))
async def start_handler(event):
    """Handle the /start command"""
    user_id = event.sender_id
    if user_id not in registered_users:
        registered_users[user_id] = {
            'date': datetime.now(),
            'coins': INITIAL_COINS,
            'history': []
        }
        # Create profile buttons
        buttons = [
            [Button.inline("📊 آنالیز پیج", b"analyze")],
            [Button.inline("📜 تاریخچه", b"history")],
            [Button.inline("💰 سکه‌های من", b"coins")],
            [Button.inline("💎 شارژ سکه", b"recharge")],
            [Button.inline("❓ راهنما", b"help")]
        ]
        await event.respond('سلام! به ربات خوش آمدید. شما با موفقیت ثبت نام شدید.', buttons=buttons)
    else:
        buttons = [
            [Button.inline("📊 آنالیز پیج", b"analyze")],
            [Button.inline("📜 تاریخچه", b"history")],
            [Button.inline("💰 سکه‌های من", b"coins")],
            [Button.inline("💎 شارژ سکه", b"recharge")],
            [Button.inline("❓ راهنما", b"help")]
        ]
        await event.respond('شما قبلاً ثبت نام کرده‌اید.', buttons=buttons)

@events.register(events.CallbackQuery)
async def callback_handler(event):
    """Handle button callbacks"""
    data = event.data.decode('utf-8')
    user_id = event.sender_id
    
    if data == "analyze":
        analyze_text = """
📊 آنالیز پیج اینستاگرام:
لطفاً نام کاربری (username) پیج اینستاگرام را ارسال کنید.
💰 هزینه: {INSTAGRAM_COST} سکه
"""
        buttons = [[Button.inline("🔙 بازگشت", b"back")]]
        await event.answer()
        await event.edit(analyze_text, buttons=buttons)
    
    elif data == "history":
        if not registered_users[user_id]['history']:
            history_text = "📜 تاریخچه خالی است."
        else:
            history_text = "📜 تاریخچه آنالیزهای اخیر:\n\n"
            for item in registered_users[user_id]['history'][-MAX_HISTORY:]:
                history_text += f"👤 پیج: {item['username']}\n"
                history_text += f"📅 تاریخ: {item['date'].strftime('%Y-%m-%d %H:%M')}\n"
                history_text += "➖➖➖➖➖➖➖➖➖➖\n"
        
        buttons = [[Button.inline("🔙 بازگشت", b"back")]]
        await event.answer()
        await event.edit(history_text, buttons=buttons)
    
    elif data == "coins":
        coins_text = f"""
💰 وضعیت سکه‌های شما:
• سکه‌های موجود: {registered_users[user_id]['coins']}
• هزینه آنالیز پیج: {INSTAGRAM_COST} سکه
"""
        buttons = [[Button.inline("🔙 بازگشت", b"back")]]
        await event.answer()
        await event.edit(coins_text, buttons=buttons)
    
    elif data == "recharge":
        recharge_text = """
💎 شارژ سکه:
لطفاً یکی از پکیج‌های زیر را انتخاب کنید:

1️⃣ پکیج کوچک: 100 سکه
2️⃣ پکیج متوسط: 500 سکه
3️⃣ پکیج بزرگ: 1000 سکه

برای شارژ سکه، لطفاً با ادمین ربات در ارتباط باشید.
"""
        buttons = [
            [Button.inline("🔙 بازگشت", b"back")]
        ]
        await event.answer()
        await event.edit(recharge_text, buttons=buttons)
    
    elif data == "help":
        help_text = """
❓ راهنمای استفاده از ربات:
1. روی دکمه "آنالیز پیج" کلیک کنید
2. نام کاربری (username) پیج اینستاگرام را ارسال کنید
3. ربات لینک پیج را برای شما برمی‌گرداند
4. برای هر آنالیز {INSTAGRAM_COST} سکه هزینه دارد
"""
        buttons = [[Button.inline("🔙 بازگشت", b"back")]]
        await event.answer()
        await event.edit(help_text, buttons=buttons)
    
    elif data == "back":
        buttons = [
            [Button.inline("📊 آنالیز پیج", b"analyze")],
            [Button.inline("📜 تاریخچه", b"history")],
            [Button.inline("💰 سکه‌های من", b"coins")],
            [Button.inline("💎 شارژ سکه", b"recharge")],
            [Button.inline("❓ راهنما", b"help")]
        ]
        await event.answer()
        await event.edit("منوی اصلی:", buttons=buttons)

@events.register(events.NewMessage)
async def message_handler(event):
    """Handle incoming messages"""
    user_id = event.sender_id
    
    # Check if user is registered
    if user_id not in registered_users:
        buttons = [
            [Button.inline("📊 آنالیز پیج", b"analyze")],
            [Button.inline("📜 تاریخچه", b"history")],
            [Button.inline("💰 سکه‌های من", b"coins")],
            [Button.inline("💎 شارژ سکه", b"recharge")],
            [Button.inline("❓ راهنما", b"help")]
        ]
        await event.respond('لطفاً ابتدا با دستور /start ثبت نام کنید.', buttons=buttons)
        return

    # Ignore commands
    if event.message.text.startswith('/'):
        return

    # Handle Instagram username
    username = event.message.text.strip().replace('@', '')
    
    # Check if user has enough coins
    if registered_users[user_id]['coins'] < INSTAGRAM_COST:
        await event.respond(f"❌ سکه‌های شما کافی نیست! برای آنالیز پیج به {INSTAGRAM_COST} سکه نیاز دارید.")
        return
    
    # Deduct coins
    registered_users[user_id]['coins'] -= INSTAGRAM_COST
    
    # Send processing message
    processing_msg = await event.respond(f'در حال آنالیز پیج اینستاگرام...\n💰 سکه‌های باقیمانده: {registered_users[user_id]["coins"]}')
    
    try:
        # Get profile data using the insta.py function
        profile_data = get_insta_data(username)
        posts_data = get_insta_posts(username)
        
        if not profile_data:
            await processing_msg.edit("❌ خطا در دریافت اطلاعات پیج. لطفاً دوباره تلاش کنید.")
            return
            
        # Get user data from profile response
        user_data = profile_data.get('data', {}).get('user', {})
        
        # Add to history
        history_item = {
            'username': username,
            'date': datetime.now(),
            'followers': user_data.get('edge_followed_by', {}).get('count', 'نامشخص'),
            'following': user_data.get('edge_follow', {}).get('count', 'نامشخص'),
            'posts': user_data.get('edge_owner_to_timeline_media', {}).get('count', 'نامشخص')
        }
        registered_users[user_id]['history'].append(history_item)
        
        # Format and send the response
        response_text = f"""
📱 اطلاعات پیج اینستاگرام:
👤 نام کاربری: {username}
👥 تعداد فالوور: {user_data.get('edge_followed_by', {}).get('count', 'نامشخص')}
👤 تعداد فالووینگ: {user_data.get('edge_follow', {}).get('count', 'نامشخص')}
📸 تعداد پست‌ها: {user_data.get('edge_owner_to_timeline_media', {}).get('count', 'نامشخص')}
🔗 لینک پیج: https://instagram.com/{username}

📸 عکس پروفایل:
{user_data.get('profile_pic_url_hd', 'بدون عکس')}

📝 بایو:
{user_data.get('biography', 'بدون بایو')}

🔗 لینک‌های بایو:
"""
        
        # Add bio links
        bio_links = user_data.get('bio_links', [])
        if bio_links:
            for link in bio_links:
                response_text += f"• {link.get('title', 'بدون عنوان')}: {link.get('url', 'بدون لینک')}\n"
        else:
            response_text += "بدون لینک\n"

        response_text += "\n📊 اطلاعات پست‌های اخیر:\n"
        
        # Add recent posts information
        timeline_media = user_data.get('edge_owner_to_timeline_media', {})
        posts = timeline_media.get('edges', [])
        
        if posts:
            for i, post_edge in enumerate(posts[:5], 1):  # Show last 5 posts
                post = post_edge.get('node', {})
                response_text += f"""
📌 پست {i}:
❤️ لایک: {post.get('edge_liked_by', {}).get('count', 'نامشخص')}
💬 کامنت: {post.get('edge_media_to_comment', {}).get('count', 'نامشخص')}
📅 تاریخ: {post.get('taken_at_timestamp', 'نامشخص')}
🔗 لینک: https://instagram.com/p/{post.get('shortcode', '')}
"""
        else:
            response_text += "❌ اطلاعات پست‌ها در دسترس نیست. لطفاً بعداً دوباره تلاش کنید."
        
        await processing_msg.edit(response_text)
        
        # Add back button after showing results
        buttons = [[Button.inline("🔙 بازگشت به منوی اصلی", b"back")]]
        await event.respond("برای بازگشت به منوی اصلی روی دکمه زیر کلیک کنید:", buttons=buttons)
        
    except Exception as e:
        print(f"Error in message handler: {str(e)}")
        await processing_msg.edit(f"❌ خطا در دریافت اطلاعات پیج: {str(e)}")
        
        # Add back button even if there's an error
        buttons = [[Button.inline("🔙 بازگشت به منوی اصلی", b"back")]]
        await event.respond("برای بازگشت به منوی اصلی روی دکمه زیر کلیک کنید:", buttons=buttons)

async def shutdown(signal, loop):
    """Cleanup tasks tied to the service's shutdown."""
    print(f"Received exit signal {signal.name}...")
    
    # Cancel all running tasks
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    
    print(f"Cancelling {len(tasks)} outstanding tasks")
    
    # Wait for all tasks to complete
    await asyncio.gather(*tasks, return_exceptions=True)
    
    # Disconnect the client
    if client:
        await client.disconnect()
    
    # Stop the loop
    loop.stop()

def handle_exception(loop, context):
    """Handle exceptions that escape the event loop."""
    msg = context.get("exception", context["message"])
    print(f"Caught exception: {msg}")

async def main():
    """Main function to run the bot"""
    global client
    
    # Create new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Set exception handler
    loop.set_exception_handler(handle_exception)
    
    # Initialize client
    client = TelegramClient('bot_session', API_ID, API_HASH)
    
    # Add signal handlers
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda s=sig: asyncio.create_task(shutdown(s, loop))
        )
    
    try:
        # Start the client
        await client.start(bot_token=BOT_TOKEN)
        
        # Register event handlers
        client.add_event_handler(start_handler)
        client.add_event_handler(message_handler)
        client.add_event_handler(callback_handler)
        
        print('Bot is running...')
        
        # Run until disconnected
        await client.run_until_disconnected()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if client:
            await client.disconnect()
        loop.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Received exit signal")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1) 