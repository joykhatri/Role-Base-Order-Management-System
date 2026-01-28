from rest_framework import serializers
from .models import Order, OrderItem
from customers.serializers import CustomerSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2)

    class Meta:
        model = OrderItem
        fields = ['quantity', 'product_price', 'product_name']

class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'status', 'items']

    def get_customer(self, obj):
        return {
            "id": obj.customer.id,
            "name": obj.customer.name,
            "email": obj.customer.email
        }

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order