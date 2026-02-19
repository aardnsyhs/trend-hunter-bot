import requests
from bs4 import BeautifulSoup
import telebot
import schedule
import time
import os
import logging

# --- KONFIGURASI ---
# Kita ambil token rahasia dari Environment Variable (Settingan Docker nanti)
TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
URL_TARGET = "https://www.ultimate-guitar.com/explore?order=hitstotal_desc&type=Chords"

# Setup Bot & Logging
bot = telebot.TeleBot(TOKEN)
logging.basicConfig(level=logging.INFO)

def get_trending_tabs():
    logging.info("Sedang mencari lagu trending...")
    
    # Header palsu biar dikira browser beneran (bukan bot)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(URL_TARGET, headers=headers)
        if response.status_code != 200:
            return "Gagal akses website Ultimate-Guitar :("
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Mencari data lagu (Disclaimer: Class ini bisa berubah sewaktu-waktu kalau web update)
        # Kita coba ambil teks kasar dulu karena UG pakai banyak JavaScript
        # Untuk versi simpel, kita scraping meta description atau title halaman yang sering berisi top songs
        # Atau opsi lain: Scraping Billboard charts yang lebih statis HTML-nya.
        
        # OPSI ALTERNATIF LEBIH STABIL: Billboard Hot 100
        url_billboard = "https://www.billboard.com/charts/hot-100/"
        resp_bb = requests.get(url_billboard, headers=headers)
        soup_bb = BeautifulSoup(resp_bb.text, 'html.parser')
        
        songs = soup_bb.select('li.o-chart-results-list__item h3.c-title')
        artists = soup_bb.select('li.o-chart-results-list__item span.c-label')
        
        msg = "🎸 **IDE KONTEN TIKTOK HARI INI** 🎸\n\n"
        msg += "Top 5 Lagu Billboard (Cek Chord-nya!):\n"
        
        for i in range(5): # Ambil 5 teratas
            try:
                title = songs[i].text.strip()
                # Artist selector di Billboard agak tricky, kita ambil title dulu yang utama
                msg += f"{i+1}. {title}\n"
            except:
                continue
                
        msg += "\nGas rekam bang! 📹"
        return msg

    except Exception as e:
        return f"Error scraping: {str(e)}"

def job():
    pesan = get_trending_tabs()
    bot.send_message(CHAT_ID, pesan)
    logging.info("Laporan terkirim!")

# --- JADWAL KERJA ---
# Atur jam pengiriman (Format 24 jam Server Azure - biasanya UTC)
# Kalau WIB jam 08:00 pagi, berarti UTC jam 01:00 pagi.
schedule.every().day.at("01:00").do(job)

logging.info("Bot Trend Hunter Berjalan! Menunggu jadwal...")

# Kirim pesan "Saya Hidup" pas pertama kali jalan
bot.send_message(CHAT_ID, "🤖 Bot Trend Hunter Siap! Laporan akan dikirim tiap pagi jam 08:00 WIB.")

while True:
    schedule.run_pending()
    time.sleep(60)
