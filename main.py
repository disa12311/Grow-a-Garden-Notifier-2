import discord
import re
import requests
import json # Cần import json nếu CHANNEL_IDS được đọc từ biến môi trường dạng JSON
import os   # Cần import os nếu DISCORD_TOKEN, NTFY_TOPIC được đọc từ biến môi trường

# Import các biến cấu hình từ tệp config.py
# Đảm bảo rằng config.py của bạn đã được cập nhật để đọc các biến này từ môi trường Railway
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
    # In ra các kênh bot đang theo dõi từ CHANNEL_IDS.values()
    print(f"Bot is ready to process messages in channels: {CHANNEL_IDS.values()}")

# Tạo danh sách các mục kết hợp để kiểm tra thông báo
combined_items = default_priority_items + high_priority_items

@client.event
async def on_message(message):
    """
    Sự kiện khi bot nhận được tin nhắn.
    """
    global current_stock, previous_stock, items_to_notify

    # Bỏ qua tin nhắn từ chính bot để tránh lặp vô hạn
    # Bỏ qua tin nhắn nếu kênh không nằm trong danh sách CHANNEL_IDS được cấu hình
    if message.author == client.user or message.channel.id not in CHANNEL_IDS.values():
        return

    # Lấy tên kênh từ ID của kênh, giả sử CHANNEL_IDS là {tên_kênh: ID_kênh}
    # Đây là một cách lấy tên kênh, có thể tối ưu hơn nếu CHANNEL_IDS được cấu trúc khác
    # Ví dụ: channel_name = next((name for name, id_val in CHANNEL_IDS.items() if id_val == message.channel.id), None)
    # Và sau đó kiểm tra 'if channel_name is None: return'
    channel_name = [name for name, id_val in CHANNEL_IDS.items() if id_val == message.channel.id][0]

    any_stock_found = False
    current_stock.clear() # Xóa danh sách stock hiện tại cho tin nhắn mới
    items_to_notify.clear() # Xóa danh sách thông báo cho tin nhắn mới

    # Xử lý các embeds (nhúng) trong tin nhắn
    for embed in message.embeds:
        # Xử lý thông báo thời tiết nếu kênh là "Weather"
        if channel_name == "Weather": # Bạn cần đảm bảo có một key "Weather" trong CHANNEL_IDS của mình
            print("\n╭── Weather Alert ──╮")
            if embed.title:
                print(f"│ {embed.title}")
            if embed.description:
                for line in embed.description.splitlines():
                    print(f"│ {line.strip()}")
            print("╰────────────────────╯")
            weather_msg = f"{embed.title or 'Weather Update'}\n{embed.description or ''}"
            # Gửi thông báo Ntfy mà không chặn main event loop
            await client.loop.run_in_executor(
                None, _send_ntfy_notification_blocking, "Weather Alert", weather_msg.strip(), "default"
            )
            continue # Chuyển sang embed tiếp theo hoặc kết thúc xử lý tin nhắn nếu không có gì khác

        # Xử lý các trường (fields) trong embed (thường chứa danh sách vật phẩm)
        for field in embed.fields:
            stock_items = extract_items(field.value) # Trích xuất vật phẩm từ giá trị của trường
            if not stock_items:
                continue # Bỏ qua nếu không có vật phẩm nào được trích xuất

            any_stock_found = True
            print(f"\n╭── {field.name.strip()} ──╮")
            for item_text in stock_items:
                current_stock.add(item_text) # Thêm vật phẩm vào danh sách stock hiện tại

                # Kiểm tra các mục ưu tiên để thông báo nếu đó là vật phẩm MỚI
                for notify_item in combined_items:
                    # Kiểm tra xem item có trong danh sách cần thông báo VÀ CHƯA TỪNG được thông báo TRƯỚC ĐÓ không
                    if notify_item.lower() in item_text.lower() and item_text not in previous_stock:
                        items_to_notify.append(item_text)

                # Xác định màu sắc để in ra console
                item_color = None
                for item_name, color in color_map.items():
                    if item_name.lower() in item_text.lower():
                        item_color = color
                        break # Tìm thấy màu, thoát vòng lặp

                if item_color:
                    print(colorize_text(f"│ • {item_text}", item_color))
                else:
                    print(f"│ • {item_text}")
            print("╰" + "─" * (len(field.name.strip()) + 6) + "╯")

    # Gửi thông báo Ntfy nếu có bất kỳ vật phẩm mới nào được tìm thấy
    if any_stock_found and items_to_notify:
        for item in items_to_notify:
            priority = "high" if any(h.lower() in item.lower() for h in high_priority_items) else "default"
            # Gửi thông báo Ntfy mà không chặn main event loop
            await client.loop.run_in_executor(
                None, _send_ntfy_notification_blocking, "Grow A Garden: New Stock", f"{item} is now on stock!", priority
            )

    # Cập nhật previous_stock cho lần kiểm tra tiếp theo
    previous_stock = current_stock.copy()

# Chạy bot
client.run(DISCORD_TOKEN)
