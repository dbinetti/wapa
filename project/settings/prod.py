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

# Cloudinary
CLOUDINARY_PREFIX = 'wapa'
CLOUDINARY_STORAGE = {
    'PREFIX': CLOUDINARY_PREFIX,
}

# GIS
GDAL_LIBRARY_PATH = env("GDAL_LIBRARY_PATH")
GEOS_LIBRARY_PATH = env("GEOS_LIBRARY_PATH")
