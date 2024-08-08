import os
import json
from datetime import datetime

# Configuration
CONFIG_DIR = os.path.expanduser("~/.cased/config")
TOKEN_FILE = os.path.join(CONFIG_DIR, "session_token")


def get_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            data = json.load(f)
        temp_file = data.get("temp_file")

        if temp_file and os.path.exists(temp_file):
            with open(temp_file, "r") as tf:
                token_data = json.load(tf)
                expiry = datetime.fromisoformat(token_data["expiry"])
                if datetime.now() < expiry:
                    return token_data["token"]

    return None
