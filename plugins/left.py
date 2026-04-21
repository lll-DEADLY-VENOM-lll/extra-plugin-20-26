import asyncio
import random
from typing import Optional, Union

from PIL import Image, ImageDraw, ImageFont
from pyrogram import filters
from pyrogram.types import ChatMemberUpdated, InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.enums import ChatMemberStatus

from VIPMUSIC import app
# Maan lete hain ki aapke bot mein database system hai, agar nahi hai toh ye dictionary temporary kaam karegi
# Lekin bot restart hone par settings reset ho jayengi.
# Permanent ke liye MongoDB use karna behtar hota hai.
goodbye_status = {} 

random_photo = [
    "https://telegra.ph/file/1949480f01355b4e87d26.jpg",
    "https://telegra.ph/file/3ef2cc0ad2bc548bafb30.jpg",
    "https://telegra.ph/file/a7d663cd2de689b811729.jpg",
    "https://telegra.ph/file/6f19dc23847f5b005e922.jpg",
    "https://telegra.ph/file/2973150dd62fd27a3a6ba.jpg",
]

bg_path = "assets/userinfo.png"
font_path = "assets/hiroko.ttf"

get_font = lambda font_size, font_path: ImageFont.truetype(font_path, font_size)

async def get_userinfo_img(
    bg_path: str,
    font_path: str,
    user_id: Union[int, str],
    profile_path: Optional[str] = None,
):
    bg = Image.open(bg_path)
    if profile_path:
        img = Image.open(profile_path)
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.pieslice([(0, 0), img.size], 0, 360, fill=255)
        circular_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
        circular_img.paste(img, (0, 0), mask)
        resized = circular_img.resize((400, 400))
        bg.paste(resized, (440, 160), resized)

    img_draw = ImageDraw.Draw(bg)
    img_draw.text(
        (529, 627),
        text=str(user_id).upper(),
        font=get_font(46, font_path),
        fill=(255, 255, 255),
    )
    path = f"downloads/userinfo_img_{user_id}.png"
    bg.save(path)
    return path

# --- COMMAND TO ON/OFF GOODBYE ---
@app.on_message(filters.command(["goodbye"]) & filters.group)
async def toggle_goodbye(client, message: Message):
    # Check if user is admin
    user_status = await client.get_chat_member(message.chat.id, message.from_user.id)
    if user_status.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return await message.reply_text("Aapke paas isse on/off karne ki permission nahi hai.")

    if len(message.command) < 2:
        return await message.reply_text("Usage: `/goodbye on` ya `/goodbye off`")

    state = message.command[1].lower()
    if state == "on":
        goodbye_status[message.chat.id] = True
        await message.reply_text("✅ Goodbye messages enabled for this chat.")
    elif state == "off":
        goodbye_status[message.chat.id] = False
        await message.reply_text("❌ Goodbye messages disabled for this chat.")
    else:
        await message.reply_text("Sahi command use karein: `on` ya `off`")

# --- MODIFIED LEFT HANDLER ---
@app.on_chat_member_updated(filters.group, group=-7)
async def member_has_left(client: app, member: ChatMemberUpdated):
    # Check if feature is ON for this group (Default Off)
    if not goodbye_status.get(member.chat.id, False):
        return

    if (
        not member.new_chat_member
        and member.old_chat_member.status not in {ChatMemberStatus.BANNED, ChatMemberStatus.LEFT, ChatMemberStatus.RESTRICTED}
        and member.old_chat_member
    ):
        user = (
            member.old_chat_member.user if member.old_chat_member else member.from_user
        )
        
        try:
            if user.photo:
                photo = await app.download_media(user.photo.big_file_id)
                welcome_photo = await get_userinfo_img(
                    bg_path=bg_path,
                    font_path=font_path,
                    user_id=user.id,
                    profile_path=photo,
                )
            else:
                welcome_photo = random.choice(random_photo)

            caption = f"**#New_Member_Left**\n\n**๏** {user.mention} **ʜᴀs ʟᴇғᴛ ᴛʜɪs ɢʀᴏᴜᴘ**\n**๏ sᴇᴇ ʏᴏᴜ sᴏᴏɴ ᴀɢᴀɪɴ..!**"
            button_text = "๏ ᴠɪᴇᴡ ᴜsᴇʀ ๏"

            message = await client.send_photo(
                chat_id=member.chat.id,
                photo=welcome_photo,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(button_text, user_id=user.id)]]
                ),
            )

            # Auto delete after 30 seconds
            await asyncio.sleep(30)
            await message.delete()
        except Exception as e:
            print(f"Error in goodbye: {e}")

__MODULE__ = "Goodbye"
__HELP__ = """
**Goodbye Feature**

/goodbye on - Group mein goodbye message chalu karne ke liye.
/goodbye off - Group mein goodbye message band karne ke liye.

Note: Ye sirf group admins hi kar sakte hain.
"""
