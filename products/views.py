from rest_framework import viewsets, status, permissions
from .models import Product
from .serializers import ProductSerializer
from rest_framework.response import Response

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and user.role == "ADMIN":
            return Product.objects.all()
        
        elif user.is_authenticated and user.role == "USER":
            return Product.objects.filter(id=user.id)
        
        return Product.objects.none()

    def create(self, request):
        user = request.user
        if user.role != "ADMIN":
            return Response({
                "status": False,
                "message": "You do not have permission to Create Products.",
                "data": None
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": True,
                "message": "Product created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": False,
            "message": serializer.errors,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)
        
    def list(self, request):
        product = Product.objects.all()
        serializer = ProductSerializer(product, many=True)
        return Response({
            "status": True,
            "message": "List of products are",
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
        if user.role != "ADMIN":
            return Response({
                "status": False,
                "message": "You do not have permission to update product",
                "data": None
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({
                "status": False,
                "message": f"Product with id {pk} does not exist",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            updated_data = serializer.validated_data
            has_changes = any(getattr(product, field) != value for field, value in updated_data.items())
            if not has_changes:
                return Response({
                    "status": True,
                    "message": "No changes detected.",
                    "data": ProductSerializer(product).data
                }, status=status.HTTP_200_OK)

            serializer.save()
            return Response({
                "status": True,
                "message": "Product updated successfully",
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
        if user.role != "ADMIN":
            return Response({
                "status": False,
                "message": "You do not have permission to delete product.",
                "data": None
            })
        
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({
                "status": False,
                "message": f"Product with id {pk} does not exist",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        
        product.delete()
        return Response({
            "status": True,
            "message": "Product deleted successfully",
            "data": None
        })