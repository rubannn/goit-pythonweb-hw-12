from email.message import EmailMessage

import aiosmtplib

from src.database.config import settings


def create_email_token(email: str) -> str:
    from itsdangerous import URLSafeTimedSerializer

    serializer = URLSafeTimedSerializer(settings.JWT_SECRET_KEY)
    return serializer.dumps(email, salt="email-confirm")


def get_email_from_token(token: str) -> str:
    from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

    serializer = URLSafeTimedSerializer(settings.JWT_SECRET_KEY)
    try:
        return serializer.loads(
            token,
            salt="email-confirm",
            max_age=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_SECONDS,
        )
    except SignatureExpired as exc:
        raise ValueError("Verification token has expired") from exc
    except BadSignature as exc:
        raise ValueError("Invalid verification token") from exc


async def send_verification_email(email: str, username: str) -> None:
    token = create_email_token(email)
    verification_link = f"{settings.BACKEND_BASE_URL}/api/auth/verify-email/{token}"

    if settings.MAIL_SUPPRESS_SEND:
        print(
            "Email sending suppressed. Verification link for "
            f"{email}: {verification_link}"
        )
        return

    message = EmailMessage()
    message["From"] = settings.MAIL_FROM or settings.MAIL_USERNAME or "noreply@example.com"
    message["To"] = email
    message["Subject"] = "Verify your email"
    message.set_content(
        f"Hello, {username}!\n\n"
        f"Please verify your email by opening this link:\n{verification_link}\n"
    )

    await aiosmtplib.send(
        message,
        hostname=settings.MAIL_SERVER,
        port=settings.MAIL_PORT,
        username=settings.MAIL_USERNAME,
        password=settings.MAIL_PASSWORD,
        start_tls=settings.MAIL_STARTTLS,
        use_tls=settings.MAIL_SSL_TLS,
    )
