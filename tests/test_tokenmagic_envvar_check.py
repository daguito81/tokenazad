from tokenazad.tokenmagic import AzureADTokenSetter
from tokenazad.utils.errors import BadClientException
from tests.conftest import MainTestSetup
import dotenv
import os

dotenv.load_dotenv()


class TestTokenazadNoEnvVar(MainTestSetup):

    def test_tokenmagic_noenv_missing_tenant(self):
        client = os.getenv("CLIENT_ID")
        secret = os.getenv("CLIENT_SECRET")
        scope = os.getenv("OAUTH_SCOPE")
        try:
            client = AzureADTokenSetter(None, client, secret, scope)
            client.do_magic_trick()
            assert 0
        except BadClientException as e:
            assert str(e) == "TENANT_ID is not set as Environment Variable"

    def test_tokenmagic_noenv_missing_client(self):
        tenant = os.getenv("TENANT_ID")
        secret = os.getenv("CLIENT_SECRET")
        scope = os.getenv("OAUTH_SCOPE")
        try:
            client = AzureADTokenSetter(tenant, None, secret, scope)
            client.do_magic_trick()
            assert 0
        except BadClientException as e:
            assert str(e) == "CLIENT_ID is not set as Environment Variable"

    def test_tokenmagic_noenv_missing_secret(self):
        tenant = os.getenv("TENANT_ID")
        client = os.getenv("CLIENT_ID")
        scope = os.getenv("OAUTH_SCOPE")
        try:
            client = AzureADTokenSetter(tenant, client, None, scope)
            client.do_magic_trick()
            assert 0
        except BadClientException as e:
            assert str(e) == "CLIENT_SECRET is not set as Environment Variable"

    def test_tokenmagic_noenv_missing_scope(self):
        tenant = os.getenv("TENANT_ID")
        client = os.getenv("CLIENT_ID")
        secret = os.getenv("CLIENT_SECRET")
        try:
            client = AzureADTokenSetter(tenant, client, secret, None)
            client.do_magic_trick()
            assert 0
        except BadClientException as e:
            assert str(e) == "OAUTH_SCOPE is not set as Environment Variable"