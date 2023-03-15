import json

from urllib import request
from urllib.parse import urljoin

from arcane_illusion.constants import EXTENSION_ID, EXTENSION_VERSION
from arcane_illusion.image_generation.response import GenerationResponse, ProgressResponse
from arcane_illusion.settings import Options


class Client:

    def __init__(self) -> None:
        super().__init__()
        self._options = Options()
        self._headers = {
            "User-Agent": f"{EXTENSION_ID}/{EXTENSION_VERSION}"
        }

    def get_models(self):
        path = "/sdapi/v1/sd-models"
        response = self._request(path)
        return [item["model_name"] for item in response]

    def get_samplers(self):
        path = "/sdapi/v1/samplers"
        response = self._request(path)
        return [item["name"] for item in response]

    def generate(self, data):
        path = "/sdapi/v1/txt2img"
        headers = {
            "Content-Type": "application/json"
        }
        response = self._request(path, method="POST", data=json.dumps(data).encode('utf-8'), headers=headers)
        return GenerationResponse(**response)

    def progress(self):
        """Not helpful as multiple requests crash Krita"""
        path = "/sdapi/v1/progress"
        response = self._request(path)
        return ProgressResponse(**response)

    def get_control_net_models(self):
        path = "/controlnet/model_list"
        response = self._request(path)
        return response["model_list"]

    def _request(self, path, method=None, data=None, headers=None):
        url = urljoin(self._options.url, path)
        req = request.Request(url=url, method=method, headers={**self._headers, **(headers or {})})
        with request.urlopen(req, data) as res:
            return json.loads(res.read())
