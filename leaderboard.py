import discord
from discord.ext import commands
import json
import os

DATA_FILE = "xp_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def leaderboard(self, ctx):
        xp_data = load_data()
        if not xp_data:
            await ctx.send("📊 No one has earned XP yet!")
            return

        sorted_data = sorted(xp_data.items(), key=lambda x: x[1], reverse=True)[:10]
        desc = ""
        for i, (user_id, xp) in enumerate(sorted_data, 1):
            member = ctx.guild.get_member(int(user_id))
            name = member.name if member else f"User ID {user_id}"
            desc += f"**{i}.** {name} — {xp} XP\n"

        embed = discord.Embed(title="🏆 BeachTrivia Leaderboard", description=desc, color=discord.Color.gold())
        await ctx.send(embed=embed)
