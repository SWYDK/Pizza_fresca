from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async

from decimal import Decimal  # Добавьте этот импорт
import aiofiles
import os

from main.models import User,Menu,Ingredients
from main.tg_bot.database import *
from main.tg_bot.classes_functions import Admin
import main.tg_bot.reply as kb
from main.tg_bot.database import check_admin



admin_private = Router()




@admin_private.message(Command('admin'))
async def admin_panel(message: Message):
    ch = await check_admin(message.from_user.id)
    if ch:
        await message.answer('🔒 Админ-панель', reply_markup=kb.admin_panel())
    else:
        await message.answer('У вас нет доступа')

@admin_private.callback_query(F.data == 'statistics')
async def statistics(callback: CallbackQuery):
    await callback.answer()
    
    q = await get_users() 
    q2 = await get_users_status() 
    q3 = await get_users_status2() 
    
    total_orders = await get_total_orders_count()
    today_orders = await get_today_orders_count()
    week_orders = await get_week_orders_count()
    month_orders = await get_month_orders_count()
    
    await callback.message.answer('📊 <b>Статистика</b> \n'
                                  f'Всего пользователей: <b>{q}</b> \n'
                                  f'Активных пользователей: <b>{q2}</b> \n'
                                  f'Неактивных пользователей: <b>{q3}</b> \n'
                                  '\n'
                                  '📦 <b>Заказы</b> \n'
                                  f'Всего заказов: <b>{total_orders}</b>\n'
                                  f'Заказов сегодня: <b>{today_orders}</b>\n'
                                  f'Заказов за неделю: <b>{week_orders}</b>\n'
                                  f'Заказов за месяц: <b>{month_orders}</b>')


@admin_private.callback_query(F.data == 'add_position')
async def mailing_users(callback: CallbackQuery):
    await callback.message.edit_text('Выберите категорию', reply_markup=kb.add_categories())

@admin_private.callback_query(F.data == 'add_pizza')
async def add_pizza(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.position_name)

    await callback.message.answer('Введите название позиции', reply_markup=kb.offer_cancel())

@admin_private.message(Admin.position_name)
async def proccess__pizza_name(message: Message, state: FSMContext):
    await state.update_data(position_name=message.text)
    user_message = message.text
    await state.set_state(Admin.position_photo)

    if user_message == 'Вернуться':
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.add_categories())
        await state.clear()
    else:
        await message.answer('Введите фото позиции')

@admin_private.message(Admin.position_photo)
async def process_position_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer('Пожалуйста, отправьте фото позиции.')
        return
    
    file_id = message.photo[-1].file_id
    file_info = await message.bot.get_file(file_id)
    file_path = file_info.file_path
    file_name = f"static/media/menu_photos/{file_id}.jpg"
    destination = f"{file_name}"
    
    await state.update_data(position_photo=file_name)

    async with aiofiles.open(destination, 'wb') as out_file:
        file = await message.bot.download_file(file_path)
        await out_file.write(file.read())
    
    await state.set_state(Admin.description)
    await message.answer('Введите описание')

@admin_private.message(Admin.description)
async def proccess_pizza_description(message: Message, state: FSMContext):
    user_message = message.text
    await state.update_data(description=message.text)
    await state.set_state(Admin.calorie_content)

    if user_message == 'Вернуться':
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.add_categories())
        await state.clear()
    else:
        await message.answer('Введите калорийность')


@admin_private.message(Admin.calorie_content)
async def proccess_desserts_calorie_content(message: Message, state: FSMContext):
    user_message = message.text
    await state.update_data(calorie_content=message.text)
    await state.set_state(Admin.ingredients)

    if user_message == 'Вернуться':
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.add_categories())
        await state.clear()
    else:
        await message.answer('Введите ингредиенты через запятую')


@admin_private.message(Admin.ingredients)
async def proccess_desserts_calorie_content(message: Message, state: FSMContext):
    user_message = message.text
    ingredients_list = [ingredient.strip() for ingredient in message.text.split(',')]
    await state.update_data(ingredients=ingredients_list)
    await state.set_state(Admin.allergens)

    if user_message == 'Вернуться':
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.add_categories())
        await state.clear()
    else:
        await message.answer('Введите аллергенты')

@admin_private.message(Admin.allergens)
async def proccess_desserts_allergens(message: Message, state: FSMContext):
    user_message = message.text
    await state.update_data(allergens=message.text)
    await state.set_state(Admin.cost)

    if user_message == 'Вернуться':
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.add_categories())
        await state.clear()
    else:
        await message.answer('Введите стоимость (только число)')

