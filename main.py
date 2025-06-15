import discord
from discord.ext import commands, tasks
import json
import datetime
import random
import requests
from flask import Flask
import threading

# === DISCORD BOT SETUP ===
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# === FLASK APP FOR NETWORK PORT ===
app = Flask(__name__)

@app.route("/")
def home():
    return "🌊 BeachTrivia Bot is running!", 200

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# Start Flask in a background thread
threading.Thread(target=run_flask).start()

# === CONFIG ===
WEBHOOK_URL = "https://discord.com/api/webhooks/..."  # Replace with your webhook
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

# === USER XP DATABASE ===
user_data = {}

# === LOAD QUESTIONS ===
with open("questions.json", "r") as f:
    questions = json.load(f)

# === STORE DAILY QUESTION ===
current_question_index = datetime.datetime.utcnow().timetuple().tm_yday % len(questions)

# === FUNCTIONS ===

def get_today_question():
    index = datetime.datetime.utcnow().timetuple().tm_yday % len(questions)
    return questions[index]

def send_webhook_message(webhook_url, title, description, color=3447003):
    payload = {
        "username": "🌊 BeachTrivia Bot",
        "embeds": [
            {
                "title": title,
                "description": description,
                "color": color
            }
        ]
    }
    requests.post(webhook_url, json=payload)

def get_user_role(xp):
    role = XP_ROLES[0][1]
    for level, r in XP_ROLES:
        if xp >= level:
            role = r
    return role

# === COMMANDS ===

@bot.event
async def on_ready():
    print(f"✅ Bot is ready as {bot.user}")
    send_webhook_message(WEBHOOK_URL, "BeachTrivia Bot", "Bot is now online and monitoring waves 🏝️")

@bot.command(name="beachtrivia")
async def beachtrivia(ctx):
    user_id = str(ctx.author.id)
    question = get_today_question()

    embed = discord.Embed(
        title="🌊 BeachTrivia: Daily Quiz",
        description=f"**{question['question']}**\n" +
                    "\n".join([f"{chr(65+i)}) {ans}" for i, ans in enumerate(question['choices'])]),
        color=discord.Color.blurple()
    )
    embed.set_footer(text="Answer using A, B, C, or D.")
    await ctx.send(embed=embed)

@bot.command(name="answer")
async def answer(ctx, choice: str):
    user_id = str(ctx.author.id)
    question = get_today_question()
    correct_letter = chr(65 + question["correct_index"]).upper()

    if user_id not in user_data:
        user_data[user_id] = {"xp": 0, "answered_day": -1}

    today = datetime.datetime.utcnow().timetuple().tm_yday

    if user_data[user_id]["answered_day"] == today:
        await ctx.send("❌ You've already answered today's question!")
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
        title="🧠 Trivia Result",
        description=f"{result}\n**XP:** {xp}\n**Role:** {role}",
        color=discord.Color.green() if choice.upper() == correct_letter else discord.Color.red()
    )
    await ctx.send(embed=embed)

@bot.command(name="leaderboard")
async def leaderboard(ctx):
    if not user_data:
        await ctx.send("Leaderboard is empty 🌊")
        return

    sorted_users = sorted(user_data.items(), key=lambda x: x[1]["xp"], reverse=True)[:10]
    desc = ""

    for i, (uid, data) in enumerate(sorted_users, 1):
        user = await bot.fetch_user(int(uid))
        role = get_user_role(data["xp"])
        desc += f"{i}. **{user.name}** — {data['xp']} XP • {role}\n"

    embed = discord.Embed(
        title="🏆 BeachTrivia Leaderboard",
        description=desc,
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed)

# === RUN BOT ===
bot.run("YOUR_DISCORD_BOT_TOKEN")
