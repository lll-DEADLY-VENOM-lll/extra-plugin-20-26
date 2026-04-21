import random
import asyncio
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.errors import ChatAdminRequired, PeerIdInvalid, ChatWriteForbidden

from config import LOG_GROUP_ID
from VIPMUSIC import app
from VIPMUSIC.utils.database import add_served_chat, get_assistant
from VIPMUSIC.misc import SUDOERS
from VIPMUSIC.core.mongo import mongodb

# --- Database for Toggle ---
db = mongodb.join_log_toggle

async def is_join_log_on() -> bool:
    res = await db.find_one({"id": "join_log"})
    if not res:
        return True
    return res.get("status", True)

# --- Photos List ---
photo_list = [
    "https://telegra.ph/file/1949480f01355b4e87d26.jpg",
    "https://telegra.ph/file/3ef2cc0ad2bc548bafb30.jpg",
    "https://telegra.ph/file/a7d663cd2de689b811729.jpg",
    "https://telegra.ph/file/6f19dc23847f5b005e922.jpg",
    "https://telegra.ph/file/2973150dd62fd27a3a6ba.jpg",
]

# --- Bot Join Watcher ---
@app.on_message(filters.new_chat_members, group=-9)
async def join_watcher(_, message):
    if not await is_join_log_on():
        return

    chat = message.chat
    for member in message.new_chat_members:
        if member.id == app.id:
            try:
                userbot = await get_assistant(chat.id)
                
                try:
                    invitelink = await app.export_chat_invite_link(chat.id)
                except:
                    invitelink = "No Link (Admin Required)"

                count = await app.get_chat_members_count(chat.id)
                username = f"@{chat.username}" if chat.username else "𝐏ʀɪᴠᴀᴛᴇ 𝐆ʀᴏᴜᴘ"
                added_by = message.from_user.mention if message.from_user else "𝐔ɴᴋɴᴏᴡɴ 𝐔sᴇʀ"

                msg = (
                    f"✨ <b><u>ʙᴏᴛ ᴀᴅᴅᴇᴅ ᴛᴏ ɴᴇᴡ ɢʀᴏᴜᴘ</u></b> ✨\n\n"
                    f"<b>📝 ᴄʜᴀᴛ ɴᴀᴍᴇ:</b> {chat.title}\n"
                    f"<b>🍂 ᴄʜᴀᴛ ɪᴅ:</b> <code>{chat.id}</code>\n"
                    f"<b>🔐 ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ:</b> {username}\n"
                    f"<b>📈 ᴍᴇᴍʙᴇʀs:</b> {count}\n"
                    f"<b>🖇️ ʟɪɴᴋ:</b> <a href='{invitelink}'>ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>\n"
                    f"<b>🤔 ᴀᴅᴅᴇʀ ʙʏ:</b> {added_by}"
                )

                await app.send_photo(
                    LOG_GROUP_ID,
                    photo=random.choice(photo_list),
                    caption=msg,
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("👤 View Adder", user_id=message.from_user.id if message.from_user else 777000)]]
                    )
                )

                await add_served_chat(chat.id)
                if chat.username:
                    try: await userbot.join_chat(chat.username)
                    except: pass

            except Exception as e:
                print(f"Error in join_watcher: {e}")

# --- Toggle Join Log ---
@app.on_message(filters.command(["joinlog"]) & SUDOERS)
async def toggle_join_log(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text("<b>Usage:</b>\n/joinlog [on | off]")
    
    state = message.command[1].lower()
    if state == "on":
        await db.update_one({"id": "join_log"}, {"$set": {"status": True}}, upsert=True)
        await message.reply_text("✅ <b>Join Log system Enabled.</b>")
    elif state == "off":
        await db.update_one({"id": "join_log"}, {"$set": {"status": False}}, upsert=True)
        await message.reply_text("❌ <b>Join Log system Disabled.</b>")

# --- Get Link Feature (Extracts link from any group where bot is present) ---
@app.on_message(filters.command(["getlink", "link"]) & SUDOERS)
async def get_link_logic(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text("<b>Usage:</b>\n/getlink [Chat ID]")

    query = message.command[1]
    try:
        chat_id = int(query)
    except ValueError:
        return await message.reply_text("❌ <b>Please provide a valid Group ID (Numbers only).</b>")

    # Bot ko us chat mein check karna
    try:
        chat = await app.get_chat(chat_id)
        
        # 1. Agar group Public hai
        if chat.username:
            return await message.reply_text(f"🔗 <b>Public Link:</b> @{chat.username}")
        
        # 2. Agar bot Admin hai to link generate karega
        try:
            link = await app.export_chat_invite_link(chat_id)
            return await message.reply_text(f"📌 <b>Group:</b> {chat.title}\n🔗 <b>Link:</b> {link}")
        except ChatAdminRequired:
            # 3. Agar bot admin nahi hai, to Assistant (Userbot) se try karega
            try:
                userbot = await get_assistant(chat_id)
                user_chat = await userbot.get_chat(chat_id)
                if user_chat.invite_link:
                    return await message.reply_text(f"📌 <b>Group (via Assistant):</b> {chat.title}\n🔗 <b>Link:</b> {user_chat.invite_link}")
                else:
                    return await message.reply_text("❌ <b>Bot is in the group but doesn't have permission to get the link.</b>")
            except Exception:
                return await message.reply_text("❌ <b>Bot is a member, but I cannot extract the link (No Admin rights).</b>")
        
    except PeerIdInvalid:
        await message.reply_text("❌ <b>Bot is not in this group, or haven't seen it yet.</b>")
    except Exception as e:
        await message.reply_text(f"❌ <b>Error:</b> {str(e)}")

__MODULE__ = "JoinLog"
__HELP__ = """
<b>/joinlog [on/off]</b> - Bot join notifications control.
<b>/getlink [Chat ID]</b> - Get invite link of any group where bot/assistant is added.
"""