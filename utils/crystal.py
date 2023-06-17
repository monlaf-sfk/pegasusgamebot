from __future__ import annotations


class BaseCrystalPayException(Exception):
    pass


class AuthorizationError(BaseCrystalPayException):
    pass


import hashlib
import typing
import aiohttp


class CrystalPay:
    default_url = "https://api.crystalpay.io/v2/"

    def __init__(self, name, secret1, secret2):
        self.secret1 = secret1
        self.secret2 = secret2
        self.name = name

    def prepare_body(self, **kwargs) -> dict:
        params = {
            "auth_secret": self.secret1,
            "auth_login": self.name,
        }
        params.update(
            **{key: value for key, value in kwargs.items() if value is not None}
        )
        return params

    async def _request(
            self,
            method: typing.Literal["post"],
            path: str,
            body: typing.Optional[dict] = None,
    ):
        if body is None:
            body = {}
        body = self.prepare_body(**body)

        async with aiohttp.ClientSession() as session:
            response = await session.request(method, self.default_url + path, json=body)
            await response.read()

        await self._handle_response(response)
        return await response.json(content_type=None)

    @classmethod
    async def _handle_response(cls, response: aiohttp.ClientResponse):
        data = await response.json(content_type=None)
        if data["error"]:
            errors = data["errors"]
            if 1 == len(errors) and "Invalid auth credentials" == errors[0]:
                raise AuthorizationError(errors[0])

            raise BaseCrystalPayException(data)

    async def create_invoice(
            self,
            amount,
            lifetime,
            invoice_type: typing.Literal["purchase", "topup"] = "purchase",
            extra=None,
            callback_url=None,
            redirect_url=None,
            currency=None,
    ):
        body = dict(
            amount=amount,
            lifetime=lifetime,
            type=invoice_type,
            extra=extra or None,
            callback_url=callback_url,
            redirect_url=redirect_url,
        )
        response = await self._request("post", "invoice/create/", body)

        if currency:
            response["url"] = response["url"] + "&m=" + currency
        return response

    async def get_balance(self, hide_empty: bool = False):
        response = await self._request(
            "post", "balance/info/", {"hide_empty": hide_empty}
        )
        return response["balances"]

    async def get_invoice(self, payment_id):
        body = {
            "auth_secret": self.secret1,
            "auth_login": self.name,
            'id': payment_id
        }
        response = await self._request(
            "post", "invoice/info/", body
        )
        return response

    def generate_payment_hash(self, payment_id: typing.Union[int, str]) -> str:
        hash_object = hashlib.sha1("{}:{}".format(payment_id, self.secret2).encode())
        return hash_object.hexdigest()
