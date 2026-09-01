import time
from typing import Iterable
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def format_seconds(seconds: int) -> str:
    minutes, secs = divmod(seconds, 60)
    return f"{minutes}m {secs}s" if minutes else f"{secs}s"

def build_inline_keyboard(rows: Iterable[list[InlineKeyboardButton]]) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    for row in rows:
        markup.row(*row)
    return markup

def parse_target(query: str) -> str:
    return query.strip().lstrip("@")
