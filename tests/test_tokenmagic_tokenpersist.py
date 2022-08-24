import pytest

from tests.conftest import MainTestSetup
import dotenv

dotenv.load_dotenv()


class TestTokenazadTokenPersist(MainTestSetup):

    @pytest.mark.parametrize("service", ["SNOWFLAKE", "AZURE", "DATABRICKS", "SQL", None])
    def test_tokenmagic_token_persist_no_path(self, token_client, service):
        token_client.var_prefix = service
        token_client.do_magic_trick()
        token_client.persist_token()
        if service is None:
            file_name = "TOKEN.token"
        else:
            file_name = f"{service}.token"
        with open(f"/tmp/tokenazad/{file_name}", "r") as f:
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
        token_client.var_prefix = service if service != "None" else None
        token_client.do_magic_trick()
        token_client.persist_token(custom_path)
        if service is None:
            full_path = custom_path / "TOKEN.token"
        else:
            full_path = custom_path / f"{service}.token"
        with open(full_path, "r") as f:
            token = f.read()
            token.strip()
        assert token == token_client.token['access_token']
