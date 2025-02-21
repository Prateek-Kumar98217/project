from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from . import models, serializers, permissions
import math
from datetime import date
def permission_instantiate(permission_classes):
    permissions = []
    for perms in permission_classes:
        permissions.append(perms())
    return permissions

class CategoryList(generics.ListCreateAPIView):
    queryset = models.Category.objects.all()
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    serializer_class = serializers.CategorySerializer
    permission_classes = [IsAuthenticated]

class MenuItemsList(generics.ListCreateAPIView):
    queryset = models.MenuItem.objects.all()
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    serializer_class = serializers.MenuSerializer
    search_fields = ['title', 'category__title']
    ordering_fields = ['Category', 'price']

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes =  [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [IsAuthenticated, permissions.IsManager | IsAdminUser]
        return permission_instantiate(permission_classes)

class SingleMenuItem(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.MenuItem.objects.all()
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    serializer_class = serializers.MenuSerializer
    
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method == 'PATCH':
            permission_classes = [IsAuthenticated, permissions.IsManager | IsAdminUser]
        if self.request.method == 'DELETE':
            permission_classes = [IsAuthenticated, IsAdminUser]
        return permission_instantiate(permission_classes)

    def patch(self, request, *args, **kwargs):
        item = models.MenuItem.objects.get(pk = kwargs['pk'])
        item.featured = self.request.data['featured']
        item.save()

        return Response({'message':f'Status of {item.title} changed to {item.featured}'}, status = status.HTTP_200_OK)

class ManagersList(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name = 'Manager')
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated, permissions.IsManager|IsAdminUser]

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        user = get_object_or_404(User, username = username)
        managers = Group.objects.get(name = 'Manager')
        managers.user_set.add(user)

        return Response({'message':f'{username} is now a manager'},status = status.HTTP_201_CREATED)
    
class ManagerDeleteView(generics.DestroyAPIView):
    queryset = User.objects.filter(groups__name = 'Manager')
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated,permissions.IsManager|IsAdminUser]

    def delete(self, request, *args, **kwargs):
        pk =  self.kwargs['pk']
        user = get_object_or_404(User, pk = pk)
        managers = Group.objects.get(name = 'Manager')
        managers.user_set.remove(user)

        return Response({'message':f'{user.username} is no longer a manager'},status = status.HTTP_200_OK)
    
class CrewAssignList(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name = 'Delivery-crew')
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated,permissions.IsManager|IsAdminUser]

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        user = get_object_or_404(User, username = username)
        crew = Group.objects.get(name = 'Delivery-crew')
        crew.user_set.add(user)

        return Response({'message':f'{username} is now a member of the delivery crew'},status = status.HTTP_201_CREATED)

class CrewDeleteView(generics.DestroyAPIView):
    queryset = User.objects.filter(groups__name = 'Delivery-crew')
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated,permissions.IsManager|IsAdminUser]

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk = pk)
        crew = Group.objects.get(name = 'Delivery-crew')
        crew.user_set.remove(user)

        return Response({'message':f'{user.username} is no longer a member of the delivery crew'},status = status.HTTP_200_OK)
    
class CartList(generics.ListCreateAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    serializer_class = serializers.CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return models.Cart.objects.filter(user = self.request.user)

    def post(self, request, *args, **kwargs):
        try:
            serializer = serializers.CartAddSerializer(data = request.data)
            serializer.is_valid(raise_exception = True)
            menuitem = serializer.validated_data['menuitem']
            quantity = serializer.validated_data['quantity']
            unit_price = menuitem.price
            user = request.user

            cart, created = models.Cart.objects.get_or_create(user = user, menuitem = menuitem, defaults = {'quantity': quantity, 'unit_price': unit_price})
            if not created:
                cart.quantity += quantity
                cart.save()

            return Response({'message':'Item added to cart'},status = status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message':str(e)},status = status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        if 'menuitem' in request.data:
            serializer = serializers.CartRemovalSerializer(data = request.data)
            serializer.is_valid(raise_exception = True)
            menuitem = serializer.validated_data['menuitem']
            user = request.user

            cart = get_object_or_404(models.Cart, user = user, menuitem = menuitem)
            cart.delete()

            return Response({'message':'Item removed from cart'},status = status.HTTP_200_OK)
        else:
            models.Cart.objects.filter(user = request.user).delete()
            return Response({'message':'Cart emptied'},status = status.HTTP_200_OK)
        
class OrderList(generics.ListCreateAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    serializer_class = serializers.OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name = 'Manager').exists():
            return models.Order.objects.all()
        elif user.groups.filter(name = 'Delivery-crew').exists():
            return models.Order.objects.filter(delivery_crew = user)
        else:
            return models.Order.objects.filter(user = user)
        
    def get_permissions(self):
        if self.request.method in ['GET', 'POST']:
            permission_classes=[IsAuthenticated]
        else:
            permission_classes=[IsAuthenticated, permissions.IsManager|IsAdminUser]
        return permission_instantiate(permission_classes)

    def post(self, request, *args, **kwargs):
        cart = models.Cart.objects.filter(user = request.user)
        values = cart.values_list()

        if len(values) == 0:
            return Response({'message':'Cart is empty'},status = status.HTTP_400_BAD_REQUEST)
        
        total = math.fsum([float(value[-1]) for value in values])
        order = models.Order.objects.create(user = request.user, total = total, date = date.today())

        for i in cart.values():
            item = get_object_or_404(models.MenuItem, id = i['menuitem_id'])
            orderitem =  models.OrderItem.objects.create(order = order, menuitem = item, quantity = i['quantity'])
            orderitem.save()
        cart.delete()

        return Response({'message':'Order placed'},status = status.HTTP_201_CREATED)

class OrderDetail(generics.RetrieveUpdateDestroyAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    serializer_class = serializers.OrderSerializer

    def get_permissions(self):
        user = self.request.user
        method = self.request.method
        order = get_object_or_404(models.Order, pk = self.kwargs['pk'])
        if user == order.user and method == 'GET':
            return permission_instantiate([IsAuthenticated])
        elif method == 'PUT' or method == 'DELETE':
            permission_classes=[IsAuthenticated, permissions.IsManager|IsAdminUser]
        else:
            permission_classes=[IsAuthenticated, permissions.IsCrew|permissions.IsManager|IsAdminUser]
        return permission_instantiate(permission_classes)

    def get_queryset(self):
        return models.Order.objects.filter(pk = self.kwargs['pk'])

    def patch(self, request, *args, **kwargs):
        if 'status' in request.data:
            return self.update_status(request, *args, **kwargs)
        return self.assign_crew(request, *args, **kwargs)
    
    def update_status(self, request, *args, **kwargs):
        order = get_object_or_404(models.Order, pk=kwargs['pk'])
        order.status = not order.status
        order.save()
        return Response(
            {'message': f'Status of order {order.id} changed to {order.status}'},
            status=status.HTTP_200_OK
        )
    
    def assign_crew(self, request, *args, **kwargs):
        item = serializers.OrderItemSerializer(data=request.data)
        item.is_valid(raise_exception=True)
        order = get_object_or_404(models.Order, pk=self.kwargs['pk'])
        crew = get_object_or_404(User, pk=item.validated_data['delivery_crew'])
        order.delivery_crew = crew
        order.save()
        return Response(
            {'message': f'{crew.username} assigned to order {order.id}'},
            status=status.HTTP_200_OK
        )
    def delete(self, request, *args, **kwargs):
        order = get_object_or_404(models.Order, pk = self.kwargs['pk'])
        order.delete()

        return Response({'message':f'Order {order.id} deleted'},status = status.HTTP_200_OK)