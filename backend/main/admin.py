
from django.contrib import admin
from .models import (User,Menu,Orders,Category,Position,Сompound,Admins,Ingredients,Couriers,Order_list)
from django.contrib.auth.models import Group

admin.site.unregister(Group)

admin.site.register(User)
admin.site.register(Menu)
admin.site.register(Orders)
admin.site.register(Category)
admin.site.register(Position)
admin.site.register(Сompound)
admin.site.register(Admins)
admin.site.register(Ingredients)
admin.site.register(Couriers)
admin.site.register(Order_list)





