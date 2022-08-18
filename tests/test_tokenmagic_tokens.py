import pytest

from tests.conftest import MainTestSetup
from tokenazad.tokenmagic import AzureADTokenSetter
import os
import dotenv

dotenv.load_dotenv()


class TestTokenazadTokens(MainTestSetup):

    def test_tokenazad_token_getter(self, token_client):
        assert token_client.token is not None
        assert "access_token" in token_client.token
        assert "expires_in" in token_client.token
        assert token_client.token["access_token"] is not None
        assert int(token_client.token["expires_in"]) > 60

    def test_tokenazad_token_setter_no_service(self, token_client):
        token_client._set_token_env_var()
        assert os.environ["TOKEN"] is not None and os.environ["TOKEN"] != ""
        assert os.environ["TOKEN_TIME_UTC"] is not None and os.environ["TOKEN_TIME_UTC"] != ""
        assert os.environ["TOKEN_TYPE"] is not None and os.environ["TOKEN_TYPE"] != ""

    @pytest.mark.parametrize("service", ["SNOWFLAKE", "AZURE", "DATABRICKS", "SQL"])
    def test_tokenazad_token_setter_with_service(self, token_client, service):
        self.cleanup(service)
        token_client.var_prefix = service
        token_client._set_token_env_var()
        print(f"Testing {service}")
        assert os.environ[f"{service}_TOKEN"] is not None and os.environ[f"{service}_TOKEN"] != ""
        assert os.environ[f"{service}_TOKEN_TIME_UTC"] is not None and os.environ[f"{service}_TOKEN_TIME_UTC"] != ""
        assert os.environ[f"{service}_TOKEN_TYPE"] is not None and os.environ[f"{service}_TOKEN_TYPE"] != ""
        assert os.getenv("TOKEN", "NA") == "NA"
        assert os.getenv("TOKEN_TIME_UTC", "NA") == "NA"
        assert os.getenv("TOKEN_TYPE", "NA") == "NA"
        assert token_client._error is None
        self.cleanup(service)

    def test_tokenazad_token_setter_bad_creds(self, token_client):
        TENANT = os.getenv('TENANT_ID')
        CLIENT_ID = os.getenv('CLIENT_ID')
        CLIENT_SECRET = "bad_secret"

        client = AzureADTokenSetter(TENANT, CLIENT_ID, CLIENT_SECRET)
        client._get_token_client_secret()
        client._set_token_env_var()
        assert os.getenv("TOKEN", "NA") == "NA"
        assert os.getenv("TOKEN_TIME_UTC", "NA") == "NA"
        assert os.getenv("TOKEN_TYPE", "NA") == "NA"
        assert client._error is not None
        assert client._error == "invalid_client"
        self.cleanup()

    def test_tokenazad_token_setting_fail(self, token_client):
        failure_trigger = "access_token"
        token_client._token.pop(failure_trigger)
        token_client._set_token_env_var()
        assert os.getenv("TOKEN", "NA") == "NA"
        assert os.getenv("TOKEN_TIME_UTC", "NA") == "NA"
        assert os.getenv("TOKEN_TYPE", "NA") == "NA"
        assert token_client._error is not None
        assert token_client._error == f"KeyError: '{failure_trigger}'"
        self.cleanup()