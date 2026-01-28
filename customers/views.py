from rest_framework import viewsets, status, permissions
from .models import Customer
from .serializers import CustomerSerializer, LoginSerializer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and user.role == "ADMIN":
            return Customer.objects.all()
        
        elif user.is_authenticated and user.role == "USER":
            return Customer.objects.filter(id=user.id)
        
        return Customer.objects.none()

    def create(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": True,
                "message": "Customer created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "message": serializer.errors,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)
    
        
    def list(self, request):
        user = request.user

        if not user.is_authenticated:
            return Response({
                "status": False,
                "message": "Authentication credentials were not provided.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)

        if user.role != "ADMIN":
            return Response({
                "status": False,
                "message": "You do not have permission to access this data.",
                "data": None
            }, status=status.HTTP_403_FORBIDDEN)

        # customers = Customer.objects.all()
        customers = self.get_queryset()
        serializer = CustomerSerializer(customers, many=True)
        return Response({
            "status": True,
            "message": "List of customers",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    
    def retrieve(self, request, pk=None):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "status": False,
                "message": "Authentication credentials were not provided.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return Response({
                "status": False,
                "message": f"Customer with id {pk} does not exist",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        
        # USER can only access own record
        if user.role == "USER" and customer.id != user.id:
            return Response({
                "staus": False,
                "message": "You are not allowed to access this data.",
                "data": None
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = CustomerSerializer(customer)
        return Response({
            "status": True,
            "message": "Customer detail is",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    

    def update(self, request, pk=None):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "status": False,
                "message": "Authentication credentials were not provided.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return Response({
                "status": False,
                "message": f"Customer with id {pk} does not exist",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        
        # USER can only update own record
        if user.role == "USER" and customer.id != user.id:
            return Response({
                "success": False,
                "message": "You are not allowed to update this data.",
                "data": None
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        
        if serializer.is_valid():
            updated_data = serializer.validated_data
            has_changes = False
            for field, value in updated_data.items():
                if getattr(customer, field) != value:
                    has_changes = True
                    break

            if not has_changes:
                return Response({
                    "status": True,
                    "message": "No changes detected.",
                    "data": CustomerSerializer(customer).data
                }, status=status.HTTP_200_OK)

            serializer.save()
            return Response({
                "status": True,
                "message": "Customer updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "status": False,
            "message": serializer.errors,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, pk=None):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "status": False,
                "message": "Authentication credentials were not provided.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return Response({
                "status": False,
                "message": f"Customer with id {pk} does not exist",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        
        # USER can only delete own record
        if user.role == "USER" and customer.id != user.id:
            return Response({
                "success": False,
                "message": "You are not allowed to delete this data.",
                "data": None
            }, status=status.HTTP_403_FORBIDDEN)

        customer.delete()
        return Response({
            "success": True,
            "message": "Customer deleted successfully",
            "data": None
        }, status=status.HTTP_204_NO_CONTENT)
    

class LoginViewSet(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            error_messages = []
            for field, errors in serializer.errors.items():
                for error in errors:
                    text = str(error).lower()
                    if "required" in text:
                        error_messages.append(f"{field.replace('_',' ').title()} is required.")
                    elif "blank" in text:
                        error_messages.append(f"{field.replace('_',' ').title()} cannot be empty.")
                    else:
                        error_messages.append(str(error))

            return Response({
                "status": False,
                "message": " ".join(error_messages),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
            
        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")

        try:
            user = Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            return Response({
                "status": False,
                "message": "User not exists.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        if not check_password(password, user.password):
            return Response({
                "status": False,
                "message": "Invalid Password",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
            
        refresh = RefreshToken.for_user(user)

        return Response({
            "status": True,
            "message": "Login Successful",
            "data": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }},
        }, status=status.HTTP_200_OK)