import smtplib
from email.message import EmailMessage
import os

def send_buyer_notification(
    seller_email: str,
    listing_title: str,
    listing_quantity: float,
    listing_unit: str,
    buyer_company: str,
    buyer_email: str
):
    try:
        email_host = os.getenv("EMAIL_HOST")
        email_port = int(os.getenv("EMAIL_PORT", "587"))
        email_user = os.getenv("EMAIL_USER")
        email_pass = os.getenv("EMAIL_PASSWORD")
        
        if not all([email_host, email_user, email_pass]):
            print("Warning: Email configuration is incomplete. Skipping email notification.")
            return

        msg = EmailMessage()
        msg["Subject"] = "New Buyer Interested in Your Waste Listing"
        msg["From"] = email_user
        msg["To"] = seller_email

        body = f"""Hello,

A buyer is interested in purchasing your waste listing.

Listing Title: {listing_title}
Quantity: {listing_quantity} {listing_unit}
Buyer Company: {buyer_company}
Buyer Email: {buyer_email}

Please contact the buyer to finalize the transaction.

Thank you,
ReLoop Platform
"""
        msg.set_content(body)

        with smtplib.SMTP(email_host, email_port) as server:
            server.starttls()
            server.login(email_user, email_pass)
            server.send_message(msg)
            
        print(f"Successfully sent buyer notification to {seller_email}")
        
    except Exception as e:
        print(f"Failed to send email to {seller_email}: {str(e)}")
