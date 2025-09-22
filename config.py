import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

admins_str = os.getenv("ADMINS")

ADMINS = [
    int(admin_id) for admin_id in admins_str.split(',')
    ] if admins_str else []
