from fastapi import FastAPI
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import NameEmail
from starlette.responses import JSONResponse

from src.core import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.EMAIL_USERNAME,
    MAIL_PASSWORD=settings.EMAIL_PASSWORD,
    MAIL_FROM=settings.EMAIL_FROM,
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM_NAME="doaks",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


class EmailSender:
    @staticmethod
    async def send_url(email: str, url: str) -> JSONResponse:
        html = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ссылка подтверждения</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #050505; color: #111111;">
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center" width="100%" style="max-width: 620px; margin: 40px auto; background-color: #ffffff; border: 1px solid #d7d7d7; border-radius: 0; overflow: hidden;">
            <tr>
                <td style="background-color: #000000; padding: 28px 30px; text-align: left; border-bottom: 4px solid #ffffff;">
                    <p style="color: #bdbdbd; margin: 0 0 8px; font-size: 12px; font-weight: bold; letter-spacing: 2px; text-transform: uppercase;">ECHOMESS SECURITY</p>
                    <h1 style="color: #ffffff; margin: 0; font-size: 26px; font-weight: 800; letter-spacing: 0;">Подтверждение аккаунта</h1>
                </td>
            </tr>
            <tr>
                <td style="padding: 38px 34px; text-align: left;">
                    <p style="font-size: 18px; line-height: 1.5; color: #111111; margin: 0 0 14px; font-weight: 700;">
                        Осталось подтвердить почту.
                    </p>
                    <p style="font-size: 15px; line-height: 1.6; color: #333333; margin: 0 0 30px;">
                        Это письмо пришло от ECHOMESS. Нажмите кнопку ниже, чтобы завершить регистрацию и защитить доступ к аккаунту.
                    </p>

                    <a href="{url}" target="_blank" style="display: inline-block; background-color: #000000; color: #ffffff; text-decoration: none; padding: 15px 28px; font-size: 15px; font-weight: 800; border-radius: 0; border: 2px solid #000000; text-transform: uppercase; letter-spacing: 1px;">
                        Подтвердить аккаунт
                    </a>

                    <p style="font-size: 12px; line-height: 1.6; color: #555555; margin: 30px 0 0; word-break: break-all;">
                        Если кнопка не открылась, используйте прямую ссылку:<br>
                        <a href="{url}" style="color: #000000; font-weight: 700;">{url}</a>
                    </p>
                    <p style="font-size: 12px; line-height: 1.6; color: #555555; margin: 26px 0 0;">
                        Если запрос был не ваш, ничего не нажимайте. Аккаунт без подтверждения активирован не будет.
                    </p>
                </td>
            </tr>
            <tr>
                <td style="background-color: #000000; padding: 18px 30px; text-align: left; border-top: 1px solid #222222;">
                    <p style="font-size: 12px; color: #ffffff; margin: 0; font-weight: 700;">ECHOMESS</p>
                    <p style="font-size: 11px; color: #a8a8a8; margin: 6px 0 0;">&copy; 2026 ECHOMESS. Все права защищены.</p>
                </td>
            </tr>
        </table>
    </body>
    </html>
        """

        message = MessageSchema(
            subject="ECHOMESS | Подтверждение аккаунта",
            recipients=[NameEmail(name="ECHOMESS", email=email)],
            body=html,
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        return JSONResponse(status_code=200, content={"message": "email has been sent"})

    @staticmethod
    async def send_code(email: str, code: str) -> JSONResponse:
        html = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Код подтверждения</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #050505; color: #111111;">
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center" width="100%" style="max-width: 620px; margin: 40px auto; background-color: #ffffff; border: 1px solid #d7d7d7; border-radius: 0; overflow: hidden;">
            <tr>
                <td style="background-color: #000000; padding: 28px 30px; text-align: left; border-bottom: 4px solid #ffffff;">
                    <p style="color: #bdbdbd; margin: 0 0 8px; font-size: 12px; font-weight: bold; letter-spacing: 2px; text-transform: uppercase;">ECHOMESS SECURITY</p>
                    <h1 style="color: #ffffff; margin: 0; font-size: 26px; font-weight: 800; letter-spacing: 0;">Код подтверждения входа</h1>
                </td>
            </tr>
            <tr>
                <td style="padding: 38px 34px; text-align: left;">
                    <p style="font-size: 18px; line-height: 1.5; color: #111111; margin: 0 0 14px; font-weight: 700;">
                        Оодноразовый код.
                    </p>
                    <p style="font-size: 15px; line-height: 1.6; color: #333333; margin: 0 0 24px;">
                        Введите его в ECHOMESS, чтобы подтвердить вход. Код нужен только для текущей попытки авторизации.
                    </p>

                    <div style="display: inline-block; background-color: #000000; border: 2px solid #000000; padding: 16px 36px; font-size: 34px; font-weight: 800; font-family: 'Courier New', Courier, monospace; color: #ffffff; letter-spacing: 7px; border-radius: 0; margin-bottom: 24px;">
                        {code}
                    </div>

                    <p style="font-size: 13px; line-height: 1.6; color: #555555; margin: 0;">
                        Код действует 5 минут. Не пересылайте его и не диктуйте никому, даже если человек представляется поддержкой.
                    </p>
                    <p style="font-size: 12px; line-height: 1.6; color: #555555; margin: 26px 0 0;">
                        Если вход был не ваш, не используйте код. Без него доступ к аккаунту не будет подтвержден.
                    </p>
                </td>
            </tr>
            <tr>
                <td style="background-color: #000000; padding: 18px 30px; text-align: left; border-top: 1px solid #222222;">
                    <p style="font-size: 12px; color: #ffffff; margin: 0; font-weight: 700;">ECHOMESS</p>
                    <p style="font-size: 11px; color: #a8a8a8; margin: 6px 0 0;">&copy; 2026 ECHOMESS. Все права защищены.</p>
                </td>
            </tr>
        </table>
    </body>
    </html>
        """

        message = MessageSchema(
            subject="ECHOMESS | Код подтверждения",
            recipients=[NameEmail(name="ECHOMESS", email=email)],
            body=html,
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        return JSONResponse(
            status_code=200, content={"message": "Verification code has been sent"}
        )
