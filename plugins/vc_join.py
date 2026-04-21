import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from pytgcalls.types import JoinedGroupCallParticipant, LeftGroupCallParticipant
from VIPMUSIC.core.mongo import mongodb 
from VIPMUSIC import app
from VIPMUSIC.core.call import VIP

# MongoDB collection
db = mongodb.vc_monitoring

# --- HELPER FUNCTIONS ---

async def is_monitoring_enabled(chat_id):
    if not chat_id:
        return False
    try:
        status = await db.find_one({"chat_id": chat_id})
        return status is not None and status.get("status") == "on"
    except Exception:
        return False

async def is_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
    except Exception:
        return False

# --- VC PARTICIPANTS HANDLER ---

@VIP.one.on_participants_change()
async def vc_participants_handler(client, update):
    chat_id = getattr(update, "chat_id", None)
    
    if not chat_id or not await is_monitoring_enabled(chat_id):
        return

    user_id = None
    action_text = ""

    if isinstance(update, JoinedGroupCallParticipant):
        user_id = update.participant.user_id
        action_text = "ne VC join kiya. 👤"
    elif isinstance(update, LeftGroupCallParticipant):
        user_id = update.participant.user_id
        action_text = "ne VC leave kiya. 🏃"

    if user_id:
        try:
            try:
                user = await app.get_users(user_id)
                name = user.first_name or "User"
                username = f"@{user.username}" if user.username else "N/A"
                mention = f"[{name}](tg://user?id={user_id})"
            except Exception:
                name = "Unknown"
                username = "N/A"
                mention = f"User ID `{user_id}`"

            final_text = (
                f"{mention} {action_text}\n\n"
                f"**👤 Name:** {name}\n"
                f"**🔗 Username:** {username}\n"
                f"**🆔 User ID:** `{user_id}`"
            )

            # Message bhejna aur 15 second baad delete karna
            sent_msg = await app.send_message(chat_id, final_text)
            await asyncio.sleep(15)
            await sent_msg.delete()
            
        except Exception as e:
            print(f"Error in VC Logger Handler: {e}")

# --- COMMANDS SECTION ---

@app.on_message(filters.command(["vclogon", "checkvcon"]) & filters.group)
async def start_vc_monitor(client: Client, message: Message):
    # Admin check
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❌ Aapke paas permissions nahi hain (sirf Admins ke liye).")

    chat_id = message.chat.id
    try:
        await db.update_one(
            {"chat_id": chat_id},
            {"$set": {"status": "on"}},
            upsert=True
        )
        msg = await message.reply_text(f"✅ **VC Monitoring ON**\n\nAb VC join/leave alerts milenge. (15s mein delete ho jayega)")
        await asyncio.sleep(15)
        await msg.delete()
        try:
            await message.delete()
        except:
            pass
    except Exception as e:
        print(f"Error in vclogon command: {e}")

@app.on_message(filters.command(["vclogoff", "checkvcoff"]) & filters.group)
async def stop_vc_monitor(client: Client, message: Message):
    # Admin check
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❌ Aapke paas permissions nahi hain (sirf Admins ke liye).")
        
    chat_id = message.chat.id
    try:
        await db.update_one(
            {"chat_id": chat_id},
            {"$set": {"status": "off"}},
            upsert=True
        )
        msg = await message.reply_text("❌ **VC Monitoring OFF.**\n\nAb alerts nahi milenge.")
        await asyncio.sleep(15)
        await msg.delete()
        try:
            await message.delete()
        except:
            pass
    except Exception as e:
        print(f"Error in vclogoff command: {e}")

# --- HELP SECTION ---

__MODULE__ = "VC Logger"
__HELP__ = """
**Voice Chat Monitor Tool**

Is module se aap track kar sakte hain ki group VC mein kaun join kar raha hai aur kaun leave.

**Commands:**
- `/vclogon` : VC monitoring chalu karne ke liye. (Admins Only)
- `/checkvcon` : Same as vclogon.
- `/vclogoff` : VC monitoring band karne ke liye. (Admins Only)
- `/checkvcoff` : Same as vclogoff.

**Notes:**
- Saare notification messages 15 seconds ke baad auto-delete ho jayenge.
- Ye feature sirf groups mein kaam karta hai.
"""
