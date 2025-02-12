"""
Cased CLI Tool

This script provides a command-line interface for interacting with the Cased API.
It offers functionality to manage projects, view deployments, list targets, and display active branches.

The tool uses the Click library for creating CLI commands and the Rich library for enhanced console output.
It also utilizes questionary for interactive prompts and the Cased API client for data retrieval.

Commands:
    projects: Display and select Cased projects.
    deployments: Show recent deployments for a selected project and target.
    targets: List target environments for a selected project.
    branches: Display active branches with various details.

Each command supports different options for customizing the output and filtering results.

Usage:
    cased [COMMAND] [OPTIONS]

For detailed usage of each command, use the --help option:
    cased [COMMAND] --help

Dependencies:
    - click
    - questionary
    - rich
    - dateutil

Author: Cased
Date: 10/01/2024
Version: 1.0.0
"""  # noqa: E501

import click
import questionary
from cased_cli.utils.api import CasedAPI
from cased_cli.utils.auth import validate_credentials
from cased_cli.utils.config import load_config, save_config
from cased_cli.utils.constants import CasedConstants
from cased_cli.utils.progress import run_process_with_status_bar
from dateutil import parser
from questionary import Style
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

# Custom style for questionary
custom_style = Style(
    [
        ("qmark", "fg:#673ab7 bold"),  # token in front of the question
        ("question", "bold"),  # question text
        ("answer", "fg:#f44336 bold"),  # submitted answer text behind the question
        ("pointer", "fg:#673ab7 bold"),  # pointer used in select and checkbox prompts
        (
            "highlighted",
            "fg:#673ab7 bold",
        ),  # pointed-at choice in select and checkbox prompts
        ("selected", "fg:#cc5454"),  # style for a selected item of a checkbox
        ("separator", "fg:#cc5454"),  # separator in lists
        ("instruction", ""),  # user instructions for select, rawselect, checkbox
        ("text", ""),  # plain text
        (
            "disabled",
            "fg:#858585 italic",
        ),  # disabled choices for select and checkbox prompts
    ]
)


@click.command()
@click.option(
    "--details",
    "-d",
    is_flag=True,
    default=True,
    help="Show detailed information about projects",
)
@validate_credentials(check_project_set=False)
def projects(details=True):
    """
    Display and select Cased projects.

    This command shows a list of available projects and allows you to select one as your current working project.
    If a project is already selected, it will be highlighted in the list.
    The selected project's name and ID are stored as environment variables for future use.

    Use the --details or --d option to show detailed information about each project, by default it is set to True.
    """  # noqa: E501
    # Check if a project is already selected
    config = load_config()
    current_project_name = config.get(CasedConstants.CASED_WORKING_PROJECT_NAME)
    current_project_id = config.get(CasedConstants.CASED_WORKING_PROJECT_ID)

    raw_projects = CasedAPI().get_projects()
    projects = [
        {
            "id": project["id"],
            "repository_full_name": project["repository_full_name"],
            "code_host": project["code_host"],
            "latest_deployment": (
                project["latest_deployment"].get("branch")
                if project["latest_deployment"]
                else "N/A"
            ),
        }
        for project in raw_projects["projects"]
    ]

    if details:
        table = Table(title="Projects Details", box=box.ROUNDED)
        table.add_column("Repository", style="magenta")
        table.add_column("Code Host", style="green")
        table.add_column("Latest Deployment", style="yellow")

        for project in projects:
            row_style = "bold" if str(project["id"]) == current_project_id else ""
            table.add_row(
                project["repository_full_name"],
                project["code_host"],
                project["latest_deployment"],
                style=row_style,
            )

        console.print(table)

    if current_project_name and current_project_id:
        console.print(
            f"[bold green]Currently working on:[/bold green] {current_project_name}"
        )
        console.print()
    else:
        console.print(
            "[yellow]No project selected. Please select a project from the list below:[/yellow]"
        )
    choices = ["Exit without changing project"]
    choices.extend(
        [
            f"{project['repository_full_name']} ({project['code_host']})"
            for project in projects
        ]
    )

    try:
        selection = questionary.select(
            "Select a project:", choices=choices, style=custom_style
        ).ask()
    except KeyboardInterrupt:
        console.print("[yellow]Exiting without changing project.[/yellow]")
        return

    if not selection:
        console.print("[yellow]No project selected. [/yellow]")
        return

    if selection == "Exit without changing project":
        console.print("[yellow]No updates.[/yellow]")
        return

    # Extract project ID from selection
    selected_id = int(selection.split(" - ")[0])

    # Update environment variables
    selected_project = next(p for p in projects if p["id"] == selected_id)
    selected_data = {
        CasedConstants.CASED_WORKING_PROJECT_NAME: selected_project[
            "repository_full_name"
        ],
        CasedConstants.CASED_WORKING_PROJECT_ID: str(selected_id),
    }
    save_config(selected_data)

    console.print(
        Panel(
            f"[bold green]Project updated:[/bold green] {selected_project['repository_full_name']}"
        )
    )


