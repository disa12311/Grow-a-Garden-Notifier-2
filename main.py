import discord
import re
import requests
import json
import os
from config import DISCORD_TOKEN, CHANNEL_IDS, NTFY_TOPIC

# Các danh sách và từ điển cấu hình cho vật phẩm và màu sắc
default_priority_items = [
    "Nectarine", "Mango", "Grape", "Mushroom", "Pepper", "Cacao",
    "Beanstalk", "Stone Pillar", "Bird Bath", "Lamp Post",
    "Tractor", "Lightning Rod", "Godly"
]

high_priority_items = [
    "Beanstalk", "Friendship Pot", "Ember Lily", "Hive Fruit", "Master Sprinkler",
    "Honey Sprinkler", "Bee Egg", "Bug Egg", "Mythical Egg"
]

color_map = {
    "Carrot": "\033[92m", "Strawberry": "\033[92m", "Blueberry": "\033[92m", "Orange": "\033[92m",
    "Tomato": "\033[92m", "Corn": "\033[92m", "Daffodil": "\033[92m",
    "Watermelon": "\033[93m", "Pumpkin": "\033[93m", "Apple": "\033[93m", "Bamboo": "\033[93m",
    "Coconut": "\033[33m", "Cactus": "\033[33m", "Dragon": "\033[33m", "Mango": "\033[33m",
    "Grape": "\033[95m", "Mushroom": "\033[95m", "Pepper": "\033[95m", "Cacao": "\033[95m",
    "Beanstalk": "\033[96m",
    "Watering": "\033[92m", "Trowel": "\033[92m", "Recall": "\033[92m",
    "Basic": "\033[93m",
    "Advanced": "\033[95m",
    "Lightning": "\033[33m", "Godly": "\033[33m",
    "Harvest": "\033[35m", "Master": "\033[35m", "Favorite": "\033[35m",
    "Common Egg": "\033[92m", "Uncommon Egg": "\033[92m",
    "Legendary Egg": "\033[95m", "Bug Egg": "\033[91m", "Mythical Egg": "\033[33m",
    "Flower Seed Pack": "\033[92m",
    "Nectarine Seed": "\033[33m",
    "Hive Fruit Seed": "\033[93m",
    "Honey Sprinkler": "\033[33m",
    "Bee Egg": "\033[33m",
    "Bee Crate": "\033[95m",
    "Brick Stack": "\033[92m",
    "Compost Bin": "\033[92m",
    "Log": "\033[92m",
    "Wood Pile": "\033[92m",
    "Torch": "\033[92m",
    "Circle Tile": "\033[92m",
    "Path Tile": "\033[92m",
    "Rock Pile": "\033[92m",
    "Pottery": "\033[92m",
    "Rake": "\033[92m",
    "Umbrella": "\033[92m",
    "Log Bench": "\033[94m",
    "Brown Bench": "\033[94m",
    "White Bench": "\033[94m",
    "Hay Bale": "\033[94m",
    "Stone Pad": "\033[94m",
    "Stone Table": "\033[94m",
    "Wood Fence": "\033[94m",
    "Wood Flooring": "\033[94m",
    "Mini TV": "\033[94m",
    "Viney Beam": "\033[94m",
    "Light On Ground": "\033[94m",
    "Water Trough": "\033[94m",
    "Shovel Grave": "\033[94m",
    "Stone Lantern": "\033[94m",
    "Bookshelf": "\033[94m",
    "Axe Stump": "\033[94m",
    "Stone Pillar": "\033[95m",
    "Wood Table": "\033[95m",
    "Canopy": "\033[95m",
    "Campfire": "\033[95m",
    "Cooking Pot": "\033[95m",
    "Clothesline": "\033[95m",
    "Wood Arbour": "\033[93m",
    "Metal Arbour": "\033[93m",
    "Bird Bath": "\033[95m",
    "Lamp Post": "\033[95m",
    "Wind Chime": "\033[95m",
    "Well": "\033[93m",
    "Ring Walkway": "\033[93m",
    "Tractor": "\033[93m",
    "Honey Comb": "\033[33m",
    "Honey Torch": "\033[33m",
    "Bee Chair": "\033[33m",
    "Honey Walkway": "\033[33m",
    "Gnome Crate": "\033[33m",
    "Sign Crate": "\033[33m",
    "Bloodmoon Crate": "\033[33m",
    "Twilight Crate": "\033[33m",
    "Mysterious Crate": "\033[33m",
    "Fun Crate": "\033[33m",
    "Monster Mash Trophy": "\033[91m"
}

