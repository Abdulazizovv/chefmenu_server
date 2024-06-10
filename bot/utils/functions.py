from aiogram import types
from bot.utils.db_api.db import get_tg_user_by_phone
from bot.loader import dp
import logging
import asyncio


# yangi userlar uchun xabar yuborish
async def send_user_created_message(phone_number: str):
    tg_user = await get_tg_user_by_phone(phone_number)
    if tg_user:
        try:
            await dp.bot.send_message(tg_user.user_id, "Siz bizning saytda muvaffaqiyatli ro'yxatdan o'tdingiz!\n"\
                                      "Endi xizmatlarimizdan to'liq foydalanishingiz mumkin!")
        except Exception as e:
            logging.error(f"Error while sending message to user: {e}")
    else:
        logging.error(f"User with phone number {phone_number} not found in database")


def send_notify(phone_number: str):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_user_created_message(phone_number))

