# example/urls.py
from django.urls import path

from example.views import index,donate,payment_success,carrer,about_us,contact_us,privacy_policy,terms_condition,dashboard_callback


urlpatterns = [
    path('', index,name="index"),
    path('donate/',donate,name="donate"),
    path('payment-success/<str:pay_id>', payment_success, name='payment_success'),
    path('carrer/',carrer,name="carrer"),
    path('about-us',about_us,name="about-us"),
    path('contact-us',contact_us,name="contact-us"),
    path('privacy-policy',privacy_policy,name="privacy-policy"),
    path("terms-condition",terms_condition,name="terms-condition"),

]