RESET_COLOR = "\033[0m"

# Các biến toàn cục để theo dõi trạng thái
previous_stock = set()
current_stock = set()
items_to_notify = []

# Cấu hình Intents cho bot Discord
intents = discord.Intents.default()
# Cần bật MESSAGE CONTENT INTENT trong Discord Developer Portal (phần Bot)
intents.message_content = True
# intents.messages và intents.guilds đã được bao gồm trong discord.Intents.default()
# nhưng việc để rõ ràng cũng không sao
# intents.messages = True
# intents.guilds = True

# Khởi tạo Discord client với các intents đã cấu hình
client = discord.Client(intents=intents)

def extract_items(text):
    """
    Trích xuất các mục từ văn bản, loại bỏ emoji và định dạng Discord.
    """
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        # Loại bỏ các emoji tùy chỉnh Discord (<:tên_emoji:ID>)
        line = re.sub(r"<:[^:]+:\d+>", "", line)
        # Loại bỏ định dạng markdown (*, _, ~, `)
        line = re.sub(r"[*_~`]", "", line)
        line = line.strip()
        # Chỉ thêm các dòng có chứa " x" (thường là số lượng vật phẩm)
        if " x" in line.lower():
            cleaned.append(line)
    return cleaned

def colorize_text(text, color_code):
    """
    Thêm mã màu ANSI vào văn bản để in ra console.
    """
    return f"{color_code}{text}{RESET_COLOR}"

def _send_ntfy_notification_blocking(title, message, priority):
    """
    Hàm gửi thông báo Ntfy. Hàm này là blocking I/O (đồng bộ).
    Nó sẽ được gọi thông qua client.loop.run_in_executor để không chặn event loop chính.
    """
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    headers = {
        "Title": title,
        "Priority": "5" if priority == "high" else "3"
    }
    try:
        requests.post(url, data=message.encode('utf-8'), headers=headers)
    except Exception as e:
        print(f"Failed to send Ntfy notification: {e}")

@client.event
async def on_ready():
    """
    Sự kiện khi bot đã sẵn sàng và đăng nhập thành công.
    """
    print(f"Logged in as {client.user} ({client.user.id})")
    print(f"Bot is ready to process messages in channels (configured IDs): {CHANNEL_IDS.values()}")
    # === DEBUG: In ra cấu hình CHANNEL_IDS để kiểm tra ===
    print(f"Full CHANNEL_IDS dictionary: {CHANNEL_IDS}")
    # =====================================================

# Tạo danh sách các mục kết hợp để kiểm tra thông báo
combined_items = default_priority_items + high_priority_items