@admin_private.message(Admin.cost)
async def procces_pizza_cost(message: Message, state: FSMContext):
    await state.update_data(cost=message.text)
    data = await state.get_data()
    # name = data['position_name']
    # photo = data['position_photo']
    # description = data['description']
    # calorie_content = data['calorie_content']
    # allergens = data['allergens']
    cost = data['cost']
    try:
        # здесь нужно обработать логику добавления позиции в бд
        cost = Decimal(data['cost'])
        category_name = 'Пицца'
        category = await sync_to_async(Category.objects.get)(name=category_name)
        
        menu_item = await sync_to_async(Menu.objects.create)(
            photo=data['position_photo'],
            name=data['position_name'],
            weight='500',  # Измените это значение по необходимости
            allergens=data['allergens'],
            energy_valuable=data['calorie_content'],
            compounds='Ингредиенты',  # Измените это значение по необходимости
            category=category,
            price=cost
        )
        ingredients_list = data['ingredients']
        for ingredient_name in ingredients_list:
            await sync_to_async(Ingredients.objects.create)(
                name=ingredient_name,
                dish=menu_item,
                isInDish=True
            )
        await message.answer(f'✅ Позиция успешно добавлена - {cost}')
        await admin_panel(message)
        await state.clear()
    except TypeError as te:
        await message.answer(f'Это не число')
        await state.set_state(Admin.cost)



@admin_private.callback_query(F.data == 'add_desserts')
async def add_desserts(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.position_name)

    await callback.message.answer('Введите название позиции', reply_markup=kb.offer_cancel())

@admin_private.message(Admin.position_name)
async def proccess__desserts_name(message: Message, state: FSMContext):
    await state.update_data(position_name=message.text)
    user_message = message.text
    await state.set_state(Admin.position_photo)

    if user_message == 'Вернуться':
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.add_categories())
        await state.clear()
    else:
        await message.answer('Введите фото позиции')

@admin_private.message(Admin.position_photo)
async def process_position_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer('Пожалуйста, отправьте фото позиции.')
        return
    
    file_id = message.photo[-1].file_id
    file_info = await message.bot.get_file(file_id)
    file_path = file_info.file_path
    file_name = f"static/media/menu_photos/{file_id}.jpg"

    destination = f"{file_name}"
    
    await state.update_data(position_photo=file_name)

    async with aiofiles.open(destination, 'wb') as out_file:
        file = await message.bot.download_file(file_path)
        await out_file.write(file.read())
    
    await state.set_state(Admin.description)
    await message.answer('Введите описание')

@admin_private.message(Admin.description)
async def proccess_desserts_description(message: Message, state: FSMContext):
    user_message = message.text
    await state.update_data(description=message.text)
    await state.set_state(Admin.calorie_content)

    if user_message == 'Вернуться':
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.add_categories())
        await state.clear()
    else:
        await message.answer('Введите калорийность')

@admin_private.message(Admin.calorie_content)
async def proccess_desserts_calorie_content(message: Message, state: FSMContext):
    user_message = message.text
    await state.update_data(calorie_content=message.text)
    await state.set_state(Admin.ingredients)

    if user_message == 'Вернуться':
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.add_categories())
        await state.clear()
    else:
        await message.answer('Введите ингредиенты через запятую')


@admin_private.message(Admin.ingredients)
async def proccess_desserts_calorie_content(message: Message, state: FSMContext):
    user_message = message.text
    ingredients_list = [ingredient.strip() for ingredient in message.text.split(',')]
    await state.update_data(ingredients=ingredients_list)
    await state.set_state(Admin.allergens)

    if user_message == 'Вернуться':
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.add_categories())
        await state.clear()
    else:
        await message.answer('Введите аллергенты')

@admin_private.message(Admin.allergens)
async def proccess_desserts_allergens(message: Message, state: FSMContext):
    user_message = message.text
    await state.update_data(allergens=message.text)
    await state.set_state(Admin.cost)

    if user_message == 'Вернуться':
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.add_categories())
        await state.clear()
    else:
        await message.answer('Введите стоимость (только число)')
@admin_private.message(Admin.cost)
async def procces_pizza_cost(message: Message, state: FSMContext):
    await state.update_data(cost=message.text)
    data = await state.get_data()
    # name = data['position_name']
    # photo = data['position_photo']
    # description = data['description']
    # calorie_content = data['calorie_content']
    # allergens = data['allergens']
    cost = data['cost']
    try:
        # здесь нужно обработать логику добавления позиции в бд
        cost = Decimal(data['cost'])
        category_name = 'Пицца'
        category = await sync_to_async(Category.objects.get)(name=category_name)
        
        menu_item = await sync_to_async(Menu.objects.create)(
            photo=data['position_photo'],
            name=data['position_name'],
            weight='500',  # Измените это значение по необходимости
            allergens=data['allergens'],
            energy_valuable=data['calorie_content'],
            compounds='Ингредиенты',  # Измените это значение по необходимости
            category=category,
            price=cost
        )
        ingredients_list = data['ingredients']
        for ingredient_name in ingredients_list:
            await sync_to_async(Ingredients.objects.create)(
                name=ingredient_name,
                dish=menu_item,
                isInDish=True
            )
        await message.answer(f'✅ Позиция успешно добавлена - {cost}')
        await admin_panel(message)
        await state.clear()
    except TypeError as te:
        await message.answer(f'Это не число')
        await state.set_state(Admin.cost)

