# example/views.py
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.conf import settings
import razorpay
from .models import Donation



razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID , settings.RAZORPAY_SECRET_KEY))


def index(request):
    now = datetime.now()
    return render(request,"index.html")
def donate(request):
    if request.method == "POST":
        donor_name = request.POST.get('name')
        email = request.POST.get('email')
        amount = float(request.POST.get('amount')) * 100  # Convert to paisa (Razorpay's unit)
        message = request.POST.get("message")

        # Create Razorpay order with additional notes
        razorpay_order = razorpay_client.order.create({
            "amount": int(amount),  # Amount in paisa
            "currency": "INR",
            "payment_capture": "1",  # Auto-capture
            "notes": {
                "donor_name": donor_name,
                "email": email,
                "message":message
            }
        })

        context = {
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'amount': amount,
            'donor_name': donor_name,
            'email': email,
            "message":message
        }
        return render(request, 'payment.html', context)


def payment_success(request, pay_id):
    try:
        # Fetch payment details from Razorpay
        payment_details = razorpay_client.payment.fetch(pay_id)

        # Extract relevant data from the payment
        donor_name = payment_details.get('notes', {}).get('donor_name', 'Anonymous')
        email = payment_details.get('notes', {}).get('email', 'N/A')
        amount = int(payment_details.get('amount')) / 100  # Convert back to rupees
        message = payment_details.get('notes', {}).get('message', '')  # Get the message

        # Save the donation details to the database
        Donation.objects.create(
            name=donor_name,
            email=email,
            amount=amount,
            message=message
        )

        # Redirect to a success page
        return redirect('index')
    except Exception as e:
        # Handle errors (e.g., payment ID not found or API issues)
        return HttpResponse(f"Error: {str(e)}")
