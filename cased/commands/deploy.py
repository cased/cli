import time
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
import random
import questionary

from cased.utils.auth import get_token

console = Console()


def get_deployable_branches():
    # Simulate fetching deployable branches with their available targets
    branches = [
        {"name": "feature-branch-1", "targets": ["dev", "staging"]},
        {"name": "feature-branch-2", "targets": ["dev", "staging", "prod"]},
        {"name": "feature-branch-3", "targets": ["dev"]},
        {"name": "main", "targets": ["dev", "staging", "prod"]},
        {"name": "hotfix-branch", "targets": ["staging", "prod"]},
    ]
    return branches


def simulate_api_call(branch, target):
    time.sleep(1)  # Simulate network delay
    return random.choice(["dispatch succeeded", "failed"])


def run_deployment(branch, target):
    with Progress() as progress:
        deploy_task = progress.add_task(
            f"[green]Deploying {branch} to {target}...", total=100
        )
        while not progress.finished:
            progress.update(deploy_task, advance=0.5)
            time.sleep(0.1)
    console.print(f"[green]Deployment of {branch} to {target} completed successfully!")


@click.command()
@click.option("--branch", help="Branch to deploy")
@click.option("--target", help="Target environment for deployment")
def deploy(branch, target):
    """
    Deploy a branch to a target environment.

    This command allows you to deploy a specific branch to a target environment.
    If --branch or --target are not provided, you will be prompted to select from available options.

    The command will display deployable branches with their available targets, initiate the deployment process,
    and show the deployment progress.

    Examples:
        cased deploy
        cased deploy --branch feature-branch-1 --target dev
    """
    token = get_token()
    if not token:
        console.print("[red]Please log in first using 'cased login'[/red]")
        return

    deployable_branches = get_deployable_branches()

    if not branch:
        # Prepare choices for questionary
        choices = [
            f"{b['name']} -> [{', '.join(b['targets'])}]" for b in deployable_branches
        ]

        if not choices:
            console.print("[red]No deployable branches available.[/red]")
            return

        selected = questionary.select(
            "Select a branch to deploy:", choices=choices
        ).ask()

        branch = selected.split(" -> ")[0]

    # Find the selected branch in our data
    selected_branch = next(
        (b for b in deployable_branches if b["name"] == branch), None
    )
    if not selected_branch:
        console.print(f"[red]Error: Branch '{branch}' is not deployable.[/red]")
        return

    if not target:
        available_targets = selected_branch["targets"]
        if not available_targets:
            console.print(
                f"[red]Error: No targets available for branch '{branch}'.[/red]"
            )
            return
        target = questionary.select(
            "Select a target environment:", choices=available_targets
        ).ask()
    elif target not in selected_branch["targets"]:
        console.print(
            f"[red]Error: Target '{target}' is not available for branch '{branch}'.[/red]"
        )
        return

    console.print(
        f"Preparing to deploy [cyan]{branch}[/cyan] to [yellow]{target}[/yellow]"
    )

    # Simulate API call
    result = simulate_api_call(branch, target)

    if result == "dispatch succeeded":
        console.print("[green]Dispatch succeeded. Starting deployment...[/green]")
        run_deployment(branch, target)
    else:
        console.print("[red]Deployment dispatch failed. Please try again later.[/red]")
