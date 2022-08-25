from __future__ import annotations

from tokenazad.utils.errors import BadClientException

import dotenv
import os
import logging
import time
from datetime import datetime as datetime
import sys
from pathlib import Path

from typing import Dict, Optional
from msal import ConfidentialClientApplication


class AzureADTokenSetter:
    def __init__(self, tenant, client_id, client_secret, oauth_scope,
                 var_prefix=None, token_expiration_min=60) -> None:
        self._tenant: str = tenant
        self._client_id: str = client_id
        self.__client_secret: str = client_secret
        self._oauth_scope: str = oauth_scope
        self._token: Optional[Dict[str, str]] = None
        self._app: Optional[ConfidentialClientApplication] = None
        self.ready: bool = False
        self.var_prefix: Optional[str] = var_prefix
        self._error: Optional[str] = None
        self._token_expiration_min: int = token_expiration_min
        self._init_check()
        self._create_client()

    def _init_check(self) -> None:
        if self._tenant is None:
            logging.error("TENANT_ID is not set as Environment Variable")
            self._error = "TENANT_ID is not set as Environment Variable"
            raise BadClientException(self._error)
        if self._client_id is None:
            logging.error("CLIENT_ID is not set as Environment Variable")
            self._error = "CLIENT_ID is not set as Environment Variable"
            raise BadClientException(self._error)
        if self.__client_secret is None:
            logging.error("CLIENT_SECRET is not set as Environment Variable")
            self._error = "CLIENT_SECRET is not set as Environment Variable"
            raise BadClientException(self._error)
        if self._oauth_scope is None:
            logging.error("OAUTH_SCOPE is not set as Environment Variable")
            self._error = "OAUTH_SCOPE is not set as Environment Variable"
            raise BadClientException(self._error)

    def _create_client(self):
        try:
            temp_client = ConfidentialClientApplication(self._client_id, self.__client_secret,
                                                        authority=f'https://login.microsoftonline.com/{self._tenant}')
            self._app = temp_client
            self.ready = True
        except Exception as e:
            logging.error(e)
            self._error = str(e)

    def _get_token_client_secret(self) -> None:
        if self.ready:
            result: Dict[str, str] = self._app.acquire_token_for_client(scopes=[self._oauth_scope])
            try:
                _ = result['access_token']
            except KeyError:
                logging.error("Token was not pulled because of an Error")
                logging.error(result['error'])
                logging.error(result['error_description'])
                self.ready = False
                self._error = result['error']
                return
            self._token = result
        else:
            logging.error('Client not ready, probably credentials error. Recreate client')

    def _set_token_env_var(self) -> None:
        if self._token is not None:
            try:
                if self.var_prefix is not None:
                    os.environ[f'{self.var_prefix}_TOKEN'] = self._token['access_token']
                    os.environ[f'{self.var_prefix}_TOKEN_TYPE'] = self._token['token_type']
                    os.environ[f'{self.var_prefix}_TOKEN_TIME_UTC'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
                else:
                    os.environ['TOKEN'] = self._token['access_token']
                    os.environ['TOKEN_TYPE'] = self._token['token_type']
                    os.environ['TOKEN_TIME_UTC'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

            except KeyError as e:
                logging.error("Token not set because it was empty")
                self._error = "KeyError: " + str(e)
                logging.error(self._error)
                return

    def do_magic_trick(self) -> None:
        self._get_token_client_secret()
        try:
            expiration: int = int(self._token['expires_in'])
            if expiration < self._token_expiration_min:
                logging.info("Expiration less than 60 seconds, waiting to get new token")
                time.sleep(self._token_expiration_min)
                self._get_token_client_secret()
        except KeyError:
            logging.error("Token was not pulled because of an Error")
            logging.error(self._token['error'])
            self._error = self._token['error']
            return
        self._set_token_env_var()

    def persist_token(self, persist_path=None) -> None:
        """
        This function will persist the token in a local filepath
        :return:
        """
        token_to_write = self._token['access_token']
        service = self.var_prefix if self.var_prefix is not None else "TOKEN"
        if persist_path is not None:
            file_path = Path(persist_path) / f"{service}.token"
        else:
            file_path = Path(f'/tmp/tokenazad/{service}.token')

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(token_to_write)

    @property
    def token(self) -> Dict[str, str]:
        return self._token


def main(service: str) -> None:
    try:
        print("Running Module with Service: " + service)
    except TypeError:
        print("Running Module with Generic Service")
    dotenv.load_dotenv()

    tenant = os.getenv('TENANT_ID')
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    oauth_scope = os.getenv('OAUTH_SCOPE')

    print("Creating Client")
    client: AzureADTokenSetter = AzureADTokenSetter(tenant, client_id, client_secret, oauth_scope, service)
    print("Getting Token")
    client.do_magic_trick()
    print("Persisting Token")
    client.persist_token()
    print("Done")


if __name__ == '__main__':
    service_prefix = sys.argv[1] if len(sys.argv) > 1  else None
    main(service_prefix)
