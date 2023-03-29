from yt_dlp import YoutubeDL
from pathlib import Path
from system.bot import client
import app.conf.config as cf
import discord
import os

is_playing = False
is_paused = False
music_queue = []
# FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
FFMPEG_OPTIONS = {'options': '-vn'}

vc = None
nptitle = ""
pru = ""

def search_yt(item):
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    with YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            info = ydl.extract_info("ytsearch:%s" % item, download=True)['entries'][0]
        except Exception:
            return False
    return {'source': info['requested_downloads'][0]['filepath'], 'title': info['title']}

async def download_file(msg: discord.Message):
    await msg.attachments[0].save(Path(msg.attachments[0].filename))
    return {'source': msg.attachments[0].filename, 'title': msg.attachments[0].filename}

def play_next(prev_url):
    global is_playing, is_paused, music_queue, vc, nptitle, pru, FFMPEG_OPTIONS
    os.remove(prev_url)
    if len(music_queue) > 0:
        is_playing = True
        nptitle = music_queue[0][0]['title']
        m_url = music_queue[0][0]['source']
        pru = m_url
        client.loop.create_task(client.change_presence(
            activity=discord.Activity(name=music_queue[0][0]['title'], type=discord.ActivityType.listening)))
        music_queue.pop(0)
        if vc is not None:
            vc.play(discord.FFmpegPCMAudio(m_url, **FFMPEG_OPTIONS), after=lambda e: play_next(m_url))
    else:
        client.loop.create_task(client.change_presence(
            activity=discord.Activity(name=cf.precense_text, type=discord.ActivityType.playing)))
        nptitle = ""
        is_playing = False

async def play_music(msg):
    global is_playing, is_paused, music_queue, vc, nptitle, pru, FFMPEG_OPTIONS
    if len(music_queue) > 0:
        is_playing = True
        nptitle = music_queue[0][0]['title']
        m_url = music_queue[0][0]['source']
        if vc is None or not vc.is_connected():
            vc = await music_queue[0][1].connect()
            if vc is None:
                await msg.reply("음성 채널에 연결할 수 없습니다.")
                return
        else:
            await vc.move_to(music_queue[0][1])
        prev_url = m_url
        pru = prev_url
        await client.change_presence(
            activity=discord.Activity(name=music_queue[0][0]['title'], type=discord.ActivityType.listening))
        music_queue.pop(0)
        vc.play(discord.FFmpegPCMAudio(m_url, **FFMPEG_OPTIONS), after=lambda e: play_next(prev_url))
    else:
        await client.change_presence(
            activity=discord.Activity(name=cf.precense_text, type=discord.ActivityType.playing))
        nptitle = ""
        is_playing = False
