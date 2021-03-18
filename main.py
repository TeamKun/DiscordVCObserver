#!/usr/bin/env python
# -*- coding: utf-8 -*-

# discord.py

import configparser
import csv
import datetime
import os

import discord
from discord.ext import commands

# タイムゾーン (日付は朝9時に変更=UTC)
timezone_date = datetime.timezone(datetime.timedelta(hours=0))
timezone = datetime.timezone(datetime.timedelta(hours=9))

# 起動
print('起動しました')

# コンフィグ
config = configparser.ConfigParser()
config.read('config.ini', encoding='UTF-8')

ss_guild = int(config['SESSION']['GUILD'])

# 起動
print(f"設定を読み込みました: guild={ss_guild}")

# フォルダ
os.makedirs('./data', exist_ok=True)
os.makedirs('./data/log', exist_ok=True)
os.makedirs('./data/corrupted', exist_ok=True)

# 起動
print('フォルダを生成しました')

# セッション
session_path = f'./data/corrupted/{datetime.datetime.now(timezone_date).date()}.csv'

# 接続に必要なオブジェクトを生成
bot = commands.Bot(command_prefix='/')


# 起動時に動作する処理
@bot.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される

    guild = bot.get_guild(ss_guild)
    if guild is None:
        print('サーバーが見つかりません')
        return
    print('ログインしました')


# ログ
class Log:
    def __init__(self, path):
        self.path = path
        self.fd = None
        self.writer = None

    def __enter__(self):
        is_new = os.path.exists(self.path)
        self.fd = open(self.path, 'a', newline='', encoding='UTF-8')
        self.writer = csv.writer(self.fd)
        if not is_new: self.writer.writerow(['Type', 'Time', 'Discord ID', 'VC Name', 'Discord Name'])
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fd.close()

    def log(self, time, uid, fullname, vc_name, joined):
        self.writer.writerow(['join' if joined else 'leave', time, uid, vc_name, fullname])


# VCのメンバー移動時の処理
@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    # 移動していない
    if before.channel == after.channel:
        return

    # 現在時刻を取得
    now = datetime.datetime.now(timezone)

    # 参加
    if after.channel:
        vc_name = after.channel.name
        print("join", str(member), "to", vc_name)

        with Log(session_path) as log:
            log.log(now, member.id, str(member), vc_name, True)

    # 退出
    if before.channel:
        vc_name = before.channel.name
        print("leave", str(member), "from", vc_name)

        with Log(session_path) as log:
            log.log(now, member.id, str(member), vc_name, False)


# 初期化
print('初期化しました')

# Botの起動とDiscordサーバーへの接続
bot.run(os.environ["DISCORD_TOKEN"])
