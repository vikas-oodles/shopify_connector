from requests import request
from requests.exceptions import HTTPError

import json
import logging

_logger = logging.getLogger(__name__)


class BadRequestError(Exception):

    def __init__(self, message='Kindly check the request again!!'):
        self.message = message
        super().__init__(self.message)


class Shopify(object):
    default_uri = "/"

    def __init__(self, shopify_api_key: str, shopify_password: str, uri: str = None):
        self.shopify_api_key = shopify_api_key
        self.shopify_password = shopify_password
        self.uri = uri or self.default_uri

    def get_url(self, uri):
        url = "https://"+ self.shopify_api_key + ":" + self.shopify_password + "@vikas-oodles.myshopify.com/admin/api/2020-07" + (
                    uri or self.uri)
        return url

    def get_request(self, url: str, headers: dict, params: dict):
        try:
            response = request("GET", url, headers=headers, params=params)
            return json.loads(response.content), response.status_code
        except HTTPError as e:
            _logger.error(e)
            raise e

    def post_request(self, url: str, headers: dict, data: dict):
        try:
            response = request('POST', url, data=json.dumps(data), headers=headers)
            return json.loads(response.content), response.status_code
        except HTTPError as e:
            _logger.error(e)
            raise e

    def put_request(self, url: str, headers: dict, data: dict):
        try:
            response = request('PUT', url, data=json.dumps(data), headers=headers)
            print(response, url, headers, data)
            return json.loads(response.content), response.status_code
        except HTTPError as e:
            _logger.error(e)
            raise e

    def request(self, method: str, uri: str = None, data: dict = None, params: dict = None):
        url = self.get_url(uri)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if method == 'GET':
            return self.get_request(url, headers, params)

        if method == 'POST' and data:
            return self.post_request(url, headers, data)

        if method == 'PUT' and data:
            return self.put_request(url, headers, data)

        else:
            raise BadRequestError


class Product(Shopify):
    default_uri = '/products.json'

    def get_products_list(self, params: dict = None):
        # url = self.get_url(self.default_uri)
        response, status_code = self.request('GET', uri=self.default_uri)
        if status_code == 200:
            return response.get('data')
        else:
            _logger.error('get_products_list')
            return None

    def create_product(self, data: dict, fields: tuple = None):
        response, status_code = self.request('POST', data=data, params={
            'include_fields': fields
        })
        if status_code == 200:
            return response.get('data')
        else:
            _logger.error('create_product')
            return None



