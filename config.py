import os
import json

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
NTFY_TOPIC = os.getenv("NTFY_TOPIC")

# SỬA LỖI Ở ĐÂY:
# Kiểm tra nếu biến môi trường "CHANNEL_IDS" tồn tại
if os.getenv("CHANNEL_IDS"):
    # Nếu có, tải từ chuỗi JSON của biến môi trường
    CHANNEL_IDS = json.loads(os.getenv("CHANNEL_IDS"))
else:
    # Nếu không, sử dụng từ điển mặc định trong code
    CHANNEL_IDS = {
        "channelid1": "1384132746586095717",
        "channelid2": "1384341013895839864",
        "channelid3": "1384341088936005663",
        "channelid4": "1384341088936005663"
    }
