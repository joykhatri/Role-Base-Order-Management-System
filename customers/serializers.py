# from rest_framework import serializers
# from .models import Customer

# class CustomerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Customer
#         fields = ['id', 'name', 'email', 'phone', 'created_at']

#     def validate_phone(self, value):
#         if not value:
#             raise serializers.ValidationError("Phone number is required.")
#         digits = ''.join(filter(str.isdigit, value))
#         if len(digits) < 10:
#             raise serializers.ValidationError("Phone number must be at least 10 digits")
#         if digits.startswith('-'):
#             raise serializers.ValidationError("Phone number cannot be negative.")
#         if Customer.objects.filter(phone=digits).exists():
#             raise serializers.ValidationError("Phone number is already in use.")
#         return digits
    
    
#     def validate(self, data):
#         if not data.get('name'):
#             raise serializers.ValidationError({"name": "Name field is required"})
#         if not data.get('email'):
#             raise serializers.ValidationError({"email": "Email field is required"})
#         if not data.get('phone'):
#             raise serializers.ValidationError({"phone": "Phone field is required"})
#         return data


from rest_framework import serializers
from .models import Customer
from django.contrib.auth.hashers import make_password

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone', 'role', 'password', 'created_at']
        extra_kwargs = {'password' : {'write_only': True}}

    def validate_phone(self, value):
        digits = ''.join(filter(str.isdigit, value))
        if len(digits) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits")

        customer_id = self.instance.id if self.instance else None
        if Customer.objects.exclude(id=customer_id).filter(phone=digits).exists():
            raise serializers.ValidationError("Phone number is already in use.")
        return digits

    def validate_email(self, value):
        customer_id = self.instance.id if self.instance else None
        if Customer.objects.exclude(id=customer_id).filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value

    def validate(self, data):
        if self.instance is None:
            required_fields = ['name', 'email', 'phone']
            errors = {}
            for field in required_fields:
                if not data.get(field):
                    errors[field] = [f"{field.capitalize()} is required"]
            if errors:
                raise serializers.ValidationError(errors)
        return data

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.password = make_password(validated_data['password'])
            validated_data.pop('password')
        return super().update(instance, validated_data)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, error_messages={"required": "Email is required"})
    password = serializers.CharField(write_only=True, required=True, error_messages={"required": "Password is required"})