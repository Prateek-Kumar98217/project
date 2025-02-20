from django.urls import path
from . import views
urlpatterns = [
    path('menu-items/', views.menu_item_list, name = 'menu_item_list'),
    path('menu-items/<int:pk>/', views.menu_item_detail, name = 'menu_item_detail'),
    path('groups/manger/users', views.manager_change, name = 'manager_change'),
    path('groups/manager/users/<int:pk>/', views.manager_delete, name = 'manager_delete'),
    path('groups/delivery-crew/users/', views.crew_assign, name = 'crew_assign'),
    path('groups/delivery-crew/users/<int:pk>/', views.crew_delete, name = 'crew_delete'),
    path('cart/menu-items/', views.cart_alter, name = 'cart_alter'),
    path('orders/', views.order_alter, name = 'order_alter'),
    path('orders/<int:pk>/', views.order_detail, name = 'order_detail'),
]