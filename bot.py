import os
import zipfile
import asyncio
import time
import logging
from pyrogram import Client, filters, idle
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

def delete_old_backup():
    latest_backup = os.popen(f"rclone lsf {GDRIVE_FOLDER} --format \"t\" | sort | tail -1").read().strip()
    if latest_backup:
        os.system(f"rclone delete {GDRIVE_FOLDER}{latest_backup}")

async def do_backup(message: Message):
    global last_backup
    last_backup = time.time()
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    backup_zip_path = os.path.join(BACKUP_DIR, f"my_backup_{timestamp}.zip")

    with zipfile.ZipFile(backup_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(WORLD_FOLDER):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), WORLD_FOLDER))

    upload_message = await message.reply_text("Backup started. Uploading...")
    proc = await asyncio.create_subprocess_shell(
        f"rclone copy {backup_zip_path} {GDRIVE_FOLDER}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    while proc.returncode is None:
        await asyncio.sleep(5)
        await upload_message.edit_text("Uploading backup... Still in progress.")

    delete_old_backup()
    os.remove(backup_zip_path)
    await upload_message.edit_text("Backup uploaded to Google Drive successfully.")

@app.on_message(filters.command("backup"))
async def manual(_, message: Message):
    if time.time() - last_backup < MANUAL_GAP:
        await message.reply_text("Manual backup is on cooldown.")
        return
    await do_backup(message)

@app.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply_text("I'm a Minecraft backup bot! Use /backup to trigger a backup manually.")

async def main():
    await app.start()
    await idle()

if __name__ == "__main__":
    app.run()