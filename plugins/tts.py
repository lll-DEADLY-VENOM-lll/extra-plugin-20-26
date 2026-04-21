import io
from gtts import gTTS
from pyrogram import filters
from pyrogram.types import Message
from VIPMUSIC import app

@app.on_message(filters.command("tts"))
async def text_to_speech(client, message: Message):
    # If no text is provided and it's not a reply
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text(
            "✨ **ᴜsᴀɢᴇ:**\n\n"
            "● `/tts [ᴛᴇxᴛ]` - ᴄᴏɴᴠᴇʀᴛ ᴛᴇxᴛ ᴛᴏ sᴘᴇᴇᴄʜ.\n"
            "● `/tts [ʟᴀɴɢ ᴄᴏᴅᴇ] [ᴛᴇxᴛ]` - ᴄᴏɴᴠᴇʀᴛ ɪɴ sᴘᴇᴄɪғɪᴄ ʟᴀɴɢ.\n"
            "● **ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴡɪᴛʜ** `/tts`"
        )

    m = await message.reply_text("⚙️ **ᴘʀᴏᴄᴇssɪɴɢ...**")
    
    # Check if it's a reply or direct text
    if message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text
    else:
        text = message.text.split(None, 1)[1]

    # Language support logic
    # Example: /tts en Hello (it will use 'en')
    lang = "hi" # Default language
    if len(message.command) > 1:
        check_lang = message.command[1]
        if len(check_lang) == 2: # Simple check for lang codes like 'en', 'hi', 'fr'
            lang = check_lang
            if not message.reply_to_message:
                if len(message.command) > 2:
                    text = message.text.split(None, 2)[2]
                else:
                    return await m.edit("❌ **ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴛᴇxᴛ ᴀғᴛᴇʀ ʟᴀɴɢ ᴄᴏᴅᴇ.**")

    try:
        tts = gTTS(text, lang=lang)
        audio_data = io.BytesIO()
        tts.write_to_fp(audio_data)
        audio_data.seek(0)

        audio_file = io.BytesIO(audio_data.read())
        audio_file.name = f"tts_{lang}.mp3"
        
        await m.delete()
        await message.reply_audio(
            audio_file, 
            caption=f"✨ **ᴛᴛs ᴄᴏɴᴠᴇʀᴛᴇᴅ ɪɴ** `{lang}`\n\n👤 **ʙʏ:** {message.from_user.mention}"
        )
    except Exception as e:
        await m.edit(f"❌ **ᴇʀʀᴏʀ:** `{str(e)}`")


__MODULE__ = "ᴛᴛs"
__HELP__ = """
✨ **ᴛᴇxᴛ ᴛᴏ sᴘᴇᴇᴄʜ ᴍᴏᴅᴜʟᴇ** ✨

● `/tts [ᴛᴇxᴛ]` : ᴄᴏɴᴠᴇʀᴛ ᴛᴇxᴛ ᴛᴏ ʜɪɴᴅɪ ᴀᴜᴅɪᴏ.
● `/tts [ʟᴀɴɢ] [ᴛᴇxᴛ]` : ᴄᴏɴᴠᴇʀᴛ ᴛᴇxᴛ ᴛᴏ sᴘᴇᴄɪғɪᴄ ʟᴀɴɢ ᴀᴜᴅɪᴏ (ᴇ.ɢ. `en`, `hi`, `ar`, `fr`).
● `/tts [ʀᴇᴘʟʏ]` : ᴄᴏɴᴠᴇʀᴛ ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ ᴛᴇxᴛ ᴛᴏ ᴀᴜᴅɪᴏ.

**ʟᴀɴɢᴜᴀɢᴇ ᴄᴏᴅᴇs:** `hi` (ʜɪɴᴅɪ), `en` (ᴇɴɢʟɪsʜ), `ml` (ᴍᴀʟᴀʏᴀʟᴀᴍ), `ta` (ᴛᴀᴍɪʟ), ᴇᴛᴄ.
"""
