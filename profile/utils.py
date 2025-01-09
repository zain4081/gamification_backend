import random
import string

from django.conf import settings
from django.core.mail import send_mail


def custom_error_message(errors):
    for key, value in errors.items():
        if isinstance(value, list):
            return {'error': value[0].replace('field', key + ' field')}
        elif isinstance(value, dict):
            return custom_error_message(value)
    return {'error': 'Unknown error'}

def send_mail_forgot_password(email, token, full_name):
    try:
        subject = 'Set Password Request'
        message = (f"Hi, {full_name},\n\n"
                   "We've received a password reset request from your Gardening Care account. If this was you, please use"
                   " url below to set a new password. If this was not you, please ignore this email.\n\n"
                   f"{settings.EMAIL_BASE_URL}{token}")

        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email, ]

        send_mail(subject, message, email_from, recipient_list)

        return True
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False

def generate_token():
    number =  random.randint(14, 34)
    return ''.join(random.choices(string.digits + string.ascii_uppercase, k=number))