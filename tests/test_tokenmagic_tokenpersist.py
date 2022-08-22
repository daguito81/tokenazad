import time

import pytest

from tests.conftest import MainTestSetup
import dotenv

dotenv.load_dotenv()


class TestTokenazadTokenPersist(MainTestSetup):

    @pytest.mark.parametrize("service", ["SNOWFLAKE", "AZURE", "DATABRICKS", "SQL", None])
    def test_tokenmagic_token_persist_no_path(self, token_client, service):
        token_client.var_prefix = service
        token_client.do_magic_trick()
        token_client.persist_token(service)
        with open(f"/tmp/tokenazad/{service}.token", "r") as f:
            token = f.read()
            token.strip()
        assert token == token_client.token['access_token']

    @pytest.mark.parametrize("service, custom_path_suffix", [
        ("SNOWFLAKE", "tokenazad/custom"),
        ("SNOWFLAKE", "tokenazad/custom/"),
        (None, "tokenazad/custom"),
        (None, "tokenazad/custom/"),
        ("AZURE", "tokenazad/custom"),
        ("DATABRICKS", "tokenazad/custom/"),
        ("SQL", "tokenazad/custom"),
    ])
    def test_tokenmagic_token_persist_with_path(self, token_client, service, custom_path_suffix, tmp_path):
        custom_path = tmp_path / custom_path_suffix
        token_client.var_prefix = service
        token_client.do_magic_trick()
        token_client.persist_token(service, custom_path)
        with open(f"{custom_path}/{service}.token", "r") as f:
            token = f.read()
            token.strip()
        assert token == token_client.token['access_token']
