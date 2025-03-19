from aiosmtplib import SMTP

from app.core.config import settings


async def send_email(to: str, subject: str, body: str):
    message = f"Subject: {subject}\n\n{body}"
    async with SMTP(
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
    ) as smtp:
        await smtp.sendmail(settings.smtp_from, to, message)
