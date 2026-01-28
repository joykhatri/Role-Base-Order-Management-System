from rest_framework import serializers
from .models import Product
from decimal import Decimal, InvalidOperation

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'created_at']

    def validate(self, data):
        errors = {}
        if not data.get('name'):
            raise serializers.ValidationError({"name": "Name field is required"})
        # if not data.get('price'):
        #     raise serializers.ValidationError({"price": "Price field is required"})

        price = data.get('price')
        if price in [None, '']:
            errors['price'] = ["Price field is required"]
        else:
            try:
                price_val = Decimal(str(price))
                if price_val <= 0:
                    errors['price'] = ["Ensure this value is greater than or equal to 0."]
            except (InvalidOperation, ValueError):
                errors['price'] = ["Price must be a valid number"]

        if not data.get('stock'):
            raise serializers.ValidationError({"stock": "Stock field is required"})
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data