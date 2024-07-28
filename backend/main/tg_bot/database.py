from asgiref.sync import sync_to_async
from main.models import User, Orders,Admins,Category,Menu,Position,Order_list

import json


@sync_to_async
def n_cooks(order_id):
    order = Orders.objects.get(id=order_id)
    order.notify_cooks = True
    order.save()

    return True

@sync_to_async
def n_pickers(order_id):
    order = Orders.objects.get(id=order_id)
    old_delivered = order.deliveredSucces
    order.notify_pickers = True
    order.save()

    return True

@sync_to_async
def d_success(order_id):
    order = Orders.objects.get(id=order_id)
    old_delivered = order.deliveredSucces
    order.deliveredSucces = True
    order.delivered_notifyed_user = True
    order.paid = True

    order.save()

    # Логика после обновления заказа
    if old_delivered != order.deliveredSucces and order.deliveredSucces:
        Order_list.objects.create(
            tg_id=order.user.tg_id, 
            withOrder=f"🎉 Твой заказ #{order.id} доставлен.\n Надеемся тебе понравится!"
        )

    
        
        order.status = Orders.StatusEnum.RECEIVED
        order.save()
    return True

@sync_to_async
def add_order(tg_id, withOrder):
    Order_list.objects.create(tg_id=tg_id, withOrder=withOrder)
    return True

@sync_to_async
def get_all_orders():
    return list(Order_list.objects.all().values('tg_id', 'withOrder'))
@sync_to_async
def delete_orders(tg_ids):
    # Удаляем записи с указанными tg_id
    Order_list.objects.filter(tg_id__in=tg_ids).delete()
# Users
@sync_to_async
def get_users():

    queryset = User.objects.all().values('tg_id')
    return len(list(queryset))
@sync_to_async
def get_users_status():
    return User.objects.filter(isActive=True).count()

@sync_to_async
def get_users_status2():
    return User.objects.filter(isActive=False).count()

@sync_to_async
def add_phone_number(user_id, phone_number):
    user = User.objects.get(tg_id=user_id)
    user.phone_number = phone_number
    user.save()
    return True
@sync_to_async
def add_user(user_id):
    if not User.objects.filter(tg_id=user_id).exists():
        user = User(tg_id=user_id)
        user.save()
    return True
@sync_to_async
def get_users_post():
    queryset = User.objects.all().values('tg_id')
    return list(queryset)

# Orders


@sync_to_async
def fetch_orders(tg_id, start_idx, end_idx):
    return list(Orders.objects.filter(user__tg_id=tg_id)[start_idx:end_idx])

@sync_to_async
def count_orders(tg_id):
    return Orders.objects.filter(user__tg_id=tg_id).count()

@sync_to_async
def fetch_order_by_id(order_id):
    return list(Orders.objects.filter(id=order_id).values('id', 'date', 'status', 'summa', 'user__tg_id', 'user__isActive', 'user__phone_number'))

@sync_to_async
def get_pos(order_id):
    positions = []
    for pos in  Orders.objects.get(id=order_id).position.all().values('id','name','price'):
        positions.append(pos)
    return positions


# admins



@sync_to_async
def check_admin(user_id):
    if not Admins.objects.filter(tg_id=user_id).exists():
        return False
    return True






# Orders
from datetime import datetime, timedelta
from django.utils import timezone

@sync_to_async
def get_total_orders_count():
    return Orders.objects.count()

@sync_to_async
def get_today_orders_count():
    today = timezone.now().date()
    return Orders.objects.filter(date__date=today).count()

@sync_to_async
def get_week_orders_count():
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    return Orders.objects.filter(date__date__gte=week_start, date__date__lte=today).count()

@sync_to_async
def get_month_orders_count():
    today = timezone.now().date()
    month_start = today.replace(day=1)
    return Orders.objects.filter(date__date__gte=month_start, date__date__lte=today).count()




# Admin menu
@sync_to_async
def get_categories():
    queryset = Category.objects.all().values('name')
    return list(queryset)




@sync_to_async
def get_menus(ftype):
    queryset = Menu.objects.filter(category__name=ftype).all().values('id','name','price','weight','energy_valuable','category__name')
    return list(queryset)


@sync_to_async
def delete_menu_item(menu_id):
    Menu.objects.filter(id=menu_id).delete()



# notify orders

@sync_to_async
def notify_cooks(order_id):
    if Orders.objects.filter(notify_cooksDone=False,id=order_id).exists():
        order = Orders(id=order_id)
        notify_cooks = True
        user.save()
        return True
    return False

