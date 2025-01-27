# example/urls.py
from django.urls import path

from example.views import index,donate,payment_success,carrer


urlpatterns = [
    path('', index,name="index"),
    path('donate/',donate,name="donate"),
    path('payment-success/<str:pay_id>', payment_success, name='payment_success'),
    path('carrer/',carrer,name="carrer")
]