import requests
from bs4 import BeautifulSoup
import telebot
import schedule
import time
import os
import logging
import random
import tweepy
from datetime import datetime

TELEGRAM_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')

TIPTAP_LINK = "https://tiptap.gg/aardnsyhs"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
logging.basicConfig(level=logging.INFO)

def post_to_twitter(tweet_text):
    try:
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_SECRET
        )
        
        response = client.create_tweet(text=tweet_text)
        return f"✅ Sukses Tweet ID: {response.data['id']}"
    except Exception as e:
        return f"❌ Gagal Tweet: {e}"

def get_viral_chord():
    logging.info("Mencari lagu viral...")
    url = "https://kworb.net/spotify/country/id_daily.html"
    
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find('table').find_all('tr')
        
        top_songs = []
        count = 0
        for row in rows[1:]:
            if count >= 10: break
            cols = row.find_all('td')
            if not cols: continue
            
            song_info = cols[2].text.strip()
            if " - " in song_info:
                artist, title = song_info.split(" - ", 1)
            else:
                artist = "Unknown"
                title = song_info
                
            top_songs.append({"title": title, "artist": artist})
            count += 1
            
        chosen_song = random.choice(top_songs)
        
        query_google = f"Chord {chosen_song['title']} {chosen_song['artist']} ChordTela"
        
        search_url = f"https://www.google.com/search?q={query_google.replace(' ', '+')}"
        
        tweet = f"🎸 Chord Viral Hari Ini: {chosen_song['title']}\n"
        tweet += f"🎤 Artis: {chosen_song['artist']}\n\n"
        tweet += f"Cek kunci gitarnya (Versi Gampang) 👇\n"
        tweet += f"{search_url}\n\n"
        tweet += f"☕ Dukung admin beli senar: {TIPTAP_LINK}\n"
        tweet += "#ChordGitar #GitarisIndonesia #InfoMusik"
        
        return tweet

    except Exception as e:
        return None

def job():
    konten_tweet = get_viral_chord()
    
    if konten_tweet:
        status_twitter = post_to_twitter(konten_tweet)
        
        laporan = f"🤖 **Laporan Bot Chord**\n\n{status_twitter}\n\nIsi Tweet:\n{konten_tweet}"
        bot.send_message(CHAT_ID, laporan)
    else:
        bot.send_message(CHAT_ID, "⚠️ Gagal mengambil data lagu viral.")

schedule.every().day.at("10:00").do(job)

logging.info("Bot Juragan Chord (Fix Google Link) Berjalan!")
bot.send_message(CHAT_ID, "🤖 Bot Juragan Chord (Versi Google) Siap! Nunggu jam 5 sore.")

while True:
    schedule.run_pending()
    time.sleep(60)