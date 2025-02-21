from django.urls import path
from . import views
urlpatterns = [
    path('categories/', views.CategoryList.as_view(), name = 'category_list'),
    path('menu-items/', views.MenuItemsList.as_view(), name = 'menu_item_list'),
    path('menu-items/<int:pk>/', views.SingleMenuItem.as_view(), name = 'menu_item_detail'),
    path('groups/manager/users/', views.ManagersList.as_view(), name = 'manager_change'),
    path('groups/manager/users/<int:pk>/', views.ManagerDeleteView.as_view(), name = 'manager_delete'),
    path('groups/delivery-crew/users/', views.CrewAssignList.as_view(), name = 'crew_assign'),
    path('groups/delivery-crew/users/<int:pk>/', views.CrewDeleteView.as_view(), name = 'crew_delete'),
    path('cart/menu-items/', views.CartList.as_view(), name = 'cart_alter'),
    path('orders/', views.OrderList.as_view(), name = 'order_alter'),
    path('orders/<int:pk>/', views.OrderDetail.as_view(), name = 'order_detail'),
]