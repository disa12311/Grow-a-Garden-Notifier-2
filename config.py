import os
import json

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
NTFY_TOPIC = os.getenv("NTFY_TOPIC")

# SỬA LỖI Ở ĐÂY: Dùng dấu ngoặc kép ba (""") để bao bọc chuỗi JSON
CHANNEL_IDS_STR = os.getenv("CHANNEL_IDS", """{"channelid1": "1384132746586095717", "channelid2": "1384341013895839864", "channelid3": "1384341088936005663", "channelid4": "1384341088936005663"}""")
CHANNEL_IDS = json.loads(CHANNEL_IDS_STR)