@admin_private.callback_query(F.data == 'add_salads')
async def add_salads(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.position_name)

    await callback.message.answer('Введите название позиции', reply_markup=kb.offer_cancel())

@admin_private.message(Admin.position_name)
async def proccess__salads_name(message: Message, state: FSMContext):
    await state.update_data(position_name=message.text)
    user_message = message.text
    await state.set_state(Admin.position_photo)

    if user_message == 'Вернуться':
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.add_categories())
        await state.clear()
    else:
        await message.answer('Введите фото позиции')

@admin_private.message(Admin.position_photo)
async def process_position_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer('Пожалуйста, отправьте фото позиции.')
        return
    
    file_id = message.photo[-1].file_id
    file_info = await message.bot.get_file(file_id)
    file_path = file_info.file_path
    file_name = f"static/media/menu_photos/{file_id}.jpg"
    
    destination = f"{file_name}"
    
    await state.update_data(position_photo=file_name)

    async with aiofiles.open(destination, 'wb') as out_file:
        file = await message.bot.download_file(file_path)
        await out_file.write(file.read())
    
    await state.set_state(Admin.description)
    await message.answer('Введите описание')

@admin_private.message(Admin.description)
async def proccess_salads_description(message: Message, state: FSMContext):
    user_message = message.text
    await state.update_data(description=message.text)
    await state.set_state(Admin.calorie_content)

    if user_message == 'Вернуться':
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.add_categories())
        await state.clear()
    else:
        await message.answer('Введите калорийность')



@admin_private.message(Admin.calorie_content)
async def proccess_desserts_calorie_content(message: Message, state: FSMContext):
    user_message = message.text
    await state.update_data(calorie_content=message.text)
    await state.set_state(Admin.ingredients)

    if user_message == 'Вернуться':
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.add_categories())
        await state.clear()
    else:
        await message.answer('Введите ингредиенты через запятую')


@admin_private.message(Admin.ingredients)
async def proccess_desserts_calorie_content(message: Message, state: FSMContext):
    user_message = message.text
    ingredients_list = [ingredient.strip() for ingredient in message.text.split(',')]
    await state.update_data(ingredients=ingredients_list)
    await state.set_state(Admin.allergens)

    if user_message == 'Вернуться':
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.add_categories())
        await state.clear()
    else:
        await message.answer('Введите аллергенты')

@admin_private.message(Admin.allergens)
async def proccess_desserts_allergens(message: Message, state: FSMContext):
    user_message = message.text
    await state.update_data(allergens=message.text)
    await state.set_state(Admin.cost)

    if user_message == 'Вернуться':
        await message.answer('Вы отменили данное действие ', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.add_categories())
        await state.clear()
    else:
        await message.answer('Введите стоимость (только число)')


@admin_private.message(Admin.cost)
async def procces_pizza_cost(message: Message, state: FSMContext):
    await state.update_data(cost=message.text)
    data = await state.get_data()
    # name = data['position_name']
    # photo = data['position_photo']
    # description = data['description']
    # calorie_content = data['calorie_content']
    # allergens = data['allergens']
    cost = data['cost']
    try:
        # здесь нужно обработать логику добавления позиции в бд
        cost = Decimal(data['cost'])
        category_name = 'Пицца'
        category = await sync_to_async(Category.objects.get)(name=category_name)
        
        menu_item = await sync_to_async(Menu.objects.create)(
            photo=data['position_photo'],
            name=data['position_name'],
            weight='500',  # Измените это значение по необходимости
            allergens=data['allergens'],
            energy_valuable=data['calorie_content'],
            compounds='Ингредиенты',  # Измените это значение по необходимости
            category=category,
            price=cost
        )
        ingredients_list = data['ingredients']
        for ingredient_name in ingredients_list:
            await sync_to_async(Ingredients.objects.create)(
                name=ingredient_name,
                dish=menu_item,
                isInDish=True
            )
        await message.answer(f'✅ Позиция успешно добавлена - {cost}')
        await admin_panel(message)
        await state.clear()
    except TypeError as te:
        await message.answer(f'Это не число')
        await state.set_state(Admin.cost)


