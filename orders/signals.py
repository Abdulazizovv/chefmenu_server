# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Orders
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync
# from django.core.serializers import serialize



# @receiver(post_save, sender=Orders)
# def notify_new_order(sender, instance, created, **kwargs):
#     if created:
#         print(f"sender: {sender}")
#         channel_layer = get_channel_layer()
#         print(instance.kitchen.kitchen_id)
#         async_to_sync(channel_layer.group_send)(
#             f'kitchen_orders_{instance.kitchen.kitchen_id}',
#             {
#                 'type': 'send_latest_orders',
#                 'orders': serialize('json', [instance])
#             }
#         )


from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Orders
from users.models import KitchenOrderReceiver
from bot.utils.functions import send_order_created_message
import logging
import asyncio
import threading
from bot.utils.helper import send_order_notification, send_getting_order_notification, send_order_ready_notification


def send_async_message(text: str, user_id: int, order_id: int):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        asyncio.get_event_loop().run_until_complete(send_order_created_message(text, user_id, order_id))
    finally:
        loop.close()

def send_order_created_notification(order):
    receivers = KitchenOrderReceiver.objects.filter(kitchen=order.kitchen)
    if not receivers:
        logging.error(f"No receivers found for kitchen {order.kitchen}")
        return
    for receiver in receivers:
        if receiver.user.profile.tg_profile and receiver.user.is_kitchen:
            if order.user:
                if receiver.user.id != order.user.id:
                    order_items = order.foods.all()
                    order_items_text = "\n".join([f"{item.food.name} - x{item.quantity}" for item in order_items])
                    order_status = "Yangi"
                    if order.status == 'new':
                        order_status = "Yangi"
                    elif order.status == 'in_progress':
                        order_status = "Ishlanmoqda"
                    elif order.status == 'done':
                        order_status = "Bajarildi" 
                    
                    created_time = order.created.strftime("%H:%M %d-%m-%Y")

                    text = f"➖➖➖➖🆕➖➖➖➖\n"\
                        f"Yangi buyurtma!\n"\
                        f"🆔raqami: {order.id}\n"\
                        f"💸narxi: {order.total_price} so'm\n"\
                        f"📍stol:{order.table.name}\n"\
                        f"👤buyurtma berdi: {order.user.full_name}\n"\
                        f"ℹ️holati: {order_status}\n"\
                        f"⏰vaqti: {created_time}\n"\
                        f"➖➖➖➖🍽➖➖➖➖\n"\
                        f"{order_items_text}\n"\
                        f"➖➖➖➖➖➖➖➖➖"
                    threading.Thread(target=send_order_notification, args=(text, receiver.user.profile.tg_profile.user_id, order.id)).start()
                    # threading.Thread(target=send_async_message, args=(text, receiver.user.profile.tg_profile.user_id, order.id)).start()
                    # asyncio.create_task(send_order_created_message(text, receiver.user.profile.tg_profile.user_id, order.id))
            else:
                order_items = order.foods.all()
                order_items_text = "\n".join([f"{item.food.name} - x{item.quantity}" for item in order_items])
                order_status = "Yangi"
                if order.status == 'new':
                    order_status = "Yangi"
                elif order.status == 'in_progress':
                    order_status = "Ishlanmoqda"
                elif order.status == 'done':
                    order_status = "Bajarildi" 
                
                created_time = order.created.strftime("%H:%M %d-%m-%Y")

                text = f"➖➖➖➖🆕➖➖➖➖\n"\
                    f"Yangi buyurtma!\n"\
                    f"🆔raqami: {order.id}\n"\
                    f"💸narxi: {order.total_price} so'm\n"\
                    f"📍stol:{order.table.name}\n"\
                    f"👤buyurtma berdi: Anonim mijoz\n"\
                    f"ℹ️holati: {order_status}\n"\
                    f"⏰vaqti: {created_time}\n"\
                    f"➖➖➖➖🍽➖➖➖➖\n"\
                    f"{order_items_text}\n"\
                    f"➖➖➖➖➖➖➖➖➖"
                threading.Thread(target=send_order_notification, args=(text, receiver.user.profile.tg_profile.user_id, order.id)).start()
        else:
            logging.error(f"Telegram profile not found for user {receiver.user}")


