# example/views.py
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.conf import settings
import razorpay
from .models import Donation
from datetime import datetime

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from datetime import date


from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from django.http import JsonResponse
from reportlab.lib.colors import black, Color


from .models import VolunteerApplication


logo_path ="https://res.cloudinary.com/dplbdop3n/image/upload/v1737955474/logo_l00s7s.png"



smtp_host = "smtp.hostinger.com"
smtp_port = 587  
smtp_user = "support@truehealtheducationfoundation.org"  
smtp_password = "@Support48096"  

def generate_certificate(name, donation_amount,email):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Gradient Background - Light Blue to Green
    c.setFillColorRGB(0.5, 0.8, 1)  # Sky Blue at the top
    c.rect(0, height / 2, width, height / 2, fill=1, stroke=0)

    c.setFillColorRGB(0.3, 0.7, 0.3)  # Light Green at the bottom
    c.rect(0, 0, width, height / 2, fill=1, stroke=0)

    # Golden Elegant Border
    c.setStrokeColorRGB(0.9, 0.7, 0.2)  # Gold
    c.setLineWidth(10)
    c.roundRect(30, 30, width - 60, height - 60, 20, stroke=1, fill=0)

    # Inner White Box (Shadow Effect)
    c.setFillColorRGB(1, 1, 1)  # White Box
    c.roundRect(40, 40, width - 80, height - 80, 15, stroke=0, fill=1)

    # Header - Foundation Name & Logo Placeholder
    c.setFont("Helvetica-Bold", 20)
    c.setFillColorRGB(0, 0.5, 0.7)  # Dark Blue
    c.drawCentredString(width / 2, height - 60, " TRUE HEALTH EDUCATION FOUNDATION ")

    c.setFont("Helvetica", 13)
    c.setFillColor(black)
    c.drawCentredString(width / 2, height - 85, "A Non-Profit Organization")
    c.drawCentredString(width / 2, height - 105, "Building a Healthier Future, One Step at a Time")

    # Donor Information
    c.setFont("Helvetica-Bold", 11)
    c.setFillColorRGB(0, 0.4, 0)  # Green
    c.drawString(60, height - 150, f"Received with gratitude from:{name} ")
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    c.drawString(60, height - 170, f"Email:{email}")

    # Payment Details
    c.setFont("Helvetica-Bold", 10)
    c.setFillColorRGB(0.9, 0.3, 0)  # Dark Orange
    today = date.today()
    current_time = datetime.datetime.now()


    c.drawString(400, height - 150, f"Payment Date:{today}")
    c.drawString(400, height - 170, f"Receipt No.: {current_time.year}-HEALTH-12345")

    # Table Header (Styled & Bold)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, height - 230, "S.No")
    c.drawString(160, height - 230, " Contribution Type")
    c.drawString(420, height - 230, "Amount (Rs.)")

    # Table Content
    c.setFont("Helvetica", 10)
    c.drawString(60, height - 250, "1️")
    c.drawString(160, height - 250, "General Donation")
    c.drawString(420, height - 250, donation_amount)

    # Total Amount
    c.setFont("Helvetica-Bold", 11)
    c.setFillColorRGB(0, 0.5, 0)  # Green
    c.drawString(160, height - 280, " Total Amount")
    c.drawString(420, height - 280, donation_amount)

    # Tax Exemption Note
    c.setFont("Helvetica", 9)
    c.setFillColor(black)
    c.drawCentredString(width / 2, height - 310, "Donations to True Health Education Foundation are tax-exempt under Section 80G.")

    # PAN and Registration Info
    c.setFont("Helvetica", 10)
    c.drawString(60, height - 330, " PAN No.: AAABB0123G")
    c.drawString(60, height - 345, " Regn. No.: NGO/456/2020 | Date: 15 May, 2020")

    # Footer
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0.5, 0.2, 0.2)  # Dark Red
    c.drawCentredString(width / 2, height - 370, " This is a system-generated receipt, signature not required.")

    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer

def send_email_with_certificate(name, donation_amount, recipient_email):


    certificate_buffer = generate_certificate(name, donation_amount,recipient_email)

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
    send_email_with_certificate("amit",500,"kamit896837@gmail.com")

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

def admin_dashboard(request):
    # Calculate total, daily, and yearly donations
    total_donations = Donation.objects.aggregate(total=models.Sum('amount'))['total'] or 0
    today_donations = Donation.objects.filter(created_at__date=datetime.today()).aggregate(total=models.Sum('amount'))['total'] or 0
    yearly_donations = Donation.objects.filter(created_at__year=datetime.today().year).aggregate(total=models.Sum('amount'))['total'] or 0
    
    chart_data = {
        'total': total_donations,
        'daily': today_donations,
        'yearly': yearly_donations
    }
    
    return render(request, 'admin/index.html', {'chart_data': chart_data})