Create virtual environment.
-> python -m venv .venv

Activate virtual environment.
-> .venv\Scripts\activate

for server run.
-> python manage.py runserver

install django, django rest framework & MySQL.
-> pip install django djangorestframework
-> pip install mysqlclient
-> django-admin startproject project .
-> django-admin startapp customers
-> django-admin startapp orders
-> django-admin startapp products
-> pip install djangorestframework-simplejwt   

Add apps to INSTALLED_APPS in vehicle_system/settings.py:INSTALLED_APPS = [
    ...
    'rest_framework',
    'customer',
    'orders',
    'products',
]

Add this to settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'DB_NAME',
        'USER': 'DB_USER',
        'PASSWORD': 'DB_PASSWORD',
        'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}

after creating model.py
python manage.py makemigrations
python manage.py migrate

for runserver
python manage.py runserver

for APIs testing - Postman

APIs endpoint:
-> For Customers
1. POST /api/customers/ → Create customer
   {
    "name": "",
    "email": "",
    "phone": ""
   }

2. GET /api/customers/ → List customers

3. GET /api/customers/{id}/ → Customer details

4. PUT /api/customers/{id}/ → Update

5. DELETE /api/customers/{id}/ → Delete

-> For Products
1. POST /api/products/ → Create product
Ex.  {
    "name": "samsung tv",
    "price": 80000.45,
    "stock": 3
    }

2. GET /api/products/ → List products

3. PUT /api/products/{id}/ → Update

4. DELETE /api/products/{id}/ → Delete

-> For Order
1. Create Order (With Items)
   POST /api/orders/
Ex.  {
  "customer_id": 1,
  "items": [
    { "product_id": 2, "quantity": 3 },
    { "product_id": 4, "quantity": 1 }
  ]
}

2️. Get Orders List
  GET /api/orders/

3. Get Order Detail
  GET /api/orders/{id}/

4️. Update Order Status
  PATCH /api/orders/{id}/

-> For Login
POST /api/cutomers/login/

after login you have get 2 tokens (access & refresh).
enter access token in authorization with Berear
ex. Berear (access token)
