import discord
import system.log_manager as log
from discord.ext import commands

WORKDIR = "/home/ubuntu"

# 내 전용 좆집이므로 사용 가능한 인텐트 전체를 위임함
intents = discord.Intents.all()

client = commands.Bot(command_prefix='$', intents=intents)

@client.event
async def on_ready():
    log.info("Bot is on ready")
