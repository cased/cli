"""
Cased CLI Authentication Module

This module provides command-line interface (CLI) functionality for authenticating
with the Cased system. It includes commands for logging in and out of the Cased
CLI, handling API key validation, and managing user sessions.

Dependencies:
    - click: For creating CLI commands
    - rich: For enhanced console output and user interaction
    - cased: Custom package for Cased-specific functionality

Commands:
    - login: Initiates the login process, validates credentials, and stores session information
    - logout: Removes locally stored credentials and logs the user out of the Cased CLI

The module uses the Rich library to provide a visually appealing and interactive
console interface, including progress bars and styled text output.

Usage:
    To use this module, import it into your main CLI application and add the
    login and logout commands to your command group.

Note:
    This module assumes the existence of various utility functions and constants
    from the cased package, which should be properly set up for the module to function correctly.

Author: Cased
Date: 10/01/2024
Version: 1.0.0
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.prompt import Prompt

from cased.commands.resources import projects
from cased.utils.api import validate_tokens
from cased.utils.auth import validate_credentials
from cased.utils.config import delete_config, save_config
from cased.utils.constants import CasedConstants

console = Console()


@click.command()
def login():
    """
    Log in to the Cased system.

    This command initiates a login process, stores a session token,
    and provides information about the session expiration.
    """
    console.print(Panel("Welcome to Cased CLI", style="bold blue"))

    org_name = Prompt.ask("Enter your organization name")
    api_key = Prompt.ask("Enter your API key", password=True)

    with Progress() as progress:
        task = progress.add_task("[cyan]Validating credentials...", total=100)

        # Simulate API call with progress
        for i in range(0, 101, 10):
            progress.update(task, advance=10)
            if i == 50:
                response = validate_tokens(api_key, org_name)
                progress.update(task, completed=100)

    # 200 would mean success,
    # 403 would mean validation success but necessary integration is not set up.
    # (E.g. Github)
    if response.status_code == 200 or response.status_code == 403:
        data = response.json()
    elif response.status_code == 401:
        console.print(
            Panel(
                f"[bold red]Unauthorized:[/bold red] Invalid API token. Please try again or check your API token at {CasedConstants.BASE_URL}/settings/",  # noqa: E501
                expand=False,
            )
        )
        return
    elif response.status_code == 404:
        console.print(
            Panel(
                f"[bold red]Organization not found:[/bold red] Please check your organization name at {CasedConstants.BASE_URL}/settings/",  # noqa: E501
                expand=False,
            )
        )
        return
    else:
        click.echo("Sorry, something went wrong. Please try again later.")
        return

    if data.get("validation"):
        org_id = data.get("org_id")
        data = {
            CasedConstants.CASED_API_AUTH_KEY: api_key,
            CasedConstants.CASED_ORG_ID: org_id,
            CasedConstants.CASED_ORG_NAME: org_name,
        }
        save_config(data)
        console.print(Panel("[bold green]Login successful![/bold green]", expand=False))
        # Ask user to select a project.
        ctx = click.get_current_context()
        ctx.invoke(projects, details=False)
    else:
        console.print(
            Panel(
                f"[bold red]Login failed:[/bold red] {data.get('reason', 'Unknown error')}",
                title="Error",
                expand=False,
            )
        )


@click.command()
@validate_credentials(check_project_set=False)
def logout():
    """
    Log out from your Cased account.

    This command removes all locally stored credentials,
    effectively logging you out of the Cased CLI.
    """
    delete_config()
    console.print(
        Panel("[bold green]Logged out successfully![/bold green]", expand=False)
    )
