import os

from cased.utils.constants import CasedConstants


def load_config(file_path=CasedConstants.ENV_FILE):
    if not os.path.exists(file_path):
        return None
    config = {}
    with open(file_path, "r") as f:
        for line in f:
            key, value = line.strip().split("=", 1)
            config[key] = value
    return config


def save_config(
    data, config_dir=CasedConstants.CONFIG_DIR, file_name=CasedConstants.ENV_FILE
):
    os.makedirs(config_dir, mode=0o700, exist_ok=True)
    current_config = load_config(file_name)
    if not current_config:
        current_config = {}
    current_config.update(data)
    with open(file_name, "w") as f:
        for key, value in current_config.items():
            f.write(f"{key}={value}\n")


def delete_config(file_name=CasedConstants.ENV_FILE):
    if os.path.exists(file_name):
        os.remove(file_name)
