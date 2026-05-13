from email.message import EmailMessage

import aiosmtplib

from src.database.config import settings


def _create_token(email: str, salt: str) -> str:
    from itsdangerous import URLSafeTimedSerializer

    serializer = URLSafeTimedSerializer(settings.JWT_SECRET_KEY)
    return serializer.dumps(email, salt=salt)


def _get_email_from_token(token: str, salt: str, max_age: int, expired_message: str) -> str:
    from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

    serializer = URLSafeTimedSerializer(settings.JWT_SECRET_KEY)
    try:
        return serializer.loads(
            token,
            salt=salt,
            max_age=max_age,
        )
    except SignatureExpired as exc:
        raise ValueError(expired_message) from exc
    except BadSignature as exc:
        raise ValueError("Invalid token") from exc


def create_email_token(email: str) -> str:
    return _create_token(email, salt="email-confirm")


def get_email_from_token(token: str) -> str:
    try:
        return _get_email_from_token(
            token,
            salt="email-confirm",
            max_age=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_SECONDS,
            expired_message="Verification token has expired",
        )
    except ValueError as exc:
        if str(exc) == "Invalid token":
            raise ValueError("Invalid verification token") from exc
        raise


def create_password_reset_token(email: str) -> str:
    return _create_token(email, salt="password-reset")


def get_email_from_password_reset_token(token: str) -> str:
    try:
        return _get_email_from_token(
            token,
            salt="password-reset",
            max_age=settings.PASSWORD_RESET_TOKEN_EXPIRE_SECONDS,
            expired_message="Password reset token has expired",
        )
    except ValueError as exc:
        if str(exc) == "Invalid token":
            raise ValueError("Invalid password reset token") from exc
        raise


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


async def send_password_reset_email(email: str, username: str) -> None:
    token = create_password_reset_token(email)
    reset_link = f"{settings.PASSWORD_RESET_PAGE_URL}?token={token}"

    if settings.MAIL_SUPPRESS_SEND:
        print(
            "Email sending suppressed. Password reset link for "
            f"{email}: {reset_link}"
        )
        return

    message = EmailMessage()
    message["From"] = settings.MAIL_FROM or settings.MAIL_USERNAME or "noreply@example.com"
    message["To"] = email
    message["Subject"] = "Reset your password"
    message.set_content(
        f"Hello, {username}!\n\n"
        f"Use this link to set a new password:\n{reset_link}\n"
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