@sync_to_async
def notify_pickers(order_id):
    if Orders.objects.filter(notify_pickersDone=False,id=order_id).exists():
        order = Orders(id=order_id)
        notify_pickers = True
        user.save()
        return True
    return False

@sync_to_async
def delivered(order_id):
    if Orders.objects.filter(deliveredDone=False,id=order_id).exists():
        order = Orders(id=order_id)
        delivered = True
        user.save()
        return True
    return False

@sync_to_async
def isCooked(order_id):
    if Orders.objects.filter(notify_cooksDone=True,id=order_id).exists() and Orders.objects.filter(notify_cooks=True,id=order_id).exists() and Orders.objects.filter(cooked=True,id=order_id).exists():
        return True
    return False

@sync_to_async
def isReady(order_id):
    if Orders.objects.filter(notify_pickersDone=True,id=order_id).exists() and Orders.objects.filter(notify_pickers=True,id=order_id).exists() and Orders.objects.filter(ready=True,id=order_id).exists():
        return True
    return False

@sync_to_async
def isDelivered(order_id):
    if Orders.objects.filter(deliveredDone=True,id=order_id).exists() and Orders.objects.filter(delivered=True,id=order_id).exists() and Orders.objects.filter(deliveredSucces=True,id=order_id).exists():
        return True
    return False



#  Создан новый заказ и надо передать в готовку

@sync_to_async
def notify_cooks_for_new_order(order_id):
    if Orders.objects.filter(notify_cooksDone=False,id=order_id).exists():
        order = Orders(id=order_id)
        notify_cooks = True
        order.save()
        return True
    return False

@sync_to_async
def notify_user_about_cooking(order_id):
    if Orders.objects.filter(notify_cooksDone=True,id=order_id).exists() and cooked.objects.filter(cooked=True,id=order_id).exists():
        order = Orders(id=order_id)
        cooking_notifyed_user = True
        order.save()
        return True
    return False

@sync_to_async
def notify_pickers_for_new_order(order_id):
    if Orders.objects.filter(notify_pickersDone=False,id=order_id).exists():
        order = Orders(id=order_id)
        notify_pickers = True
        order.save()
        return True
    return False

@sync_to_async
def notify_user_about_cooking(order_id):
    if Orders.objects.filter(notify_cooksDone=True,id=order_id).exists() and cooked.objects.filter(cooked=True,id=order_id).exists():
        order = Orders(id=order_id)
        cooking_notifyed_user = True
        order.save()
        return True
    return False










@sync_to_async
def create_order(data):
    # Разбираем данные заказа
    order_data = json.loads(data['order_data'])
    address = data['address']
    time_data = data['time_data']
    number = data['number']
    payment = data['payment']
    get_way = data['get_way']

    ingredients_list = []
    compounds_list = []
    order_info = order_data['Order']['info']

    positions = []
    for key, value in order_data['Order'].items():
        if key.startswith('Position'):
            # Получаем ингредиенты
            ingredients = value.get('ingredients', {})
            ingredients_list = [ingredient_value['name'] for ingredient_value in ingredients.values()]
            ingredients_str = ', '.join(ingredients_list)

            # Получаем составы
            compounds = value.get('compounds', {})
            compounds_list = [compound_value['name'] for compound_value in compounds.values()] if compounds else []
            compounds_str = ', '.join(compounds_list)

            position = {
                'name': value['name'],
                'quantity': value.get('quantity', 1),  # Default quantity to 1 if not provided
                'price': value['price'],
                'ingredients': ingredients_str,
                'compounds': compounds_str
            }
            
            positions.append(position)

    # Получаем значения ингредиентов и состава для первой позиции
    ingredients = positions[0]['ingredients'] if positions else ''
    compounds = positions[0]['compounds'] if positions else ''

    # Создаем заказ
    user = User.objects.get(tg_id=data['user_tg_id'])
    order = Orders.objects.create(
        user=user,
        summa=order_info['summa'],
        pay=payment,
        address=address,
        time_date=time_data,
        get_way=get_way,
        number=number,
        status=Orders.StatusEnum.COOKING,
        date=timezone.now(),
        comment=data.get('comment', 'Без комментариев'),
        delivery_info=address,
        promocode=order_info.get('promo', 'Без промокода'),
    )

    # Создаем позиции и ингредиенты
    for position in positions:
        Position.objects.create(
            order=order,
            name=position['name'],
            price=position['price'],
            ingredients=position['ingredients'],
            compounds=position['compounds'],
            quantity=position['quantity']
        )
    order2 = Orders.objects.get(id=order.id)
    order2.notify_cooks = True
    order2.save()
    return True












    