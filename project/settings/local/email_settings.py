from project.utils.settings import get_env_variable
EMAIL_HOST_USER = get_env_variable("ADMIN_EMAIL_ADDRESS", "noreply@pennycreditonline.com")
EMAIL_HOST_PASSWORD = get_env_variable("ADMIN_EMAIL_PASSWORD", "")
EMAIL_PORT = 587
EMAIL_HOST = get_env_variable("EMAIL_HOST", "smtp.zeptomail.com")
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = "Penny Credit <noreply@pennycreditonline.com>"
