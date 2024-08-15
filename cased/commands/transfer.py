import click
import rich
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
import time
import random
import os

console = Console()


def generate_image_tag():
    return f"{random.randint(100, 999)}.{random.randint(10, 99)}.{random.randint(1, 9)}"


@click.command()
@click.option("--destination", required=True, help="Destination machine address")
@click.option("--registry", default="docker.io", help="Docker registry to use")
def transfer(destination, registry):
    """Build Docker image and transfer to the destination machine."""
    # Simulate getting current repository name
    repo_name = os.path.basename(os.getcwd())
    image_tag = generate_image_tag()
    image_name = f"{registry}/{repo_name}:{image_tag}"

    console.print(
        Panel(
            f"Building and transferring Docker image for {repo_name} to {destination}",
            style="bold blue",
        )
    )

    steps = [
        ("Analyzing source code", 10),
        ("Building Docker image", 40),
        ("Running security scan", 15),
        ("Pushing to registry", 25),
        ("Transferring to destination", 30),
        ("Verifying integrity", 10),
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

    # Simulate transfer details
    image_size = f"{random.randint(50, 500)} MB"
    transfer_speed = f"{random.randint(5, 50)} MB/s"

    console.print(
        "\n[bold green]Docker image built and transferred successfully![/bold green]"
    )
    console.print(
        Panel.fit(
            f"[bold]Transfer Details[/bold]\n"
            f"Repository: {repo_name}\n"
            f"Image: {image_name}\n"
            f"Destination: {destination}\n"
            f"Image size: {image_size}\n"
            f"Transfer speed: {transfer_speed}\n"
            f"Status: Completed",
            title="Transfer Information",
            border_style="green",
        )
    )

    console.print(
        "\n[yellow]To run the Docker image on the destination machine, use:[/yellow]"
    )
    console.print(f"[bold]docker run -d {image_name}[/bold]")
