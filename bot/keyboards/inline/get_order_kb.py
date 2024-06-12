from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_order_kb(order_id: int):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="Tayyor✅", callback_data=f"order:ready:{order_id}"))
    return kb