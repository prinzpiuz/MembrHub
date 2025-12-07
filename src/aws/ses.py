import logging
from typing import Any

import boto3
from botocore.exceptions import ClientError

from src.aws.config import ses_config
from src.aws.exceptions import EmailSendError
from src.aws.utils import retry
from src.core.config import settings


logger = logging.getLogger(__name__)


class SESService:
    def __init__(self) -> None:
        self._client: Any | None = None

    @property
    def client(self) -> Any:
        if self._client is None:
            self._client = boto3.client(
                "ses",
                region_name=ses_config.region,
                aws_access_key_id=ses_config.access_key_id,
                aws_secret_access_key=ses_config.secret_access_key,
            )
        return self._client

    @retry
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str | None = None,
    ) -> bool:
        if settings.is_development and not ses_config.access_key_id:
            logger.info(
                f"[DEV] Email to {to_email}: {subject}\n{text_body or html_body}"
            )
            return True

        try:
            message: dict[str, Any] = {
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Html": {"Data": html_body, "Charset": "UTF-8"},
                },
            }

            if text_body:
                message["Body"]["Text"] = {"Data": text_body, "Charset": "UTF-8"}

            self.client.send_email(
                Source=f"{ses_config.from_name} <{ses_config.from_email}>",
                Destination={"ToAddresses": [to_email]},
                Message=message,
            )
            logger.info(f"Email sent successfully to {to_email}")
            return True

        except ClientError as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            raise EmailSendError(str(e)) from e

    async def send_invitation_email(
        self,
        to_email: str,
        community_name: str,
        inviter_name: str,
        role: str,
        invitation_link: str,
        expires_in_days: int = 7,
    ) -> bool:
        subject = f"You've been invited to join {community_name}"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">You're Invited!</h2>
                <p>Hi there,</p>
                <p><strong>{inviter_name}</strong> has invited you to join
                   <strong>{community_name}</strong> as a <strong>{role}</strong>.</p>
                <p>Click the button below to accept the invitation:</p>
                <p style="text-align: center; margin: 30px 0;">
                    <a href="{invitation_link}"
                       style="background-color: #2563eb; color: white; padding: 12px 24px;
                              text-decoration: none; border-radius: 6px; display: inline-block;">
                        Accept Invitation
                    </a>
                </p>
                <p style="color: #666; font-size: 14px;">
                    This invitation will expire in {expires_in_days} days.
                </p>
                <p style="color: #666; font-size: 14px;">
                    If you didn't expect this invitation, you can safely ignore this email.
                </p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #999; font-size: 12px;">
                    Sent by {settings.APP_NAME}
                </p>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        You're Invited!

        {inviter_name} has invited you to join {community_name} as a {role}.

        Accept the invitation: {invitation_link}

        This invitation will expire in {expires_in_days} days.

        If you didn't expect this invitation, you can safely ignore this email.
        """

        return await self.send_email(to_email, subject, html_body, text_body)

    async def send_password_reset_email(
        self,
        to_email: str,
        reset_link: str,
        expires_in_hours: int = 1,
    ) -> bool:
        subject = f"Reset your {settings.APP_NAME} password"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Reset Your Password</h2>
                <p>Hi,</p>
                <p>We received a request to reset your password. Click the button below
                   to create a new password:</p>
                <p style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}"
                       style="background-color: #2563eb; color: white; padding: 12px 24px;
                              text-decoration: none; border-radius: 6px; display: inline-block;">
                        Reset Password
                    </a>
                </p>
                <p style="color: #666; font-size: 14px;">
                    This link will expire in {expires_in_hours} hour(s).
                </p>
                <p style="color: #666; font-size: 14px;">
                    If you didn't request a password reset, you can safely ignore this email.
                </p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #999; font-size: 12px;">
                    Sent by {settings.APP_NAME}
                </p>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Reset Your Password

        We received a request to reset your password.

        Reset your password: {reset_link}

        This link will expire in {expires_in_hours} hour(s).

        If you didn't request a password reset, you can safely ignore this email.
        """

        return await self.send_email(to_email, subject, html_body, text_body)

    async def send_welcome_email(
        self,
        to_email: str,
        first_name: str,
        community_name: str,
    ) -> bool:
        subject = f"Welcome to {community_name}!"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Welcome to {community_name}!</h2>
                <p>Hi {first_name},</p>
                <p>You've successfully joined <strong>{community_name}</strong>.
                   We're excited to have you as a member!</p>
                <p>You can now access all community features and connect with
                   other members.</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #999; font-size: 12px;">
                    Sent by {settings.APP_NAME}
                </p>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Welcome to {community_name}!

        Hi {first_name},

        You've successfully joined {community_name}. We're excited to have you
        as a member!

        You can now access all community features and connect with other members.
        """

        return await self.send_email(to_email, subject, html_body, text_body)


ses_service = SESService()
