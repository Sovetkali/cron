import requests
import datetime
import os

# --- Настройки ---
LAT = os.getenv("LAT", "43.238293")          # широта
LNG = os.getenv("LNG", "76.945465")          # долгота
TG_TOKEN = os.getenv("TG_TOKEN")             # токен Telegram-бота
TG_CHAT_ID = os.getenv("TG_CHAT_ID")         # ID чата / пользователя

today = datetime.date.today().isoformat()
year = datetime.date.today().year

URL = f"https://api.muftyat.kz/prayer-times/{year}/{LAT}/{LNG}"


def get_prayer_times():
    resp = requests.get(URL)
    resp.raise_for_status()

    data = resp.json()
    result = data.get("result", [])

    for i, day in enumerate(result):
        if day.get("Date") == today:
            next_day = result[i + 1] if i + 1 < len(result) else None
            return day, next_day

    return None, None


def send_telegram(text: str):
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
    today_prayer, tomorrow_prayer = get_prayer_times()

    if not today_prayer:
        text = f"Нет данных на {today}"
    else:
        today_sunrise = today_prayer.get("sunrise", "—")

        tomorrow_fajr = (
            tomorrow_prayer.get("fajr") if tomorrow_prayer else "—"
        )
        tomorrow_sunrise = (
            tomorrow_prayer.get("sunrise") if tomorrow_prayer else "—"
        )

        text = (
            f"<b>🕌 Расписание намаза на {today}</b>\n\n"
            f"🌙 <b>Fajr:</b> {today_prayer['fajr']}\n"
            f"🌅 <b>Окончание фаджра:</b> {today_sunrise}\n\n"
            f"☀️ <b>Dhuhr:</b> {today_prayer['dhuhr']}\n"
            f"🌤 <b>Asr:</b> {today_prayer['asr']}\n"
            f"🌇 <b>Maghrib:</b> {today_prayer['maghrib']}\n"
            f"🌌 <b>Isha:</b> {today_prayer['isha']}\n\n"
            f"<b>🌙 Fajr следующего дня</b>\n"
            f"🌙 Начало: {tomorrow_fajr}\n"
            f"🌅 Окончание: {tomorrow_sunrise}"
        )

    print("Отправка в Telegram…")
    send_telegram(text)
    print("Готово.")
