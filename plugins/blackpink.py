import requests
from pyrogram import filters
from VIPMUSIC import app
from config import BANNED_USERS

@app.on_message(filters.command(["blackpink"]) & ~BANNED_USERS)
async def blackpink_chat(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "कृपया नाम लिखें, उदाहरण: `/blackpink Radhe Radhe`"
        )
    
    # यूजर द्वारा दिया गया नाम
    args = message.text.split(None, 1)[1]
    a = await message.reply_text("Creating BlackPink for You.....")

    # हमने safoneAPI लाइब्रेरी हटाकर सीधा API लिंक इस्तेमाल किया है
    # इससे बोट क्रैश नहीं होगा
    api_url = f"https://api.single-developers.software/blackpink?name={args}"

    try:
        # फोटो भेजना
        await message.reply_photo(
            photo=api_url,
            caption=f"✨ BlackPink Logo Created for: **{args}**"
        )
        await a.delete()
    except Exception as e:
        await a.edit_text(f"फोटो बनाने में समस्या आई। शायद API डाउन है।\nError: {e}")

# --- RedBlue Command (बिना किसी एक्स्ट्रा लाइब्रेरी के) ---

@app.on_message(filters.command(["redblue"]) & ~BANNED_USERS)
async def redblue_chat(client, message):
    if len(message.command) < 2:
        return await message.reply_text("कृपया नाम लिखें, उदाहरण: `/redblue Radhe` ")
    
    args = message.text.split(None, 1)[1]
    a = await message.reply_text("Creating RedBlue for You.....")
    
    # RedBlue के लिए API लिंक
    api_url = f"https://api.single-developers.software/texttoimage?name={args}"

    try:
        await message.reply_photo(photo=api_url, caption=f"RedBlue Logo for: **{args}**")
        await a.delete()
    except Exception as e:
        await a.edit_text(f"Error: {e}")
