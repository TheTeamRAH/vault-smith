import os
import subprocess
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


def vaults():
    prefix = "ANSIBLE_VAULT_"
    return sorted(k[len(prefix):] for k in os.environ if k.startswith(prefix) and os.environ[k])


def encrypt(vault_id: str, variable: str, value: str) -> str:
    password = os.environ.get(f"ANSIBLE_VAULT_{vault_id}")
    if not password:
        raise ValueError("Unknown vault")
    if not variable or not variable.replace("_", "").isalnum() or variable[0].isdigit():
        raise ValueError("Variable names must start with a letter and contain letters, numbers, or underscores")
    if not value:
        raise ValueError("Value is required")
    proc = subprocess.run(
        ["ansible-vault", "encrypt_string", "--vault-id", f"{vault_id}@/dev/stdin", "--name", variable, value],
        input=password + "\n", text=True, capture_output=True, check=False,
    )
    if proc.returncode:
        raise RuntimeError("ansible-vault failed")
    return proc.stdout


@app.get("/")
def index():
    return render_template("index.html", vaults=vaults())


@app.get("/api/vaults")
def api_vaults():
    return jsonify({"vaults": vaults()})


@app.post("/api/encrypt")
def api_encrypt():
    data = request.get_json(silent=True) or {}
    try:
        result = encrypt(str(data.get("vault_id", "")), str(data.get("variable", "")), str(data.get("value", "")))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 502
    return jsonify({"result": result})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