@admin_private.callback_query(F.data == 'add_soups')
async def add_soups(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.position_name)

    await callback.message.answer('Введите название позиции', reply_markup=kb.offer_cancel())

@admin_private.message(Admin.position_name)
async def proccess__soups_name(message: Message, state: FSMContext):
    await state.update_data(position_name=message.text)
    user_message = message.text
    await state.set_state(Admin.position_photo)

    if user_message == 'Вернуться':
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.add_categories())
        await state.clear()
    else:
        await message.answer('Введите фото позиции')

@admin_private.message(Admin.position_photo)
async def process_position_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer('Пожалуйста, отправьте фото позиции.')
        return
    
    file_id = message.photo[-1].file_id
    file_info = await message.bot.get_file(file_id)
    file_path = file_info.file_path
    file_name = f"static/media/menu_photos/{file_id}.jpg"

    destination = f"{file_name}"
    
    await state.update_data(position_photo=file_name)

    async with aiofiles.open(destination, 'wb') as out_file:
        file = await message.bot.download_file(file_path)
        await out_file.write(file.read())
    
    await state.set_state(Admin.description)
    await message.answer('Введите описание')

@admin_private.message(Admin.description)
async def proccess_soups_description(message: Message, state: FSMContext):
    user_message = message.text
    await state.update_data(description=message.text)
    await state.set_state(Admin.calorie_content)

    if user_message == 'Вернуться':
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.add_categories())
        await state.clear()
    else:
        await message.answer('Введите калорийность')


@admin_private.message(Admin.calorie_content)
async def proccess_desserts_calorie_content(message: Message, state: FSMContext):
    user_message = message.text
    await state.update_data(calorie_content=message.text)
    await state.set_state(Admin.ingredients)

    if user_message == 'Вернуться':
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.add_categories())
        await state.clear()
    else:
        await message.answer('Введите ингредиенты через запятую')


@admin_private.message(Admin.ingredients)
async def proccess_desserts_calorie_content(message: Message, state: FSMContext):
    user_message = message.text
    ingredients_list = [ingredient.strip() for ingredient in message.text.split(',')]
    await state.update_data(ingredients=ingredients_list)
    await state.set_state(Admin.allergens)

    if user_message == 'Вернуться':
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.add_categories())
        await state.clear()
    else:
        await message.answer('Введите аллергенты')

@admin_private.message(Admin.allergens)
async def proccess_desserts_allergens(message: Message, state: FSMContext):
    user_message = message.text
    await state.update_data(allergens=message.text)
    await state.set_state(Admin.cost)

    if user_message == 'Вернуться':
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.add_categories())
        await state.clear()
    else:
        await message.answer('Введите стоимость (только число)')


@admin_private.message(Admin.cost)
async def procces_pizza_cost(message: Message, state: FSMContext):
    await state.update_data(cost=message.text)
    data = await state.get_data()
    # name = data['position_name']
    # photo = data['position_photo']
    # description = data['description']
    # calorie_content = data['calorie_content']
    # allergens = data['allergens']
    cost = data['cost']
    try:
        # здесь нужно обработать логику добавления позиции в бд
        cost = Decimal(data['cost'])
        category_name = 'Пицца'
        category = await sync_to_async(Category.objects.get)(name=category_name)
        
        menu_item = await sync_to_async(Menu.objects.create)(
            photo=data['position_photo'],
            name=data['position_name'],
            weight='500',  # Измените это значение по необходимости
            allergens=data['allergens'],
            energy_valuable=data['calorie_content'],
            compounds='Ингредиенты',  # Измените это значение по необходимости
            category=category,
            price=cost
        )
        ingredients_list = data['ingredients']
        for ingredient_name in ingredients_list:
            await sync_to_async(Ingredients.objects.create)(
                name=ingredient_name,
                dish=menu_item,
                isInDish=True
            )
        await message.answer(f'✅ Позиция успешно добавлена - {cost}')
        await admin_panel(message)
        await state.clear()
    except TypeError as te:
        await message.answer(f'Это не число')
        await state.set_state(Admin.cost)

@admin_private.callback_query(F.data == 'add_Drinks')
async def add_Drinks(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.position_name)

    await callback.message.answer('Введите название позиции', reply_markup=kb.offer_cancel())

@admin_private.message(Admin.position_name)
async def proccess__Drinks_name(message: Message, state: FSMContext):
    await state.update_data(position_name=message.text)
    user_message = message.text
    await state.set_state(Admin.position_photo)

    if user_message == 'Вернуться':
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.add_categories())
        await state.clear()
    else:
        await message.answer('Введите фото позиции')

