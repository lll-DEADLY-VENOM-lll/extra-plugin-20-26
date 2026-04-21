from pyrogram import filters
from VIPMUSIC import app

@app.on_message(filters.command("hastag"))
async def hastag(bot, message):

    try:
        text = message.text.split(" ", 1)[1]
        res = api.gen_hashtag(text)
    except IndexError:
        return await message.reply_text("Example:\n\n/hastag python")

    await message.reply_text(f"ʜᴇʀᴇ ɪs ʏᴏᴜʀ  ʜᴀsᴛᴀɢ :\n<pre>{res}</pre>", quote=True)


__MODULE__ = "Hᴀsʜᴛᴀɢ"
__HELP__ = """
**ʜᴀsʜᴛᴀɢ ɢᴇɴᴇʀᴀᴛᴏʀ:**

• `/hashtag [text]`: Gᴇɴᴇʀᴀᴛᴇ ʜᴀsʜᴛᴀɢs ғᴏʀ ᴛʜᴇ ɢɪᴠᴇɴ ᴛᴇxᴛ.
"""
