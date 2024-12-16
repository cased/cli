import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import click
import yaml
from jinja2 import Environment, FileSystemLoader
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from cased.utils.api import CasedAPI
from cased.utils.constants import CasedConstants
from cased.utils.git import get_repo_name

console = Console()
# Get the directory of the current script
CURRENT_DIR = Path(__file__).resolve().parent
# Go up one level to the 'cased' directory
CASED_DIR = CURRENT_DIR.parent
# Set the path to the templates directory
TEMPLATES_DIR = CASED_DIR / "templates"
CONFIG_PATH = ".cased/config.yaml"


@click.command()
def build() -> None:
    """
    Generate a GitHub Actions workflow based on the configuration in .cased/config.yaml.

    This command reads the configuration file, validates it, generates a workflow file
    in the .github/workflows directory, and sets up necessary secrets.
    """
    if not os.path.exists(CONFIG_PATH):
        console.print(
            "[red]Error: Configuration file not found at .cased/config.yaml[/red]"
        )
        console.print(
            "Please run 'cased init' to generate the configuration file first."
        )
        sys.exit(1)

    config = load_config(CONFIG_PATH)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        validate_task = progress.add_task(
            "[cyan]Validating configuration...", total=100
        )
        try:
            validate_config(config)
            progress.update(
                validate_task,
                completed=100,
                description="[bold green]Configuration validated successfully!",
            )
        except ValueError as e:
            progress.update(validate_task, completed=100)
            console.print(f"[red]Configuration validation failed: {str(e)}[/red]")
            sys.exit(1)

        generate_task = progress.add_task("[cyan]Generating workflow...", total=100)
        workflow_content = generate_workflow(config)
        save_workflow(workflow_content)
        progress.update(
            generate_task,
            completed=100,
            description="[bold green]Workflow generated successfully!",
        )

    project_name = get_repo_name()
    secrets = extract_secrets_from_workflow(workflow_content)
    CasedAPI().create_secrets(project_name, secrets)

    console.print(
        Panel(
            f"""
            [bold green]GitHub Actions workflow generated successfully![/bold green]
            [bold green]Please complete the following steps for the workflow to work correctly: [/bold green]
            1. Review the generated workflow file in .github/workflows/deploy.yaml
            2. Go to {CasedConstants.API_BASE_URL}/secrets/{project_name} to update the secrets.
            3. Commit the changes to your repository, and the workflow will be triggered.
            4. Go to {CasedConstants.API_BASE_URL}/deployments/ to monitor the deployment status.
            """,  # noqa: E501
            title="Success",
            expand=False,
        )
    )


def load_config(file_path: str) -> Dict[str, Any]:
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def generate_workflow(config: Dict[str, Any]) -> str:
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

    if config["docker"]["enabled"]:
        template = env.get_template("docker_ec2_template.yaml")
    else:
        template = env.get_template("non_docker_ec2_template.yaml")

    return template.render(config=config)


def save_workflow(content: str) -> None:
    os.makedirs(".github/workflows", exist_ok=True)
    with open(".github/workflows/deploy.yaml", "w") as file:
        file.write(content)


def extract_secrets_from_workflow(workflow_content: str) -> List[str]:
    secrets = []
    for line in workflow_content.split("\n"):
        if "secrets." in line:
            secret = line.split("secrets.")[1].split("}")[0].strip()
            if secret not in secrets:
                secrets.append(secret)
    return secrets


def validate_config(config: Dict[str, Any]) -> None:
    # Project validation
    if "project" not in config:
        raise ValueError("Missing 'project' section in config")
    if "name" not in config["project"]:
        raise ValueError("Missing 'name' in 'project' section")

    # Environment validation
    if "environment" not in config:
        raise ValueError("Missing 'environment' section in config")
    required_env_fields = ["language", "python_version"]
    for field in required_env_fields:
        if field not in config["environment"]:
            raise ValueError(f"Missing '{field}' in 'environment' section")

    # Docker validation
    if "docker" not in config:
        raise ValueError("Missing 'docker' section in config")
    if "enabled" not in config["docker"]:
        raise ValueError("Missing 'enabled' field in 'docker' section")

    if config["docker"]["enabled"]:
        required_docker_fields = [
            "ECR Repository Name",
            "dockerfile_path",
            "image_name",
        ]
        for field in required_docker_fields:
            if field not in config["docker"]:
                raise ValueError(f"Missing '{field}' in 'docker' section")

        if not isinstance(config["docker"].get("ports", []), list):
            raise ValueError("'ports' in 'docker' section must be a list")

        if "environment" in config["docker"] and not isinstance(
            config["docker"]["environment"], list
        ):
            raise ValueError("'environment' in 'docker' section must be a list")
    else:
        # Non-docker validation
        if "runtime" not in config:
            raise ValueError("Missing 'runtime' section in config for non-docker setup")
        required_runtime_fields = ["commands", "entry_point"]
        for field in required_runtime_fields:
            if field not in config["runtime"]:
                raise ValueError(f"Missing '{field}' in 'runtime' section")

        required_commands = ["start", "stop", "restart"]
        for command in required_commands:
            if command not in config["runtime"]["commands"]:
                raise ValueError(f"Missing '{command}' in 'runtime.commands' section")
