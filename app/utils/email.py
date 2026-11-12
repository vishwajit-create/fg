import smtplib
from email.message import EmailMessage
from flask import current_app


def is_mail_configured():
    """Return True if SMTP settings are present in app config."""
    return bool(
        current_app.config.get('MAIL_SERVER')
        and current_app.config.get('MAIL_USERNAME')
        and current_app.config.get('MAIL_PASSWORD')
    )


def send_otp_email(to_email, username, otp_code):
    """Send a 6-digit password reset OTP email via SMTP.

    Returns (success: bool, error_message: str | None).
    """
    if not is_mail_configured():
        current_app.logger.warning(
            f'SMTP not configured. OTP for {username} ({to_email}) was generated but not emailed.'
        )
        return False, 'Email service (SMTP) is not configured on the server. Please contact the administrator.'

    institution = current_app.config.get('INSTITUTION_NAME', 'CSFMS')
    sender = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')
    server_host = current_app.config['MAIL_SERVER']
    port = current_app.config.get('MAIL_PORT', 587)
    use_tls = current_app.config.get('MAIL_USE_TLS', True)

    msg = EmailMessage()
    msg['Subject'] = f'Password Reset OTP — {institution}'
    msg['From'] = sender
    msg['To'] = to_email
    msg.set_content(
        f'Hello {username},\n\n'
        f'Your One-Time Password (OTP) to reset your CSFMS account password is:\n\n'
        f'    {otp_code}\n\n'
        f'This OTP is valid for 10 minutes. Do not share this code with anyone.\n\n'
        f'If you did not request a password reset, please ignore this email.\n\n'
        f'Regards,\n{institution}'
    )

    try:
        if port == 465 and not use_tls:
            with smtplib.SMTP_SSL(server_host, port, timeout=15) as smtp:
                smtp.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(server_host, port, timeout=15) as smtp:
                if use_tls:
                    smtp.starttls()
                smtp.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
                smtp.send_message(msg)
        return True, None
    except Exception as exc:
        current_app.logger.error(f'Failed to send OTP email to {to_email}: {exc}')
        return False, f'Failed to send OTP email: {exc}'
