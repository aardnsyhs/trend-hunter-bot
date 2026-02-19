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
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(URL_TARGET, headers=headers)
        if response.status_code != 200:
            return "⚠️ Gagal akses data Spotify Indonesia."
            
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find('table').find_all('tr')
        
        date_now = datetime.now().strftime("%d-%m-%Y")
        msg = f"🇮🇩 <b>TOP HITS INDONESIA ({date_now})</b> 🇮🇩\n"
        msg += "Ide Konten Gitar Viral Hari Ini:\n\n"
        
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
            
        msg += "\n💡 <i>Tips: Cek chord-nya di Ultimate-Guitar dan sikat!</i>"
        return msg

    except Exception as e:
        return f"Error scraping: {str(e)}"

def job():
    pesan = get_indo_trends()
    try:
        bot.send_message(CHAT_ID, pesan, parse_mode='HTML')
        logging.info("Laporan sukses terkirim!")
    except Exception as e:
        logging.error(f"Gagal kirim Telegram: {e}")

schedule.every().day.at("01:00").do(job)

logging.info("Bot Trend Hunter V2.1 (HTML Fix) Berjalan!")

first_run_msg = get_indo_trends()
bot.send_message(CHAT_ID, f"🤖 <b>Bot Upgrade V2.1 Berhasil!</b>\nIni tes data terbaru:\n\n{first_run_msg}", parse_mode='HTML')

while True:
    schedule.run_pending()
    time.sleep(60)