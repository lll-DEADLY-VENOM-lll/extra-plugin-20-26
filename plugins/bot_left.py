import random
from pyrogram import filters
from pyrogram.types import Message
from motor.motor_asyncio import AsyncIOMotorClient as MongoClient
from config import LOG_GROUP_ID, MONGO_DB_URI
from VIPMUSIC import app
from VIPMUSIC.core.call import VIP
from VIPMUSIC.utils.database import delete_served_chat, get_assistant, set_loop

# --- Database Setup (Direct Connection) ---
# Yahan hum direct Mongo URI use kar rahe hain taaki 'AttributeError' na aaye
mongo = MongoClient(MONGO_DB_URI)
autoleavedb = mongo.VIPMUSIC.autoleave 

async def is_autoleave_on(chat_id: int) -> bool:
    chat = await autoleavedb.find_one({"chat_id": chat_id})
    if not chat:
        return True  # Default: ON
    return chat.get("state", True)

async def autoleave_on(chat_id: int):
    await autoleavedb.update_one(
        {"chat_id": chat_id}, {"$set": {"state": True}}, upsert=True
    )

async def autoleave_off(chat_id: int):
    await autoleavedb.update_one(
        {"chat_id": chat_id}, {"$set": {"state": False}}, upsert=True
    )

# --- Photos for Logs ---
photo = [
    "https://telegra.ph/file/1949480f01355b4e87d26.jpg",
    "https://telegra.ph/file/3ef2cc0ad2bc548bafb30.jpg",
    "https://telegra.ph/file/a7d663cd2de689b811729.jpg",
    "https://telegra.ph/file/6f19dc23847f5b005e922.jpg",
    "https://telegra.ph/file/2973150dd62fd27a3a6ba.jpg",
]

# --- Toggle Command Handler ---
@app.on_message(filters.command(["autoleave"]) & filters.group)
async def toggle_autoleave(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "**Usage:**\n`/autoleave on` - Assistant leaves when bot is removed.\n`/autoleave off` - Assistant stays when bot is removed."
        )
    
    state = message.command[1].lower()
    if state == "on":
        await autoleave_on(message.chat.id)
        await message.reply_text(f"✅ **Auto Leave Enabled** for {message.chat.title}")
    elif state == "off":
        await autoleave_off(message.chat.id)
        await message.reply_text(f"❌ **Auto Leave Disabled** for {message.chat.title}")
    else:
        await message.reply_text("Invalid option! Use `on` or `off`.")

# --- Left Chat Member Handler ---
@app.on_message(filters.left_chat_member, group=-12)
async def on_left_chat_member(_, message: Message):
    try:
        # 1. Check if the member who left is the BOT itself
        bot_details = await app.get_me()
        if message.left_chat_member.id != bot_details.id:
            return

        chat_id = message.chat.id
        
        # 2. Check if Auto-Leave is ON/OFF
        if not await is_autoleave_on(chat_id):
            return 

        # 3. Get Assistant
        userbot = await get_assistant(chat_id)
        remove_by = (
            message.from_user.mention if message.from_user else "𝐔ɴᴋɴᴏᴡɴ 𝐔sᴇʀ"
        )
        title = message.chat.title
        
        # 4. Send Log
        left_msg = (
            f"✫ <b><u>#𝐋ᴇғᴛ_𝐆ʀᴏᴜᴘ</u></b> ✫\n\n"
            f"<b>𝐂ʜᴀᴛ 𝐓ɪᴛʟᴇ :</b> {title}\n"
            f"<b>𝐂ʜᴀᴛ 𝐈ᴅ :</b> {chat_id}\n"
            f"<b>𝐑ᴇᴍᴏᴠᴇᴅ 𝐁ʏ :</b> {remove_by}\n"
            f"<b>𝐁ᴏᴛ :</b> @{bot_details.username}"
        )
        try:
            await app.send_photo(LOG_GROUP_ID, photo=random.choice(photo), caption=left_msg)
        except:
            pass

        # 5. Cleanup Actions
        await delete_served_chat(chat_id)
        await VIP.st_stream(chat_id)
        await set_loop(chat_id, 0)
        
        # 6. Assistant leaves group
        await userbot.leave_chat(chat_id)

    except Exception as e:
        print(f"Error in autoleave: {e}")
        return 

__MODULE__ = "AutoLeave"
__HELP__ = """
**/autoleave [on/off]** - Jab bot group se nikala jayega, to assistant ko bhi nikalna hai ya nahi, ye yahan se set karein.
"""
