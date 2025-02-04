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

from datetime import date, datetime

from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from datetime import date

from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet


from .models import VolunteerApplication


logo_path ="https://res.cloudinary.com/dplbdop3n/image/upload/v1737955474/logo_l00s7s.png"



smtp_host = "smtp.hostinger.com"
smtp_port = 587  
smtp_user = "support@truehealtheducationfoundation.org"  
smtp_password = "@Support48096"  


def generate_certificate(name, donation_amount, email, pay_id, logo_path=logo_path):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    width, height = letter

    # Background Color
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFillColorRGB(200/255, 162/255, 200/255)  # Soft Lavender
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Gold Elegant Border
    c.setStrokeColorRGB(0.85, 0.65, 0.13)  # Gold
    c.setLineWidth(12)
    c.roundRect(25, 25, width - 50, height - 50, 15, stroke=1, fill=0)

    c.showPage()
    c.save()

    # Add Logo
    try:
        logo = Image(logo_path, width=100, height=100)  # Adjust logo size
        logo.hAlign = 'CENTER'
        elements.append(logo)
    except Exception as e:
        print(f"Error loading logo: {e}")

    # Receipt Date & Number
    today = date.today().strftime('%d %b %Y')
    receipt_number = f"{today[-4:]}-HEALTH-{pay_id[-3:]}"  # Year + Last 3 digits of pay_id

    # Header
    header = [
        ["TRUE HEALTH EDUCATION FOUNDATION"],
        ["A Non-Profit Organization"],
        ["Building a Healthier Future, One Step at a Time"]
    ]
    header_table = Table(header, colWidths=[450])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 18),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (1, 1), (-1, -1), 12),
        ('TEXTCOLOR', (1, 1), (-1, -1), colors.black),
    ]))
    elements.append(header_table)

    # Donor & Payment Details
    donor_details = [
        ["Received with gratitude from:", f"{name}"],
        ["Email:", email],
        ["Payment Date:", today],
        ["Receipt No.:", receipt_number]
    ]
    donor_table = Table(donor_details, colWidths=[180, 300])
    donor_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(donor_table)

    # Spacer
    elements.append(Paragraph("<br/><br/>", styles["Normal"]))

    # Styled Table for Donations
    data = [
        ["S.No", "Contribution Type", "Amount (Rs.)"],
        ["1", "General Donation", f"Rs {donation_amount:,.2f}"],  # ₹ Format
        ["", "Total Amount", f"Rs {donation_amount:,.2f}"]
    ]

    table = Table(data, colWidths=[60, 300, 100])
    table.setStyle(TableStyle([ 
        ('BACKGROUND', (0, 0), (-1, 0), colors.gold),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, 1), colors.whitesmoke),
        ('BACKGROUND', (0, 2), (-1, 2), colors.beige),
    ]))
    elements.append(table)

    # Spacer
    elements.append(Paragraph("<br/><br/>", styles["Normal"]))

    # Tax Exemption Notice
    tax_info = Paragraph(
        "<b>Donations to True Health Education Foundation are tax-exempt under Section 80G.</b>",
        styles["Normal"]
    )
    elements.append(tax_info)

    # PAN & Registration
    reg_info = [
        ["PAN No.:", "AALCT2406R"],
        ["Regn. No.:", "NGO/456/2020 | Date: 30 Aug, 2024"]
    ]
    reg_table = Table(reg_info, colWidths=[150, 300])
    reg_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(reg_table)

    # Footer
    footer = Paragraph(
        "<b><font color='#800000'>This is a system-generated receipt, signature not required.</font></b>",
        styles["Normal"]
    )
    elements.append(footer)

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def send_email_with_certificate(name, donation_amount, recipient_email,pay_id):


    certificate_buffer = generate_certificate(name, donation_amount,recipient_email,pay_id)

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
        send_email_with_certificate(donor_name,amount,email,pay_id)
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



from django.db.models import Sum
from django.utils.timezone import now, localdate
from .models import Donation

def dashboard_callback(request, context):
    # Aggregate data
    total_donations = Donation.objects.aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    total_donations_today = Donation.objects.filter(created_at=localdate()).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    total_donations_year = Donation.objects.filter(created_at__year=now().year).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

    # Prepare chart data
    chart_data = {
        'labels': ["Total Donations", "Today's Donations", "This Year's Donations"],
        'datasets': [{
            'label': 'Donation Amount',
            'data': [total_donations, total_donations_today, total_donations_year],
            'backgroundColor': ['#FF6384', '#36A2EB', '#FFCE56'],
        }]
    }

    # Update context with chart data
    context.update({
        'chart_data': chart_data
    })
    return context