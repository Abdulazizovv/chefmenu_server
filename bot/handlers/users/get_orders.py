from aiogram import types
from bot.loader import dp
from bot.utils.helper import change_order_status
from bot.keyboards.inline import get_order_kb


@dp.callback_query_handler()
async def get_order_or_cancel(call: types.CallbackQuery):
    if call.data.startswith("order") and len(call.data.split(":")) == 3:
        if call.data.split(":")[1] == "accept":
            order = await change_order_status("in_progress", int(call.data.split(":")[2]))
            if order:
                await call.message.edit_text("Buyurtmani qabul qildingiz⏳\n" + call.message.text, reply_markup=get_order_kb(order_id=order.id))
            else:
                await call.message.edit_text("Buyurtma allaqachon qabul qilib bo'lingan!")
        elif call.data.split(":")[1] == "cancel":
            print("bekor qilindi")
            await call.message.delete()
        elif call.data.split(":")[1] == "ready":
            order = await change_order_status("done", int(call.data.split(":")[2]))
            if order:
                await call.message.edit_reply_markup()
                await call.message.reply("✅")
            elif order == False:
                await call.message.edit_text("Buyurtma allaqachon bajarilgan!")
            else:
                await call.message.edit_text("Buyurtma topilmadi!")
            
