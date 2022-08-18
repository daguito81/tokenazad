from tokenazad.tokenmagic import AzureADTokenSetter
import os
import dotenv

dotenv.load_dotenv()


class TestTokenazadClient:
    def test_tokenazad_client_generator(self):
        TENANT = os.getenv('TENANT_ID')
        CLIENT_ID = os.getenv('CLIENT_ID')
        CLIENT_SECRET = os.getenv('CLIENT_SECRET')
        client = AzureADTokenSetter(TENANT, CLIENT_ID, CLIENT_SECRET)
        client._get_token_client_secret()
        assert client._app is not None
        assert client.ready is True
        assert client._app.authority.authorization_endpoint == f"https://login.microsoftonline.com/{TENANT}" \
                                                               f"/oauth2/v2.0/authorize"
        assert client.token is not None
        assert "access_token" in client.token

    def test_tokenazad_client_failed_generator_bad_secret(self):
        TENANT = os.getenv('TENANT_ID')
        CLIENT_ID = os.getenv('CLIENT_ID')
        CLIENT_SECRET = "bad_secret"
        client = AzureADTokenSetter(TENANT, CLIENT_ID, CLIENT_SECRET)
        client._get_token_client_secret()
        assert client.ready is False
        assert client._app.authority.authorization_endpoint == f"https://login.microsoftonline.com/{TENANT}" \
                                                               f"/oauth2/v2.0/authorize"
        assert client.token is None
        assert client._error == "invalid_client"

    def test_tokenazad_client_failed_generator_bad_id(self):
        TENANT = os.getenv('TENANT_ID')
        CLIENT_ID = "bad_id"
        CLIENT_SECRET = os.getenv('CLIENT_SECRET')
        client = AzureADTokenSetter(TENANT, CLIENT_ID, CLIENT_SECRET)
        client._get_token_client_secret()
        assert client.ready is False
        assert client._app.authority.authorization_endpoint == f"https://login.microsoftonline.com/{TENANT}" \
                                                               f"/oauth2/v2.0/authorize"
        assert client.token is None
        assert client._error == "unauthorized_client"

    def test_tokenazad_client_failed_generator_bad_tenant(self):
        TENANT = "a34de1ed-779e-40e2-baa2-038614t129d8"  # Made up tenant id
        CLIENT_ID = os.getenv('CLIENT_ID')
        CLIENT_SECRET = os.getenv('CLIENT_SECRET')
        client = AzureADTokenSetter(TENANT, CLIENT_ID, CLIENT_SECRET)
        client._get_token_client_secret()
        assert client.ready is False
        assert client._app is None
        assert client.token is None
        assert client._error.startswith(
            f"Unable to get authority configuration for https://login.microsoftonline.com/{TENANT}.")
