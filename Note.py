import telebot
import json
import os
from telebot import types

bot = telebot.TeleBot("YOUR_BOT_TOKEN")

admin_id = 1234567890  # ← Yahan apna Telegram user ID daalna

# Load users.json or create if not exist
if os.path.exists("users.json"):
    with open("users.json", "r") as f:
        users = json.load(f)
else:
    users = {}

# Save function
def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f, indent=2)

# /start command
@bot.message_handler(commands=["start"])
def start(message):
    user_id = str(message.from_user.id)
    if user_id not in users:
        users[user_id] = {
            "username": message.from_user.username or "NoUsername",
            "points": 5,
            "referrals": [],
            "total_notes": 0
        }
        save_users()
        bot.reply_to(message, "Welcome! 5 free points diye gaye hain.")
    else:
        bot.reply_to(message, "Tum already registered ho.")

# /notes command
@bot.message_handler(commands=["notes"])
def notes(message):
    user_id = str(message.from_user.id)
    if user_id not in users:
        bot.reply_to(message, "Pehle /start bhejo register hone ke liye.")
        return

    if users[user_id]["points"] > 0:
        users[user_id]["points"] -= 1
        users[user_id]["total_notes"] += 1
        save_users()
        bot.reply_to(message, "Yeh raha tumhara note:\n\n[Note content here]")
    else:
        bot.reply_to(message, "Tumhare points khatam ho gaye hain. Use /buy ya /refer.")

# /buy command
@bot.message_handler(commands=["buy"])
def buy(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username or "NoUsername"

    # Send UPI instructions to user
    bot.reply_to(message, "₹20 = 20 Points\n\nPay karo:\n\n**UPI ID: raaz@upi**\n\nPayment ke baad screenshot bhejo.")

    # Notify admin
    bot.send_message(admin_id, f"User `{username}` (ID: `{user_id}`) ne points buy kiye hain. Screenshot ka wait hai.", parse_mode="Markdown")

# Screenshot handler
@bot.message_handler(content_types=["photo"])
def handle_screenshot(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username or "NoUsername"

    # Forward photo to admin
    bot.forward_message(admin_id, message.chat.id, message.message_id)
    bot.send_message(admin_id, f"Screenshot from `{username}` (ID: `{user_id}`)", parse_mode="Markdown")

    bot.reply_to(message, "Screenshot bhej diya gaya hai. Verification ke baad points milenge (1-2 min).")

# /addpoints (admin-only)
@bot.message_handler(commands=["addpoints"])
def addpoints(message):
    if str(message.from_user.id) != str(admin_id):
        return

    try:
        parts = message.text.split()
        target_id = str(parts[1])
        points = int(parts[2])

        if target_id in users:
            users[target_id]["points"] += points
            save_users()
            bot.reply_to(message, f"Points added successfully to {target_id}.")
            bot.send_message(target_id, f"Congrats! {points} points added to your account.")
        else:
            bot.reply_to(message, "User not found.")
    except:
        bot.reply_to(message, "Usage: /addpoints user_id points")

bot.polling()