@admin_private.message(Admin.position_photo)
async def process_position_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer('Пожалуйста, отправьте фото позиции.')
        return
    
    file_id = message.photo[-1].file_id
    file_info = await message.bot.get_file(file_id)
    file_path = file_info.file_path
    file_name = f"static/media/menu_photos/{file_id}.jpg"

    destination = f"{file_name}"
    
    await state.update_data(position_photo=file_name)

    async with aiofiles.open(destination, 'wb') as out_file:
        file = await message.bot.download_file(file_path)
        await out_file.write(file.read())
    
    await state.set_state(Admin.description)
    await message.answer('Введите описание')

@admin_private.message(Admin.description)
async def proccess_Drinks_description(message: Message, state: FSMContext):
    user_message = message.text
    await state.update_data(description=message.text)
    await state.set_state(Admin.calorie_content)

    if user_message == 'Вернуться':
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.add_categories())
        await state.clear()
    else:
        await message.answer('Введите калорийность')



@admin_private.message(Admin.calorie_content)
async def proccess_desserts_calorie_content(message: Message, state: FSMContext):
    user_message = message.text
    await state.update_data(calorie_content=message.text)
    await state.set_state(Admin.ingredients)

    if user_message == 'Вернуться':
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.add_categories())
        await state.clear()
    else:
        await message.answer('Введите ингредиенты через запятую')


@admin_private.message(Admin.ingredients)
async def proccess_desserts_calorie_content(message: Message, state: FSMContext):
    user_message = message.text
    ingredients_list = [ingredient.strip() for ingredient in message.text.split(',')]
    await state.update_data(ingredients=ingredients_list)
    await state.set_state(Admin.allergens)

    if user_message == 'Вернуться':
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.add_categories())
        await state.clear()
    else:
        await message.answer('Введите аллергенты')

@admin_private.message(Admin.allergens)
async def proccess_desserts_allergens(message: Message, state: FSMContext):
    user_message = message.text
    await state.update_data(allergens=message.text)
    await state.set_state(Admin.cost)

    if user_message == 'Вернуться':
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.add_categories())
        await state.clear()
    else:
        await message.answer('Введите стоимость (только число)')


@admin_private.message(Admin.cost)
async def procces_pizza_cost(message: Message, state: FSMContext):
    await state.update_data(cost=message.text)
    data = await state.get_data()
    # name = data['position_name']
    # photo = data['position_photo']
    # description = data['description']
    # calorie_content = data['calorie_content']
    # allergens = data['allergens']
    cost = data['cost']
    try:
        # здесь нужно обработать логику добавления позиции в бд
        cost = Decimal(data['cost'])
        category_name = 'Пицца'
        category = await sync_to_async(Category.objects.get)(name=category_name)
        
        menu_item = await sync_to_async(Menu.objects.create)(
            photo=data['position_photo'],
            name=data['position_name'],
            weight='500',  # Измените это значение по необходимости
            allergens=data['allergens'],
            energy_valuable=data['calorie_content'],
            compounds='Ингредиенты',  # Измените это значение по необходимости
            category=category,
            price=cost
        )
        ingredients_list = data['ingredients']
        for ingredient_name in ingredients_list:
            await sync_to_async(Ingredients.objects.create)(
                name=ingredient_name,
                dish=menu_item,
                isInDish=True
            )
        await message.answer(f'✅ Позиция успешно добавлена - {cost}')
        await admin_panel(message)
        await state.clear()
    except TypeError as te:
        await message.answer(f'Это не число')
        await state.set_state(Admin.cost)


@admin_private.callback_query(F.data == 'add_come_out')
async def come_out_menu(callback: CallbackQuery):
    await callback.message.edit_text('🔒 Админ-панель', reply_markup=kb.admin_panel())


@admin_private.callback_query(F.data == 'mailing')
async def post_mailing(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.mailing_state)

    await callback.message.answer('Выберите тип рассылки ',reply_markup=kb.post_type())

@admin_private.message(Admin.mailing_state)
async def proccess_text(message: Message, state: FSMContext):
    if message.text == "Только текст":


        await state.set_state(Admin.mailing_text_only)
    elif message.text == "С фото":
        await state.set_state(Admin.mailing_text)


    await message.answer('Отправьте пост для рассылки',reply_markup=ReplyKeyboardRemove())

@admin_private.message(Admin.mailing_text_only)
async def proccess_text(message: Message, state: FSMContext):
    await state.update_data(mailing_text=message.text)
    await state.set_state(Admin.ask)

    await message.answer('Добавить кнопку <b>Заказать</b>?')

