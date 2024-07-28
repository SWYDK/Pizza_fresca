from aiogram import Bot
from asgiref.sync import sync_to_async
from main.tg_bot.database import *
import main.tg_bot.reply as kb
import re

# П
# Регулярное выражение для поиска номера заказа




async def notify_user(bot: Bot):
    
    # Получаем все заказы
    orders_data = await get_all_orders()
    
    # Список tg_id для удаления
    tg_ids_to_delete = []
    
    # Обрабатываем каждый заказ
    for order in orders_data:
        user_id = order['tg_id']
        if user_id == -4272922175:
            message = order['withOrder']
            print(message)
            match = re.search(r'Заказ\s#(\d+)', message)

            # Извлечение номера заказа
            if match:
                order_number = match.group(1)
            else:
                order_number = None
            print(order_number)
            await bot.send_message(chat_id=user_id, text=message,reply_markup=kb.order_delivered(order_number))
            tg_ids_to_delete.append(user_id)  
        else:

            message = order['withOrder']
            await bot.send_message(chat_id=user_id, text=message)
            tg_ids_to_delete.append(user_id)  # Добавляем tg_id в список для удаления
    
    # Удаляем обработанные заказы
    await delete_orders(tg_ids_to_delete)