import json
import os
import random
import stat
import tempfile
import time
from datetime import datetime, timedelta

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

from cased.utils.auth import CONFIG_DIR, TOKEN_FILE

console = Console()


def ensure_config_dir():
    # Create dir with restricted permissions if it doesn't exist
    os.makedirs(CONFIG_DIR, mode=0o700, exist_ok=True)


def secure_write(file_path, data):
    ensure_config_dir()
    # Write data to a file with restricted permissions
    with open(file_path, "w") as f:
        json.dump(data, f)
    os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)  # Read/write only for the owner


def create_temp_token_file(token_data):
    # Create a temporary file that will be automatically deleted after 24 hours
    temp_dir = tempfile.gettempdir()
    temp_file = tempfile.NamedTemporaryFile(
        mode="w+", delete=False, dir=temp_dir, prefix="cased_token_", suffix=".json"
    )

    with temp_file:
        json.dump(token_data, temp_file)

    os.chmod(
        temp_file.name, stat.S_IRUSR | stat.S_IWUSR
    )  # Read/write only for the owner

    # Schedule file for deletion after 24 hours
    deletion_time = datetime.now() + timedelta(hours=24)
    deletion_command = f"(sleep {(deletion_time - datetime.now()).total_seconds()} && rm -f {temp_file.name}) &"  # noqa: E501
    os.system(deletion_command)

    return temp_file.name


@click.command()
def login():
    """
    Log in to the Cased system.

    This command initiates a login process, stores a session token,
    and provides information about the session expiration.
    """
    with Progress() as progress:
        task1 = progress.add_task("[green]Initiating handshake...", total=100)
        task2 = progress.add_task("[yellow]Authenticating...", total=100)

        while not progress.finished:
            progress.update(task1, advance=100)
            time.sleep(0.25)
            progress.update(task2, advance=15)

    # Simulate getting a session token
    session_token = "fake_session_token_" + str(random.randint(1000, 9999))
    expiry = datetime.now() + timedelta(hours=24)  # Token expires in 1 hour

    token_data = {"token": session_token, "expiry": expiry.isoformat()}

    # Create a temporary token file
    temp_token_file = create_temp_token_file(token_data)

    # Store the path to the temporary file
    secure_write(TOKEN_FILE, {"temp_file": temp_token_file})

    # Calculate time until expiration
    time_until_expiry = expiry - datetime.now()
    hours, remainder = divmod(time_until_expiry.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    console.print(
        Panel(
            f"[green]Login successful![/green]\nSession token stored securely.\nSession expires in {hours} hours {minutes} minutes.",  # noqa: E501
            title="Login Status",
        )
    )


@click.command()
def logout():
    """
    Log out from the Cased system.

    This command removes the stored session token and ends the current session.
    """
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            data = json.load(f)
        temp_file = data.get("temp_file")

        # Remove the temporary token file if it exists
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)

        # Remove the token file in the config directory
        os.remove(TOKEN_FILE)

        console.print(
            Panel(
                "[green]Logout successful![/green]\nSession token has been removed.",
                title="Logout Status",
            )
        )
    else:
        console.print(
            Panel(
                "[yellow]No active session found.[/yellow]\nYou are already logged out.",  # noqa: E501
                title="Logout Status",
            )
        )
