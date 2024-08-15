import click
import rich
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
import time
import random
import os

console = Console()


@click.command()
@click.option("--server", required=True, help="Server address to push to")
@click.option("--branch", default="main", help="Branch to push")
def push(server, branch):
    """Push code to the destination server and run the app."""
    # Simulate getting current repository name
    repo_name = os.path.basename(os.getcwd())

    console.print(
        Panel(
            f"Pushing code from {repo_name} ({branch} branch) to {server}",
            style="bold blue",
        )
    )

    steps = [
        ("Checking out branch", 10),
        ("Compressing files", 20),
        ("Uploading to server", 40),
        ("Unpacking files", 15),
        ("Installing dependencies", 25),
        ("Running database migrations", 15),
        ("Starting application", 10),
    ]

    with Progress(
        SpinnerColumn(),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for description, weight in steps:
            task = progress.add_task(description, total=weight)
            while not progress.finished:
                progress.update(task, advance=0.5)
                time.sleep(0.05)

    # Simulate app details
    port = random.randint(3000, 9000)
    pid = random.randint(1000, 9999)

    console.print(
        "\n[bold green]Code pushed and app started successfully![/bold green]"
    )
    console.print(
        Panel.fit(
            f"[bold]Application Details[/bold]\n"
            f"Repository: {repo_name}\n"
            f"Branch: {branch}\n"
            f"Server: {server}\n"
            f"Running on port: {port}\n"
            f"Process ID: {pid}\n"
            f"Status: Running",
            title="Deployment Information",
            border_style="green",
        )
    )

    console.print("\n[yellow]To stop the application, use:[/yellow]")
    console.print(f"[bold]cased stop --server {server} --pid {pid}[/bold]")
