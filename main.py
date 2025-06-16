import discord
from discord.ext import commands
import os
from trivia import Trivia 
from leaderboard import Leaderboard
from dotenv import load_dotenv
from flask import Flask

# Load environment variables from .env
load_dotenv()

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

# Add trivia and leaderboard
bot.add_cog(Trivia(bot))
bot.add_cog(Leaderboard(bot))

# Optional Flask web server (Render often checks this)
app = Flask(__name__)

@app.route("/")
def home():
    return "🌴 Beachtrivia Bot is running!"

if __name__ == "__main__":
    # Run Discord bot
    import threading

    def run_bot():
        bot.run(os.getenv("DISCORD_TOKEN"))

    def run_web():
        port = int(os.environ.get("PORT", 8080))  # default for Render
        app.run(host="0.0.0.0", port=port)

    threading.Thread(target=run_bot).start()
    run_web()
