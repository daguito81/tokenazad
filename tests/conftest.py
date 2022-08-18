import pytest
import os
from tokenazad.tokenmagic import AzureADTokenSetter


class MainTestSetup:
    @staticmethod
    def cleanup(service=None):
        # Cleanup
        os.environ.pop("TOKEN", None)
        os.environ.pop("TOKEN_TIME_UTC", None)
        os.environ.pop("TOKEN_TYPE", None)
        if service is not None:
            os.environ.pop(f"{service}_TOKEN", None)
            os.environ.pop(f"{service}_TOKEN_TIME_UTC", None)
            os.environ.pop(f"{service}_TOKEN_TYPE", None)

    @pytest.fixture(scope="session")
    def token_client(self, service=None):
        self.cleanup(service)
        TENANT = os.getenv('TENANT_ID')
        CLIENT_ID = os.getenv('CLIENT_ID')
        CLIENT_SECRET = os.getenv('CLIENT_SECRET')
        client = AzureADTokenSetter(TENANT, CLIENT_ID, CLIENT_SECRET, service)
        client._get_token_client_secret()
        yield client
        self.cleanup(service)