@click.command()
@click.option("--limit", default=5, help="Number of deployments to show")
@click.option("--project", default="", help="Project name to filter branches")
@click.option("--target", default="", help="Target name to filter branches")
@validate_credentials(check_project_set=True)
def deployments(limit, project, target):
    """
    Display recent deployments.

    This command shows a table of recent deployments, including information
    such as begin time, end time, deployer, status, branch, and target.

    Use the --limit option to specify the number of deployments to display.
    Use the --project and --target options to filter deployments by project and target.
    """
    data = (
        CasedAPI()
        .get_deployments(project_name=project, target_name=target)
        .get("deployments", [])
    )
    if not data:
        console.print("[red]No deployments available.[/red]")
        return

    deployments_data = []
    for idx, deployment in enumerate(data):
        if idx == limit:
            break
        begin_time = parser.parse(deployment.get("start_time"))
        end_time = (
            parser.parse(deployment.get("end_time"))
            if deployment.get("end_time")
            else ""
        )
        status = deployment.get("status", "Unknown")
        deployment_id = deployment.get("id")
        view_url = f"{CasedConstants.API_BASE_URL}/deployments/{deployment_id}"
        deployer_full_name = (
            f"{deployment.get('deployer').get('first_name')} {deployment.get('deployer').get('last_name')}"  # noqa: E501
            if deployment.get("deployer")
            else "Unknown"
        )

        deployments_data.append(
            {
                "begin_time": begin_time,
                "end_time": end_time,
                "deployer": deployer_full_name,
                "status": status,
                "branch": deployment.get("ref").replace("refs/heads/", ""),
                "target": deployment.get("target").get("name"),
                "view": (deployment_id, view_url),
            }
        )

    # Sort deployments by start time in descending order
    deployments_data.sort(key=lambda x: x["begin_time"], reverse=True)

    # Add sorted data to the table
    table = Table(title="Recent Deployments")

    table.add_column("Begin Time", style="cyan")
    table.add_column("End Time", style="cyan")
    table.add_column("Deployer", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Branch", style="yellow")
    table.add_column("Target", style="blue")
    table.add_column("View", style="cyan")

    for deployment in deployments_data:
        table.add_row(
            deployment["begin_time"].strftime("%Y-%m-%d %H:%M"),
            (
                deployment["end_time"].strftime("%Y-%m-%d %H:%M")
                if deployment["end_time"]
                else "NULL"
            ),
            deployment["deployer"],
            deployment["status"],
            deployment["branch"],
            deployment["target"],
            Text(
                f"View {deployment['view'][0]}", style=f"link {deployment['view'][1]}"
            ),
        )

    console.print(table)


@click.command()
@click.option("--project", default="", help="Project name to filter branches")
@validate_credentials(check_project_set=True)
def targets(project):
    """
    Display target environments.

    This command shows a list of target environments for the selected project.
    """
    data = run_process_with_status_bar(
        CasedAPI().get_targets, "Fetching targets...", timeout=10, project_name=project
    )
    targets = data.get("targets", [])
    if not targets:
        console.print("[red]No targets available.[/red]")
        return

    table = Table(title="Targets")

    table.add_column("Name", style="cyan")

    for target in targets:
        table.add_row(
            target.get("name"),
        )

    console.print(table)


@click.command()
@click.option("--limit", default=5, help="Number of branches to show")
@click.option("--project", default="", help="Project name to filter branches")
@validate_credentials(check_project_set=True)
def branches(limit, project):
    """
    Display active branches.

    This command shows a table of active branches, including information
    such as name, author, PR number, PR title, deployable status, and various checks.

    Use the --limit option to specify the number of branches to display.
    Use the --project option to filter branches by project.
    """
    data = run_process_with_status_bar(
        CasedAPI().get_branches,
        "Fetching branches...",
        timeout=10,
        project_name=project,
    )
    branches = data.get("pull_requests", [])
    print(len(branches))

    table = Table(title="Active Branches")

    table.add_column("Name", style="cyan")
    table.add_column("Author", style="magenta")
    table.add_column("PR Number", style="yellow")
    table.add_column("PR Title", style="green")
    table.add_column("Deployable", style="blue")
    table.add_column("Mergeable", style="blue")
    table.add_column("Checks", style="cyan")
    for idx, branch in enumerate(branches):
        if idx == limit:
            break

        table.add_row(
            branch.get("branch_name"),
            branch.get("owner"),
            str(branch.get("number")),
            branch.get("title"),
            str(branch.get("deployable")),
            str(branch.get("mergeable")),
            ", ".join(
                [
                    f"approved: {branch.get('approved')}",
                    f"up-to-date: {branch.get('up_to_date')}",
                    f"checks-passed: {branch.get('checks_passing')}",
                ]
            ),
        )

    console.print(table)
