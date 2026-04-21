import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import enums, filters
from pyrogram.types import (
    CallbackQuery,
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from VIPMUSIC import app
# Database logic ko isi file mein merge kar diya gaya hai error fix karne ke liye
from VIPMUSIC.core.mongo import mongodb

# --- Database Setup ---
nightdb = mongodb.nightmode

async def get_nightchats() -> list:
    chats = nightdb.find({"chat_id": {"$exists": True}})
    if not chats:
        return []
    return await chats.to_list(length=10000)

async def nightmode_on(chat_id: int):
    return await nightdb.insert_one({"chat_id": chat_id})

async def nightmode_off(chat_id: int):
    return await nightdb.delete_one({"chat_id": chat_id})

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Chat Permissions ---
CLOSE_CHAT = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_other_messages=False,
    can_send_polls=False,
    can_change_info=False,
    can_add_web_page_previews=False,
    can_pin_messages=False,
    can_invite_users=False,
)

OPEN_CHAT = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_other_messages=True,
    can_send_polls=True,
    can_change_info=True,
    can_add_web_page_previews=True,
    can_pin_messages=True,
    can_invite_users=True,
)

# --- Buttons ---
buttons = InlineKeyboardMarkup(
    [[
        InlineKeyboardButton("๏ ᴇɴᴀʙʟᴇ ๏", callback_data="add_night"),
        InlineKeyboardButton("๏ ᴅɪsᴀʙʟᴇ ๏", callback_data="rm_night"),
    ]]
)

ADD_ME_BUTTON = InlineKeyboardMarkup(
    [[
        InlineKeyboardButton(
            text=" ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ",
            url=f"https://t.me/{app.username}?startgroup=true",
        )
    ]]
)

@app.on_message(filters.command("nightmode") & filters.group)
async def _nightmode(_, message: Message):
    user = await app.get_chat_member(message.chat.id, message.from_user.id)
    if user.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
        return await message.reply_text("❌ **Sᴏʀʀʏ, ᴏɴʟʏ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀs ᴄᴀɴ ᴀᴄᴄᴇss ᴛʜᴇsᴇ sᴇᴛᴛɪɴɢs.**")

    await message.reply_photo(
        photo="https://telegra.ph//file/06649d4d0bbf4285238ee.jpg",
        caption=(
            "🌙 **ᴀᴜᴛᴏᴍᴀᴛᴇᴅ ɴɪɢʜᴛᴍᴏᴅᴇ sʏsᴛᴇᴍ ɪs ʜᴇʀᴇ!**\n\n"
            "ᴛʜɪs ғᴇᴀᴛᴜʀᴇ ʜᴇʟᴘs ʏᴏᴜ ᴍᴀɪɴᴛᴀɪɴ ɢʀᴏᴜᴘ ᴅɪsᴄɪᴘʟɪɴᴇ ʙʏ ᴀᴜᴛᴏ-ᴄʟᴏsɪɴɢ "
            "ᴛʜᴇ ᴄʜᴀᴛ ᴅᴜʀɪɴɢ ʟᴀᴛᴇ ɴɪɢʜᴛ ʜᴏᴜʀs. ᴏɴᴄᴇ ᴇɴᴀʙʟᴇᴅ, ᴛʜᴇ ʙᴏᴛ ᴡɪʟʟ "
            "ʀᴇsᴛʀɪᴄᴛ ᴍᴇssᴀɢᴇs ᴀᴛ ᴍɪᴅɴɪɢʜᴛ ᴀɴᴅ ʀᴇ-ᴏᴘᴇɴ ᴛʜᴇᴍ ɪɴ ᴛʜᴇ ᴍᴏʀɴɪɴɢ.\n\n"
            "**sᴄʜᴇᴅᴜʟᴇ:** 𝟷𝟸:𝟶𝟶 ᴀᴍ ᴛᴏ 𝟶𝟼:𝟶𝟶 ᴀᴍ [ɪsᴛ]\n"
            "**sᴛᴀᴛᴜs:** ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ᴛᴏ ᴛᴏɢɢʟᴇ sᴇᴛᴛɪɴɢs."
        ),
        reply_markup=buttons,
    )

@app.on_callback_query(filters.regex("^(add_night|rm_night)$"))
async def nightcb(_, query: CallbackQuery):
    user = await app.get_chat_member(query.message.chat.id, query.from_user.id)
    if user.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
        return await query.answer("⚠️ ᴀᴅᴍɪɴ ᴘᴇʀᴍɪssɪᴏɴ ʀᴇǫᴜɪʀᴇᴅ!", show_alert=True)

    check_night = await nightdb.find_one({"chat_id": query.message.chat.id})
    if query.data == "add_night":
        if check_night:
            await query.message.edit_caption("✨ **ɴɪɢʜᴛᴍᴏᴅᴇ ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴄᴛɪᴠᴇ ɪɴ ᴛʜɪs ᴄʜᴀᴛ.**")
        else:
            await nightmode_on(query.message.chat.id)
            await query.message.edit_caption("✅ **ɴɪɢʜᴛᴍᴏᴅᴇ sᴜᴄᴄᴇssғᴜʟʟʏ ᴇɴᴀʙʟᴇᴅ! ᴛʜᴇ ɢʀᴏᴜᴘ ᴡɪʟʟ ɴᴏᴡ ᴀᴜᴛᴏ-ᴄʟᴏsᴇ ᴅᴀɪʟʏ.**")
    elif query.data == "rm_night":
        if not check_night:
            await query.message.edit_caption("❄️ **ɴɪɢʜᴛᴍᴏᴅᴇ ɪs ᴄᴜʀʀᴇɴᴛʟʏ ᴅɪsᴀʙʟᴇᴅ ʜᴇʀᴇ.**")
        else:
            await nightmode_off(query.message.chat.id)
            await query.message.edit_caption("❌ **ɴɪɢʜᴛᴍᴏᴅᴇ ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ᴛʜɪs ᴄʜᴀᴛ.**")
    await query.answer()