@admin_private.message(Admin.mailing_text, F.photo)
async def proccess_text(message: Message, state: FSMContext):
    await state.update_data(mailing_text=message.caption)
    await state.update_data(mailing_photo=message.photo[-1].file_id)
    await state.set_state(Admin.ask)

    await message.answer('Добавить кнопку <b>Заказать</b>?')

@admin_private.message(Admin.ask)
async def procces_ask(message: Message, state: FSMContext):
    await state.update_data(ask=message.text)
    data = await state.get_data()
    if 'mailing_photo' in data:
        photo = data['mailing_photo']
        caption = data['mailing_text']
        text = data['ask']

        if message.text == 'Да' or  message.text == 'да':
            await state.set_state(Admin.confirm_yes)
            await message.answer_photo(photo=photo, caption=f'{caption} \n'
                                    '\n'
                                    'Все верно?',
                                    reply_markup=kb.choice_button_yes())

        elif message.text == 'Нет' or  message.text == 'нет':
            await state.set_state(Admin.confirm_no)
            
            await message.answer_photo(photo=photo, caption=f'{caption} \n'
                                    '\n'
                                    'Все верно?',
                                    reply_markup=kb.choice_button_no())
    else:
        caption = data['mailing_text']
        text = data['ask']

        if message.text == 'Да' or  message.text == 'да':
            await state.set_state(Admin.confirm_yes)
            await message.answer(text=f'{caption} \n'
                                    '\n'
                                    'Все верно?',
                                    reply_markup=kb.choice_button_yes())

        elif message.text == 'Нет' or  message.text == 'нет':
            await state.set_state(Admin.confirm_no)
            await message.answer(text=f'{caption} \n'
                                    '\n'
                                    'Все верно?',
                                    reply_markup=kb.choice_button_yes())


@admin_private.message(Admin.confirm_yes)
async def procces_post_yes(message: Message, state: FSMContext):
    await state.update_data(confirm_yes=message.text)
    data = await state.get_data()
    text = data['confirm_yes']

    if text == 'Да, выполнить':
        # Здесь нужно сделать функцию рассылки с кнопкой
        z = await state.get_data()

        u = await get_users_post()
        if 'mailing_photo' in data:
            c = 0
            caption = data['mailing_text']
            photo = data['mailing_photo']
            for user in u:
                

                await message.bot.send_photo(user['tg_id'], photo=data['mailing_photo'], caption=caption,reply_markup=kb.get_order_post())
                c+=1
            await message.answer('Рассылка завершена \n'
                                f'Отправлено: <b>{c} сообщений</b>',
                                reply_markup=ReplyKeyboardRemove())
            await message.answer('Вы вернулись в меню', reply_markup=kb.admin_panel())
            await state.clear()
        else:
            c = 0
            for user in u:
                

                await message.bot.send_message(user['tg_id'],f'{data["mailing_text"]}',reply_markup=kb.get_order_post())
                c+=1
            await message.answer('Рассылка завершена \n'
                                f'Отправлено: <b>{c} сообщений</b>',
                                reply_markup=ReplyKeyboardRemove())
            await message.answer('Вы вернулись в меню', reply_markup=kb.admin_panel())
            await state.clear()
    if text == 'Нет, вернуться':
        if 'mailing_photo' in data:
            await state.clear()
            await state.set_state(Admin.mailing_text)
            await message.answer('Отправьте пост для рассылки', reply_markup=ReplyKeyboardRemove())
        else:
            await state.clear()
            await state.set_state(Admin.mailing_text_only)
            await message.answer('Отправьте пост для рассылки', reply_markup=ReplyKeyboardRemove())

@admin_private.message(Admin.confirm_no)
async def procces_post_no(message: Message, state: FSMContext):
    await state.update_data(confirm_yes=message.text)
    data = await state.get_data()
    # caption = data['mailing_text']
    # photo = data['mailing_photo']
    text = data['confirm_yes']

    if text == 'Да, выполнить':
        # Здесь нужно сделать функцию рассылки с кнопкой
        z = await state.get_data()

        u = await get_users_post()

        
        if 'mailing_photo' in data:
            c = 0
            caption = data['mailing_text']
            photo = data['mailing_photo']
            for user in u:
                

                await message.bot.send_photo(user['tg_id'], photo=data['mailing_photo'], caption=caption)
                c+=1
            await message.answer('Рассылка завершена \n'
                                f'Отправлено: <b>{c} сообщений</b>',
                                reply_markup=ReplyKeyboardRemove())
            await message.answer('Вы вернулись в меню', reply_markup=kb.admin_panel())
            await state.clear()
        else:
            c = 0
            for user in u:
                

                await message.bot.send_message(user['tg_id'],f'{data["mailing_text"]}')
                c+=1
            await message.answer('Рассылка завершена \n'
                                f'Отправлено: <b>{c} сообщений</b>',
                                reply_markup=ReplyKeyboardRemove())
            await message.answer('Вы вернулись в меню', reply_markup=kb.admin_panel())
            await state.clear()
    if text == 'Нет, вернуться':
        if 'mailing_photo' in data:
            await state.clear()
            await state.set_state(Admin.mailing_text)
            await message.answer('Отправьте пост для рассылки', reply_markup=ReplyKeyboardRemove())
        else:
            await state.clear()
            await state.set_state(Admin.mailing_text_only)
            await message.answer('Отправьте пост для рассылки', reply_markup=ReplyKeyboardRemove())     

