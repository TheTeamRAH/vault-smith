import os
from unittest.mock import patch
from app.main import app


def test_vaults_are_discovered_from_environment():
    with patch.dict(os.environ, {"ANSIBLE_VAULT_HOME": "secret", "ANSIBLE_VAULT_EMPTY": ""}, clear=True):
        assert app.test_client().get("/api/vaults").json == {"vaults": ["HOME"]}


def test_encrypt_returns_ansible_output():
    with patch.dict(os.environ, {"ANSIBLE_VAULT_HOME": "secret"}, clear=True), patch("app.main.subprocess.run") as run:
        run.return_value.returncode = 0
        run.return_value.stdout = "foo: !vault |\n  $ANSIBLE_VAULT;1.2;AES256;HOME\n"
        response = app.test_client().post("/api/encrypt", json={"vault_id":"HOME", "variable":"foo", "value":"bar"})
        assert response.status_code == 200
        output = response.json["result"]
        assert output.startswith("foo: !vault |\n  $ANSIBLE_VAULT")
        assert all(line.strip() for line in output.splitlines())
        assert all(line.startswith("  ") for line in output.splitlines()[1:])
        assert run.call_args.args[0][0].endswith("/ansible-vault")
        assert run.call_args.args[0][3] == "HOME@/dev/stdin"
        run.assert_called_once()


def test_encrypt_without_variable_returns_content_only():
    with patch.dict(os.environ, {"ANSIBLE_VAULT_HOME": "secret"}, clear=True), patch("app.main.subprocess.run") as run:
        run.return_value.returncode = 0
        run.return_value.stdout = "!vault |\n          $ANSIBLE_VAULT;1.2;AES256;HOME\n"
        response = app.test_client().post("/api/encrypt", json={"vault_id":"HOME", "variable":"", "value":"bar"})
        assert response.status_code == 200
        output = response.json["result"]
        assert output.startswith("  $ANSIBLE_VAULT")
        assert "!vault |" not in output
        assert all(line.startswith("  ") for line in output.splitlines())
        assert "--name" not in run.call_args.args[0]


def test_unknown_vault_is_rejected():
    with patch.dict(os.environ, {}, clear=True):
        response = app.test_client().post("/api/encrypt", json={"vault_id":"NOPE", "variable":"foo", "value":"bar"})
        assert response.status_code == 400
