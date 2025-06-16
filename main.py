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

# === FLASK KEEP-ALIVE FOR RENDER OR SIMILAR ===
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

bot.run("YOUR_DISCORD_BOT_TOKEN")
