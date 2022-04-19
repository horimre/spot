from Sec import client_id, client_secret, refresh_token
import requests
from requests.exceptions import HTTPError
import base64
import logging


class Refresh:

    def __init__(self):
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.client_secret = client_secret

    def refresh(self):
        # logging.basicConfig(level=logging.INFO)

        url = "https://accounts.spotify.com/api/token"

        # base64 client credentials
        cred = f"{self.client_id}:{self.client_secret}"
        cred_bytes = cred.encode('ascii')
        cred_base64_bytes = base64.b64encode(cred_bytes)
        cred_base64 = cred_base64_bytes.decode('ascii')

        # request for token
        try:
            response = requests.post(url,
                                     data={"grant_type": "refresh_token",
                                           "refresh_token": self.refresh_token},
                                     headers={"Authorization": "Basic " + cred_base64}
                                     )
            response.raise_for_status()
        except HTTPError as http_err:
            logging.error(f"Request failed. HTTP error: {http_err} Message: {response.text}")
            return
        except Exception as e:
            logging.error(f"Other Error: {e}", exc_info=True)
            return
        else:
            logging.info(f"Request finished successfully. "
                         f"Status code: {response.status_code} "
                         f"Reason: {response.reason}")

            response_json = response.json()
            return response_json["access_token"]
