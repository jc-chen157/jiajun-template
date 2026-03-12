from domino.base_piece import BasePiece
from .models import InputModel, OutputModel
import requests
import base64
import json


class BulkHttpRequestPiece(BasePiece):
    def piece_function(self, input_data: InputModel):
        method = input_data.method
        headers = {}
        if input_data.bearer_token:
            headers['Authorization'] = f'Bearer {input_data.bearer_token}'

        body_data = None
        if method in ["POST", "PUT"]:
            try:
                body_data = json.loads(input_data.body_json_data)
            except json.JSONDecodeError:
                raise Exception("Invalid JSON data in the request body.")

        base64_bytes_data_list = []
        errors = []

        for i, url in enumerate(input_data.urls):
            try:
                self.logger.info(f"Making {method} request to {url} ({i+1}/{len(input_data.urls)})")
                if method == "GET":
                    response = requests.get(url, headers=headers)
                elif method == "POST":
                    response = requests.post(url, headers=headers, json=body_data)
                elif method == "PUT":
                    response = requests.put(url, headers=headers, json=body_data)
                elif method == "DELETE":
                    response = requests.delete(url, headers=headers)
                else:
                    raise Exception(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                base64_data = base64.b64encode(response.content).decode('utf-8')
                self.logger.info(
                    f"URL {url}: response size={len(response.content)} bytes, "
                    f"content_type={response.headers.get('content-type', 'unknown')}, "
                    f"base64 length={len(base64_data)}"
                )
                base64_bytes_data_list.append(base64_data)
                errors.append("")
            except Exception as e:
                self.logger.info(f"Error for URL {url}: {e}")
                base64_bytes_data_list.append("")
                errors.append(str(e))

        self.logger.info(
            f"Completed {len(input_data.urls)} requests: "
            f"{sum(1 for e in errors if e == '')} succeeded, "
            f"{sum(1 for e in errors if e != '')} failed"
        )

        return OutputModel(
            base64_bytes_data_list=base64_bytes_data_list,
            errors=errors,
        )
