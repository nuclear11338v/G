import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from yt_dlp import YoutubeDL  # Use yt-dlp instead of outdated youtube_dl
from pyrogram.raw import functions

# Replace these with your own values
API_ID = 27152769
API_HASH = "b98dff566803b43b3c3120eec537fc1d"
BOT_TOKEN = "7718086094:AAEJFB-X5rzMYLmpgxNCfdl-w7qDkfQOBt0"

# Initialize the Pyrogram client
app = Client("vc_music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# YouTube-DL options
YDL_OPTIONS = {
    "format": "bestaudio/best",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
    "outtmpl": "downloads/%(title)s.%(ext)s",
}

# Dictionary to track VC status per chat
vc_status = {}

# Function to check if the bot is in a VC
async def is_in_vc(chat_id):
    return vc_status.get(chat_id, False)

# Command: /start
@app.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply("🎵 Welcome to the VC Music Bot! Use /play <song_name> to play music in a voice chat.")

# Command: /join (Join VC)
@app.on_message(filters.command("join"))
async def join_vc(_, message: Message):
    chat_id = message.chat.id

    if message.chat.type != "supergroup":
        await message.reply("❌ Please use this command in a group with a voice chat.")
        return
    
    if await is_in_vc(chat_id):
        await message.reply("✅ Already in the voice chat.")
        return
    
    try:
        await app.send(functions.phone.JoinGroupCall(call="your_vc_call_id_here"))  
        vc_status[chat_id] = True
        await message.reply("✅ Joined the voice chat!")
    except Exception as e:
        await message.reply(f"❌ Error joining VC: {str(e)}")

# Command: /leave (Leave VC)
@app.on_message(filters.command("leave"))
async def leave_vc(_, message: Message):
    chat_id = message.chat.id

    if not await is_in_vc(chat_id):
        await message.reply("❌ Bot is not in a voice chat.")
        return

    try:
        await app.send(functions.phone.LeaveGroupCall(call="your_vc_call_id_here"))
        vc_status[chat_id] = False
        await message.reply("✅ Left the voice chat.")
    except Exception as e:
        await message.reply(f"❌ Error leaving VC: {str(e)}")

# Command: /play <song_name>
@app.on_message(filters.command("play"))
async def play_music(_, message: Message):
    chat_id = message.chat.id

    if len(message.command) < 2:
        await message.reply("❌ Please provide a song name. Usage: /play <song_name>")
        return

    song_name = " ".join(message.command[1:])
    await message.reply(f"🔍 Finding and playing: {song_name}...")

    try:
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch:{song_name}", download=False)
            if not info or not info.get("entries"):
                await message.reply("❌ No results found.")
                return

            song_url = info["entries"][0]["url"]
            song_title = info["entries"][0]["title"]

        await message.reply(f"🎶 Now playing: {song_title}")

        if not await is_in_vc(chat_id):
            await join_vc(_, message)  # Auto-join if not in VC

        await app.send_message(chat_id, "🔊 Streaming audio (functionality not implemented yet).")
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

# Command: /stop (Stop music)
@app.on_message(filters.command("stop"))
async def stop_music(_, message: Message):
    chat_id = message.chat.id

    if not await is_in_vc(chat_id):
        await message.reply("❌ Not currently playing any music.")
        return

    await message.reply("⏹️ Stopping music (Audio streaming not implemented yet).")

# Run the bot
print("🎵 VC Music Bot is running...")
app.run()
