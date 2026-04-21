import random
import re
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.enums import ChatAction, ChatMemberStatus
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from deep_translator import GoogleTranslator 
from config import MONGO_DB_URI as MONGO_URL
import config
from VIPMUSIC import app as nexichat

# --- Database Setup ---
WORD_MONGO_URL = "mongodb+srv://vishalpandeynkp:Bal6Y6FZeQeoAoqV@cluster0.dzgwt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

chatdb = MongoClient(MONGO_URL)
worddb = MongoClient(WORD_MONGO_URL)
status_db = chatdb["ChatBotStatusDb"]["StatusCollection"]
chatai = worddb["Word"]["WordDb"] 
lang_db = chatdb["ChatLangDb"]["LangCollection"]

# --- Female Tone Logic ---
def make_female_tone(text):
    replacements = {
        r"\braha hoon\b": "rahi hoon",
        r"\braha tha\b": "rahi thi",
        r"\braha hai\b": "rahi hai",
        r"\bgaya tha\b": "gayi thi",
        r"\bgaya\b": "gayi",
        r"\btha\b": "thi",
        r"\bkhata hoon\b": "khati hoon",
        r"\bkarunga\b": "karungi",
        r"\baaunga\b": "aaungi",
        r"\bdekhunga\b": "dekhungi",
        r"\bbhai\b": "behen 🌸",
        r"\bbhaiya\b": "didi",
        r"\bpagal\b": "pagli",
        r"\bhoon\b": "hoon ji ✨"
    }
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

# --- Abuse Filter ---
ABUSIVE_WORDS = ["saala", "bc", "mc", "chutiya", "randi", "bhadwa", "kamine", "gaand", "madarchod"]

# --- Helper Functions ---
async def is_admin(client, chat_id, user_id):
    if chat_id > 0: return True # Private chat
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

def get_chat_language(chat_id):
    chat_lang = lang_db.find_one({"chat_id": chat_id})
    return chat_lang["language"] if chat_lang and "language" in chat_lang else "hi"

async def get_reply(word: str):
    # Try exact match
    is_chat = list(chatai.find({"word": word.lower()}))
    if not is_chat:
        # Fallback: Get a random reply from database
        is_chat = list(chatai.aggregate([{"$sample": {"size": 1}}]))
    return random.choice(is_chat) if is_chat else None

# --- Chatbot Logic ---

@nexichat.on_message((filters.text | filters.sticker) & ~filters.bot, group=2)
async def chatbot_response(client: Client, message: Message):
    chat_id = message.chat.id
    user_text = message.text.lower() if message.text else ""
    
    # 1. Check if chatbot is disabled for this chat
    chat_status = status_db.find_one({"chat_id": chat_id})
    if chat_status and chat_status.get("status") == "disabled":
        return

    # 2. Skip commands
    if user_text.startswith(("/", "!", ".")):
        return

    # 3. Special "Radhe Radhe" Logic
    if "radhe" in user_text:
        radhe_replies = [
            "Radhe Radhe ji! 🌸 Kanha ji aap par hamesha kripa banaye rakhein.",
            "Radhe Radhe! ✨ Kaise ho aap? Krishna ki bhakti mein hi shanti hai. 🙏",
            "Radhe Radhe! ❤️ Bolo Radhe-Krishna ki Jai! 😊",
            "Radhe Radhe! 🌸 Aapka din bahut achha jaye ji."
        ]
        await client.send_chat_action(chat_id, ChatAction.TYPING)
        return await message.reply_text(random.choice(radhe_replies))

    # 4. Abuse Filter
    if any(word in user_text for word in ABUSIVE_WORDS):
        return await message.reply_text("Gandi baat nahi karte! Tameez se bolo. 😡")

    # 5. Trigger Conditions (Bot kab reply karega)
    is_private = message.chat.type.value == "private"
    is_reply_to_me = message.reply_to_message and message.reply_to_message.from_user.id == (await client.get_me()).id
    
    # Keyword list to trigger bot in groups
    keywords = ["hi", "hello", "kaise", "bot", "zoya", "hey", "namaste", "sun"]
    is_keyword = any(re.search(rf"\b{word}\b", user_text) for word in keywords)

    # Trigger logic
    if is_private or is_reply_to_me or is_keyword:
        await client.send_chat_action(chat_id, ChatAction.TYPING)
        
        reply_data = await get_reply(user_text)
        
        if reply_data:
            response_text = reply_data["text"]
            check_type = reply_data.get("check")

            # Female Tone
            if check_type != "sticker" and check_type != "photo":
                response_text = make_female_tone(response_text)

            # Translation
            chat_lang = get_chat_language(chat_id)
            if chat_lang not in ["hi", "en", "nolang"]:
                try:
                    response_text = GoogleTranslator(source='auto', target=chat_lang).translate(response_text)
                except:
                    pass

            # Final Reply Execution
            if check_type == "sticker":
                await message.reply_sticker(response_text)
            elif check_type == "photo":
                await message.reply_photo(response_text)
            else:
                await message.reply_text(response_text)
        else:
            if is_private:
                await message.reply_text("Umm... main samajh nahi paayi, par sunne mein achha laga! 🌸")

    # 6. Learning Logic (Save replies)
    if message.reply_to_message and not any(word in user_text for word in ABUSIVE_WORDS):
        if message.text and len(message.text) > 1:
            await save_reply(message.reply_to_message, message)

async def save_reply(original_message: Message, reply_message: Message):
    if not original_message.text: return
    
    content = reply_message.text or (reply_message.sticker.file_id if reply_message.sticker else None)
    if not content: return

    check_type = "sticker" if reply_message.sticker else "none"
    trigger = original_message.text.lower()
    
    if not chatai.find_one({"word": trigger, "text": content}):
        chatai.insert_one({"word": trigger, "text": content, "check": check_type})

# --- Admin Commands ---

@nexichat.on_message(filters.command("chatbot"))
async def chat_toggle(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text("Sirf admins hi ye kar sakte hain! ❌")

    status = "Enabled ✅"
    curr = status_db.find_one({"chat_id": message.chat.id})
    if curr and curr.get("status") == "disabled":
        status = "Disabled ❌"

    buttons = [[
        InlineKeyboardButton("Enable", callback_data="enable_chatbot"),
        InlineKeyboardButton("Disable", callback_data="disable_chatbot")
    ]]
    await message.reply_text(
        f"<b>Chatbot Settings for {message.chat.title if message.chat.title else 'Private Chat'}</b>\n\nStatus: {status}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@nexichat.on_callback_query(filters.regex(r"^(enable|disable)_chatbot$"))
async def cb_handler(client: Client, query: CallbackQuery):
    if not await is_admin(client, query.message.chat.id, query.from_user.id):
        return await query.answer("Access Denied! ⛔", show_alert=True)

    action = query.data.split("_")[0]
    status_db.update_one({"chat_id": query.message.chat.id}, {"$set": {"status": f"{action}d"}}, upsert=True)
    await query.edit_message_text(f"✅ Chatbot has been **{action}d** successfully!")
