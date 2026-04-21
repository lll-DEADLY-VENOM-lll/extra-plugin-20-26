import random
import asyncio
import re
from motor.motor_asyncio import AsyncIOMotorClient
from pyrogram import Client, filters
from pyrogram.enums import ChatAction, ChatMemberStatus
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery

# Configs - Ensure these are correct in your config.py
from config import MONGO_DB_URI as MONGO_URL
from VIPMUSIC import app as nexichat

# Database Connections
WORD_MONGO_URL = "mongodb+srv://vishalpandeynkp:Bal6Y6FZeQeoAoqV@cluster0.dzgwt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# MongoDB Clients (Async)
client = AsyncIOMotorClient(MONGO_URL)
word_client = AsyncIOMotorClient(WORD_MONGO_URL)

# Collections
db = client["ChatBotStatusDb"]
status_db = db["StatusCollection"]
word_db = word_client["Word"]["WordDb"]

# --- Anti-Abuse System (Hinglish Gali Filter) ---
# Yahan wo words hain jo bot na seekhega na bolega
BANNED_WORDS = [
    "chutiya", "madarchod", "behenchod", "mc", "bc", "mkl", 
    "randi", "gand", "saala", "loda", "lavda", "maderchod", 
    "bhenchod", "chut", "gaand", "harami", "kamina"
]

def is_clean(text):
    """Check if text is clean (No Hinglish Abuse)"""
    if not text: return False
    for word in BANNED_WORDS:
        if re.search(rf"\b{word}\b", text.lower()):
            return False
    return True

# --- Database Speed Optimization ---
async def create_indexes():
    await word_db.create_index("word")
    print("✅ Database Speed Optimized for Hinglish!")

asyncio.get_event_loop().create_task(create_indexes())

# --- Core Functions ---

async def save_reply(original_text, reply_message: Message):
    """Background mein Hinglish chatting save karega"""
    try:
        # 100 character se bade message bot na seekhe toh behtar hai (spam avoid karne ke liye)
        if not is_clean(original_text) or len(original_text) > 100: 
            return
        
        content = None
        check = "none"

        if reply_message.sticker:
            content = reply_message.sticker.file_id
            check = "sticker"
        elif reply_message.photo:
            content = reply_message.photo.file_id
            check = "photo"
        elif reply_message.text:
            if not is_clean(reply_message.text): return
            content = reply_message.text
            check = "none"

        if content:
            # Upsert=True se duplicate data nahi banta
            await word_db.update_one(
                {"word": original_text.lower(), "text": content},
                {"$set": {"check": check}},
                upsert=True
            )
    except Exception:
        pass

async def get_reply(word: str):
    """Fastest Random Reply fetcher using $sample"""
    cursor = word_db.aggregate([
        {"$match": {"word": word.lower()}},
        {"$sample": {"size": 1}}
    ])
    async for doc in cursor:
        return doc
    return None

# --- Chatbot Logic Handlers ---

@nexichat.on_message(filters.all & ~filters.bot, group=1)
async def chat_monitor(client: Client, message: Message):
    """Silent Learning: Har Hinglish chat ko piche se save karega"""
    if message.reply_to_message and message.reply_to_message.text:
        # Asyncio task taaki bot ki baki processing fast rahe
        asyncio.create_task(save_reply(message.reply_to_message.text, message))

@nexichat.on_message(filters.text & ~filters.bot, group=2)
async def chatbot_response(client: Client, message: Message):
    """Hinglish Auto-Reply Logic"""
    
    # 1. Check if Chatbot is ON
    chat_id = message.chat.id
    chat_status = await status_db.find_one({"chat_id": chat_id})
    if chat_status and chat_status.get("status") == "disabled":
        return

    text = message.text.lower().strip()

    # 2. Trigger Logic
    is_tagged = f"@{client.me.username}" in text
    is_reply_to_bot = (message.reply_to_message and message.reply_to_message.from_user.id == client.me.id)
    # 3 words tak ke messages par bot automatically reply dega (e.g. "Kaise ho bhai")
    is_common_hinglish = len(text.split()) <= 3 

    if is_tagged or is_reply_to_bot or is_common_hinglish or message.chat.type.name == "PRIVATE":
        if not is_clean(text): return # Gali par reply nahi
        
        # Query text prepare karna
        query_text = text.replace(f"@{client.me.username}", "").strip()
        if not query_text:
            if is_reply_to_bot: query_text = "hi"
            else: return

        # 3. Fetch from DB
        reply_data = await get_reply(query_text)

        if reply_data:
            await client.send_chat_action(chat_id, ChatAction.TYPING)
            
            content = reply_data["text"]
            check = reply_data["check"]

            if check == "sticker":
                await message.reply_sticker(content)
            elif check == "photo":
                await message.reply_photo(content)
            else:
                # No translation needed, directly send Hinglish text
                await message.reply_text(content)

# --- Chatbot ON/OFF Control ---

@nexichat.on_message(filters.command("chatbot"))
async def toggle_chatbot(client: Client, message: Message):
    """Admin only command to turn bot ON/OFF"""
    if message.chat.type.name != "PRIVATE":
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("❌ Sirf Admins hi chatbot control kar sakte hain.")

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Enable ✅", callback_data="cb_on"),
            InlineKeyboardButton("Disable ❌", callback_data="cb_off")
        ]
    ])
    await message.reply_text(
        f"**Hinglish Chatbot Settings: {message.chat.title}**\n\n"
        "Status: `Active (Hinglish Mode)` 🇮🇳\n"
        "Filter: `Anti-Abuse ON` 🛡️",
        reply_markup=buttons
    )

@nexichat.on_callback_query(filters.regex(r"cb_"))
async def chatbot_callback(client: Client, query: CallbackQuery):
    chat_id = query.message.chat.id
    data = query.data
    
    if data == "cb_on":
        await status_db.update_one({"chat_id": chat_id}, {"$set": {"status": "enabled"}}, upsert=True)
        await query.answer("Chatbot Enabled!", show_alert=True)
        await query.edit_message_text(f"✅ **Chatbot ab chalu hai aur Hinglish seekh raha hai.**")
        
    elif data == "cb_off":
        await status_db.update_one({"chat_id": chat_id}, {"$set": {"status": "disabled"}}, upsert=True)
        await query.answer("Chatbot Disabled!", show_alert=True)
        await query.edit_message_text(f"❌ **Chatbot ko band kar diya gaya hai.**")

__MODULE__ = "Chatbot"
__HELP__ = "/chatbot - Group mein chatbot ON ya OFF karne ke liye."
