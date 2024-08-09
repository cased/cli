import click
from rich.console import Console
from rich.table import Table
from rich.text import Text
from datetime import datetime, timedelta
import random


from cased.utils.auth import get_token

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

    deployments_data = []
    for _ in range(limit):
        begin_time = datetime.now() - timedelta(hours=random.randint(1, 48))
        end_time = (
            begin_time + timedelta(hours=random.randint(1, 4))
            if random.choice([True, False])
            else None
        )
        status = random.choice(["pending", "running", "success", "failed", "canceled"])
        deployment_id = random.randint(1000, 9999)
        view_url = f"https://cased.com/deployments/{deployment_id}"

        deployments_data.append(
            {
                "begin_time": begin_time,
                "end_time": end_time,
                "deployer": f"user{random.randint(1, 100)}@example.com",
                "status": status,
                "branch": f"feature-branch-{random.randint(1, 100)}",
                "target": f"env-{random.choice(['prod', 'staging', 'dev'])}",
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
    table.add_column("Deploy Checks", style="cyan")
    table.add_column("Mergeable", style="blue")
    table.add_column("Merge Checks", style="cyan")

    # Generate fake data
    for _ in range(limit):
        pr_number = random.randint(100, 999) if random.choice([True, False]) else None

        table.add_row(
            f"feature-branch-{random.randint(1, 100)}",
            f"user{random.randint(1, 100)}@example.com",
            str(pr_number) if pr_number else "NULL",
            f"Implement new feature #{random.randint(1, 100)}" if pr_number else "NULL",
            random.choice(["Yes", "No"]),
            ", ".join(
                [
                    f"{check}:{random.choice(['✓', '✗'])}"
                    for check in ["lint", "test", "build"]
                ]
            ),
            random.choice(["Yes", "No"]),
            ", ".join(
                [
                    f"{check}:{random.choice(['✓', '✗'])}"
                    for check in ["conflicts", "approvals", "checks"]
                ]
            ),
        )

    console.print(table)
