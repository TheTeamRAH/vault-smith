# Vaultsmith

A small containerised web UI for `ansible-vault encrypt_string`, designed for safe mobile use. Vault passwords are supplied only as deployment environment variables named `ANSIBLE_VAULT_<VAULT_ID>` and are never returned by the API.

## Development

Install [uv](https://docs.astral.sh/uv/) and run:

```bash
uv sync
cp .env.example .env
# Edit .env and set ANSIBLE_VAULT_RAH before starting the app.
uv run python app/main.py
```

Run the tests with `uv run pytest`. The lockfile is committed so local and container installs use the same resolved dependencies. Deploy with `docker compose -f docker-compose.yml up -d --build`; set the vault password in an untracked `.env` file first. A variable name is optional: leave it blank to generate only the indented encrypted content block, without the `!vault |` header, for embedding under an existing variable.

## Security boundary

This app should be placed behind the homelab's normal reverse proxy/access controls. Do not commit vault passwords, `.env` files, or generated vaulted values.
