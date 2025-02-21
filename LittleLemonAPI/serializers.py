from rest_framework import serializers
from . import models
from django.contrib.auth.models import User, Group

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']
        depth = 1

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ['title']

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cart
        fields = ['menuitem', 'quantity', 'unit_price']

class CartAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cart
        fields = ['menuitem', 'quantity']
        extra_kwargs = {'quantity': {'min_value': 1}}

class CartRemovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cart
        fields = ['menuitem']

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderItem
        fields = ['order', 'menuitem', 'quantity', 'unit_price', 'price']