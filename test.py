import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from io import BytesIO
from email.mime.base import MIMEBase
from email import encoders
import datetime
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# Function to generate certificate as a buffer
def create_volunteer_certificate_buffer(volunteer_name, logo_path):
    # Create a BytesIO buffer to hold the PDF
    buffer = BytesIO()

    # Change to landscape orientation
    c = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)

    # Adding a border with some padding
    border_padding = 40
    c.setStrokeColor(colors.darkblue)
    c.setLineWidth(3)
    c.rect(border_padding, border_padding, width - 2 * border_padding, height - 2 * border_padding)

    # Background color for the certificate (light)
    c.setFillColor(colors.whitesmoke)
    c.rect(border_padding, border_padding, width - 2 * border_padding, height - 2 * border_padding, fill=1)

    # Add the logo (top-left corner for example)
    logo_width = 100
    logo_height = 100
    logo_x = 50  # Adjust this for positioning
    logo_y = height - 120  # Adjust this for positioning
    c.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height)

    # Title
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2, height - 120, "Certificate of Appreciation")

    # Subtitle
    c.setFont("Helvetica", 18)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height - 160, "This Certifies That")

    # Volunteer Name
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(colors.green)
    c.drawCentredString(width / 2, height - 200, volunteer_name)

    # Main Text (Body of the certificate)
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.black)
    text = ("has joined True Health Education Foundation as a volunteer and has contributed "
            "to our cause with dedication, enthusiasm, and care. We truly appreciate your commitment "
            "to making a positive impact in the community.")

    # Wrapping the text manually
    margin = 50
    max_line_width = width - 2 * margin - 2 * border_padding
    lines = []
    current_line = ""

    # Break the text into lines that fit within the max line width
    for word in text.split():
        test_line = current_line + " " + word if current_line else word
        if c.stringWidth(test_line, "Helvetica", 14) <= max_line_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)  # Add the last line

    # Draw the wrapped text
    text_height = height - 250
    for line in lines:
        c.drawString(margin + border_padding, text_height, line)
        text_height -= 20  # Adjust the vertical position for each line

    # Date and Signature Section
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    
    # Get today's date in the format 'Month Day, Year' (e.g., 'February 21, 2025')
    today_date = datetime.datetime.now().strftime("%B %d, %Y")
    
    # Draw the date on the certificate
    c.drawString(120 + border_padding, height - 320, f"Date: {today_date}")
    
    c.drawString(120 + border_padding, height - 340, "Signature: _________________________")

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(colors.gray)
    c.drawCentredString(width / 2, 100, "True Health Education Foundation")
    c.drawCentredString(width / 2, 85, "We are grateful for your support!")

    # Save the PDF to the buffer
    c.save()

    # Get the value of the buffer
    buffer.seek(0)
    return buffer

# Function to send email with the certificate attached
def send_certificate_email(receiver_email, volunteer_name, logo_path, sender_email, sender_password):
    # Create certificate PDF buffer
    certificate_buffer = create_volunteer_certificate_buffer(volunteer_name, logo_path)

    # Setup the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Certificate of Appreciation - True Health Education Foundation"

    # Email body
    body = "Dear {0},\n\nPlease find attached your Certificate of Appreciation from True Health Education Foundation.\n\nBest regards,\nTrue Health Education Foundation".format(volunteer_name)
    msg.attach(MIMEText(body, 'plain'))

    # Attach the certificate PDF file
    part = MIMEApplication(certificate_buffer.read(), Name="Certificate.pdf")
    part['Content-Disposition'] = 'attachment; filename="Certificate.pdf"'
    msg.attach(part)

    # Send the email via SMTP
    try:
        server = smtplib.SMTP('smtp.hostinger.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Example usage:
logo_path ="https://res.cloudinary.com/dplbdop3n/image/upload/v1737955474/logo_l00s7s.png"

send_certificate_email(
    receiver_email="kamit896837@gmail.com",
    volunteer_name="Amit KUmar",
    logo_path=logo_path,
    sender_email="support@truehealtheducationfoundation.org",
    sender_password="@Support48096"
)
