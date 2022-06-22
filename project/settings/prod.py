from .base import *

# Core
SECURE_SSL_REDIRECT = True
ALLOWED_HOSTS = [
    '.westadaparents.com',
    '.herokuapp.com',
]

# SendGrid
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY = env("SENDGRID_API_KEY")
SENDGRID_TRACK_CLICKS_HTML = False
SENDGRID_TRACK_CLICKS_PLAIN = False
