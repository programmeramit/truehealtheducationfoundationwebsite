# example/views.py
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.conf import settings
import razorpay


razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID , settings.RAZORPAY_SECRET_KEY))


def index(request):
    now = datetime.now()
    return render(request,"index.html")

def donate(request):
    if request.method == "POST":
        donor_name = request.POST.get('name')
        email = request.POST.get('email')
        amount = float(request.POST.get('amount')) * 100  # Convert to paisa (Razorpay's unit)

        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            "amount": int(amount),  # Amount in paisa
            "currency": "INR",
            "payment_capture": "1"  # Auto-capture
        })

    
        context = {
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'amount': amount,
            'donor_name': donor_name,
            'email': email,
        }
        return render(request, 'payment.html', context)


def payment_success(request,pay_id):
        return redirect('index')