@admin_private.callback_query(F.data == 'delete_position')
async def delete_position(callback: CallbackQuery):
    await callback.message.edit_text('Выберите категорию', reply_markup=kb.delete_categories())

@admin_private.callback_query(F.data == 'delete_pizza')
async def delete_pizza(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.number_position)

    # Получение всех позиций из базы данных
    positions = await get_menus('Пицца')
    
    positions_text = '🧾 Существующие позиции:\n\n'
    for idx, position in enumerate(positions, start=1):
        positions_text += f"{position['id']}. {position['name']}, {position['price']}р, {position['weight']}г., {position['energy_valuable']} ккал\n({position['category__name']})\n\n"

    positions_text += '👉 Введите <b>номер блюда</b>, которое хотите удалить'

    await callback.message.answer(positions_text, reply_markup=kb.offer_cancel())

@admin_private.message(Admin.number_position)
async def proccess_name_pizza(message: Message, state: FSMContext):
    user_message = message.text

    # Проверка, не отменил ли пользователь действие
    if user_message.lower() in ['вернуться', 'отмена']:
        await state.clear()
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.delete_categories())
        return

    try:
        # Получение всех позиций из базы данных
        positions = await get_menus('Пицца')
        
        # Преобразование введенного номера в индекс
        position_index = int(user_message) - 1
        if position_index < 0:
            raise ValueError("Некорректный номер позиции")
        
        # Получение позиции по индексу
        position_id = position_index + 1
        
        # Удаление позиции из базы данных
        await delete_menu_item(position_id)

        await message.answer(f'Товар успешно удален', reply_markup=ReplyKeyboardRemove())
    except (ValueError, IndexError):
        await message.answer('Ошибка: Некорректный номер позиции. Попробуйте снова.')

    await state.clear()
    await message.answer('Выберите категорию', reply_markup=kb.delete_categories())


@admin_private.callback_query(F.data == 'delete_desserts')
async def delete_desserts(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.number_position)

    # Получение всех позиций из базы данных
    positions = await get_menus('Десерты')
    
    positions_text = '🧾 Существующие позиции:\n\n'
    for idx, position in enumerate(positions, start=1):
        positions_text += f"{position['id']}. {position['name']}, {position['price']}р, {position['weight']}г., {position['energy_valuable']} ккал\n({position['category__name']})\n\n"

    positions_text += '👉 Введите <b>номер блюда</b>, которое хотите удалить'

    await callback.message.answer(positions_text, reply_markup=kb.offer_cancel())


@admin_private.message(Admin.number_position)
async def proccess_name_desserts(message: Message, state: FSMContext):
    user_message = message.text

    # Проверка, не отменил ли пользователь действие
    if user_message.lower() in ['вернуться', 'отмена']:
        await state.clear()
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.delete_categories())
        return

    try:
        # Получение всех позиций из базы данных
        positions = await get_menus('Десерты')
        
        # Преобразование введенного номера в индекс
        position_index = int(user_message) - 1
        if position_index < 0:
            raise ValueError("Некорректный номер позиции")
        
        # Получение позиции по индексу
        position_id = position_index + 1
        
        # Удаление позиции из базы данных
        await delete_menu_item(position_id)

        await message.answer(f'Товар успешно удален', reply_markup=ReplyKeyboardRemove())
    except (ValueError, IndexError):
        await message.answer('Ошибка: Некорректный номер позиции. Попробуйте снова.')

    await state.clear()
    await message.answer('Выберите категорию', reply_markup=kb.delete_categories())


@admin_private.callback_query(F.data == 'delete_salads')
async def delete_salads(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.number_position)

    # Получение всех позиций из базы данных
    positions = await get_menus("Салаты")
    
    positions_text = '🧾 Существующие позиции:\n\n'
    for idx, position in enumerate(positions, start=1):
        positions_text += f"{position['id']}. {position['name']}, {position['price']}р, {position['weight']}г., {position['energy_valuable']} ккал\n({position['category__name']})\n\n"

    positions_text += '👉 Введите <b>номер блюда</b>, которое хотите удалить'

    await callback.message.answer(positions_text, reply_markup=kb.offer_cancel())


