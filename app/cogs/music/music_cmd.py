from . import common
from system.bot import client
from random import shuffle
import os
import discord

import yt_dlp
import nacl

@client.listen()
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    if message.content.startswith("mb play "):
        query = message.content.replace("mb play ", "")
        voice_channel = message.author.voice.channel
        if voice_channel is None:
            await message.channel.send("음성 채널에 연결하여 주십시오.")
        else:
            msg = await message.channel.send("다운로드 중입니다. 잠시만 기다려 주십시오.")
            song = common.search_yt(query)
            if type(song) == type(True):
                await msg.edit(content="해당 키워드로 YouTube 영상을 쿼리할 수 없습니다.")
            else:
                common.music_queue.append([song, voice_channel])
                title = song['title']
                await msg.edit(content=f"{title}을(를) 대기열에 추가하였습니다.")
                if not common.is_playing:
                    await common.play_music(message)
    elif message.content == "mb addfile":
        voice_channel = message.author.voice.channel
        if len(message.attachments) == 0:
            await message.channel.send("파일을 첨부하여 주십시오.")
        elif voice_channel is None:
            await message.channel.send("음성 채널에 연결하여 주십시오.")
        else:
            msg = await message.channel.send("첨부파일 다운로드 중입니다. 잠시만 기다려 주십시오.")
            dlf = await common.download_file(message)
            common.music_queue.append([dlf, voice_channel])
            if not common.is_playing:
                await common.play_music(message)
            title = message.attachments[0].filename
            await msg.edit(content=f"{title}을(를) 대기열에 추가하였습니다.")
    elif message.content == "mb pause":
        if common.is_playing:
            common.is_playing = False
            common.is_paused = True
            common.vc.pause()
            await message.channel.send("일시 정지됨\nmb pause를 다시 입력하여 계속 재생합니다.")
        elif common.is_paused:
            common.is_paused = False
            common.is_playing = True
            common.vc.resume()
            await message.channel.send("일시 정지 해제됨")
    elif message.content == "mb skip":
        if common.vc != None and common.vc:
            common.vc.stop()
            await common.play_music(message)
            await message.channel.send(f"{common.nptitle} 스킵됨")
        else:
            await message.channel.send("뮤직봇이 비활성 상태입니다.")
    elif message.content == "mb queue":
        retval = f"대기열 : {len(common.music_queue)}개\n"
        for i in range(0, len(common.music_queue)):
            # display a max of 5 songs in the current queue
            if i > 4: break
            retval += common.music_queue[i][0]['title'] + "\n"
        if retval != "":
            await message.channel.send(retval)
        else:
            await message.channel.send("대기열이 비어 있습니다.")
    elif message.content == "mb purge":
        if common.vc is not None and common.is_playing:
            common.vc.stop()
        try:
            for i in common.music_queue:
                os.remove(i[0]['source'])
            os.remove(common.pru)
        except:
            pass
        common.music_queue = []
        await message.channel.send("대기열 전체 삭제됨")
    elif message.content == "mb shuffle":
        shuffle(common.music_queue)
        await message.channel.send("셔플 완료")
    elif message.content == "mb np":
        if common.nptitle is "":
            await message.channel.send("재생 중인 미디어가 없습니다.")
        else:
            await message.channel.send(common.nptitle)
    elif message.content == "mb exit":
        common.is_playing = False
        common.is_paused = False
        await common.vc.disconnect()
        await message.channel.send("뮤직봇 종료됨")
    elif message.content == "mb info":
        ffv = os.popen("ffmpeg -version").read()
        ffv = ffv.split("Copyright")[0][15:-1]
        t = f"**yt-dlp** : {yt_dlp.update.__version__}\n"
        t += f"**NaCl** : {nacl.__version__}\n"
        t += f"**ffmpeg** : {ffv}"
        await message.channel.send(t)
