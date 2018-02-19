import os
import time
import uuid
import hmac
import hashlib
import base64
import requests
import json
import logging

LOGGER = logging.getLogger(__name__)


# Taken from https://pritunl.com/api
def pritunl_auth_request(method, path, headers=None, data=None):

    api_token = os.getenv('PRITUNL_API_TOKEN')
    api_secret = os.getenv('PRITUNL_API_SECRET')
    base_url = os.getenv('PRITUNL_API_URL')

    auth_timestamp = str(int(time.time()))
    auth_nonce = uuid.uuid4().hex
    auth_string = '&'.join([api_token, auth_timestamp, auth_nonce,
        method.upper(), path])
    auth_signature = base64.b64encode(hmac.new(
        api_secret, auth_string, hashlib.sha256).digest())
    auth_headers = {
        'Auth-Token': api_token,
        'Auth-Timestamp': auth_timestamp,
        'Auth-Nonce': auth_nonce,
        'Auth-Signature': auth_signature,
    }
    if headers:
        auth_headers.update(headers)
    try:
        return getattr(requests, method.lower())(
            base_url + path,
            headers=auth_headers,
            data=data,
        )
    except Exception as e:
        LOGGER.debug('Could not connect to %s: %s' % (base_url, e))
