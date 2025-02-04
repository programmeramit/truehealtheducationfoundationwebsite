import smtplib


smtp_host = "smtp.hostinger.com"
smtp_port = 587  
smtp_user = "support@truehealtheducationfoundation.org"  
smtp_password = "@Support48096" 

logo_path ="https://res.cloudinary.com/dplbdop3n/image/upload/v1737955474/logo_l00s7s.png"


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
