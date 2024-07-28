# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, OrdersViewSet, PositionViewSet, CategoryViewSet, MenuViewSet, СompoundViewSet, \
    IngredientsViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'orders', OrdersViewSet)
router.register(r'positions', PositionViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'menu', MenuViewSet)
router.register(r'compounds', СompoundViewSet)
router.register(r'ingredients', IngredientsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
