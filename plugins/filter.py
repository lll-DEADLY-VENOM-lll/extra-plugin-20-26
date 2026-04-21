import re
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from config import BANNED_USERS, MONGO_DB_URI
from VIPMUSIC import app
from motor.motor_asyncio import AsyncIOMotorClient

# --- MONGODB SETUP ---
mongo = AsyncIOMotorClient(MONGO_DB_URI)
db = mongo.VIP_FILTERS_DB
filtersdb = db.filters

# --- DATABASE FUNCTIONS ---
async def save_filter(chat_id, name, data):
    await filtersdb.update_one(
        {"chat_id": chat_id, "name": name},
        {"$set": {"data": data}},
        upsert=True
    )

async def get_filter(chat_id, name):
    _filter = await filtersdb.find_one({"chat_id": chat_id, "name": name})
    return _filter["data"] if _filter else None

async def get_filters_names(chat_id):
    _filters = []
    async for _filter in filtersdb.find({"chat_id": chat_id}):
        _filters.append(_filter["name"])
    return _filters

async def delete_filter(chat_id, name):
    await filtersdb.delete_one({"chat_id": chat_id, "name": name})

async def deleteall_filters(chat_id):
    await filtersdb.delete_many({"chat_id": chat_id})

# --- UTILS ---
from utils.permissions import adminsOnly
from VIPMUSIC.utils.functions import check_format, extract_text_and_keyb
from VIPMUSIC.utils.keyboard import ikb

__MODULE__ = "Filters"
__HELP__ = """
**Groups Only Commands:**
/filter [NAME] - Reply to Text, Sticker, or Video to save it.
/filters - List all active filters.
/stop [NAME] - Delete a filter.
/stopall - Delete all filters.

**Example:**
Reply to a sticker with `/filter kiru_op`
Now whenever someone says `kiru_op`, bot will send that sticker.
"""

# --- 1. SAVE FILTER (Text, Sticker, Video, etc.) ---
@app.on_message(filters.command("filter") & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_change_info")
async def save_filter_cmd(_, message):
    if len(message.command) < 2 or not message.reply_to_message:
        return await message.reply_text("**Sahi Tarika:**\nKisi text, sticker ya video ko reply karke `/filter [NAME]` likhein.")

    # Name with underscore support
    name = message.text.split(None, 1)[1].strip().lower()
    rep = message.reply_to_message
    
    file_id = None
    _type = "text"
    content = None

    # Check Message Type
    if rep.text:
        _type = "text"
        content = rep.text
    elif rep.sticker:
        _type = "sticker"
        file_id = rep.sticker.file_id
    elif rep.photo:
        _type = "photo"
        file_id = rep.photo.file_id
        content = rep.caption
    elif rep.video:
        _type = "video"
        file_id = rep.video.file_id
        content = rep.caption
    elif rep.animation:
        _type = "animation"
        file_id = rep.animation.file_id
        content = rep.caption
    elif rep.voice:
        _type = "voice"
        file_id = rep.voice.file_id
        content = rep.caption
    
    # Save to dictionary
    filter_data = {
        "type": _type,
        "file_id": file_id,
        "text": content
    }

    await save_filter(message.chat.id, name, filter_data)
    await message.reply_text(f"**Saved `{name}` as {_type} filter!**")


# --- 2. TRIGGER FILTERS ---
@app.on_message((filters.text | filters.caption) & ~filters.private & ~BANNED_USERS, group=4)
async def filters_trigger(_, message: Message):
    if not message.text and not message.caption:
        return

    text = message.text or message.caption
    chat_id = message.chat.id
    
    # Get all filter names for this chat
    all_names = await get_filters_names(chat_id)
    if not all_names:
        return

    for word in all_names:
        # Regex to match exact word (supports kiru_op)
        pattern = r"( |^|[^\w])" + re.escape(word) + r"( |$|[^\w])"
        if re.search(pattern, text.lower()):
            data = await get_filter(chat_id, word)
            if not data:
                continue

            _type = data["type"]
            file_id = data.get("file_id")
            msg_text = data.get("text")
            keyb = None

            # Handle Placeholders in text/caption
            if msg_text:
                if "{NAME}" in msg_text:
                    msg_text = msg_text.replace("{NAME}", message.from_user.mention if message.from_user else "User")
                if "{ID}" in msg_text:
                    msg_text = msg_text.replace("{ID}", str(message.from_user.id))
                
                # Extract Buttons
                if "[" in msg_text and "]" in msg_text:
                    try:
                        extracted = extract_text_and_keyb(ikb, msg_text)
                        if extracted:
                            msg_text, keyb = extracted
                    except:
                        pass

            # SEND RESPONSE
            target = message.reply_to_message or message
            try:
                if _type == "text":
                    await target.reply_text(msg_text, reply_markup=keyb, disable_web_page_preview=True)
                elif _type == "sticker":
                    await target.reply_sticker(file_id)
                elif _type == "photo":
                    await target.reply_photo(file_id, caption=msg_text, reply_markup=keyb)
                elif _type == "video":
                    await target.reply_video(file_id, caption=msg_text, reply_markup=keyb)
                elif _type == "animation":
                    await target.reply_animation(file_id, caption=msg_text, reply_markup=keyb)
                elif _type == "voice":
                    await target.reply_voice(file_id, caption=msg_text, reply_markup=keyb)
            except Exception as e:
                print(f"Filter Error: {e}")
            return


# --- 3. OTHER COMMANDS ---
@app.on_message(filters.command("filters") & ~filters.private & ~BANNED_USERS)
async def list_filters(_, message):
    names = await get_filters_names(message.chat.id)
    if not names:
        return await message.reply_text("No filters in this chat.")
    msg = f"**Filters in {message.chat.title}:**\n" + "\n".join([f"- `{n}`" for n in sorted(names)])
    await message.reply_text(msg)

@app.on_message(filters.command("stop") & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_change_info")
async def stop_filter(_, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/stop [NAME]`")
    name = message.text.split(None, 1)[1].strip().lower()
    await delete_filter(message.chat.id, name)
    await message.reply_text(f"**Stopped filter `{name}`.**")

@app.on_message(filters.command("stopall") & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_change_info")
async def stop_all_filters(_, message):
    await deleteall_filters(message.chat.id)
    await message.reply_text("**All filters deleted.**")
