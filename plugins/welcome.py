import asyncio
import re
import os
from logging import getLogger
from time import time
from pyrogram import enums, filters
from pyrogram.types import ChatMemberUpdated, InlineKeyboardButton, InlineKeyboardMarkup
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFont
from pytz import timezone
from datetime import datetime
from pymongo import MongoClient
import config
from VIPMUSIC import app # Aapka bot instance

# --- Database Setup ---
welcomedb = MongoClient(config.MONGO_DB_URI)
status_db = welcomedb.welcome_status_db.status

# --- Spam Protection Vars ---
user_last_message_time = {}
user_command_count = {}
SPAM_THRESHOLD = 2
SPAM_WINDOW_SECONDS = 5

LOGGER = getLogger(__name__)

# --- Helper Functions ---

def convert_to_small_caps(text):
    mapping = str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘϙʀꜱᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘϙʀꜱᴛᴜᴠᴡxʏᴢ",
    )
    return text.translate(mapping)

def circle(pfp, size=(415, 415)):
    """User ki profile pic ko round circle banane ke liye"""
    pfp = pfp.resize(size, Image.Resampling.LANCZOS).convert("RGBA")
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    pfp.putalpha(mask)
    return pfp

def welcomepic(user_id, user_username, user_names, chat_name, user_photo):
    # Template Image open karein (Aapki image)
    background = Image.open("assets/welcome.png").convert("RGBA")
    
    # Profile Photo process
    try:
        user_img = Image.open(user_photo).convert("RGBA")
    except:
        user_img = Image.open("assets/nodp.png").convert("RGBA")
        
    pfp = circle(user_img, size=(385, 385)) # Size adjusted for the template circle

    # Profile Picture placement (Template ke bade circle ke andar)
    background.paste(pfp, (595, 165), pfp)
    
    draw = ImageDraw.Draw(background)
    
    # --- Multiple Fonts Usage ---
    try:
        font_bold = ImageFont.truetype("assets/font1.ttf", size=50) # Bold style
        font_regular = ImageFont.truetype("assets/font2.ttf", size=35) # Light style
    except:
        font_bold = font_regular = ImageFont.load_default()

    # Colors
    cyan = (0, 255, 255)
    white = (255, 255, 255)

    # Text on Left Side (Black area)
    draw.text((60, 280), f"NAME: {user_names[:15]}", fill=cyan, font=font_bold)
    draw.text((60, 360), f"ID: {user_id}", fill=white, font=font_regular)
    draw.text((60, 410), f"USER: {user_username[:18]}", fill=white, font=font_regular)
    draw.text((60, 460), f"CHAT: {chat_name[:15]}", fill=cyan, font=font_regular)
    
    # Save output
    out_path = f"downloads/welcome_{user_id}.png"
    background.convert("RGB").save(out_path)
    return out_path

# --- Database Handlers ---
async def get_welcome_status(chat_id):
    status = status_db.find_one({"chat_id": chat_id})
    return status.get("welcome", "on") if status else "on"

async def set_welcome_status(chat_id, state):
    status_db.update_one({"chat_id": chat_id}, {"$set": {"welcome": state}}, upsert=True)

# --- Bot Commands ---

@app.on_message(filters.command("welcome") & ~filters.private)
async def welcome_cmd(_, message):
    user_id = message.from_user.id
    current_time = time()
    last_time = user_last_message_time.get(user_id, 0)
    
    if current_time - last_time < SPAM_WINDOW_SECONDS:
        return
    user_last_message_time[user_id] = current_time

    if len(message.command) == 1:
        return await message.reply_text("**Usage:**\n`/welcome on` or `/welcome off`")

    chat_id = message.chat.id
    user = await app.get_chat_member(chat_id, user_id)
    
    if user.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        state = message.text.split(None, 1)[1].strip().lower()
        if state in ["on", "off"]:
            await set_welcome_status(chat_id, state)
            await message.reply_text(f"**Welcome notification turned {state}!**")
        else:
            await message.reply_text("**Usage:** `/welcome on` or `/welcome off`")
    else:
        await message.reply("**Only admins can use this command!**")

# --- Chat Member Handler ---

