from django.db import models
from django.utils.translation import gettext_lazy as _


class User(models.Model):
    tg_id = models.BigIntegerField('Telegram ID')
    isActive = models.BooleanField('Активен', default=False)
    phone_number = models.CharField('Номер телефона', max_length=200, default="Неизвестно")

    list_per_page = 500

    def __str__(self):
        return str(self.tg_id)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Orders(models.Model):
    class StatusEnum(models.TextChoices):
        COOKING = 'CK', _('Cooking')
        DELIVERY = 'DL', _('Delivery')
        RECEIVED = 'RC', _('Received')

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    summa = models.CharField('Итого', max_length=200)
    paid = models.BooleanField('Оплачен', default=False)
    address = models.TextField('Адрес клиента', default="Без адреса", blank=True)
    pay = models.CharField('Способ оплаты', max_length=250)
    get_way = models.CharField('Способ получения', max_length=250)
    time_date = models.CharField('Время доставки', max_length=300,default="Самовывоз")
    number = models.CharField('Номер телефона', max_length=250)
    status = models.CharField('Статус', choices=StatusEnum.choices, default=StatusEnum.COOKING, max_length=250)
    date = models.DateTimeField('Дата текущей позиции')
    comment = models.TextField('Комментарий', default="Без комментариев", blank=True)
    delivery_info = models.CharField('Информация о доставке', max_length=350, default="Без информации", blank=True)
    promocode = models.CharField('Промокод', max_length=200, default="Без промокода", blank=True)
    notify_cooks = models.BooleanField('Оповещение поваров', default=False)
    notify_pickers = models.BooleanField('Оповещение сборщиков', default=False)
    notify_cooksDone = models.BooleanField('Оповещение поваров 2', default=False)
    notify_pickersDone = models.BooleanField('Оповещение сборщиков 2', default=False)

    cooked = models.BooleanField('Приготовлен', default=False)
    ready = models.BooleanField('Собран', default=False)
    deliveredSucces = models.BooleanField('Доставлен', default=False)
    
    cooking_notifyed_user = models.BooleanField('Оповещение пользователя о готовке заказа', default=False)
    picking_notifyed_user = models.BooleanField('Оповещение пользователя о сборке', default=False)
    delivered_notifyed_user = models.BooleanField('Оповещение пользователя о доставке', default=False)

    list_per_page = 100

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class Position(models.Model):
    order = models.ForeignKey(Orders, related_name='position', on_delete=models.CASCADE)
    name = models.CharField('Имя', max_length=100)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    ingredients = models.TextField('Ингридиенты')
    compounds = models.TextField('Долонительное', default='null')

    quantity = models.BigIntegerField()

    list_per_page = 500

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Позиция'
        verbose_name_plural = 'Позиции'


class Category(models.Model):
    name = models.CharField('Имя категории', max_length=100)
    list_per_page = 500

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Катергории'


class Menu(models.Model):
    photo = models.ImageField('Фото', upload_to='static/media/menu_photos/')
    name = models.CharField('Имя', max_length=250)
    weight = models.CharField('Вес в граммах', max_length=250)
    allergens = models.TextField('Аллергены', default="Без аллергенов")
    energy_valuable = models.CharField('Энерг. ценность', max_length=100)
    compounds = models.TextField('Список блюд', default="Ингединты")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    list_per_page = 100

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Меню'
        verbose_name_plural = 'Меню'


class Сompound(models.Model):
    photo = models.ImageField('Фото', upload_to='static/media/compound_photos/')
    name = models.CharField('Имя', max_length=250)
    weight = models.CharField('Вес в граммах', max_length=250)
    quantity = models.CharField('Количество', max_length=250)
    dish = models.ForeignKey(Menu, on_delete=models.CASCADE, default=1)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    list_per_page = 500

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Дополнительное'
        verbose_name_plural = 'Дополнительные'


class Ingredients(models.Model):
    name = models.CharField('Имя', max_length=250)
    dish = models.ForeignKey(Menu, on_delete=models.CASCADE, default=1)
    isInDish = models.BooleanField(default=True)
    list_per_page = 500

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Admins(models.Model):
    tg_id = models.BigIntegerField('Админы')
    list_per_page = 500

    def __str__(self):
        return str(self.tg_id)

    class Meta:
        verbose_name = 'Админ'
        verbose_name_plural = 'Админы'


class Couriers(models.Model):
    tg_id = models.BigIntegerField('Курьеры')
    withOrder = models.BooleanField('С заказом')
    list_per_page = 500

    def __str__(self):
        return str(self.tg_id)

    class Meta:
        verbose_name = 'Курьер'
        verbose_name_plural = 'Курьеры'
class Order_list(models.Model):
    tg_id = models.BigIntegerField('User iId')
    withOrder = models.TextField('Текст')

    def __str__(self):
        return str(self.tg_id)

    class Meta:
        verbose_name = 'список заказов'
        verbose_name_plural = 'списки заказов'
