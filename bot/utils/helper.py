from asgiref.sync import sync_to_async
from verification.utils import get_verification_code
import logging
from bot.data.config import BOT_TOKEN
import telebot
from telebot import types
from telebot.callback_data import CallbackData
import time
from users.models import KitchenOrderReceiver
from orders.models import Orders


bot = telebot.TeleBot(BOT_TOKEN, parse_mode="html")

order_call_data = CallbackData("choice", "id", prefix="order")

def get_order_kb(order_id):
    kb = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton(text="Qabul qilish✅", callback_data=order_call_data.new(choice="accept", id=order_id))
    item2 = types.InlineKeyboardButton(text="Bekor qilish❌", callback_data=order_call_data.new(choice="cancel", id=order_id))
    kb.add(item1, item2, row_width=1)
    return kb    


def send_order_notification(text, user_id, order_id):
    try:
        bot.send_message(chat_id=user_id, text=text, reply_markup=get_order_kb(order_id))
        time.sleep(0.3)
    except Exception as err:
        logging.error(f"error sending new order notification: {err}")



def send_getting_order_notification(text, user_id, order_id):
    try:
        bot.send_message(chat_id=user_id, text=text)
        time.sleep(0.3)
    except Exception as err:
        logging.error(f"error sending getting order notification: {err}")


def send_order_ready_notification(text: str, user_id: int, order_id: int):
    try:
        bot.send_message(chat_id=user_id, text=text)
        time.sleep(0.3)
    except Exception as err:
        logging.error(f"error sending ready order notification: {err}")


@sync_to_async
def change_order_status(status: str, order_id: int):
    try:
        order = Orders.objects.get(id=order_id)
        if order.status == status:
            return False
        order.status = status
        order.save()
        return order
    except Exception as err:
        logging.error(f"error getting order: {err}")
        return None




@sync_to_async
def get_verification_code_async(phone_number):
    return get_verification_code(phone_number)