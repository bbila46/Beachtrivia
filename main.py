import discord
from discord.ext import commands
import json
import datetime
import requests
import os
from flask import Flask
import threading

# === DISCORD BOT SETUP ===
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# === FLASK APP FOR NETWORK KEEP-ALIVE ===
app = Flask(__name__)

@app.route("/")
def home():
    return "🌊 BeachTrivia Bot is running!", 200

def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask).start()

# === ENV VARIABLES (insert via Render Dashboard or .env locally) ===
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# === XP ROLES ===
XP_ROLES = [
    (0, "🏖️ Beach First-Aid Trainee"),
    (75, "🩹 Sandy Bandage Applier"),
    (150, "☀️ Sunburn Relief Specialist"),
    (225, "🪼 Jellyfish Sting Soother"),
    (300, "🌊 Tidal Wound Healer"),
    (375, "🐚 Seashell Scrapes Medic"),
    (450, "🚤 Ocean Lifesaver"),
    (525, "🪸 Coral Cut Caretaker"),
    (600, "🏥 Beach ER Doctor"),
    (675, "🩺 Chief of Coastal Medicine"),
    (750, "🌟🏄 Legendary Surf Medic")
]

user_data = {}

# === LOAD QUESTIONS ===
with open("questions.json", "r") as f:
    questions = json.load(f)

def get_today_question():
    index = datetime.datetime.utcnow().timetuple().tm_yday % len(questions)
    return questions[index]

def send_webhook_message(title, description, color=3447003):
    if not WEBHOOK_URL:
        return
    payload = {
        "username": "🌊 BeachTrivia Bot",
        "embeds": [{
            "title": title,
            "description": description,
            "color": color
        }]
    }
    try:
        requests.post(WEBHOOK_URL, json=payload)
    except:
        pass

def get_user_role(xp):
    role = XP_ROLES[0][1]
    for level, r in XP_ROLES:
        if xp >= level:
            role = r
    return role

# === BOT EVENTS ===

@bot.event
async def on_ready():
    print(f"✅ Bot is ready as {bot.user}")
    send_webhook_message("BeachTrivia Bot", "Bot is online and ready 🏝️")

# === BOT COMMANDS ===

@bot.command(name="beachtrivia")
async def beachtrivia(ctx):
    question = get_today_question()
    embed = discord.Embed(
        title="🌊 BeachTrivia: Daily Quiz",
        description=f"**{question['question']}**\n" +
                    "\n".join

Here's a **clean, final version** of your `BeachTrivia` Discord bot in `main.py`, completely **without `audioop`**, **without webhooks**, and suitable for deployment on **GitHub** or **Render**.

---

## ✅ `main.py`

```python
import discord
from discord.ext import commands
import json
import datetime
import threading
from flask import Flask

# === DISCORD BOT SETUP ===
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# === FLASK KEEP-ALIVE FOR RENDER ===
app = Flask(__name__)

@app.route('/')
def home():
    return "🌴 BeachTrivia Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run_flask).start()

# === XP ROLES ===
XP_ROLES = [
    (0, "🏖️ Beach First-Aid Trainee"),
    (75, "🩹 Sandy Bandage Applier"),
    (150, "☀️ Sunburn Relief Specialist"),
    (225, "🪼 Jellyfish Sting Soother"),
    (300, "🌊 Tidal Wound Healer"),
    (375, "🐚 Seashell Scrapes Medic"),
    (450, "🚤 Ocean Lifesaver"),
    (525, "🪸 Coral Cut Caretaker"),
    (600, "🏥 Beach ER Doctor"),
    (675, "🩺 Chief of Coastal Medicine"),
    (750, "🌟🏄 Legendary Surf Medic")
]

# === LOAD USER DATA & QUESTIONS ===
user_data = {}
with open("questions.json", "r") as f:
    questions = json.load(f)

def get_today_question():
    index = datetime.datetime.utcnow().timetuple().tm_yday % len(questions)
    return questions[index]

def get_user_role(xp):
    role = XP_ROLES[0][1]
    for level, r in XP_ROLES:
        if xp >= level:
            role = r
    return role

# === BOT EVENTS ===

@bot.event
async def on_ready():
    print(f"✅ Bot is ready: {bot.user}")

@bot.command()
async def beachtrivia(ctx):
    question = get_today_question()
    embed = discord.Embed(
        title="🌊 BeachTrivia: Daily Question",
        description=f"**{question['question']}**\n" +
                    "\n".join([f"{chr(65+i)}) {ans}" for i, ans in enumerate(question['choices'])]),
        color=discord.Color.blurple()
    )
    embed.set_footer(text="Answer using /answer A, B, C or D.")
    await ctx.send(embed=embed)

@bot.command()
async def answer(ctx, choice: str):
    user_id = str(ctx.author.id)
    question = get_today_question()
    correct_letter = chr(65 + question["correct_index"]).upper()
    today = datetime.datetime.utcnow().timetuple().tm_yday

    if user_id not in user_data:
        user_data[user_id] = {"xp": 0, "answered_day": -1}

    if user_data[user_id]["answered_day"] == today:
        await ctx.send("❌ You’ve already answered today’s question!")
        return

    if choice.upper() == correct_letter:
        user_data[user_id]["xp"] += 25
        result = "✅ Correct!"
    else:
        result = f"❌ Incorrect. The correct answer was **{correct_letter}**."

    user_data[user_id]["answered_day"] = today
    xp = user_data[user_id]["xp"]
    role = get_user_role(xp)

    embed = discord.Embed(
        title="📋 Your Result",
        description=f"{result}\n**XP:** {xp}\n**Role:** {role}",
        color=discord.Color.green() if choice.upper() == correct_letter else discord.Color.red()
    )
    await ctx.send(embed=embed)

@bot.command()
async def leaderboard(ctx):
    if not user_data:
        await ctx.send("🏖️ Leaderboard is empty.")
        return

    sorted_users = sorted(user_data.items(), key=lambda x: x[1]["xp"], reverse=True)[:10]
    desc = ""

    for i, (uid, data) in enumerate(sorted_users, 1):
        try:
            user = await bot.fetch_user(int(uid))
            name = user.name
        except:
            name = f"User {uid}"
        role = get_user_role(data["xp"])
        desc += f"{i}. **{name}** — {data['xp']} XP • {role}\n"

    embed = discord.Embed(
        title="🏆 BeachTrivia Leaderboard",
        description=desc,
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed)

# === START BOT ===
bot.run("YOUR_DISCORD_BOT_TOKEN")
