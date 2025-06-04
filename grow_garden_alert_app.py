import discord
import serial
import time
import threading
import re

# === CONFIGURATION ===
DISCORD_BOT_TOKEN = "MTM3ODcyOTQzMTAwMTk4OTE0MA.GxV3i0.RPRjT8iyrgznC1nhpa80Uzi1UgW5jp7sO61PBM"
STOCK_BOT_ID = 1378640081237049405
ARDUINO_PORT = "/dev/tty.usbmodem1101"
BAUD_RATE = 9600
STATUS_CHANNEL_ID = 1378406177112850583

# === DM TARGET USERS ===
DM_USER_IDS = [1280115220395593823, 805670742808985610]

# === ALERT CRITERIA ===
SEEDS_OF_INTEREST = [
    "cacao", "pepper", "beanstalk", "mango",
    "cactus", "bamboo", "mushroom", "grape", "coconut"
]
SPECIAL_SEEDS = ["bamboo", "cacao", "beanstalk", "grape", "mango", "pepper", "mushroom",]
WEATHER_OF_INTEREST = ["snow", "thunderstorm"]
EGGS_OF_INTEREST = ["bug egg", "legendary egg", "mythical egg"]


# === HELPER: CLEAN DISCORD TEXT ===
def clean_discord_text(text):
    text = re.sub(r'<a?:\w+:\d+>', '', text)
    text = re.sub(r'[*_~]', '', text)
    return text.lower()

# === CONNECT TO ARDUINO ===
try:
    arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(f"[✓] Connected to Arduino on {ARDUINO_PORT}")
except Exception as e:
    arduino = None
    print(f"[!] Could not connect to Arduino: {e}")

# === FUNCTION TO BUZZ BUZZER IN PATTERN ===
def buzz_buzzer():
    if arduino:
        print("[!] Activating buzzer in repeating pattern!")
        for _ in range(10):
            arduino.write(b'1')   # turn buzzer ON
            arduino.flush()
            time.sleep(0.05)         # wait 1 second
            arduino.write(b'0')   # turn buzzer OFF
            arduino.flush()
            time.sleep(0.05)         # wait 1 second
    else:
        print("[!] Arduino not connected — cannot buzz.")

# === FUNCTION TO DM USERS ===
async def dm_users(message_text):
    for user_id in DM_USER_IDS:
        try:
            user = await client.fetch_user(user_id)
            await user.send(f"[SEED ALERT] A tracked seed is in stock:\n```{message_text}```")
            print(f"[✓] DM sent to user {user_id}")
        except Exception as e:
            print(f"[!] Failed to DM user {user_id}: {e}")

# === DISCORD CLIENT SETUP ===
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"[✓] Logged in as {client.user}")

    await client.change_presence(
        status=discord.Status.idle,
        activity=discord.Activity(type=discord.ActivityType.watching, name="yug._.")
    )

    channel = client.get_channel(STATUS_CHANNEL_ID)
    if channel:
        try:
            await channel.send("Status: ON!!! 🟢 -- Made by @yug._. + calz (monitoring Grow a Garden for him)")
            print("[✓] Status message sent.")
        except Exception as e:
            print(f"[!] Failed to send status message: {e}")
    else:
        print(f"[!] Could not find channel with ID {STATUS_CHANNEL_ID}")

    for user_id in DM_USER_IDS:
        try:
            user = await client.fetch_user(user_id)
            await user.send("hi mrigank >:)")
            await user.send("halak tuah")
            print(f"[✓] DM sent to user {user_id}")
        except Exception as e:
            print(f"[!] Failed to send DM to user {user_id}: {e}")

@client.event
async def on_message(message):
    if message.author.id != STOCK_BOT_ID:
        return

    print(f"[DEBUG] Received message from {message.author} (ID: {message.author.id}): {message.content}")
    msg = message.content.lower()

    if msg:
        print(f"[DEBUG] Plain message content: {msg}")
        if "shop stock refreshed!" in msg:
            if any(seed in msg for seed in SEEDS_OF_INTEREST):
                print("[!] Matching seed found!")
                threading.Thread(target=buzz_buzzer).start()
            if any(seed in msg for seed in SPECIAL_SEEDS):
                await dm_users(msg)

        elif "weather" in msg and any(weather in msg for weather in WEATHER_OF_INTEREST):
            print("[!] Matching weather found!")
            threading.Thread(target=buzz_buzzer).start()

        elif "egg" in msg and any(egg in msg for egg in EGGS_OF_INTEREST):
            print("[!] Matching egg found!")
            threading.Thread(target=buzz_buzzer).start()

    if message.embeds:
        for embed in message.embeds:
            embedded_text = ""
            if embed.title:
                embedded_text += f"{embed.title} "
            if embed.description:
                embedded_text += f"{embed.description} "
            if embed.footer and embed.footer.text:
                embedded_text += f"{embed.footer.text} "
            if embed.fields:
                for field in embed.fields:
                    embedded_text += f"{field.name} {field.value} "

            cleaned_text = clean_discord_text(embedded_text)
            print(f"[DEBUG] Cleaned embed content: {cleaned_text}")

            if any(seed in cleaned_text for seed in SEEDS_OF_INTEREST):
                print("[!] Matching seed found in embed!")
                threading.Thread(target=buzz_buzzer).start()

            if any(seed in cleaned_text for seed in SPECIAL_SEEDS):
                await dm_users(cleaned_text)

            if any(weather in cleaned_text for weather in WEATHER_OF_INTEREST):
                print("[!] Matching weather found in embed!")
                threading.Thread(target=buzz_buzzer).start()

            if any(egg in cleaned_text for egg in EGGS_OF_INTEREST):
                print("[!] Matching egg found in embed!")
                threading.Thread(target=buzz_buzzer).start()

# === START BOT ===
client.run(DISCORD_BOT_TOKEN)
