import os import shutil import asyncio import logging import time from pyrogram import Client, filters from pyrogram.types import Message

API_ID = 123456 API_HASH = "your_api_hash" BOT_TOKEN = "your_bot_token" CHAT_ID = -1001234567890 WORLD_FOLDER = "/home/mcserver/minecraft_bedrock/worlds/my folder" BACKUP_COPY = "/home/mcserver/minecraft_backup" BACKUP_ZIP = "/home/mcserver/minecraft_backup.zip" BACKUP_INTERVAL = 4 * 60 * 60 MANUAL_GAP = 30 * 60 last_backup = 0

app = Client("mc_backup_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def auto_backup(): while True: await do_backup() await asyncio.sleep(BACKUP_INTERVAL)

async def do_backup(): try: if os.path.exists(BACKUP_COPY): shutil.rmtree(BACKUP_COPY) shutil.copytree(WORLD_FOLDER, BACKUP_COPY) shutil.make_archive(BACKUP_ZIP.replace(".zip", ""), 'zip', BACKUP_COPY) await app.send_document(CHAT_ID, BACKUP_ZIP, caption="Minecraft world backup") os.remove(BACKUP_ZIP) shutil.rmtree(BACKUP_COPY) except Exception as e: logging.error(f"Backup failed: {e}")

@app.on_message(filters.command("backup") & filters.chat(CHAT_ID)) async def manual(_, message: Message): global last_backup if time.time() - last_backup < MANUAL_GAP: await message.reply_text("Manual backup can only be triggered every 30 minutes.") return last_backup = time.time() await do_backup() await message.reply_text("Backup completed and sent.")

@app.on_message(filters.command("start")) async def start(_, message: Message): await message.reply_text("I'm a Minecraft backup bot! Use /backup to trigger a backup manually.")

async def main(): async with app: asyncio.create_task(auto_backup()) await app.run()

if name == "main": asyncio.run(main())

