import discord
from discord.ext import commands
import json
import random
import os

XP_FILE = "xp_data.json"

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

QUESTIONS = [
    ("What is the most common medical issue faced by beachgoers?", "B"),
    ("Which vitamin is primarily produced by sun exposure?", "C"),
    ("What is the best way to treat a jellyfish sting?", "B"),
    ("What SPF is recommended for effective sun protection?", "B"),
    ("Which of these can prevent swimmer’s ear?", "A"),
    ("What is a symptom of heat exhaustion?", "B"),
    ("How often should you reapply sunscreen at the beach?", "B"),
    ("What is the main cause of dehydration at the beach?", "B"),
    ("Which of these is NOT a sign of severe sunburn?", "D"),
    ("What should you do if someone is drowning?", "B"),
    ("What bacteria is commonly found in warm seawater that can infect wounds?", "B"),
    ("Which drink is best for rehydrating at the beach?", "C"),
    ("What is the medical term for 'sand in the eye'?", "B"),
    ("How can you avoid foot burns on hot sand?", "B"),
    ("What is the first aid for a severe cut from a seashell?", "B"),
    ("Which of these increases the risk of skin cancer?", "A"),
    ("What is a common allergic reaction to sunscreen?", "A"),
    ("What should you do if you step on a stingray?", "B"),
    ("Which mineral is lost through excessive sweating?", "B"),
    ("What is the best way to prevent heatstroke?", "B"),
    ("What is the most dangerous type of skin cancer linked to sun exposure?", "C"),
    ("Why is it risky to drink alcohol while at the beach?", "A"),
    ("What should you do if someone is having a heatstroke?", "B"),
    ("Which of these is NOT a symptom of saltwater aspiration (near-drowning)?", "D"),
    ("What parasite can you get from walking barefoot on contaminated sand?", "A"),
    ("How does UV radiation primarily damage the skin?", "A"),
    ("What is 'surfer’s ear'?", "B"),
    ("Why is it bad to urinate on a jellyfish sting?", "A"),
    ("What is the best way to remove a tick after a beach hike?", "D"),
    ("Which of these can cause 'sea lice' rash?", "A"),
    ("What is the medical term for 'sun poisoning'?", "D"),
    ("Why should you avoid shaving before swimming in the ocean?", "B"),
    ("What is the first sign of hypothermia in water?", "A"),
    ("What bacteria causes 'swimmer’s itch'?", "B"),
    ("How can you tell if a beach has dangerous rip currents?", "B"),
    ("What is the safest time to avoid UV radiation at the beach?", "A"),  # Accepts A or C
    ("What is the main danger of swallowing too much seawater?", "A"),
    ("Which of these can help soothe a severe sunburn?", "A"),
    ("What is 'coral poisoning'?", "A"),
    ("Why is it dangerous to dig deep holes in the sand?", "A"),
    ("What is the best way to prevent 'swimmer’s ear'?", "A"),
    ("What is a common symptom of sea urchin stings?", "B"),
    ("What should you do if you see a bluebottle (Portuguese man o’ war)?", "B"),
    ("Which of these is NOT a treatment for a stingray injury?", "D"),
    ("What is 'aquagenic urticaria'?", "C"),
    ("Why should you avoid ocean swimming with open wounds?", "B"),
    ("What is the best way to prevent sand fleas bites?", "D"),
    ("What is 'photokeratitis'?", "A"),
    ("How can you avoid 'beach diarrhea'?", "D"),
    ("What is the most important first-aid tool to bring to the beach?", "C")
]

def load_xp():
    if os.path.exists(XP_FILE):
        with open(XP_FILE, "r") as f:
            return json.load(f)
    return {}

def save_xp(data):
    with open(XP_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_rank(xp):
    for amount, role in reversed(XP_ROLES):
        if xp >= amount:
            return role
    return XP_ROLES[0][1]

class Trivia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.xp_data = load_xp()

    @commands.command()
    async def beachtrivia(self, ctx):
        await ctx.send(embed=discord.Embed(
            title="🌴 Welcome to BeachTrivia! ☀️",
            description="Get ready for a sizzling summer quiz! Each correct answer earns you **25 XP**.\nLet’s dive in! 🌊",
            color=0x00BFFF
        ))

        question, answer = random.choice(QUESTIONS)
        await ctx.send(f"**❓ Question:** {question}")

        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author

        try:
            response = await self.bot.wait_for("message", check=check, timeout=30.0)
            if response.content.lower().strip() == answer.lower():
                user_id = str(ctx.author.id)
                self.xp_data[user_id] = self.xp_data.get(user_id, 0) + 25
                save_xp(self.xp_data)
                role = get_rank(self.xp_data[user_id])
                await ctx.send(f"✅ Correct! You earned 25 XP! Total: {self.xp_data[user_id]} XP\n🏅 Rank: **{role}**")
            else:
                await ctx.send("❌ Oops! That wasn’t the right answer.")
        except Exception:
            await ctx.send("⌛ Time’s up! Better luck next time!")

    @commands.command()
    async def leaderboard(self, ctx):
        sorted_xp = sorted(self.xp_data.items(), key=lambda x: x[1], reverse=True)
        embed = discord.Embed(title="🏖️ BeachTrivia Leaderboard", color=0xFFA500)
        for i, (user_id, xp) in enumerate(sorted_xp[:10], 1):
            user = await self.bot.fetch_user(int(user_id))
            embed.add_field(name=f"#{i} - {user.name}", value=f"XP: {xp} • {get_rank(xp)}", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Trivia(bot))