@admin_private.message(Admin.number_position)
async def proccess_name_salads(message: Message, state: FSMContext):
    user_message = message.text

    # Проверка, не отменил ли пользователь действие
    if user_message.lower() in ['вернуться', 'отмена']:
        await state.clear()
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.delete_categories())
        return

    try:
        # Получение всех позиций из базы данных
        positions = await get_menus("Салаты")
        
        # Преобразование введенного номера в индекс
        position_index = int(user_message) - 1
        if position_index < 0:
            raise ValueError("Некорректный номер позиции")
        
        # Получение позиции по индексу
        position_id = position_index + 1
        
        # Удаление позиции из базы данных
        await delete_menu_item(position_id)

        await message.answer(f'Товар успешно удален', reply_markup=ReplyKeyboardRemove())
    except (ValueError, IndexError):
        await message.answer('Ошибка: Некорректный номер позиции. Попробуйте снова.')

    await state.clear()
    await message.answer('Выберите категорию', reply_markup=kb.delete_categories())


@admin_private.callback_query(F.data == 'delete_soups')
async def delete_soups(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.number_position)

    # Получение всех позиций из базы данных
    positions = await get_menus("Супы")
    
    positions_text = '🧾 Существующие позиции:\n\n'
    for idx, position in enumerate(positions, start=1):
        positions_text += f"{position['id']}. {position['name']}, {position['price']}р, {position['weight']}г., {position['energy_valuable']} ккал\n({position['category__name']})\n\n"

    positions_text += '👉 Введите <b>номер блюда</b>, которое хотите удалить'

    await callback.message.answer(positions_text, reply_markup=kb.offer_cancel())


@admin_private.message(Admin.number_position)
async def proccess_name_soups(message: Message, state: FSMContext):
    user_message = message.text

    # Проверка, не отменил ли пользователь действие
    if user_message.lower() in ['вернуться', 'отмена']:
        await state.clear()
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.delete_categories())
        return

    try:
        # Получение всех позиций из базы данных
        positions = await get_menus("Супы")
        
        # Преобразование введенного номера в индекс
        position_index = int(user_message) - 1
        if position_index < 0:
            raise ValueError("Некорректный номер позиции")
        
        # Получение позиции по индексу
        position_id = position_index + 1
        
        # Удаление позиции из базы данных
        await delete_menu_item(position_id)

        await message.answer(f'Товар успешно удален', reply_markup=ReplyKeyboardRemove())
    except (ValueError, IndexError):
        await message.answer('Ошибка: Некорректный номер позиции. Попробуйте снова.')

    await state.clear()
    await message.answer('Выберите категорию', reply_markup=kb.delete_categories())


@admin_private.callback_query(F.data == 'delete_Drinks')
async def delete_Drinks(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.number_position)

    # Получение всех позиций из базы данных
    positions = await get_menus("Напитки")
    
    positions_text = '🧾 Существующие позиции:\n\n'
    for idx, position in enumerate(positions, start=1):
        positions_text += f"{position['id']}. {position['name']}, {position['price']}р, {position['weight']}г., {position['energy_valuable']} ккал\n({position['category__name']})\n\n"

    positions_text += '👉 Введите <b>номер блюда</b>, которое хотите удалить'

    await callback.message.answer(positions_text, reply_markup=kb.offer_cancel())


@admin_private.message(Admin.number_position)
async def proccess_name_Drinks(message: Message, state: FSMContext):
    user_message = message.text

    # Проверка, не отменил ли пользователь действие
    if user_message.lower() in ['вернуться', 'отмена']:
        await state.clear()
        await message.answer('Вы отменили данное действие', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выберите категорию', reply_markup=kb.delete_categories())
        return

    try:
        # Получение всех позиций из базы данных
        positions = await get_menus("Напитки")
        
        # Преобразование введенного номера в индекс
        position_index = int(user_message) - 1
        if position_index < 0:
            raise ValueError("Некорректный номер позиции")
        
        # Получение позиции по индексу
        position_id = position_index + 1
        
        # Удаление позиции из базы данных
        await delete_menu_item(position_id)

        await message.answer(f'Товар успешно удален', reply_markup=ReplyKeyboardRemove())
    except (ValueError, IndexError):
        await message.answer('Ошибка: Некорректный номер позиции. Попробуйте снова.')

    await state.clear()
    await message.answer('Выберите категорию', reply_markup=kb.delete_categories())


@admin_private.callback_query(F.data == 'delete_come_out')
async def delete_come_out(callback: CallbackQuery):
    await callback.message.edit_text('Выберите категорию', reply_markup=kb.admin_panel())
