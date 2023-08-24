import hashlib
import re
import time
import uuid
from urllib.parse import urlencode
import aiohttp


class AAIOAPI:
    def __init__(self, merchant_id, secret, api_key):
        self.merchant_id = merchant_id
        self.secret = secret
        self.api_key = api_key
        self.base_url = 'https://aaio.io/'

    def generate_sign(self, order_id, amount, currency):
        sign_data = f':'.join([
            str(self.merchant_id),
            str(amount),
            str(currency),
            str(self.secret),
            str(order_id)
        ])
        return hashlib.sha256(sign_data.encode('utf-8')).hexdigest()

    def create_payment_link(self, amount, currency, order_id, desc, lang):

        sign = self.generate_sign(order_id, amount, currency)
        params = {
            'merchant_id': self.merchant_id,
            'amount': amount,
            'currency': currency,
            'order_id': order_id,
            'sign': sign,
            'desc': desc,
            'lang': lang
        }
        return self.base_url + "merchant/pay?" + urlencode(params)

    async def get_payment_info(self, order_id):
        url = self.base_url + 'api/info-pay'
        headers = {
            'Accept': 'application/json',
            'X-Api-Key': self.api_key
        }
        params = {
            'merchant_id': self.merchant_id,
            'order_id': order_id
        }
        timeout = aiohttp.ClientTimeout(total=60)  # Define the timeout

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, data=params, headers=headers, timeout=timeout) as response:
                    response_text = await response.text()
            except aiohttp.ClientTimeout:
                return 'Timeout'

        if response.status in [200, 400, 401]:
            try:
                response_json = await response.json()
            except:
                return 'Failed to parse response'

            if response_json['type'] == 'success':
                return response_json
            else:
                return 'Error: ' + response_json['message']
        else:
            return 'Response code: ' + str(response.status)


def generate_order_id():
    unique_id = str(uuid.uuid4())[:8]  # Get a unique identifier
    timestamp = str(int(time.time()))  # Get the current timestamp
    order_id = f"{timestamp}_{unique_id}"  # Combine timestamp and unique identifier

    # Remove non-allowed characters and truncate if needed
    order_id = re.sub(r'[^\w\:\-\_\[\]\|]', '', order_id)[:64]

    return order_id
