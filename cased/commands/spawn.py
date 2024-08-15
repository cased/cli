import click
import rich
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
import time
import random

console = Console()


def generate_project_name():
    adjectives = ["happy", "sunny", "clever", "brave", "mighty", "nimble", "swift"]
    nouns = ["panda", "rocket", "river", "mountain", "ocean", "forest", "star"]
    return f"{random.choice(adjectives)}-{random.choice(nouns)}"


@click.command()
@click.option(
    "--instance-type", default="standard", help="Type of server instance to spawn"
)
@click.option("--region", default="us-west", help="Region to spawn the server in")
@click.option("--environment", default="dev", help="Environment (dev, staging, prod)")
def spawn(instance_type, region, environment):
    """Spawn a new server instance."""
    console.print(
        Panel(
            f"Spawning a new {instance_type} server in {region} for {environment} environment",
            style="bold blue",
        )
    )

    steps = [
        ("Initializing instance", 10),
        ("Configuring network", 20),
        ("Setting up security", 15),
        ("Installing dependencies", 25),
        ("Configuring environment", 20),
        ("Starting services", 15),
        ("Generating domain", 5),
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
                time.sleep(0.1)

    # Simulate server details
    ip_address = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
    instance_id = f"i-{random.randint(1000000, 9999999)}"
    project_name = generate_project_name()
    domain = f"https://{project_name}.cased.{environment}.app"

    console.print("\n[bold green]Server spawned successfully![/bold green]")
    console.print(
        Panel.fit(
            f"[bold]Instance Details[/bold]\n"
            f"Instance ID: {instance_id}\n"
            f"IP Address: {ip_address}\n"
            f"Type: {instance_type}\n"
            f"Region: {region}\n"
            f"Environment: {environment}\n"
            f"Domain: {domain}",
            title="Server Information",
            border_style="green",
        )
    )
