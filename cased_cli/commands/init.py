import os

import click
import inquirer
import yaml
from cased_cli.utils.auth import validate_credentials
from cased_cli.utils.progress import run_process_with_status_bar
from rich.console import Console
from rich.panel import Panel

console = Console()


@click.command()
@validate_credentials(check_project_set=False)
def init():
    """Initialize a new project configuration (alpha)"""
    console.print(Panel.fit("Welcome to Cased", style="bold magenta"))

    config = {}
    config.update(get_project_info())
    config.update(get_environment_info())
    config.update(get_deployment_info())

    run_process_with_status_bar(
        generate_config_file, description="Generating config file...", config=config
    )

    display_results()


def get_project_info():
    questions = [inquirer.Text("name", message="Enter your project name")]
    answers = inquirer.prompt(questions)

    return {"project": {"name": answers["name"]}}


def get_environment_info():
    questions = [
        inquirer.List(
            "language",
            message="Select the primary language for your project",
            choices=["Python", "JavaScript"],
        ),
        inquirer.List(
            "framework",
            message="Select the framework (optional)",
            choices=["None", "Django", "Flask", "Node.js"],
        ),
    ]

    answers = inquirer.prompt(questions)

    environment = {
        "environment": {
            "language": answers["language"],
            "framework": answers["framework"],
        },
    }
    if answers["language"] == "Python":
        environment["environment"]["dependency_manager"] = "poetry"
        environment["environment"]["python_version"] = "[REQUIRED] <PYTHON_VERSION>"

    return environment


def get_deployment_info():
    questions = [
        inquirer.List(
            "deployment_target",
            message="Select your deployment target",
            choices=["AWS", "Custom"],
        ),
    ]

    answers = inquirer.prompt(questions)

    deployment_info = {
        "cloud_deployment": {
            "provider": answers["deployment_target"],
        },
    }

    return deployment_info


def check_for_docker(config):
    def find_dockerfile(start_path="."):
        for root, _, files in os.walk(start_path):
            if "Dockerfile" in files:
                return os.path.join(root, "Dockerfile")
        return None

    dockerfile_path = find_dockerfile()
    if dockerfile_path:
        config["docker"] = {
            "enabled": True,
            "ECR Repository Name": "[REQUIRED] <Name of ECR Repository>",
            "dockerfile_path": dockerfile_path,
            "build_args": [
                "[OPTIONAL]",
                "<BUILD_ARG1>=<VALUE1>",
                "<BUILD_ARG2>=<VALUE2>",
            ],
            "image_name": "[OPTIONAL] <IMAGE_NAME>",
            "environment": [
                "[OPTIONAL]",
                "<ENV_VAR1>=<VALUE1>",
                "<ENV_VAR2>=<VALUE2>",
            ],
            "ports": ["[OPTIONAL] <HOST_PORT>:<CONTAINER_PORT>"],
        }
    else:
        config["docker"] = {"enabled": False}


def expand_config_with_placeholders(config):
    config["project"]["version"] = "<[OPTIONAL] PROJECT_VERSION>"
    config["project"]["description"] = "<[OPTIONAL] PROJECT_DESCRIPTION>"

    config["environment"]["dependency_files"] = [
        "<[OPTIONAL] Cased build will smart detect these files if not provided here>"
    ]
    if config["docker"]["enabled"]:
        config["runtime"] = {
            "entry_point": "docker",
        }
    else:
        config["runtime"] = {
            "entry_point": "[REQUIRED]<The path to the file contains your main function>",  # noqa: E501
            "flags": ["[OPTIONAL]", "<FLAG_A>", "<FLAG_B>"],
            "commands": {
                "start": "<START_COMMAND>",
                "stop": "<STOP_COMMAND>",
                "restart": "<RESTART_COMMAND>",
            },
        }

    config["cloud_deployment"] = config.get("cloud_deployment", {})
    config["cloud_deployment"].update(
        {
            "region": "<CLOUD_REGION>",
            "instance_type": "<INSTANCE_TYPE>",
            "autoscaling": {
                "enabled": True,
                "min_instances": "<MIN_INSTANCES>",
                "max_instances": "<MAX_INSTANCES>",
            },
            "load_balancer": {"enabled": True, "type": "<LOAD_BALANCER_TYPE>"},
        }
    )

    return config


def rearrange_config_sections(config):
    return {
        "project": config["project"],
        "environment": config["environment"],
        "runtime": config["runtime"],
        "docker": config["docker"],
        "cloud_deployment": config["cloud_deployment"],
    }


def write_config_file(config):
    comments = """# CASED Configuration File
#
# This file contains the configuration for your project's DevOps processes.
# Please read the following instructions carefully before editing this file.
#
# Instructions:
# 1. Required fields are marked with [REQUIRED]. These must be filled out for the tool to function properly.
# 2. Optional fields are marked with [OPTIONAL]. Fill these out if they apply to your project.
# 3. Fields with default values are pre-filled. Modify them as needed.
# 4. Do not change the structure of this file (i.e., don't remove or rename sections).
# 5. Use quotes around string values, especially if they contain special characters.
# 6. For boolean values, use true or false (lowercase, no quotes).
# 7. For lists, maintain the dash (-) format for each item.
#
# Sections:
# - Project Metadata: Basic information about your project. All fields are required.
# - Environment Configuration: Specify your project's runtime environment. Python or Node version is required if applicable.
# - Application Runtime Configuration: Define how your application runs. The entry_point is required.
# - Docker Configuration: Required if you're using Docker. Set enabled to false if not using Docker.
# - Cloud Deployment Configuration: Required if deploying to a cloud provider.
#
# After editing this file, run 'cased build' to generate your GitHub Actions workflow.
# If you need help, refer to the documentation or run 'cased --help'.

        """  # noqa: E501
    os.makedirs(".cased", exist_ok=True)
    with open(".cased/config.yaml", "w") as f:
        f.write(f"{comments}\n")
        for section, content in config.items():
            yaml.dump({section: content}, f, default_flow_style=False)
            f.write("\n")  # Add a blank line between sections


def generate_config_file(config):
    check_for_docker(config)
    config = expand_config_with_placeholders(config)
    config = rearrange_config_sections(config)

    write_config_file(config)


def display_results():
    console.print(
        Panel.fit("Configuration files created successfully!", style="bold green")
    )
    console.print("Configuration file: [bold].cased/config.yaml[/bold]")

    console.print("\n[bold yellow]Next steps:[/bold yellow]")
    console.print("1. Review and edit the configuration files in the .cased directory.")
    console.print(
        "2. Replace all placeholder values (enclosed in < >) with your actual configuration."  # noqa: E501
    )
    console.print(
        "3. Once you've updated the config, run [bold]'cased build'[/bold] to generate your GitHub Actions workflow."  # noqa: E501
    )
