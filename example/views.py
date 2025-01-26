# example/views.py
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.conf import settings
import razorpay
from .models import Donation
from django.core.mail import send_mail

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from weasyprint import HTML
from datetime import datetime
from io import BytesIO



razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID , settings.RAZORPAY_SECRET_KEY))



smtp_server = "smtp.hostinger.com"  # Your SMTP server
smtp_port = 587  # TLS port
smtp_user = "support@truehealtheducationfoundation.org"  # Your email address
smtp_password = "@Support48096"  # Your email password


from_email = "support@truehealtheducationfoundation.org"  # From email address
to_email = "kamit896837@gmail.com"  # To email address
subject = "Test Email"
body = "This is a test email sent directly using smtplib."


msg = MIMEMultipart()
msg["From"] = from_email
msg["To"] = to_email
msg["Subject"] = subject

    # Add body to the email
msg.attach(MIMEText(body, "plain"))

def index(request):

    print("Email sent successfully!")

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




def generate_donation_certificate_in_memory(donor_name, donation_amount):
    # Get the current date in YYYY-MM-DD format
    donation_date = datetime.today().strftime('%Y-%m-%d')

    # HTML content for the certificate
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Donation Certificate</title>
      <style>
        body {{
          font-family: 'Arial', sans-serif;
          background-color: #f3f4f6;
          margin: 0;
          padding: 0;
        }}
        .certificate-container {{
          width: 800px;
          margin: 50px auto;
          padding: 30px;
          background-color: #fff;
          border: 10px solid #007bff;
          border-radius: 10px;
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }}
        .header {{
          text-align: center;
          color: #007bff;
        }}
        .header h1 {{
          margin: 0;
          font-size: 40px;
          font-weight: bold;
        }}
        .subheading {{
          text-align: center;
          font-size: 20px;
          color: #555;
          margin-bottom: 40px;
        }}
        .donor-info {{
          text-align: center;
          font-size: 24px;
          margin-bottom: 40px;
        }}
        .donation-amount {{
          text-align: center;
          font-size: 28px;
          font-weight: bold;
          color: #28a745;
        }}
        .footer {{
          text-align: center;
          font-size: 16px;
          color: #555;
          margin-top: 50px;
        }}
      </style>
    </head>
    <body>
      <div class="certificate-container">
        <div class="header">
          <h1>Donation Certificate</h1>
        </div>
        <div class="subheading">
          <p>This certificate acknowledges the generous contribution made by the donor below.</p>
        </div>
        <div class="donor-info">
          <p><strong>Donor Name:</strong> {donor_name}</p>
          <p><strong>Donation Date:</strong> {donation_date}</p>
        </div>
        <div class="donation-amount">
          <p><strong>Donation Amount:</strong> ${donation_amount}</p>
        </div>
        <div class="footer">
          <p>Thank you for your support!</p>
        </div>
      </div>
    </body>
    </html>
    """

    # Generate the PDF directly into memory
    pdf = BytesIO()
    HTML(string=html_content).write_pdf(pdf)
    pdf.seek(0)  # Go to the start of the file-like object

    return pdf

# Function to send email with certificate attached via SMTP
def send_email_with_certificate(smtp_server, smtp_port, smtp_user, smtp_password, from_email, to_email, donor_name, donation_amount):
    # Generate donation certificate in memory
    pdf = generate_donation_certificate_in_memory(donor_name, donation_amount)

    # Create message container
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = "Donation Certificate"

    # Body of the email
    body = "Dear donor,\n\nThank you for your generous donation. Please find your donation certificate attached.\n\nBest regards,"
    msg.attach(MIMEText(body, 'plain'))

    # Attach the certificate PDF (in memory)
    part = MIMEBase("application", "octet-stream")
    part.set_payload(pdf.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="donation_certificate.pdf"')
    msg.attach(part)

    # Establish connection to SMTP server
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection using TLS
        server.login(smtp_user, smtp_password)  # Log in to the server

        # Send the email
        server.sendmail(from_email, to_email, msg.as_string())
        print("Email with donation certificate sent successfully!")

    except Exception as e:
        print(f"Error sending email: {e}")

    finally:
        server.quit()



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
        send_email_with_certificate(smtp_server, smtp_port, smtp_user, smtp_password, from_email, email, donor_name,amount)
        return redirect('index')
    except Exception as e:
        # Handle errors (e.g., payment ID not found or API issues)
        return HttpResponse(f"Error: {str(e)}")
