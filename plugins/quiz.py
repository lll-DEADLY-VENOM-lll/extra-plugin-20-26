import random
import requests
import time
import html
from pyrogram import filters
from pyrogram.enums import PollType, ChatAction
from VIPMUSIC import app

# Spam control
last_command_time = {}

@app.on_message(filters.command(["quiz"]))
async def quiz(client, message):
    user_id = message.from_user.id
    current_time = time.time()

    # Cooldown Check (5 Seconds)
    if user_id in last_command_time and current_time - last_command_time[user_id] < 5:
        return await message.reply_text(
            "⏳ **ᴄᴀʟᴍ ᴅᴏᴡɴ!**\nᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ᴀ ғᴇᴡ sᴇᴄᴏɴᴅs ʙᴇғᴏʀᴇ ᴀsᴋɪɴɢ ᴀɴᴏᴛʜᴇʀ ǫᴜᴇsᴛɪᴏɴ."
        )

    last_command_time[user_id] = current_time

    # Categories: General Knowledge, Science, Computers, Mythology, Sports, History
    categories = [9, 17, 18, 20, 21, 23, 27]
    
    # Showing progress
    await app.send_chat_action(message.chat.id, ChatAction.CHOOSE_STICKER)
    m = await message.reply_text("🧠 **ꜰᴇᴛᴄʜɪɴɢ ᴀ ᴄʜᴀʟʟᴇɴɢɪɴɢ ǫᴜɪᴢ...**")

    try:
        url = f"https://opentdb.com/api.php?amount=1&category={random.choice(categories)}&type=multiple"
        response = requests.get(url).json()

        if response["response_code"] != 0:
            return await m.edit("❌ **ғᴀɪʟᴇᴅ ᴛᴏ ꜰᴇᴛᴄʜ ǫᴜɪᴢ. ᴛʀʏ ᴀɢᴀɪɴ!**")

        question_data = response["results"][0]
        
        # Unescape HTML entities (Fixes &quot;, &#039;, etc.)
        question = html.unescape(question_data["question"])
        correct_answer = html.unescape(question_data["correct_answer"])
        incorrect_answers = [html.unescape(ans) for ans in question_data["incorrect_answers"]]

        all_answers = incorrect_answers + [correct_answer]
        random.shuffle(all_answers)

        correct_id = all_answers.index(correct_answer)

        await m.delete()
        await app.send_poll(
            chat_id=message.chat.id,
            question=f"✨ ǫᴜɪᴢ: {question}",
            options=all_answers,
            is_anonymous=False,
            type=PollType.QUIZ,
            correct_option_id=correct_id,
            explanation="ᴛʜɪɴᴋ ʙᴇғᴏʀᴇ ʏᴏᴜ ᴄʟɪᴄᴋ! 🧠",
            reply_to_message_id=message.id
        )
    except Exception as e:
        await m.edit(f"❌ **ᴇʀʀᴏʀ:** `{str(e)}`")


__MODULE__ = "ǫᴜɪᴢ"
__HELP__ = """
✨ **ǫᴜɪᴢ ᴍᴏᴅᴜʟᴇ** ✨

● `/quiz` : ɢᴇᴛ ᴀ ʀᴀɴᴅᴏᴍ ɪɴᴛᴇʀᴀᴄᴛɪᴠᴇ ǫᴜɪᴢ ᴘᴏʟʟ.

**ɴᴏᴛᴇ:**
ᴘᴏʟʟs ᴀʀᴇ ɴᴏɴ-ᴀɴᴏɴʏᴍᴏᴜs, sᴏ ᴇᴠᴇʀʏᴏɴᴇ ᴄᴀɴ sᴇᴇ ʏᴏᴜʀ sᴄᴏʀᴇ!
"""
