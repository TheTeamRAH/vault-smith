# Vaultsmith

A small containerised web UI for `ansible-vault encrypt_string`, designed for safe mobile use. Vault passwords are supplied only as deployment environment variables named `ANSIBLE_VAULT_<VAULT_ID>` and are never returned by the API.

## Development

Install [uv](https://docs.astral.sh/uv/) and run:

```bash
uv sync
ANSIBLE_VAULT_HOME=not-a-real-password uv run python app/main.py
```

Run the tests with `uv run pytest`. The lockfile is committed so local and container installs use the same resolved dependencies. Deploy with `docker compose up -d --build`; set vault variables in the deployment environment first. The app currently supports encryption only; the API/UI are structured so a future decrypt flow can be added separately.

## Security boundary

This app should be placed behind the homelab's normal reverse proxy/access controls. Do not commit vault passwords, `.env` files, or generated vaulted values.
