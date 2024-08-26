import os

import click
import yaml
from rich.console import Console
from rich.panel import Panel

console = Console()


@click.command()
def build():
    """Build GitHub Actions workflow based on configuration."""
    console.print(Panel.fit("Building GitHub Actions Workflow", style="bold magenta"))

    # Validate config and workflow files
    config = validate_config_file()
    workflow = validate_workflow_file()

    if config and workflow:
        # Generate GitHub Actions workflow
        github_workflow = generate_github_actions_workflow(config, workflow)

        # Write GitHub Actions workflow file
        os.makedirs(".github/workflows", exist_ok=True)
        with open(".github/workflows/cased_workflow.yml", "w") as f:
            for key, value in github_workflow.items():
                yaml.dump({key: value}, f, default_flow_style=False)
                f.write("\n")

        console.print(
            Panel.fit(
                "GitHub Actions workflow generated successfully!", style="bold green"
            )
        )
        console.print(
            "Workflow file: [bold].github/workflows/cased_workflow.yml[/bold]"
        )
    else:
        console.print(
            Panel.fit(
                "Failed to generate GitHub Actions workflow. Please check your configuration.",  # noqa: E501
                style="bold red",
            )
        )


def validate_config_file():
    try:
        with open(".cased/config.yaml", "r") as f:
            config = yaml.safe_load(f)

        required_keys = ["project", "environment", "runtime", "testing"]
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required section: {key}")

        # Add more specific validation rules here
        if "<" in str(config) or ">" in str(config):
            console.print(
                "[bold yellow]Warning:[/bold yellow] Some placeholder values in config.yaml have not been replaced."  # noqa: E501
            )

        return config
    except FileNotFoundError:
        console.print(
            "[bold red]Error:[/bold red] config.yaml not found. Run 'cased init' first."
        )
    except yaml.YAMLError as e:
        console.print(f"[bold red]Error:[/bold red] Invalid YAML in config.yaml: {e}")
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
    return None


def validate_workflow_file():
    try:
        with open(".cased/workflow.yaml", "r") as f:
            workflow = yaml.safe_load(f)

        required_keys = ["name", "on", "jobs"]
        for key in required_keys:
            if key not in workflow:
                raise ValueError(f"Missing required key in workflow: {key}")

        # Add more specific validation rules here

        return workflow
    except FileNotFoundError:
        console.print(
            "[bold red]Error:[/bold red] workflow.yaml not found. Run 'cased init' first."  # noqa: E501
        )
    except yaml.YAMLError as e:
        console.print(f"[bold red]Error:[/bold red] Invalid YAML in workflow.yaml: {e}")
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
    return None


def generate_github_actions_workflow(config, workflow):
    github_workflow = {"name": workflow["name"], "on": workflow["on"], "jobs": {}}

    # Build and Test job
    build_and_test_job = {
        "runs-on": "ubuntu-latest",
        "steps": [
            {"name": "Checkout code", "uses": "actions/checkout@v2"},
            {
                "name": "Set up Python",
                "uses": "actions/setup-python@v2",
                "with": {"python-version": config["environment"]["python_version"]},
            },
            {"name": "Install dependencies", "run": "pip install -r requirements.txt"},
            {"name": "Run tests", "run": f"python -m {config['testing']['framework']}"},
        ],
    }

    if config["testing"]["coverage"].get("enabled"):
        build_and_test_job["steps"].append(
            {
                "name": "Run coverage",
                "run": f"coverage run -m {config['testing']['framework']} && coverage {config['testing']['coverage']['report_type']}",  # noqa: E501
            }
        )

    github_workflow["jobs"]["build_and_test"] = build_and_test_job

    # Deploy job
    deploy_job = {
        "needs": "build_and_test",
        "runs-on": "ubuntu-latest",
        "steps": [
            {"name": "Checkout code", "uses": "actions/checkout@v2"},
        ],
    }

    if config["docker"]["enabled"]:
        deploy_job["steps"].extend(
            [
                {
                    "name": "Set up Docker Buildx",
                    "uses": "docker/setup-buildx-action@v1",
                },
                {
                    "name": "Build and push Docker image",
                    "uses": "docker/build-push-action@v2",
                    "with": {
                        "context": ".",
                        "push": True,
                        "tags": f"{config['docker']['image_name']}:${{ github.sha }}",
                    },
                },
            ]
        )

    if config["cloud_deployment"]["provider"] == "AWS":
        deploy_job["steps"].extend(
            [
                {
                    "name": "Configure AWS credentials",
                    "uses": "aws-actions/configure-aws-credentials@v1",
                    "with": {
                        "aws-access-key-id": "${{ secrets.AWS_ACCESS_KEY_ID }}",
                        "aws-secret-access-key": "${{ secrets.AWS_SECRET_ACCESS_KEY }}",
                        "aws-region": config["cloud_deployment"]["region"],
                    },
                },
                {
                    "name": "Deploy to AWS",
                    "run": 'echo "Add your AWS deployment commands here"',
                },
            ]
        )

    github_workflow["jobs"]["deploy"] = deploy_job

    return github_workflow
