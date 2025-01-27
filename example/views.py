# example/views.py
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.conf import settings
import razorpay
from .models import Donation

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders



from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_certificate(name, donation_amount):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(150, 750, "Certificate of Appreciation")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 700, f"Presented to: {name}")
    pdf.drawString(100, 680, f"For your generous donation of: ${donation_amount:.2f}")
    pdf.drawString(100, 660, "Your support means a lot to us!")
    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer

def send_email_with_certificate(name, donation_amount, recipient_email):
    # Hostinger SMTP server configuration
    smtp_host = "smtp.hostinger.com"
    smtp_port = 587  # Use TLS
    smtp_user = "support@truehealtheducationfoundation.org"  # Your Hostinger email
    smtp_password = "@Support48096"   # Your Hostinger email password

    # Generate the certificate in memory
    certificate_buffer = generate_certificate(name, donation_amount)

    # Create the email
    subject = "Your Certificate of Appreciation"
    body = f"""
    Dear {name},
    
    Thank you for your generous donation of ${donation_amount:.2f}.
    Please find your Certificate of Appreciation attached.
    
    Best regards,
    [Your Organization's Name]
    """
    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = recipient_email
    msg["Subject"] = subject

    # Attach the email body
    msg.attach(MIMEText(body, "plain"))

    # Attach the certificate
    attachment = MIMEBase("application", "pdf")
    attachment.set_payload(certificate_buffer.getvalue())
    encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", f"attachment; filename=Certificate_{name}.pdf")
    msg.attach(attachment)

    # Send the email using Hostinger's SMTP server
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, recipient_email, msg.as_string())
        print(f"Email sent successfully to {recipient_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")





razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID , settings.RAZORPAY_SECRET_KEY))


def index(request):
    now = datetime.now()
    send_email_with_certificate("amit",200,"kamit896837@gmail.com")
 
    return render(request,"index.html")
def donate(request):
    if request.method == "POST":
        donor_name = request.POST.get('name')
        email = request.POST.get('email')
        amount = float(request.POST.get('amount')) * 100  
        message = request.POST.get("message")

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
            message=message,
            razorpay_payment_id=pay_id
        )

        # Redirect to a success page
        send_email_with_certificate(donor_name,amount,email)
        return redirect('index')
    except Exception as e:
        # Handle errors (e.g., payment ID not found or API issues)
        return HttpResponse(f"Error: {str(e)}")
