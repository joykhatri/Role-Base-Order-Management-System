from rest_framework import viewsets, status
from .models import Order, OrderItem
from customers.models import Customer
from products.models import Product
from .serializers import OrderSerializer
from rest_framework.response import Response
from django.db import transaction

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and user.role == "ADMIN":
            return Order.objects.all()
        elif user.is_authenticated and user.role == "USER":
            return Order.objects.filter(id=user.id)
        return Order.objects.none()

    def create(self, request):
        # Extract customer ID and items from request data
        customer_id = request.data.get('customer_id')
        items_data = request.data.get('items', [])

        if not customer_id or not items_data:
            return Response({
                "status": False,
                "message": "Customer ID or items are required.",
                "data": None}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the customer
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({
                "status": False,
                "message": "Customer not found.",
                "data": None}, status=status.HTTP_404_NOT_FOUND)

        order_items = []

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    customer=customer,
                    status='PENDING'
                )

                for item in items_data:
                    product_id = item.get('product_id')
                    quantity = item.get('quantity')

                    if not product_id or not quantity:
                        return Response({
                            "status": False,
                            "message": "Product ID and quantity are required for each item.",
                            "data": None}, status=status.HTTP_400_BAD_REQUEST)

                    try:
                        product = Product.objects.get(id=product_id)
                    except Product.DoesNotExist:
                        return Response({
                            "status": False,
                            "message": f"Product with ID {product_id} not found.",
                            "data": None
                            }, status=status.HTTP_404_NOT_FOUND)

                    # Check if there's enough stock
                    if product.stock < quantity:
                        return Response(
                            {"status": False,
                            "message": f"Not enough stock for {product.name}. Available: {product.stock}.",
                            "data": None},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    # Create the order item
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price
                    )

                    # Reduce the product stock
                    product.stock -= quantity
                    product.save()

                    order_items.append(order_item)

                order_serializer = OrderSerializer(order)

            return Response({"status": True,
                             "message": "Order create successfully",
                "data":order_serializer.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"status": False,
                "message": str(e),
                "data": None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


    def list(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "status": False,
                "message": "Authentication credentials were not provided",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        if user.role != "ADMIN":
            return Response({
                "status": False,
                "message": "You do not have permission",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        orders = Order.objects.select_related('customer').prefetch_related('items__product')

        serializer = self.get_serializer(orders, many=True)

        return Response({
            "status": True,
            "message": "Order list",
            "data":serializer.data}, status=status.HTTP_200_OK)


    def retrieve(self, request, pk=None):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "status": False,
                "message": "Authentication credentials were not provided",
                "data": False
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            order = Order.objects.select_related('customer').prefetch_related('items__product').get(pk=pk)
        except Order.DoesNotExist:
            return Response({
                "status": False,
                "messagae": "No order found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        
        if user.role == "USER" and order.customer != user:
                return Response({
                    "staus": False,
                    "message": "You are not allowed to access this data.",
                    "data": None
                }, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(order)

        return Response({"status": True,
                        "messagae": "Order details",
                        "data": serializer.data}, status=status.HTTP_200_OK)



    def partial_update(self, request, *args, **kwargs):
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
                "message": "You do not have permission to access.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            order = Order.objects.get(pk=kwargs['pk'])
        except Order.DoesNotExist:
            return Response({
                "status": False,
                "message": f"Order with id {kwargs['pk']} does not exist",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')

        if new_status is None:
            return Response({
                "status": False,
                "message": "Status field is required.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        if new_status == "":
            return Response({
                "status": False,
                "message": "Status cannot be empty.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        allowed_statuses = ['PENDING', 'COMPLETED', 'CANCELLED']
        if new_status not in allowed_statuses:
            return Response({
                "status": False,
                "message": f"Invalid status.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        if order.status == new_status:
            return Response({
                "status": True,
                "message": f"The order is already in {new_status} status.",
                "data": None
            }, status=status.HTTP_200_OK)

        order.status = new_status
        order.save()

        serializer = self.get_serializer(order)
        return Response({
            "status": True,
            "message": "Order updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.instance.save()
