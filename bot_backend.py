import os
import telebot
import requests
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# === ENVIRONMENT VARIABLES ===
TELEGRAM_TOKEN = os.getenv("8472157205:AAGGMdYazdUEz4yFFV3DsirC0IoHIc3f2bQ")
INSTAGRAM_TOKEN = os.getenv("EAALQNCNebnIBP51jM2b6NcgHZCZBP8M4sS75Vpc1S17PvEBUIU1bIDxPOz9Uf6GWSX1FfnIJkgoDEZCuea7wdYQscJVVVISU98YJfrCs4GYLyyc3SaO7RevrGcxat0GdKtdhrbKSiz84aG9WzZBzY1LThqx22dvy5GZBw6rqerVZAiADTfNADsQz5ZApVU0DrwQx5dPkH8bLGpNyAZDZD")
SHEET_URL = os.getenv("https://docs.google.com/spreadsheets/d/1RUOzf-1dM7C87CJtXo2Ae919sx_BSMDfu-APHKytFyU/edit?usp=drivesdk")

# === TELEGRAM BOT SETUP ===
bot = telebot.TeleBot("8472157205:AAGGMdYazdUEz4yFFV3DsirC0IoHIc3f2bQ")

# === GOOGLE SHEET SETUP ===
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)
sheet1 = client.open_by_url("https://docs.google.com/spreadsheets/d/1RUOzf-1dM7C87CJtXo2Ae919sx_BSMDfu-APHKytFyU/edit?usp=drivesdk").worksheet("Sheet1")
sheet2 = client.open_by_url("https://docs.google.com/spreadsheets/d/1RUOzf-1dM7C87CJtXo2Ae919sx_BSMDfu-APHKytFyU/edit?usp=drivesdk").worksheet("Sheet2")
sheet3 = client.open_by_url("https://docs.google.com/spreadsheets/d/1RUOzf-1dM7C87CJtXo2Ae919sx_BSMDfu-APHKytFyU/edit?usp=drivesdk").worksheet("Sheet3")

# === FUNCTION TO REMOVE DUPLICATES ===
def remove_duplicates(links):
    return list(dict.fromkeys(links))

# === FUNCTION TO FETCH REEL VIEWS ===
def get_reel_views(shortcode):
    url = f"https://graph.facebook.com/v21.0/instagram_oembed?url=https://www.instagram.com/reel/{shortcode}/&access_token=8472157205:AAGGMdYazdUEz4yFFV3DsirC0IoHIc3f2bQ"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        return data.get('media_id', 'No data')
    else:
        return "Error"

# === FUNCTION TO PROCESS LINKS ===
def process_links(start_date, end_date):
    data = sheet1.col_values(1)
    processed = []
    usernames = {}
    
    for link in data[1:]:
        if not link or "instagram.com/reel/" not in link:
            continue
        shortcode = link.split("reel/")[1].split("/")[0]
        views = get_reel_views(shortcode)
        if views != "Error":
            sheet3.append_row([link, views, datetime.now().strftime("%d-%m-%Y %H:%M:%S")])
            processed.append(link)
            
            user = link.split("/")[3]
            usernames[user] = usernames.get(user, 0) + 1

    sheet2.clear()
    sheet2.append_row(["Username", "Total Reels"])
    for user, total in usernames.items():
        sheet2.append_row([user, total])

    return len(processed)

# === TELEGRAM COMMAND HANDLER ===
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Hello! I’m ReelViews Smart Bot.\n\nSend /count to start counting your reels.")

@bot.message_handler(commands=['count'])
def count_views(message):
    bot.send_message(message.chat.id, "Counting reels... Please wait")

    total = process_links("27-10-2025", "31-10-2025")
    bot.send_message(message.chat.id, f"Done! Counted {total} valid reels between 27 Oct - 31 Oct 2025.")

# === RUN BOT ===

bot.polling(none_stop=True)
