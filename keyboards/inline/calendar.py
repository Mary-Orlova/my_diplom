from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import date

today = date.today()
calendar, step = DetailedTelegramCalendar(min_date=today).build()
step = LSTEP[step]
