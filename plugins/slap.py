import nekos
from pyrogram import filters
from pyrogram.types import Message
from VIPMUSIC import app

@app.on_message(filters.command("slap"))
async def slap(client, message: Message):
    try:
        # Fetching the slap animation URL
        url = nekos.img("slap")
        
        if message.reply_to_message:
            # If slapping a replied user
            sender = message.from_user.mention
            target = message.reply_to_message.from_user.mention
            caption = f"🔥 {sender} **ɢᴀᴠᴇ ᴀ ʜᴀʀᴅ sʟᴀᴘ ᴛᴏ** {target} ! 👋"
        else:
            # If no one is replied to
            sender = message.from_user.mention
            caption = f"👋 {sender} **ɪs sʟᴀᴘᴘɪɴɢ ᴇᴠᴇʀʏᴏɴᴇ ᴀʀᴏᴜɴᴅ!** 😂"

        # Sending as animation for better look
        await message.reply_animation(
            animation=url,
            caption=caption
        )
    except Exception as e:
        await message.reply_text(f"❌ **ᴇʀʀᴏʀ:** `{str(e)}`")


__MODULE__ = "sʟᴀᴘ"
__HELP__ = """
✨ **sʟᴀᴘ ᴍᴏᴅᴜʟᴇ** ✨

● `/slap` : sʟᴀᴘ ᴛʜᴇ ᴀɪʀ ᴏʀ ʏᴏᴜʀsᴇʟғ.
● `/slap [ʀᴇᴘʟʏ]` : sʟᴀᴘ ᴛʜᴇ ᴘᴇʀsᴏɴ ʏᴏᴜ ᴀʀᴇ ʀᴇᴘʟʏɪɴɢ ᴛᴏ.

**ᴇxᴀᴍᴘʟᴇ:**
ʀᴇᴘʟʏ ᴛᴏ sᴏᴍᴇᴏɴᴇ ᴡɪᴛʜ `/slap` ᴛᴏ sʜᴏᴡ ʏᴏᴜʀ ᴀɴɢᴇʀ! 😈
"""