@app.on_chat_member_updated(filters.group, group=-4)
async def greet_new_members(_, member: ChatMemberUpdated):
    try:
        if not (member.new_chat_member and not member.old_chat_member):
            return

        chat_id = member.chat.id
        if await get_welcome_status(chat_id) == "off":
            return

        user = member.new_chat_member.user
        chat_title = member.chat.title
        
        user_id = user.id
        user_name = user.first_name if user.first_name else "New Member"
        user_username = f"@{user.username}" if user.username else "No Username"
        
        # Download PFP
        try:
            photo_file = await app.download_media(user.photo.big_file_id, file_name=f"pfp_{user_id}.png")
        except:
            photo_file = "assets/nodp.png"

        # Image generation
        welcome_img = welcomepic(user_id, user_username, user_name, chat_title, photo_file)
        
        # --- YOUR NEW CUSTOM WELCOME TEXT ---
        welcome_text = (
            f"◦•●◉✿ ᴡᴇʟᴄᴏᴍᴇ ʙᴀʙʏ ✿◉●•◦\n"
            f"▰▱▱▱▱▱▱▱▱▱▱▱▱▱▰\n\n"
            f"● ɴᴀᴍᴇ ➥ {user.mention}\n"
            f"● ᴜsᴇʀɴᴀᴍᴇ ➥ {user_username}\n"
            f"● ᴜsᴇʀ ɪᴅ ➥ `{user_id}`\n\n"
            f"❖ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ➥ ˹ᴀᴀʀᴜ ᴍᴜsɪᴄ˼ ♡〬\n"
            f"▰▱▱▱▱▱▱▱▱▱▱▱▱▱▰"
        )
        
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("๏ add me in new group ๏", url=f"https://t.me/{app.username}?startgroup=true")]
        ])

        await app.send_photo(chat_id, photo=welcome_img, caption=welcome_text, reply_markup=reply_markup)
        
        # Clean files
        if os.path.exists(welcome_img): os.remove(welcome_img)
        if photo_file != "assets/nodp.png" and os.path.exists(photo_file): os.remove(photo_file)

    except Exception as e:
        LOGGER.error(f"Error: {e}")

# --- Metadata Section ---

__MODULE__ = "Wᴇᴄᴏᴍᴇ"
__HELP__ = """
## Aᴜᴛᴏ-Wᴇᴄᴏᴍᴇ Mᴏᴅᴜᴇ Cᴏᴍᴍᴀɴᴅs

### Cᴏᴍᴍᴀɴᴅ: /ᴀᴡᴇᴄᴏᴍᴇ
**Dᴇsᴄʀɪᴘᴛɪᴏɴ:**
Eɴᴀʙᴇs ᴏʀ ᴅɪsᴀʙᴇs ᴛʜᴇ ᴀᴜᴛᴏ-ᴡᴇᴄᴏᴍᴇ ғᴇᴀᴛᴜʀᴇ ɪɴ ᴀ ɢʀᴏᴜᴘ ᴄʜᴀᴛ.

**Usᴀɢᴇ:**
/welcome [ᴏɴ|ᴏғғ] (ғᴏʀ ʙᴏᴛ)

/awelcome [ᴏɴ|ᴏғғ] (ғᴏʀ ᴀssɪsᴛᴀɴᴄᴇ)

**Dᴇᴛᴀɪs:**
- ᴏɴ: Eɴᴀʙᴇs ᴀᴜᴛᴏ-ᴡᴇᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴs.
- ᴏғғ: Dɪsᴀʙᴇs ᴀᴜᴛᴏ-ᴡᴇᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴs.

**Nᴏᴛᴇs:**
- Oɴʏ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀs ᴀɴᴅ ᴛʜᴇ ɢʀᴏᴜᴘ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.

### Sᴘᴀᴍ Pʀᴏᴛᴇᴄᴛɪᴏɴ
Pʀᴇᴠᴇɴᴛs ᴄᴏᴍᴍᴀɴᴅ sᴘᴀᴍᴍɪɴɢ. Iғ ᴀ ᴜsᴇʀ sᴇɴᴅs ᴍᴏʀᴇ ᴛʜᴀɴ 2 ᴄᴏᴍᴍᴀɴᴅs ᴡɪᴛʜɪɴ 5 sᴇᴄᴏɴᴅs, ᴛʜᴇʏ ᴡɪ ʙᴇ ᴡᴀʀɴᴇᴅ ᴀɴᴅ ᴛᴇᴍᴘᴏʀᴀʀɪʏ ʙᴏᴄᴋᴇᴅ.

### Wᴇᴄᴏᴍᴇ Nᴇᴡ Mᴇᴍʙᴇʀs
Aᴜᴛᴏᴍᴀᴛɪᴄᴀʏ sᴇɴᴅs ᴀ ᴡᴇᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ ᴛᴏ ɴᴇᴡ ᴍᴇᴍʙᴇʀs ᴡʜᴏ ᴊᴏɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ.

**Bᴇʜᴀᴠɪᴏʀ:**
- Sᴇɴᴅs ᴀ ᴡᴇᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ ᴍᴇɴᴛɪᴏɴɪɴɢ ᴛʜᴇ ɴᴇᴡ ᴜsᴇʀ.
- Tʜᴇ ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴀғᴛᴇʀ ᴀ 3-sᴇᴄᴏɴᴅ ᴅᴇᴀʏ.

### Exᴀᴍᴘᴇs
- /awelcome on: Eɴᴀʙᴇs ᴀᴜᴛᴏ-ᴡᴇᴄᴏᴍᴇ.
- /awelcome off: Dɪsᴀʙᴇs ᴀᴜᴛᴏ-ᴡᴇᴄᴏᴍᴇ.

Iғ ᴀ ᴜsᴇʀ sᴇɴᴅs ᴍᴜᴛɪᴘᴇ ᴄᴏᴍᴍᴀɴᴅs ǫᴜɪᴄᴋʏ:
Tʜᴇʏ ᴡɪ ʀᴇᴄᴇɪᴠᴇ ᴀ sᴘᴀᴍ ᴡᴀʀɴɪɴɢ.
"""
