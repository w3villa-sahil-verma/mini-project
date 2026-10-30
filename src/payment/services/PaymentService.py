import asyncio
import base64
import hashlib
import hmac
import json
import os
from functools import lru_cache
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import HTTPException, status


@lru_cache(maxsize=1)
def _payment_credentials() -> tuple[str, str]:
    values = {
        "ROZAR_PAY_API_KEY": os.getenv("ROZAR_PAY_API_KEY"),
        "ROZAR_PAY_SECRET": os.getenv("ROZAR_PAY_SECRET"),
    }

    env_file = Path(__file__).resolve().parents[2] / ".env"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            key, separator, value = line.partition("=")
            if separator and key.strip() in values and not values[key.strip()]:
                values[key.strip()] = value.strip().strip("\"'")

    api_key = values["ROZAR_PAY_API_KEY"]
    secret = values["ROZAR_PAY_SECRET"]
    if not api_key or not secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Razorpay payments are not configured.",
        )

    return api_key, secret


class PaymentService:
    async def create_order(
        self,
        *,
        amount_minor: int,
        currency: str,
        receipt: str,
    ) -> dict:
        api_key, secret = _payment_credentials()
        payload = json.dumps(
            {
                "amount": amount_minor,
                "currency": currency,
                "receipt": receipt,
            }
        ).encode("utf-8")
        authorization = base64.b64encode(
            f"{api_key}:{secret}".encode("utf-8")
        ).decode("ascii")
        request = Request(
            "https://api.razorpay.com/v1/orders",
            data=payload,
            headers={
                "Authorization": f"Basic {authorization}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            response = await asyncio.to_thread(self._send_request, request)
        except HTTPError as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Razorpay could not create the payment order.",
            ) from error
        except URLError as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not connect to Razorpay.",
            ) from error

        if not isinstance(response, dict) or (
            not isinstance(response.get("id"), str)
            or response.get("amount") != amount_minor
            or response.get("currency") != currency
        ):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Razorpay returned an invalid payment order.",
            )

        return response

    @staticmethod
    def verify_signature(
        *,
        order_id: str,
        payment_id: str,
        signature: str,
    ) -> bool:
        _, secret = _payment_credentials()
        expected_signature = hmac.new(
            secret.encode("utf-8"),
            f"{order_id}|{payment_id}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected_signature, signature)

    @staticmethod
    def _send_request(request: Request) -> dict:
        with urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
