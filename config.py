import os
import json
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
NTFY_TOPIC = os.getenv("NTFY_TOPIC")
if os.getenv("CHANNEL_IDS"):
    CHANNEL_IDS = json.loads(os.getenv("CHANNEL_IDS"))
else:
    CHANNEL_IDS = {
        "channelid1": "1384132746586095717",
        "channelid2": "1384341013895839864",
        "channelid3": "1384341088936005663",
        "channelid4": "1384341088936005663"
    }