# --- Automated Group Closing ---
async def start_nightmode():
    schats = await get_nightchats()
    for chat in schats:
        chat_id = int(chat["chat_id"])
        try:
            await app.send_photo(
                chat_id,
                photo="https://telegra.ph//file/06649d4d0bbf4285238ee.jpg",
                caption=(
                    "🌟 **ɢᴏᴏᴅ ɴɪɢʜᴛ ᴅᴇᴀʀ ᴍᴇᴍʙᴇʀs! ᴛʜᴇ ᴅᴀʏ ʜᴀs ᴄᴏᴍᴇ ᴛᴏ ᴀɴ ᴇɴᴅ.**\n"
                    "ᴀs ᴛʜᴇ sᴛᴀʀs ʙᴇɢɪɴ ᴛᴏ sʜɪɴᴇ, ɪᴛ ɪs ᴛɪᴍᴇ ᴛᴏ ɢɪᴠᴇ ʏᴏᴜʀ ᴍɪɴᴅ ᴀɴᴅ ʙᴏᴅʏ ᴀ \n"
                    "ᴡᴇʟʟ-ᴅᴇsᴇʀᴠᴇᴅ ʀᴇsᴛ. ᴡᴇ ʜᴏᴘᴇ ʏᴏᴜ ʜᴀᴅ ᴀ ᴘʀᴏᴅᴜᴄᴛɪᴠᴇ ᴅᴀʏ ᴛᴏᴅᴀʏ. ɴᴏᴡ, \n"
                    "ʟᴇᴛ ᴛʜᴇ sɪʟᴇɴᴄᴇ ᴏғ ᴛʜᴇ ɴɪɢʜᴛ ʙʀɪɴɢ ʏᴏᴜ sᴇʀᴇɴɪᴛʏ ᴀɴᴅ ᴘᴇᴀᴄᴇ. ᴛʜɪs \n"
                    "ᴄʜᴀᴛ ɪs ɴᴏᴡ ᴄʟᴏsɪɴɢ ᴛᴏ ᴇɴsᴜʀᴇ ᴇᴠᴇʀʏᴏɴᴇ ᴇɴᴊᴏʏs ᴀ ᴅɪsᴛᴜʀʙᴀɴᴄᴇ-ғʀᴇᴇ \n"
                    "sʟᴇᴇᴘ. ᴘʟᴇᴀsᴇ ᴅʀᴇᴀᴍ ʙɪɢ ᴀɴᴅ ᴡᴀᴋᴇ ᴜᴘ ᴡɪᴛʜ ɴᴇᴡ ᴇɴᴇʀɢʏ ᴛᴏᴍᴏʀʀᴏᴡ. \n"
                    "ᴀʟʟ ᴍᴇssᴀɢɪɴɢ ᴘᴇʀᴍɪssɪᴏɴs ᴀʀᴇ ʜᴀʟᴛᴇᴅ ᴜɴᴛɪʟ sᴜɴʀɪsᴇ. sʟᴇᴇᴘ ᴛɪɢʜᴛ, \n"
                    "ᴛᴀᴋᴇ ᴄᴀʀᴇ ᴏғ ʏᴏᴜʀsᴇʟғ, ᴀɴᴅ ᴍᴀʏ ᴛʜᴇ ᴀɴɢᴇʟs ɢᴜᴀʀᴅ ʏᴏᴜʀ ᴅʀᴇᴀᴍs. ᴡᴇ \n"
                    "ᴡɪʟʟ ʙᴇ ʙᴀᴄᴋ ᴏɴʟɪɴᴇ ᴀᴛ **𝟶𝟼:𝟶𝟶 ᴀᴍ [ɪsᴛ]**. ɢᴏᴏᴅ ɴɪɢʜᴛ ᴇᴠᴇʀʏᴏɴᴇ! ✨"
                ),
                reply_markup=ADD_ME_BUTTON,
            )
            await app.set_chat_permissions(chat_id, CLOSE_CHAT)
            await asyncio.sleep(0.3)
        except Exception as e:
            logger.error(f"Error in start_nightmode for {chat_id}: {e}")

