from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="NeuralForge API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for consultation request
class ConsultationRequest(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    message: str

# Email configuration (using environment variables for security)
EMAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "sender_email": os.getenv("SENDER_EMAIL", "your-email@gmail.com"),
    "sender_password": os.getenv("SENDER_PASSWORD", "your-app-password"),
    "receiver_email": os.getenv("RECEIVER_EMAIL", "hello@neuralforge.ai")
}

def send_email_notification(consultation: ConsultationRequest):
    """Send email notification for new consultation request"""
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"New Consultation Request from {consultation.name}"
        msg["From"] = EMAIL_CONFIG["sender_email"]
        msg["To"] = EMAIL_CONFIG["receiver_email"]
        
        # Create the plain-text and HTML version of your message
        text = f"""
        New Consultation Request
        
        Name: {consultation.name}
        Email: {consultation.email}
        Company: {consultation.company or 'Not provided'}
        
        Message:
        {consultation.message}
        
        Received at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">
                New Consultation Request
              </h2>
              
              <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <p><strong>Name:</strong> {consultation.name}</p>
                <p><strong>Email:</strong> <a href="mailto:{consultation.email}">{consultation.email}</a></p>
                <p><strong>Company:</strong> {consultation.company or 'Not provided'}</p>
              </div>
              
              <div style="background-color: #ffffff; padding: 20px; border: 1px solid #e9ecef; border-radius: 8px;">
                <h3 style="color: #495057; margin-top: 0;">Message:</h3>
                <p style="white-space: pre-wrap;">{consultation.message}</p>
              </div>
              
              <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #e9ecef; color: #6c757d; font-size: 14px;">
                <p>Received at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
              </div>
            </div>
          </body>
        </html>
        """
        
        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        
        # Add HTML/plain-text parts to MIMEMultipart message
        msg.attach(part1)
        msg.attach(part2)
        
        # Send the message via SMTP server
        with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
            server.starttls()
            server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["sender_password"])
            server.send_message(msg)
        
        logger.info(f"Email notification sent successfully for {consultation.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email notification: {str(e)}")
        return False

def send_confirmation_email(consultation: ConsultationRequest):
    """Send confirmation email to the user"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Thank you for your consultation request - NeuralForge AI"
        msg["From"] = EMAIL_CONFIG["sender_email"]
        msg["To"] = consultation.email
        
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #667eea; margin: 0;">Neural<span style="color: #764ba2;">Forge</span></h1>
                <p style="color: #6c757d; margin-top: 5px;">Intelligence at Scale</p>
              </div>
              
              <h2 style="color: #495057;">Thank you for reaching out, {consultation.name}!</h2>
              
              <p>We've received your consultation request and appreciate your interest in NeuralForge AI solutions.</p>
              
              <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #667eea; margin-top: 0;">What happens next?</h3>
                <ul style="color: #495057;">
                  <li>Our team will review your request within 24 hours</li>
                  <li>A specialist will reach out to schedule a consultation</li>
                  <li>We'll prepare a customized AI solution proposal for your needs</li>
                </ul>
              </div>
              
              <p>In the meantime, feel free to explore our website for more information about our AI and data science services.</p>
              
              <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e9ecef; text-align: center; color: #6c757d; font-size: 14px;">
                <p>© 2024 NeuralForge AI. All rights reserved.</p>
                <p>This is an automated response. Please do not reply to this email.</p>
              </div>
            </div>
          </body>
        </html>
        """
        
        part = MIMEText(html, "html")
        msg.attach(part)
        
        with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
            server.starttls()
            server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["sender_password"])
            server.send_message(msg)
        
        logger.info(f"Confirmation email sent to {consultation.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send confirmation email: {str(e)}")
        return False

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "NeuralForge API is running",
        "version": "1.0.0",
        "endpoints": {
            "consultation": "/api/consultation",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/consultation")
async def submit_consultation(consultation: ConsultationRequest):
    """Handle consultation form submission"""
    try:
        logger.info(f"Received consultation request from {consultation.email}")
        
        # Send notification email to admin
        notification_sent = send_email_notification(consultation)
        
        # Send confirmation email to user
        confirmation_sent = send_confirmation_email(consultation)
        
        if not notification_sent and not confirmation_sent:
            raise HTTPException(
                status_code=500,
                detail="Failed to process consultation request. Please try again later."
            )
        
        return {
            "success": True,
            "message": "Your consultation request has been received. We'll be in touch soon!",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing consultation request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request. Please try again."
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 