import time

import pytest

from tests.conftest import MainTestSetup
from tokenazad.tokenmagic import main
import os
import dotenv

dotenv.load_dotenv()


class TestTokenazadEnd2End(MainTestSetup):

    @staticmethod
    def check_env(service):
        if service is not None:
            assert os.environ[f"{service}_TOKEN"] is not None and os.environ[f"{service}_TOKEN"] != ""
            assert os.environ[f"{service}_TOKEN_TIME_UTC"] is not None \
                   and os.environ[f"{service}_TOKEN_TIME_UTC"] != ""
            assert os.environ[f"{service}_TOKEN_TYPE"] is not None \
                   and os.environ[f"{service}_TOKEN_TYPE"] != ""
        else:
            assert os.environ["TOKEN"] is not None and os.environ["TOKEN"] != ""
            assert os.environ["TOKEN_TIME_UTC"] is not None and os.environ["TOKEN_TIME_UTC"] != ""
            assert os.environ["TOKEN_TYPE"] is not None and os.environ["TOKEN_TYPE"] != ""

    @pytest.mark.parametrize("service", ["SNOWFLAKE", "AZURE", "DATABRICKS", "SQL", None])
    def test_tokenmagic_end2end(self, token_client, service):
        token_client.var_prefix = service
        token_client.do_magic_trick()
        self.check_env(service)

    @pytest.mark.parametrize("service", ["SNOWFLAKE", "AZURE", "DATABRICKS", "SQL", None])
    def test_tokenmagic_main(self, service):
        self.cleanup(service)
        main(service)
        self.check_env(service)

    def test_tokenmagic_low_expiration(self, token_client):
        token_expiration = 10
        start = time.time()
        token_client._client_id = "bad_id"
        token_client._token = {"access_token": "bad_token", "expires_in": "1"}
        token_client.ready = False
        token_client._token_expiration_min = token_expiration
        token_client.do_magic_trick()
        stop = time.time()
        assert stop - start > token_expiration

    def test_tokenmagic_bad_expiration_key(self, token_client):
        token_client._token = {"no_good_token": True, "error": "test_error"}
        token_client.ready = False
        token_client.do_magic_trick()
        assert token_client._error == "test_error"
