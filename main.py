import requests
from bs4 import BeautifulSoup
import telebot
import schedule
import time
import os
import logging
from datetime import datetime

TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
URL_TARGET = "https://kworb.net/spotify/country/id_daily.html"

bot = telebot.TeleBot(TOKEN)
logging.basicConfig(level=logging.INFO)

def get_indo_trends():
    logging.info("Sedang memantau tangga lagu Indonesia...")
    try:
        response = requests.get(URL_TARGET, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200: return "⚠️ Gagal akses data."
            
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find('table').find_all('tr')
        
        date_now = datetime.now().strftime("%d-%m-%Y")
        msg = f"🇮🇩 <b>TOP HITS INDONESIA ({date_now})</b> 🇮🇩\n\n"
        
        count = 0
        for row in rows[1:]:
            if count >= 10: break
            cols = row.find_all('td')
            if not cols: continue
            song_info = cols[2].text.strip()
            
            if " - " in song_info:
                artist, title = song_info.split(" - ", 1)
                display_text = f"🎸 <b>{title}</b> - {artist}"
            else:
                display_text = f"🎵 {song_info}"
            
            count += 1
            msg += f"{count}. {display_text}\n"
            
        msg += "\n💡 <i>Data diambil otomatis dari Server Azure.</i>"
        return msg
    except Exception as e:
        return f"Error: {str(e)}"

def job():
    pesan = get_indo_trends()
    bot.send_message(CHAT_ID, pesan, parse_mode='HTML')
    logging.info("Laporan sukses terkirim ke Telegram!")

schedule.every().day.at("07:30").do(job)

logging.info("Bot Telegram Only Berjalan!")
bot.send_message(CHAT_ID, "✅ Bot kembali ke mode Telegram (Twitter dimatikan).")

while True:
    schedule.run_pending()
    time.sleep(60)