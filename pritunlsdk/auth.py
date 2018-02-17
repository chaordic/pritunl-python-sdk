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

API_TOKEN = os.getenv('PRITUNL_API_TOKEN')
API_SECRET = os.getenv('PRITUNL_API_SECRET')
BASE_URL = os.getenv('PRITUNL_API_URL')

# Taken from https://pritunl.com/api
def pritunl_auth_request(method, path, headers=None, data=None):
    auth_timestamp = str(int(time.time()))
    auth_nonce = uuid.uuid4().hex
    auth_string = '&'.join([API_TOKEN, auth_timestamp, auth_nonce,
        method.upper(), path])
    auth_signature = base64.b64encode(hmac.new(
        API_SECRET, auth_string, hashlib.sha256).digest())
    auth_headers = {
        'Auth-Token': API_TOKEN,
        'Auth-Timestamp': auth_timestamp,
        'Auth-Nonce': auth_nonce,
        'Auth-Signature': auth_signature,
    }
    if headers:
        auth_headers.update(headers)
    try:
        return getattr(requests, method.lower())(
            BASE_URL + path,
            headers=auth_headers,
            data=data,
        )
    except Exception as e:
        LOGGER.debug('Could not connect to %s: %s' % (BASE_URL, e))
