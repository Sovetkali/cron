import requests
import datetime
import os

# --- Настройки ---
LAT = os.getenv("LAT", "43.238293")          # широта
LNG = os.getenv("LNG", "76.945465")          # долгота
TG_TOKEN = os.getenv("TG_TOKEN")         # токен бота
TG_CHAT_ID = os.getenv("TG_CHAT_ID")     # ID чата/юзера

today = datetime.date.today().isoformat()
year = datetime.date.today().year

URL = f"https://api.muftyat.kz/prayer-times/{year}/{LAT}/{LNG}"

def get_prayer_times():
    resp = requests.get(URL)
    resp.raise_for_status()

    data = resp.json()
    result = data.get("result", [])

    # ищем объект с датой = сегодня
    for day in result:
        if day.get("Date") == today:
            return day

    return None


def send_telegram(text: str):
    """Отправка уведомления в Telegram"""
    tg_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    resp = requests.post(tg_url, data=payload)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    prayer = get_prayer_times()

    if not prayer:
        text = f"Нет данных на {today}"
    else:
        text = (
            f"<b>Расписание намаза на {today}</b>\n\n"
            f"Fajr: {prayer['fajr']}\n"
            f"Dhuhr: {prayer['dhuhr']}\n"
            f"Asr: {prayer['asr']}\n"
            f"Maghrib: {prayer['maghrib']}\n"
            f"Isha: {prayer['isha']}"
        )

    print("Отправка в Telegram…")
    send_telegram(text)
    print("Готово.")
