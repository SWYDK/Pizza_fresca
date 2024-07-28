from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton,WebAppInfo
from main.tg_bot.database import *


def admin_panel() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text='Статистика', callback_data='statistics')
    keyboard.button(text='Рассылка', callback_data='mailing')
    keyboard.button(text='Добавить позицию', callback_data='add_position')
    keyboard.button(text='Удалить позицию', callback_data='delete_position')
    return keyboard.adjust(1).as_markup()

def order_delivered(num) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text='Заказ доставлен', callback_data=f'order_d_{num}')
    return keyboard.adjust(1).as_markup()




start_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Начать 🍕',  web_app=WebAppInfo(text='Начать',url='https://pizzafresca.ru'))
        ],
        [
            KeyboardButton(text='Мои заказы ℹ️')
        ],
    ],
    resize_keyboard=True
)

def get_order_post() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    # url: str = 'https://www.figma.com/design/DZ86D3MECMXG1bEdZH1WgB/Untitled?node-id=0-1&t=GDOZf8b5XlANPEzd-0'

    keyboard.button(text='Заказать', web_app=WebAppInfo(text='Заказать',url='https://google.com') )
    return keyboard.adjust(1).as_markup()


ORDERS_PER_PAGE = 25

async def list_orders(tg_id, page=1) -> InlineKeyboardMarkup:
    start_idx = (page - 1) * ORDERS_PER_PAGE
    end_idx = start_idx + ORDERS_PER_PAGE

    orders = await fetch_orders(tg_id, start_idx, end_idx)
    total_orders = await count_orders(tg_id)

    keyboard = InlineKeyboardBuilder()
    for order in orders:
        a = str(order.get_status_display())
        if a=="Cooking":
            a="В готовке"
        elif a=="Delivery":
            a="В доставке"
        elif a=="Received":
            a="Доставлен"    
        m = str(order.date.month)
        d = str(order.date.day)
        if len(m)==1:
            m = '0' + m
        if len(d)==1:
            d = '0' + d
        keyboard.button(
            text=f'{order.summa}₽ - {a} ({d}.{m})',
            callback_data=f'order_{order.id}'
        )

    if page > 1:
        keyboard.button(text='⏪ Назад', callback_data=f'prev_page_{page-1}')
    if end_idx < total_orders:
        keyboard.button(text='Вперед ⏩', callback_data=f'next_page_{page+1}')

    return keyboard.adjust(1).as_markup()


def add_categories() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text='Пиццы', callback_data='add_pizza')
    keyboard.button(text='Десерты', callback_data='add_desserts')
    keyboard.button(text='Салаты', callback_data='add_salads')
    keyboard.button(text='Супы', callback_data='add_soups')
    keyboard.button(text='Напитки', callback_data='add_Drinks')
    keyboard.button(text='Выйти', callback_data='add_come_out')
    return keyboard.adjust(2).as_markup()


def delete_categories() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text='Пиццы', callback_data='delete_pizza')
    keyboard.button(text='Десерты', callback_data='delete_desserts')
    keyboard.button(text='Салаты', callback_data='delete_salads')
    keyboard.button(text='Супы', callback_data='delete_soups')
    keyboard.button(text='Напитки', callback_data='delete_Drinks')
    keyboard.button(text='Выйти', callback_data='delete_come_out')
    return keyboard.adjust(2).as_markup()


def offer_cancel() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()

    keyboard.button(text='Вернуться')
    return keyboard.as_markup(resize_keyboard=True)


def choice_button_yes() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()

    keyboard.button(text='Да, выполнить')
    keyboard.button(text='Нет, вернуться')
    return keyboard.as_markup(resize_keyboard=True)
def post_type() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()

    keyboard.button(text='Только текст')
    keyboard.button(text='С фото')
    return keyboard.as_markup(resize_keyboard=True)


def choice_button_no() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()

    keyboard.button(text='Да, выполнить')
    keyboard.button(text='Нет, вернуться')
    return keyboard.as_markup(resize_keyboard=True)


def skip_geo2() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()

    keyboard.button(text='Пропустить')
    return keyboard.as_markup(resize_keyboard=True)

def shipping_method() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()

    keyboard.button(text='🚚 Доставка')
    keyboard.button(text='📍 Самовывоз')
    return keyboard.as_markup(resize_keyboard=True)


get_geo = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='❗️ Прислать адрес', request_location=True)
        ],
        [
            KeyboardButton(text='Вернуться в меню')
        ],
    ],
    resize_keyboard=True
)

def fast_delivery() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()

    keyboard.button(text='Как можно скорее')
    keyboard.button(text='Вернуться')
    return keyboard.as_markup(resize_keyboard=True)


get_number = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='📱 Отправить телефон', request_contact=True)
        ],
        [
            KeyboardButton(text='Вернуться')
        ],
    ],
    resize_keyboard=True
)


def get_comment() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()

    keyboard.button(text='Пропустить')
    keyboard.button(text='Вернуться')
    return keyboard.as_markup(resize_keyboard=True)


def payments() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()

    keyboard.button(text='Сбербанк')
    keyboard.button(text='При получении')
    keyboard.button(text='Вернуться')
    return keyboard.as_markup(resize_keyboard=True)
