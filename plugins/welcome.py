import asyncio, os, random, aiohttp, re
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from pyrogram import enums, filters
from pyrogram.types import ChatMemberUpdated, InlineKeyboardButton, InlineKeyboardMarkup, Message
from pymongo import MongoClient
from VIPMUSIC import app
from config import MONGO_DB_URI

# --- DB & Assets --- #
db = MongoClient(MONGO_DB_URI).welcome_status_db.status
FONT = "assets/elite_font.ttf"

async def get_status(chat_id):
    s = db.find_one({"chat_id": chat_id})
    return s.get("w", "on") if s else "on"

async def set_status(chat_id, s):
    db.update_one({"chat_id": chat_id}, {"$set": {"w": s}}, upsert=True)

# --- Pro Banner Engine --- #
def create_banner(bg_img, pfp_img, u_id, u_name, count):
    W, H = 1200, 600
    bg = bg_img.resize((W, H), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(2))
    bg = ImageEnhance.Brightness(bg).enhance(0.5)
    
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    dr.polygon([(450, 0), (W, 0), (W, H), (350, H)], fill=(0, 0, 0, 200))
    dr.line([(450, 0), (350, H)], fill=(0, 255, 255), width=8)
    bg = Image.alpha_composite(bg, ov)
    
    # Profile Pic
    pfp = pfp_img.resize((350, 350), Image.Resampling.LANCZOS)
    mask = Image.new("L", (350, 350), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 350, 350), fill=255)
    pfp.putalpha(mask)
    bg.paste(pfp, (50, 125), pfp)
    ImageDraw.Draw(bg).ellipse((40, 115, 410, 485), outline=(0, 255, 255), width=10)

    try: font = ImageFont.truetype(FONT, 80)
    except: font = ImageFont.load_default()
    
    draw = ImageDraw.Draw(bg)
    u_name = re.sub(r'[^\x20-\x7E]+', '', u_name)[:12] or "User"
    draw.text((490, 100), "WELCOME", font=font, fill=(0, 255, 255))
    draw.text((490, 200), u_name.upper(), font=font, fill=(255, 255, 255))
    draw.text((490, 330), f"ID: {u_id}\nRANK: #{count}", font=ImageFont.load_default(), fill=(200, 200, 200))
    
    path = f"downloads/{u_id}.png"
    bg.convert("RGB").save(path)
    return path

# --- Short Command: /wlc --- #
@app.on_message(filters.command("wlc") & filters.group)
async def wlc_toggle(_, m: Message):
    u = await app.get_chat_member(m.chat.id, m.from_user.id)
    if u.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
        return
    
    if len(m.command) < 2:
        return await m.reply("`Usage: /wlc on | off`")
    
    state = m.command[1].lower()
    if state in ["on", "off"]:
        await set_status(m.chat.id, state)
        await m.reply(f"✅ Welcome set to **{state.upper()}**")

# --- Join Handler --- #
@app.on_chat_member_updated(filters.group, group=10)
async def join_hnd(_, member: ChatMemberUpdated):
    if not (member.new_chat_member and not member.old_chat_member): return
    if await get_status(member.chat.id) == "off": return

    user = member.new_chat_member.user
    count = await app.get_chat_members_count(member.chat.id)
    
    try:
        # Background fallback
        async with aiohttp.ClientSession() as s:
            async with s.get("https://nekos.best/api/v2/wallpaper") as r:
                bg_url = (await r.json())['results'][0]['url']
                async with s.get(bg_url) as img_r: bg_img = Image.open(BytesIO(await img_r.read())).convert("RGBA")
        
        pfp_path = await app.download_media(user.photo.big_file_id) if user.photo else None
        pfp_img = Image.open(pfp_path).convert("RGBA") if pfp_path else Image.new("RGBA", (350, 350), (20, 20, 40))

        loop = asyncio.get_running_loop()
        card = await loop.run_in_executor(None, create_banner, bg_img, pfp_img, user.id, user.first_name, count)

        await app.send_photo(
            member.chat.id, photo=card,
            caption=f"<b>🌸 ɴᴇᴡ ɴᴀᴋᴀᴍᴀ 🌸</b>\n\n<b>👤 ɴᴀᴍᴇ:</b> {user.mention}\n<b>🆔 ɪᴅ:</b> <code>{user.id}</code>\n<b>✨ ᴜsᴇʀ:</b> <code>@{user.username}</code>\n<b>📊 ʀᴀɴᴋ:</b> #{count}\n\n<b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {member.chat.title}!</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ", url=f"https://t.me/{app.username}?startgroup=true")]])
        )
        if os.path.exists(card): os.remove(card)
        if pfp_path: os.remove(pfp_path)
    except: pass

__MODULE__ = "Welcome"
__HELP__ = "/wlc on - Enable\n/wlc off - Disable"
