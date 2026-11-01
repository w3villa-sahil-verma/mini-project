import re
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from urllib.parse import parse_qs, urlparse

from fastapi import HTTPException

from src.auth.services.AuthTokenService import AuthTokenService
from src.auth.services.PasswordResetService import PasswordResetService
from src.common.notification.NotificationService import NotificationService
from src.common.token.JwtService import JwtTokenService
from src.common.token.constants import TOKEN_TYPES
from src.common.token.types import AuthTokens
from src.models.AuthToken import AuthToken
from src.models.User import USER_ROLE


class AuthTokenServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_refresh_rotates_single_use_token(self) -> None:
        db = AsyncMock()
        db.add = MagicMock()
        token_service = JwtTokenService()
        auth_token_service = AuthTokenService(db, token_service)
        now = datetime.now(timezone.utc)
        old_record = AuthToken(
            jti="old-refresh-jti",
            user_id=17,
            token_type=TOKEN_TYPES.REFRESH.value,
            expires_at=now + timedelta(days=30),
        )
        user = SimpleNamespace(
            id=17,
            role=USER_ROLE.USER,
            is_deleted=False,
        )
        db.scalar.side_effect = [old_record, user]
        old_refresh_token = token_service.sign(
            {
                "user_id": 17,
                "type": TOKEN_TYPES.REFRESH.value,
                "jti": old_record.jti,
                "exp": now + timedelta(days=30),
                "iat": now,
            }
        )

        tokens: AuthTokens = await auth_token_service.rotate_refresh_token(
            old_refresh_token
        )

        self.assertIsNotNone(old_record.used_at)
        self.assertEqual(db.commit.await_count, 1)
        new_record = db.add.call_args.args[0]
        self.assertNotEqual(new_record.jti, old_record.jti)
        self.assertEqual(
            token_service.verify(tokens["access_token"])["type"],
            TOKEN_TYPES.ACCESS.value,
        )
        self.assertEqual(
            token_service.verify(tokens["refresh_token"])["jti"],
            new_record.jti,
        )

    async def test_reused_refresh_token_is_rejected(self) -> None:
        db = AsyncMock()
        auth_token_service = AuthTokenService(db, JwtTokenService())
        now = datetime.now(timezone.utc)
        used_record = AuthToken(
            jti="used-refresh-jti",
            user_id=17,
            token_type=TOKEN_TYPES.REFRESH.value,
            expires_at=now + timedelta(days=30),
            used_at=now,
        )
        db.scalar.return_value = used_record
        token = auth_token_service.token_service.sign(
            {
                "user_id": 17,
                "type": TOKEN_TYPES.REFRESH.value,
                "jti": used_record.jti,
                "exp": now + timedelta(days=30),
                "iat": now,
            }
        )

        with self.assertRaises(HTTPException) as raised:
            await auth_token_service.rotate_refresh_token(token)

        self.assertEqual(raised.exception.status_code, 401)


class PasswordResetServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_reset_link_is_sent_and_consumed_once(self) -> None:
        db = AsyncMock()
        db.add = MagicMock()
        notification_service = AsyncMock(spec=NotificationService)
        user = SimpleNamespace(id=23, email="member@example.com", is_deleted=False)
        db.scalar.return_value = user
        service = PasswordResetService(
            db,
            JwtTokenService(),
            notification_service,
        )

        await service.request_reset(user.email)

        notification = notification_service.send.await_args.args[0]
        token_match = re.search(r"/reset-password\?token=([^\s]+)", notification.body)
        self.assertIsNotNone(token_match)
        token = parse_qs(urlparse(token_match.group(0)).query)["token"][0]
        stored_reset_token = db.add.call_args.args[0]
        self.assertEqual(stored_reset_token.token_type, TOKEN_TYPES.PASSWORD_RESET.value)
        self.assertIn("Choose a new password", notification.html_body)

        db.scalar.side_effect = [stored_reset_token, user]
        await service.validate_reset_token(token)

        credential = SimpleNamespace(user_id=user.id, hash="old-hash")
        db.scalar.side_effect = [stored_reset_token, user, credential]
        await service.reset_password(token, "correct-horse-battery")
        self.assertNotEqual(credential.hash, "old-hash")
        self.assertIsNotNone(stored_reset_token.used_at)

        db.scalar.side_effect = [stored_reset_token]
        with self.assertRaises(HTTPException) as raised:
            await service.validate_reset_token(token)
        self.assertEqual(raised.exception.status_code, 400)

    async def test_unknown_email_is_reported_without_sending_mail(self) -> None:
        db = AsyncMock()
        db.scalar.return_value = None
        notification_service = MagicMock()
        service = PasswordResetService(
            db,
            JwtTokenService(),
            notification_service,
        )

        with self.assertRaises(HTTPException) as raised:
            await service.request_reset("missing@example.com")

        self.assertEqual(raised.exception.status_code, 404)
        notification_service.send.assert_not_called()


if __name__ == "__main__":
    unittest.main()
