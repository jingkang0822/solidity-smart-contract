from dataclasses import dataclass
import requests
import json
from typing import Dict
from types import SimpleNamespace
import pickle
from logger import AppLog


@dataclass
class Requestor:
    method: str
    url: str
    headers: Dict[str, str] = None


def http_browser(requestor):
    try:

        AppLog.logger().debug(f'Request url: {requestor.url}')
        response = requests.request(
            method=requestor.method,
            url=requestor.url,
            headers=requestor.headers,
            timeout=120
        )

        if response.ok:
            return json.loads(response.text, object_hook=lambda d: SimpleNamespace(**d))
        else:
            AppLog.logger().error(f'API return error, status_code: {response.status_code}, text: {response.text}\n')
            AppLog.logger().error(f'json obj: {json.dumps(response.json(), indent=4)}\n')
            AppLog.logger().error(f'pickle obj: {pickle.dumps(response, pickle.HIGHEST_PROTOCOL)}')

    except Exception as e:
        AppLog.logger().error(e)

    return None
