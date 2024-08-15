import click
from rich.console import Console
from rich.table import Table
from rich.text import Text
from dateutil import parser


from cased.utils.auth import get_token
from cased.utils.api import get_branches, get_targets, get_deployments
from cased.utils.progress import run_process_with_status_bar

console = Console()


@click.command()
@click.option("--limit", default=5, help="Number of deployments to show")
def deployments(limit):
    """
    Display recent deployments.

    This command shows a table of recent deployments, including information
    such as begin time, end time, deployer, status, branch, and target.

    Use the --limit option to specify the number of deployments to display.
    """
    token = get_token()
    if not token:
        console.print("[red]Please log in first using 'cased login'[/red]")
        return

    table = Table(title="Recent Deployments")

    table.add_column("Begin Time", style="cyan")
    table.add_column("End Time", style="cyan")
    table.add_column("Deployer", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Branch", style="yellow")
    table.add_column("Target", style="blue")
    table.add_column("View", style="cyan")

    data = get_deployments().get("deployments", [])

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
        view_url = f"https://cased.com/deployments/{deployment_id}"
        deployer_full_name = f"{deployment.get("deployer").get("first_name")} {deployment.get("deployer").get("last_name")}" if deployment.get("deployer") else "Unknown"

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
@click.option("--limit", default=5, help="Number of branches to show")
def branches(limit):
    """
    Display active branches.

    This command shows a table of active branches, including information
    such as name, author, PR number, PR title, deployable status, and various checks.

    Use the --limit option to specify the number of branches to display.
    """
    token = get_token()
    if not token:
        console.print("[red]Please log in first using 'cased login'[/red]")
        return

    table = Table(title="Active Branches")

    table.add_column("Name", style="cyan")
    table.add_column("Author", style="magenta")
    table.add_column("PR Number", style="yellow")
    table.add_column("PR Title", style="green")
    table.add_column("Deployable", style="blue")
    table.add_column("Mergeable", style="blue")
    table.add_column("Checks", style="cyan")
    
    data = run_process_with_status_bar(get_branches, "Fetching branches...", timeout=10)
    branches = data.get("pull_requests", [])
    # Generate fake data
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
                    f"approved: {branch.get("approved")}",
                    f"up-to-date: {branch.get("up_to_date")}",
                    f"checks-passed: {branch.get("checks_passing")}",
                ]
            ),
        )

    console.print(table)
