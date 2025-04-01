import os
import shutil
import asyncio
import time
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = 13691707
API_HASH = "2a31b117896c5c7da27c74025aa602b8"
BOT_TOKEN = "7544752676:AAHG240y6RkGM5uXpWrF2GA9woCnU9hlOd8"
CHAT_ID = -1002533275162
WORLD_FOLDER = "/home/mcserver/minecraft_bedrock/worlds/my"
BACKUP_DIR = "/home/mcserver/minecraft_bedrock/backups/"
GDRIVE_FOLDER = "delta:Backups/"
MANUAL_GAP = 300

app = Client("mc_backup_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
last_backup = 0

def get_latest_backup():
    result = os.popen(f"rclone lsf {GDRIVE_FOLDER} --format ""t"" | sort | tail -1").read().strip()
    return result if result else None

async def do_backup(message):
    try:
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        backup_zip = os.path.join(BACKUP_DIR, f"my_backup_{timestamp}.zip")
        shutil.make_archive(backup_zip.replace(".zip", ""), 'zip', WORLD_FOLDER)
        await message.reply_text("Backup started. Uploading...")

        latest_backup = get_latest_backup()
        
        upload = await app.send_message(message.chat.id, "Uploading backup...")
        
        proc = await asyncio.create_subprocess_shell(
            f"rclone copy {backup_zip} {GDRIVE_FOLDER} --progress",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        while proc.returncode is None:
            await asyncio.sleep(5)
            await upload.edit_text("Uploading backup... Still in progress.")
        
        if latest_backup:
            os.system(f"rclone delete {GDRIVE_FOLDER}{latest_backup}")
        
        os.remove(backup_zip)
        await upload.edit_text("Backup uploaded to Google Drive successfully.")
    except Exception as e:
        logging.error(f"Backup failed: {e}")
        await message.reply_text(f"Backup failed: {e}")

@app.on_message(filters.command("backup"))
async def manual(_, message: Message):
    global last_backup
    if time.time() - last_backup < MANUAL_GAP:
        await message.reply_text("Manual backup is on cooldown.")
        return
    last_backup = time.time()
    await do_backup(message)

@app.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply_text("I'm a Minecraft backup bot! Use /backup to trigger a backup manually.")

if __name__ == "__main__":
    app.run()
