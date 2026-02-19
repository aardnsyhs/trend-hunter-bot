import requests
from bs4 import BeautifulSoup
import telebot
import schedule
import time
import os
import logging
from datetime import datetime

# --- KONFIGURASI ---
TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Sumber Data: Spotify Daily Chart - Indonesia (Data Real-time)
URL_TARGET = "https://kworb.net/spotify/country/id_daily.html"

# Setup Bot & Logging
bot = telebot.TeleBot(TOKEN)
logging.basicConfig(level=logging.INFO)

def get_indo_trends():
    logging.info("Sedang memantau tangga lagu Indonesia...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(URL_TARGET, headers=headers)
        if response.status_code != 200:
            return "⚠️ Gagal akses data Spotify Indonesia."
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Kworb menggunakan tabel simpel, kita ambil tabel pertama
        table = soup.find('table')
        rows = table.find_all('tr')
        
        # Header Pesan
        date_now = datetime.now().strftime("%d-%m-%Y")
        msg = f"🇮🇩 **TOP HITS INDONESIA ({date_now})** 🇮🇩\n"
        msg += "Ide Konten Gitar Viral Hari Ini:\n\n"
        
        count = 0
        # Kita skip row 0 karena itu header tabel
        for row in rows[1:]:
            if count >= 10: # Ambil Top 10 saja
                break
                
            cols = row.find_all('td')
            if not cols:
                continue
                
            # Struktur kolom Kworb: [Pos] [P+] [Artist and Title] ...
            # Kolom ke-2 (index 2) biasanya Artist and Title
            song_info = cols[2].text.strip()
            
            # Cek apakah lagu ini sedang NAIK (Hijau) di chart?
            # Biasanya ada indikator warna di HTML, tapi kita ambil simpelnya aja
            
            # Format: "Artist - Title"
            # Kita bersihkan sedikit stringnya
            if " - " in song_info:
                artist, title = song_info.split(" - ", 1)
                display_text = f"🎸 {title} - {artist}"
            else:
                display_text = f"🎵 {song_info}"
            
            count += 1
            msg += f"{count}. {display_text}\n"
            
        msg += "\n💡 *Tips:* Cek chord-nya di Ultimate-Guitar/ChordTela dan sikat bikin konten!"
        return msg

    except Exception as e:
        return f"Error scraping: {str(e)}"

def job():
    pesan = get_indo_trends()
    try:
        bot.send_message(CHAT_ID, pesan, parse_mode='Markdown')
        logging.info("Laporan sukses terkirim!")
    except Exception as e:
        logging.error(f"Gagal kirim Telegram: {e}")

# --- JADWAL KERJA ---
# Kirim setiap jam 08:00 Pagi WIB (Server Azure biasanya UTC, jadi set jam 01:00 UTC)
schedule.every().day.at("01:00").do(job)

logging.info("Bot Trend Hunter V2 (Indo Edition) Berjalan!")

# Test kirim pesan saat bot baru nyala (Biar tau codingan baru jalan)
first_run_msg = get_indo_trends()
bot.send_message(CHAT_ID, f"🤖 **Bot Upgrade V2 Berhasil!**\nIni tes data terbaru:\n\n{first_run_msg}")

while True:
    schedule.run_pending()
    time.sleep(60)