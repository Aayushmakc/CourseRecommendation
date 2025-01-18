from django.core.mail import send_mail
from django.conf import settings

def send_welcome_email(user_email, first_name):
    subject = 'Welcome to CourseMate!'
    message = f"""
    Hi {first_name},
    
    Welcome to our Course Recommendation System!🎉 
    We're excited to have you join us.
    
    Start exploring courses that match your interests.
    
    Best regards,
    CourseMate Team
    """
    print(f"Attempting to send email to {user_email}") 
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user_email],
            fail_silently=False,
        ) 
        print("Email sent successfully!")  # Debug print
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False