# --- Automated Group Opening ---
async def close_nightmode():
    schats = await get_nightchats()
    for chat in schats:
        chat_id = int(chat["chat_id"])
        try:
            await app.send_photo(
                chat_id,
                photo="https://telegra.ph//file/14ec9c3ff42b59867040a.jpg",
                caption=(
                    "☀️ **ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ ᴇᴠᴇʀʏᴏɴᴇ! ᴀ ʙʀᴀɴᴅ ɴᴇᴡ ᴅᴀʏ ʜᴀs ᴅᴀᴡɴᴇᴅ.**\n"
                    "ʀɪsᴇ ᴀɴᴅ sʜɪɴᴇ! ɪᴛ ɪs ᴛɪᴍᴇ ᴛᴏ ᴇᴍʙʀᴀᴄᴇ ᴛʜᴇ ɴᴇᴡ ᴏᴘᴘᴏʀᴛᴜɴɪᴛɪᴇs ᴛʜᴀᴛ \n"
                    "ᴛʜɪs ʙᴇᴀᴜᴛɪғᴜʟ ᴍᴏʀɴɪɴɢ ʙʀɪɴɢs ᴛᴏ ʏᴏᴜʀ ʟɪғᴇ. ᴛʜᴇ sᴜɴ ɪs ᴜᴘ, ᴀɴᴅ \n"
                    "ᴛʜᴇ ᴡᴏʀʟᴅ ɪs ᴡᴀɪᴛɪɴɢ ғᴏʀ ʏᴏᴜ ᴛᴏ ᴍᴀᴋᴇ ᴀ ᴅɪғғᴇʀᴇɴᴄᴇ. ᴡᴇ ᴀʀᴇ ɴᴏᴡ \n"
                    "ᴏᴘᴇɴɪɴɢ ᴛʜᴇ ɢʀᴏᴜᴘ ᴄʜᴀᴛ sᴏ ʏᴏᴜ ᴄᴀɴ ᴄᴏɴɴᴇᴄᴛ, sʜᴀʀᴇ, ᴀɴᴅ ɢʀᴏᴡ ᴡɪᴛʜ \n"
                    "ᴇᴀᴄʜ ᴏᴛʜᴇʀ ᴀɢᴀɪɴ. ᴍᴀʏ ᴛʜɪs ᴅᴀʏ ʙᴇ ғɪʟʟᴇᴅ ᴡɪᴛʜ ᴘᴏsɪᴛɪᴠɪᴛʏ, ʟᴏᴠᴇ, \n"
                    "ᴀɴᴅ ᴜɴsᴛᴏᴘᴘᴀʙʟᴇ sᴜᴄᴄᴇss. ʙᴇ ᴋɪɴᴅ ᴛᴏ ᴏɴᴇ ᴀɴᴏᴛʜᴇʀ ᴀɴᴅ ᴋᴇᴇᴘ ᴛʜᴇ \n"
                    "ᴇɴᴇʀɢʏ ʜɪɢʜ! ᴀʟʟ ᴍᴇssᴀɢɪɴɢ ᴘᴇʀᴍɪssɪᴏɴs ʜᴀᴠᴇ ʙᴇᴇɴ ʀᴇsᴛᴏʀᴇᴅ ʙʏ ᴛʜᴇ \n"
                    "sʏsᴛᴇᴍ. ʟᴇᴛ's sᴛᴀʀᴛ ᴛʜᴇ ᴅᴀʏ ᴡɪᴛʜ ᴀ sᴍɪʟᴇ ᴀɴᴅ ᴀ ɢʀᴇᴀᴛ ᴠɪʙᴇ. ʜᴀᴠᴇ \n"
                    "ᴀ ᴡᴏɴᴅᴇʀғᴜʟ ᴀɴᴅ ʙʟᴇssᴇᴅ ᴅᴀʏ ᴀʜᴇᴀᴅ! 🔓✨"
                ),
                reply_markup=ADD_ME_BUTTON,
            )
            await app.set_chat_permissions(chat_id, OPEN_CHAT)
            await asyncio.sleep(0.3)
        except Exception as e:
            logger.error(f"Error in close_nightmode for {chat_id}: {e}")

# --- Scheduler Setup ---
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
scheduler.add_job(start_nightmode, trigger="cron", hour=0, minute=0)
scheduler.add_job(close_nightmode, trigger="cron", hour=6, minute=0)
scheduler.start()

__MODULE__ = "Nɪɢʜᴛᴍᴏᴅᴇ"
__HELP__ = """
🌙 **ɴɪɢʜᴛᴍᴏᴅᴇ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ**

• `/nightmode` : ᴏᴘᴇɴ sᴇᴛᴛɪɴɢs ᴛᴏ ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ.

**ᴀᴜᴛᴏᴍᴀᴛɪᴏɴ:**
- ɢʀᴏᴜᴘ ᴄʟᴏsᴇs ᴀᴛ **𝟷𝟸:𝟶𝟶 ᴀᴍ**
- ɢʀᴏᴜᴘ ᴏᴘᴇɴs ᴀᴛ **𝟶𝟼:𝟶𝟶 ᴀᴍ**
"""
