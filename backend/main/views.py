from rest_framework import viewsets
from .models import User, Orders, Position, Category, Menu, Сompound, Ingredients,Order_list
from .serializers import UserSerializer, OrdersSerializer, PositionSerializer, CategorySerializer, MenuSerializer, \
    СompoundSerializer, IngredientsSerializer
from main.tg_bot.user_private import *
from main.tg_bot.database import *


from django.utils import timezone
from asgiref.sync import sync_to_async


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class OrdersViewSet(viewsets.ModelViewSet):
    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_cooked = instance.cooked
        old_ready = instance.ready
        old_delivered = instance.deliveredSucces

        # Обновляем заказ
        response = super().update(request, *args, **kwargs)

        # Получаем обновленный экземпляр
        instance.refresh_from_db()

        # Проверяем изменения полей
        if old_cooked != instance.cooked and instance.cooked:
            Order_list.objects.create(tg_id=instance.user.tg_id, withOrder=f"‍🍳 Твой заказ #{instance.id} уже приготовлен")
            order3 = Orders.objects.get(id=instance.id)
            order3.cooking_notifyed_user = True
            order3.notify_pickers = True
            order3.save()
        if old_ready != instance.ready and instance.ready:
            Order_list.objects.create(tg_id=instance.user.tg_id, withOrder=f"📦 Твой заказ #{instance.id} уже собран")
            if instance.get_way =="Доставка":
                Order_list.objects.create(tg_id=-4272922175, withOrder=f"""Заказ #{instance.id}\n📍 Адрес: {instance.address}\n🕒 Дата и время доставки: {instance.time_date}\n📞 Телефон клиента: {instance.number}""")
                order2 = Orders.objects.get(id=instance.id)
                order2.status = Orders.StatusEnum.DELIVERY
                order2.picking_notifyed_user = True
                order2.save()
            else:
                Order_list.objects.create(tg_id=instance.user.tg_id, withOrder=f"""Можешь забрать свой заказ #{instance.id}. Адрес: г. Рязань, Ул. Кутузова д. 15""")
                order = Orders.objects.get(id=order_id)
                order.deliveredSucces = True
                order.delivered_notifyed_user = True
                order.save()


        return response


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer


class СompoundViewSet(viewsets.ModelViewSet):
    queryset = Сompound.objects.all()
    serializer_class = СompoundSerializer


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
