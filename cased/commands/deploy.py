import click
import questionary
from rich.console import Console

from cased.utils.api import deploy_branch, get_branches
from cased.utils.auth import get_token
from cased.utils.progress import run_process_with_status_bar

console = Console()


def _build_questionary_choices():
    data = run_process_with_status_bar(get_branches, "Fetching branches...", timeout=10)
    branches = data.get("pull_requests", [])
    deployable_branches = [
        branch for branch in branches if branch["deployable"] is True
    ]
    # Prepare choices for questionary
    choices = [
        f"{b['branch_name']} -> [{', '.join([target.get('name') for target in b.get('targets', [])])}]"  # noqa: E501
        for b in deployable_branches
    ]

    if not choices:
        console.print("[red]No deployable branches available.[/red]")
        return

    selected = questionary.select("Select a branch to deploy:", choices=choices).ask()

    branch = selected.split(" -> ")[0]

    # Find the selected branch in our data
    selected_branch = next(
        (b for b in deployable_branches if b["branch_name"] == branch), None
    )
    if not selected_branch:
        console.print(f"[red]Error: Branch {branch} is not deployable.[/red]")
        return

    available_targets = selected_branch["targets"]
    if not available_targets:
        console.print(f"[red]Error: No targets available for branch {branch}.[/red]")
        return
    target = questionary.select(
        "Select a target environment:", choices=available_targets
    ).ask()

    return branch, target


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
    """  # noqa: E501
    token = get_token()
    if not token:
        console.print("[red]Please log in first using 'cased login'[/red]")
        return

    if not branch and not target:
        branch, target = _build_questionary_choices()

    console.print(
        f"Preparing to deploy [cyan]{branch}[/cyan] to [yellow]{target}[/yellow]"
    )

    if branch and target:
        deploy_branch(branch, target)
        console.print("[green]Dispatch succeeded. Starting deployment...[/green]")
    else:
        console.print("[red]Deployment dispatch failed. Please try again later.[/red]")
