from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Template
import aiosmtplib

from app.config import EMAIL_ADDRESS, EMAIL_PASSWORD, EMAIL_SMTP_HOST, EMAIL_SMTP_PORT


async def send_email(
    to: str, title: str, html_message: str = "", plain_message: str = ""
):
    message = MIMEMultipart("alternative")
    message["From"] = EMAIL_ADDRESS
    message["To"] = to
    message["Subject"] = title

    plain_text_message = MIMEText(plain_message, "plain", "utf-8")
    html_message = MIMEText(html_message, "html", "utf-8")
    message.attach(plain_text_message)
    message.attach(html_message)

    await aiosmtplib.send(
        message,
        hostname=EMAIL_SMTP_HOST,
        port=EMAIL_SMTP_PORT,
        username=EMAIL_ADDRESS,
        password=EMAIL_PASSWORD,
        start_tls=True,
    )


async def send_password_reset_email(to, reset_password_link):
    title = "[Engster] 비밀번호 재설정 안내"
    with open("app/templates/reset-password-request.html") as f:
        template = Template(f.read())
        html = template.render(reset_password_link=reset_password_link)
    await send_email(to, title, html)
