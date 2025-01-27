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
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors


from .models import VolunteerApplication


logo_path ="https://res.cloudinary.com/dplbdop3n/image/upload/v1737955474/logo_l00s7s.png"



smtp_host = "smtp.hostinger.com"
smtp_port = 587  
smtp_user = "support@truehealtheducationfoundation.org"  
smtp_password = "@Support48096"  

def generate_certificate(name, donation_amount):
    buffer = BytesIO()

    # Create a canvas object
    c = canvas.Canvas(buffer, pagesize=A4)

    # Set page dimensions
    width, height = A4

    # Add background color
    c.setFillColor(colors.lightblue)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Add the logo
    if logo_path:
        logo = ImageReader(logo_path)
        c.drawImage(logo, width * 0.1, height * 0.75, width=50, height=50, mask='auto')
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height * 0.8, "True Health Education Foundation")

    # Add a thank-you message title
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height * 0.7, "Thank You for Your Generosity!")

    # Add the main message
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    thank_you_message = (
        "We sincerely appreciate your generous donation to the True Health Education Foundation.\n "
        "Your support helps us in our mission to promote health awareness and education\n\n"
    
    )

    # Split the message into lines for better visibility
    y_position = height * 0.6
    for line in thank_you_message.split("\n"):
        c.drawString(width * 0.1, y_position, line)
        y_position -= 20

    # Add a simple footer
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height * 0.2, "Together, we make the world healthier!")

    # Close the canvas
    c.save()

    # Return the buffer
    buffer.seek(0)
    return buffer

def send_email_with_certificate(name, donation_amount, recipient_email):


    certificate_buffer = generate_certificate(name, donation_amount)

    subject = "Your Certificate of Appreciation"
    body = f"""
    Dear {name},
    
    Thank you for your generous donation of {donation_amount:.2f}.
    Please find your Certificate of Appreciation attached.
    
    Best regards,
    TrueHealthEducationFoundation
    """
    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = recipient_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    attachment = MIMEBase("application", "pdf")
    attachment.set_payload(certificate_buffer.getvalue())
    encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", f"attachment; filename=Certificate_{name}.pdf")
    msg.attach(attachment)

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()  
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, recipient_email, msg.as_string())
        print(f"Email sent successfully to {recipient_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")





razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID , settings.RAZORPAY_SECRET_KEY))


def index(request):
    now = datetime.now()

 
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


def carrer(request):
    if request.method == "POST":
        # Get data from the form
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone_number")
        address =  request.POST.get("address")

        # Save to the VolunteerApplication model

        message = MIMEMultipart()
        message["From"] = smtp_user
        message["To"] = email
        message["Subject"] = "Thank you for joining us as Volunteer"
        body = "Thank you to show us interest in volunteer.We will reach you for verification and after that you will become our volunteer"
        VolunteerApplication.objects.create(
            name=name,
            email=email,
            phone_number=phone,
            address=address,

            is_approved=False  # Default to not approved
        )
        message.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()  # Start TLS encryption
            server.login(smtp_user, smtp_password)  # Log in to the server
            server.sendmail(smtp_user, email, message.as_string())  # Send the email
            print("Email sent successfully!")
        return redirect('index')
    return render(request,"carrer.html")



def contact_us(request):
    return render(request,"contact-us.html")

def about_us(request):
    return render(request,"about-us.html")
def contact_us(request):
    return render(request,"contact-us.html")
def privacy_policy(request):
    return render(request,"privacy-policy.html")
def terms_condition(request):
    return render(request,"terms-condition.html")