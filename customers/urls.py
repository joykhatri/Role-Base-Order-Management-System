from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet,LoginViewSet
from django.urls import path

router = DefaultRouter()
router.register('', CustomerViewSet)
urlpatterns = [
    path('login/', LoginViewSet.as_view(), name='login')
]

urlpatterns += router.urls