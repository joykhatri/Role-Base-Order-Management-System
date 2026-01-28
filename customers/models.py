from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class CustomerManager(BaseUserManager):
    def create_user(self, email, password=None, role="USER", **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        return self.create_user(email, password, role="ADMIN", **extra_fields)

class Customer(AbstractBaseUser):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    role = models.CharField(max_length=10, choices=[
        ('USER', 'User'),
        ('ADMIN', 'Admin')
    ])
    password = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = CustomerManager()

    def __str__(self):
        return self.name