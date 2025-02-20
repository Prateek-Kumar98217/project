from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from .models import Category, MenuItem, Cart, Order, OrderItem
# Create your views here.
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def menu_item_list(request):
    if request.user.groups.filter('Manager').exists():
        if request.method == 'GET':
            items = MenuItem.objects.all()
            return Response(items)
        else:
            title = request.data.get('title')
            price = request.data.get('price')
            featured = request.data.get('featured')
            category = request.data.get('category')
            category = Category.objects.get(pk = category)
            item = MenuItem(title = title, price = price, featured = featured, category = category)
            item.save()
            return Response("Item added to the menu", status = status.HTTP_201_CREATED)
    else:
        if request.method == 'GET':
            items = MenuItem.objects.all();
            paginator = Paginator(items, 10)
            page = request.GET.get('page')
            try:
                items = paginator.page(page)
            except EmptyPage:
                items = []
            return Response(items, status = status.HTTP_200_OK)
        else:
            return Response("You are not authorized.", status = status.HTTP_401_UNAUTHORIZED)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def menu_item_detail(request, pk):
    if request.user.groups.filter(name ='Manager').exits():
        item = get_object_or_404(MenuItem, pk = pk)
        if request.method == 'GET':
            return Response(item)
        elif request.method == 'PUT':
            title = request.data.get('title')
            price = request.data.get('price')
            featured = request.data.get('featured')
            category = request.data.get('category')
            category = Category.objects.get(pk = category)
            item.title = title
            item.price = price
            item.featured = featured
            item.category = category
            item.save()
            return Response("Item updated", status = status.HTTP_200_OK)
        elif request.method == 'PATCH':
            title = request.data.get('title')
            price = request.data.get('price')
            featured = request.data.get('featured')
            category = request.data.get('category')
            category = Category.objects.get(pk = category)
            if title:
                item.title = title
            if price:
                item.price = price
            if featured:
                item.featured = featured
            if category:
                item.category = category
            item.save()
            return Response("Item updated", status = status.HTTP_200_OK)
        else:
            item.delete()
            return Response("Item deleted", status = status.HTTP_200_OK)
    else:
        return Response("You are not authorized.", status = status.HTTP_401_UNAUTHORIZED)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def manager_change(request):
    if request.user.groups.filter(name = 'Manager').exists():
        if request.method == 'GET':
            managers = Group.objects.get(name = 'Manager').user_set.all()
            return Response(managers)
        else:
            user = User.objects.get(pk = request.data.get('user'))
            user.groups.add(Group.objects.get(name = 'Manager'))
            return Response("User added to managers", status = status.HTTP_201_CREATED)
    else:
        return Response("You are not authorized.", status = status.HTTP_401_UNAUTHORIZED)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def manager_delete(request, pk):
    if request.user.groups.filter(name = 'Manager').exists():
        user = get_object_or_404(User, pk = pk)
        user.groups.remove(Group.objects.get(name = 'Manager'))
        return Response("User removed from managers", status = status.HTTP_200_OK)
    else:
        return Response("You are not authorized.", status = status.HTTP_401_UNAUTHORIZED)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def crew_assign(request):
    if request.user.groups.filter(name = 'Manager').exists():
        if request.method == 'GET':
            crew = Group.objects.get(name = 'Delivery-crew').user_set.all()
            return Response(crew)
        else:
            user = User.objects.get(pk = request.data.get('user'))
            user.groups.add(Group.objects.get(name = 'Delivery-crew'))
            return Response("User added to delivery crew", status = status.HTTP_201_CREATED)
    else:
        return Response("You are not authorized.", status = status.HTTP_401_UNAUTHORIZED)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def crew_delete(request, pk):
    if request.user.groups.filter(name = 'Manager').exists():
        user = get_object_or_404(User, pk = pk)
        user.groups.remove(Group.objects.get(name = 'Delivery-crew'))
        return Response("User removed from delivery crew", status = status.HTTP_200_OK)
    else:
        return Response("You are not authorized.", status = status.HTTP_401_UNAUTHORIZED)
    
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def cart_alter(request):
    if request.method == 'GET':
        cart = Cart.objects.filter(user = request.user)
        return Response(cart)
    elif request.method == 'POST':
        item = MenuItem.objects.get(pk = request.data.get('item'))
        quantity = request.data.get('quantity')
        unit_price = item.price
        cart = Cart(user = request.user, menuitem = item, quantity = quantity, unit_price = unit_price)
        cart.save()
        return Response("Item added to cart", status = status.HTTP_201_CREATED)
    else:
        cart = Cart.objects.filter(user = request.user)
        cart.delete()
        return Response("Cart cleared", status = status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def order_alter(request):
    if request.user.groups.filter(name = "Manager").exists():
        if request.method == 'GET':
            orders = Order.objects.all()
            return Response(orders)
    if request.user.groups.filter(name = "Delivery-crew").exists():
        if request.method == 'GET':
            orders = Order.objects.filter(delivery_crew = request.user)
            return Response(orders)
    else:
        if request.method == 'GET':
            items = Order.objects.filter(user = request.user)
            return Response(items)
        else:
            user = request.user
            cart = Cart.objects.filter(user = user)
            order = Order(user=user)  # You need to create the order first
            order.save()
            for cart_item in cart:
                order_item = OrderItem(order=order, menuitem=cart_item.menuitem, quantity=cart_item.quantity, unit_price=cart_item.unit_price)
                order_item.save()
            cart.delete()
            return Response("Order placed", status = status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def order_detail(request, pk):
    pass