@client.event
async def on_message(message):
    global current_stock, previous_stock, items_to_notify

    # === DEBUG: In ra thông tin tin nhắn đầu vào ===
    print(f"\n--- New Message Received ---")
    print(f"Message Author: {message.author} (ID: {message.author.id})")
    print(f"Message Channel ID: {message.channel.id}")
    print(f"Message Content: '{message.content}'")
    print(f"Has Embeds: {len(message.embeds) > 0}")
    # =================================================

    # Bỏ qua tin nhắn từ chính bot
    if message.author == client.user:
        print(f"Skipping own message from {message.author.name}")
        return

    # Kiểm tra xem kênh tin nhắn có trong danh sách CHANNEL_IDS không
    if message.channel.id not in CHANNEL_IDS.values():
        print(f"Channel ID {message.channel.id} is NOT in configured CHANNEL_IDS. Skipping.")
        return
    else:
        print(f"Channel ID {message.channel.id} IS IN configured CHANNEL_IDS.")

    # Lấy tên kênh từ ID của kênh
    channel_name = next((name for name, id_val in CHANNEL_IDS.items() if id_val == message.channel.id), None)
    if channel_name is None: # Về lý thuyết không nên xảy ra nếu điều kiện trên đã đúng, nhưng thêm để an toàn
        print(f"Could not find channel name for ID {message.channel.id}. Skipping.")
        return

    print(f"Processing message in channel: {channel_name}")

    any_stock_found = False
    current_stock.clear()
    items_to_notify.clear()

    if not message.embeds:
        print("Message has no embeds. Skipping embed processing.")
        return

    # Xử lý các embeds (nhúng) trong tin nhắn
    for embed_index, embed in enumerate(message.embeds):
        print(f"Processing Embed #{embed_index + 1}")
        print(f"Embed Title: {embed.title}")
        print(f"Embed Description: {embed.description}")
        print(f"Number of fields in Embed: {len(embed.fields)}")

        # Xử lý thông báo thời tiết
        if channel_name == "Weather": # Bạn cần đảm bảo có một key "Weather" trong CHANNEL_IDS của mình
            print("\n╭── Weather Alert ──╮")
            if embed.title:
                print(f"│ Title: {embed.title}")
            if embed.description:
                for line in embed.description.splitlines():
                    print(f"│ Desc: {line.strip()}")
            print("╰────────────────────╯")
            weather_msg = f"{embed.title or 'Weather Update'}\n{embed.description or ''}"
            await client.loop.run_in_executor(
                None, _send_ntfy_notification_blocking, "Weather Alert", weather_msg.strip(), "default"
            )
            print("Ntfy weather notification scheduled.")
            continue

        # Xử lý các trường (fields) trong embed (thường chứa danh sách vật phẩm)
        if not embed.fields:
            print("Embed has no fields. Skipping field processing for this embed.")
            continue

        for field_index, field in enumerate(embed.fields):
            print(f"Processing Field #{field_index + 1}: Name='{field.name.strip()}'")
            stock_items = extract_items(field.value) # Trích xuất vật phẩm từ giá trị của trường
            print(f"Extracted {len(stock_items)} items from field value.")

            if not stock_items:
                print(f"No stock items extracted from field '{field.name.strip()}'. Skipping.")
                continue

            any_stock_found = True
            print(f"\n╭── {field.name.strip()} ──╮")
            for item_text in stock_items:
                print(f"  Processing item: '{item_text}'")
                current_stock.add(item_text) # Thêm vật phẩm vào danh sách stock hiện tại

                # Kiểm tra các mục ưu tiên để thông báo nếu đó là vật phẩm MỚI
                for notify_item in combined_items:
                    if notify_item.lower() in item_text.lower() and item_text not in previous_stock:
                        items_to_notify.append(item_text)
                        print(f"    - Added '{item_text}' to items_to_notify (NEW ITEM).")

                # Xác định màu sắc để in ra console
                item_color = None
                for item_name, color in color_map.items():
                    if item_name.lower() in item_text.lower():
                        item_color = color
                        break

                if item_color:
                    print(colorize_text(f"│ • {item_text}", item_color))
                else:
                    print(f"│ • {item_text}")
            print("╰" + "─" * (len(field.name.strip()) + 6) + "╯")

    # Gửi thông báo Ntfy nếu có bất kỳ vật phẩm mới nào được tìm thấy
    if any_stock_found and items_to_notify:
        print(f"Found new items to notify: {items_to_notify}")
        for item in items_to_notify:
            priority = "high" if any(h.lower() in item.lower() for h in high_priority_items) else "default"
            await client.loop.run_in_executor(
                None, _send_ntfy_notification_blocking, "Grow A Garden: New Stock", f"{item} is now on stock!", priority
            )
            print(f"Ntfy notification scheduled for '{item}' with priority '{priority}'.")
    else:
        print("No new stock items found to notify.")

    previous_stock = current_stock.copy()
    print(f"Updated previous_stock. previous_stock now has {len(previous_stock)} items.")
    print(f"--- Message Processing Complete ---")

client.run(DISCORD_TOKEN)
