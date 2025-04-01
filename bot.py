import os
import shutil
import asyncio
import logging
import time
from pyrogram import Client, filters, idle
from pyrogram.types import Message

API_ID = 13691707
API_HASH = "2a31b117896c5c7da27c74025aa602b8"
BOT_TOKEN = "7544752676:AAHG240y6RkGM5uXpWrF2GA9woCnU9hlOd8"
CHAT_ID = -1002533275162
WORLD_FOLDER = "/home/mcserver/minecraft_bedrock/worlds/my"
BACKUP_COPY = "/home/mcserver/minecraft_bedrock/backups/my"
BACKUP_DIR = "/home/mcserver/minecraft_bedrock/backups/"
BACKUP_INTERVAL = 3600
MANUAL_GAP = 300

app = Client("mc_backup_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

last_backup = 0

async def do_backup():
    try:
        if os.path.exists(BACKUP_COPY):
            shutil.rmtree(BACKUP_COPY)
        shutil.copytree(WORLD_FOLDER, BACKUP_COPY, symlinks=True, ignore_dangling_symlinks=True)
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        backup_zip_path = os.path.join(BACKUP_DIR, f"my_folder_{timestamp}.zip")
        shutil.make_archive(backup_zip_path.replace(".zip", ""), 'zip', BACKUP_COPY)
        logging.info("Backup successful")
        await app.send_document(CHAT_ID, backup_zip_path, caption=f"Backup created: {timestamp}")
        os.remove(backup_zip_path)
    except Exception as e:
        logging.error(f"Backup failed: {e}")

async def auto_backup():
    while True:
        await do_backup()
        await asyncio.sleep(BACKUP_INTERVAL)

@app.on_message(filters.command("backup"))
async def manual(_, message: Message):
    global last_backup
    if time.time() - last_backup < MANUAL_GAP:
        await message.reply_text("Manual backup is on cooldown.")
        return
    last_backup = time.time()
    await do_backup()
    await message.reply_text("Manual backup completed and sent to the channel.")

@app.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply_text("I'm a Minecraft backup bot! Use /backup to trigger a backup manually.")

async def main():
    await app.start()
    asyncio.create_task(auto_backup())
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