def send_order_get_notification(order):
    order_user = order.user
    if order_user.profile.tg_profile:
        if order.user.is_kitchen:
            order_items = order.foods.all()
            order_items_text = "\n".join([f"{item.food.name} - x{item.quantity}" for item in order_items])
            order_status = "Yangi"
            if order.status == 'new':
                order_status = "Yangi"
            elif order.status == 'in_progress':
                order_status = "Ishlanmoqda"
            elif order.status == 'done':
                order_status = "Bajarildi" 
            
            created_time = order.updated.strftime("%H:%M %d-%m-%Y")
            text = f"➖➖➖➖⏳➖➖➖➖\n"\
                   f"Buyurtma qabul qilindi\n"\
                    f"🆔raqami: {order.id}\n"\
                    f"💸narxi: {order.total_price} so'm\n"\
                    f"📍stol:{order.table.name}\n"\
                    f"👤buyurtma berdi: {order.user.full_name}\n"\
                    f"ℹ️holati: {order_status}\n"\
                    f"⏰vaqti: {created_time}\n"\
                    f"➖➖➖➖🍽➖➖➖➖\n"\
                    f"{order_items_text}\n"\
                    f"➖➖➖➖➖➖➖➖➖"
        # text = "Buyurtmangiz qabul qilindi! Tez orada sizga xizmat ko'rsatiladi!"
        threading.Thread(target=send_getting_order_notification, args=(text, order_user.profile.tg_profile.user_id, order.id)).start()
        # threading.Thread(target=send_async_message, args=(text, order_user.profile.tg_profile.user_id, order.id)).start()
        # asyncio.create_task(send_order_created_message(text, order_user.profile.tg_profile.user_id, order.id))
    else:
        logging.error(f"Telegram profile not found for user {order_user}")


def send_ready_notification(order):
    if order.user:
        if order.user.profile.tg_profile:
            if order.user.is_kitchen:
                table = order.table.name if order.table.name else order.table.number
                order_items = order.foods.all()
                order_items_text = "\n".join([f"{item.food.name} - x{item.quantity}" for item in order_items])
                order_status = "Yangi"
                if order.status == 'new':
                    order_status = "Yangi"
                elif order.status == 'in_progress':
                    order_status = "Ishlanmoqda"
                elif order.status == 'done':
                    order_status = "Bajarildi" 
                created_time = order.updated.strftime("%H:%M %d-%m-%Y")
                text = f"{table} buyurtmasi tayyor!\n"\
                    f"➖➖➖➖✅➖➖➖➖\n"\
                    f"🆔raqami: {order.id}\n"\
                    f"💸narxi: {order.total_price} so'm\n"\
                    f"📍stol:{order.table.name}\n"\
                    f"👤buyurtma berdi: {order.user.full_name}\n"\
                    f"ℹ️holati: {order_status}\n"\
                    f"⏰vaqti: {created_time}\n"\
                    f"➖➖➖➖🍽➖➖➖➖\n"\
                    f"{order_items_text}\n"\
                    f"➖➖➖➖➖➖➖➖➖"
                threading.Thread(target=send_order_ready_notification, args=(text, order.user.profile.tg_profile.user_id, order.id)).start()
            



@receiver(post_save, sender=Orders)
def new_order_created(sender, instance, created, **kwargs):
    if created:
        pass
    else:
        if instance.status == 'new':
            send_order_created_notification(instance)
        elif instance.status == 'in_progress':
            print("Order in progress")
            send_order_get_notification(instance)
        elif instance.status == "done":
            send_ready_notification(instance)
            
