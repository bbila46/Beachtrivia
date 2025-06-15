import discord
from discord.ext import commands
from discord import app_commands
import json
import datetime
import os

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# Load questions
with open("questions.json", "r") as f:
    questions = json.load(f)

# Load or initialize user XP data
if os.path.exists("user_data.json"):
    with open("user_data.json", "r") as f:
        user_data = json.load(f)
else:
    user_data = {}

XP_PER_CORRECT = 25

roles = [
    (750, "Legendary Surf Medic 🌟🏄"),
    (675, "Chief of Coastal Medicine 🩺"),
    (600, "Beach ER Doctor 🏥"),
    (525, "Coral Cut Caretaker 🪸"),
    (450, "Ocean Lifesaver 🚤"),
    (375, "Seashell Scrapes Medic 🐚"),
    (300, "Tidal Wound Healer 🌊"),
    (225, "Jellyfish Sting Soother 🪼"),
    (150, "Sunburn Relief Specialist ☀️"),
    (75, "Sandy Bandage Applier 🩹"),
    (0, "Beach First-Aid Trainee 🏖️")
]

def get_today_index():
    base = datetime.date(2025, 1, 1)
    today = datetime.date.today()
    return (today - base).days % len(questions)

def save_user_data():
    with open("user_data.json", "w") as f:
        json.dump(user_data, f, indent=4)

async def assign_role(member: discord.Member, xp: int):
    guild = member.guild
    for threshold, role_name in roles:
        if xp >= threshold:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                # Remove other XP roles
                for _, rname in roles:
                    old_role = discord.utils.get(guild.roles, name=rname)
                    if old_role in member.roles:
                        await member.remove_roles(old_role)
                await member.add_roles(role)
            break

@tree.command(name="beachtrivia", description="Answer today's ocean emergency trivia!")
async def beachtrivia(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    today_str = str(datetime.date.today())

    if uid in user_data and user_data[uid].get("last_answered") == today_str:
        await interaction.response.send_message("🌞 You've already answered today's question!", ephemeral=True)
        return

    q = questions[get_today_index()]

    embed = discord.Embed(
        title="🌊 BeachTrivia Daily Question",
        description=q["question"],
        color=0x1abc9c
    )

    for i, choice in enumerate(q["choices"]):
        embed.add_field(name=f"{chr(65+i)}.", value=choice, inline=False)

    class QuizView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=60)
            for i, c in enumerate(q["choices"]):
                self.add_item(AnswerButton(i))

    class AnswerButton(discord.ui.Button):
        def __init__(self, idx):
            super().__init__(label=q["choices"][idx], style=discord.ButtonStyle.primary)
            self.idx = idx

        async def callback(self, interaction_btn: discord.Interaction):
            user_data.setdefault(uid, {"xp": 0})
            user_data[uid]["last_answered"] = today_str
            is_correct = self.idx == q["correct_index"]

            if is_correct:
                user_data[uid]["xp"] += XP_PER_CORRECT
                msg = f"✅ Correct! You earned {XP_PER_CORRECT} XP. Total: {user_data[uid]['xp']} XP."
            else:
                correct = q["choices"][q["correct_index"]]
                msg = f"❌ Incorrect. The correct answer was **{correct}**."

            save_user_data()
            await assign_role(interaction.user, user_data[uid]["xp"])
            for child in self.view.children:
                child.disabled = True
            await interaction_btn.message.edit(view=self.view)
            await interaction_btn.response.send_message(msg, ephemeral=True)

    await interaction.response.send_message(embed=embed, view=QuizView(), ephemeral=True)

@tree.command(name="leaderboard", description="See the top BeachTrivia scorers!")
async def leaderboard(interaction: discord.Interaction):
    top = sorted(user_data.items(), key=lambda x: x[1].get("xp", 0), reverse=True)[:10]
    embed = discord.Embed(title="🏆 BeachTrivia Leaderboard", color=0xf1c40f)

    for idx, (uid, data) in enumerate(top, 1):
        user = await bot.fetch_user(int(uid))
        xp = data.get("xp", 0)
        embed.add_field(name=f"{idx}. {user.name}", value=f"{xp} XP", inline=False)

    await interaction.response.send_message(embed=embed)

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {bot.user}!")

bot.run("YOUR_BOT_TOKEN")
