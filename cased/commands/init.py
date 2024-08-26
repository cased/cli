import os

import click
import inquirer
import yaml
from rich.console import Console
from rich.panel import Panel

console = Console()


@click.command()
def init():
    """Initialize a new project configuration."""
    console.print(Panel.fit("Welcome to Cased", style="bold magenta"))

    config = {}
    config.update(get_project_info())
    config.update(get_environment_info())
    config.update(get_additional_services_info())
    config.update(get_deployment_info())

    config = expand_config_with_placeholders(config)
    config = rearrange_config_sections(config)

    generate_config_file(config)
    generate_workflow_file(config)

    display_results(config)


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
        inquirer.List(
            "test_framework",
            message="Select your preferred testing framework",
            choices=["pytest", "unittest", "jest", "mocha"],
        ),
    ]

    answers = inquirer.prompt(questions)

    environment = {
        "environment": {
            "language": answers["language"],
            "framework": answers["framework"],
        },
        "testing": {
            "framework": answers["test_framework"],
        },
    }
    if answers["language"] == "Python":
        dependency_manager = [
            inquirer.List(
                "dependency_manager",
                message="Select the dependency manager",
                choices=["pip", "poetry"],
            )
        ]
        dependency_manager_answers = inquirer.prompt(dependency_manager)
        environment["environment"]["dependency_manager"] = dependency_manager_answers[
            "dependency_manager"
        ]
        environment["environment"]["python_version"] = "[REQUIRED] <PYTHON_VERSION>"

    return environment


def get_additional_services_info():
    questions = [
        inquirer.Confirm(
            "use_database", message="Do you want to use a database?", default=False
        ),
        inquirer.Confirm(
            "use_message_broker",
            message="Do you want to use a message broker?",
            default=False,
        ),
    ]

    answers = inquirer.prompt(questions)

    services = {}

    if answers["use_database"]:
        db_questions = [
            inquirer.List(
                "db_type",
                message="Select the database type",
                choices=["PostgreSQL", "MySQL", "MongoDB"],
            ),
        ]
        db_answers = inquirer.prompt(db_questions)
        services["database"] = {
            "type": db_answers["db_type"],
            "enabled": True,
        }
    else:
        services["database"] = {"enabled": False}

    if answers["use_message_broker"]:
        mb_questions = [
            inquirer.List(
                "mb_type",
                message="Select the message broker type",
                choices=["RabbitMQ", "Redis", "Apache Kafka"],
            ),
        ]
        mb_answers = inquirer.prompt(mb_questions)
        services["message_broker"] = {
            "type": mb_answers["mb_type"],
            "enabled": True,
        }
    else:
        services["message_broker"] = {"enabled": False}

    return services


def get_deployment_info():
    questions = [
        inquirer.Confirm(
            "use_docker", message="Do you want to use Docker?", default=False
        ),
        inquirer.List(
            "deployment_target",
            message="Select your deployment target",
            choices=["AWS", "Custom"],
        ),
    ]

    answers = inquirer.prompt(questions)

    deployment_info = {
        "docker": {
            "enabled": answers["use_docker"],
        },
        "cloud_deployment": {
            "provider": answers["deployment_target"],
        },
    }

    return deployment_info


def expand_config_with_placeholders(config):
    config["project"]["version"] = "<[OPTIONAL] PROJECT_VERSION>"
    config["project"]["description"] = "<[OPTIONAL] PROJECT_DESCRIPTION>"

    config["environment"]["dependency_files"] = [
        "<[OPTIONAL] Cased build will smart detect these files if not provided here>"
    ]

    config["testing"]["test_files"] = ["[OPTIONAL]", "<TEST_FILE1>", "<TEST_FILE2>"]
    config["testing"]["coverage"] = {"enabled": False, "report_type": "report"}

    config["runtime"] = {
        "entry_point": "<The file name that contains your main function>",
        "env_variables": ["[OPTIONAL]", "<ENV_A>", "<ENV_B>"],
        "flags": ["[OPTIONAL]", "<FLAG_A>", "<FLAG_B>"],
        "commands": {
            "start": "<START_COMMAND>",
            "stop": "<STOP_COMMAND>",
            "restart": "<RESTART_COMMAND>",
        },
    }

    if config.get("docker", {}).get("enabled", False):
        config["docker"].update(
            {
                "dockerfile": "[REQUIRED] <DOCKERFILE_PATH>",
                "build_args": [
                    "[OPTIONAL]",
                    "<BUILD_ARG1>=<VALUE1>",
                    "<BUILD_ARG2>=<VALUE2>",
                ],
                "image_name": "[REQUIRED] <IMAGE_NAME>",
                "environment": [
                    "[OPTIONAL]",
                    "<ENV_VAR1>=<VALUE1>",
                    "<ENV_VAR2>=<VALUE2>",
                ],
                "ports": ["[REQUIRED] <HOST_PORT>:<CONTAINER_PORT>"],
            }
        )

    if config.get("database", {}).get("enabled", False):
        config["database"].update(
            {
                "version": "<DB_VERSION>",
                "host": "<DB_HOST>",
                "port": "<DB_PORT>",
                "dbname": "<DB_NAME>",
                "migration_files": ["<MIGRATION_FILE1>", "<MIGRATION_FILE2>"],
            }
        )

    if config.get("message_broker", {}).get("enabled", False):
        config["message_broker"].update(
            {"host": "<BROKER_HOST>", "port": "<BROKER_PORT>"}
        )

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

    config["post_deployment"] = {
        "health_check": {
            "url": "<HEALTH_CHECK_URL>",
            "interval": "<HEALTH_CHECK_INTERVAL>",
        },
        "notifications": {
            "enabled": True,
            "channels": ["<NOTIFICATION_CHANNEL1>", "<NOTIFICATION_CHANNEL2>"],
            "slack": {"webhook_url": "<SLACK_WEBHOOK_URL>"},
            "email": {"recipients": ["<EMAIL1>", "<EMAIL2>"]},
        },
    }

    return config


def rearrange_config_sections(config):
    return {
        "project": config["project"],
        "environment": config["environment"],
        "runtime": config["runtime"],
        "testing": config["testing"],
        "docker": config.get("docker", {"enabled": False}),
        "kubernetes": config.get("kubernetes", {"enabled": False}),
        "database": config.get("database", {"enabled": False}),
        "message_broker": config.get("message_broker", {"enabled": False}),
        "cloud_deployment": config["cloud_deployment"],
        "post_deployment": config["post_deployment"],
    }


def generate_config_file(config):
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
# - Testing Configuration: Set up your testing framework and files. Required if you want to run tests.
# - Application Runtime Configuration: Define how your application runs. The entry_point is required.
# - Docker Configuration: Required if you're using Docker. Set enabled to false if not using Docker.
# - Kubernetes Configuration: Optional. Set enabled to true if you're using Kubernetes.
# - Database Configuration: Optional. Fill out if your project uses a database.
# - Message Broker Configuration: Optional. Fill out if your project uses a message broker.
# - Cloud Deployment Configuration: Required if deploying to a cloud provider.
# - Post-Deployment Actions: Optional. Configure health checks and notifications.
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


def generate_workflow_file(config):
    workflow = generate_workflow_template()
    with open(".cased/workflow.yaml", "w") as f:
        for section, content in workflow.items():
            yaml.dump({section: content}, f, default_flow_style=False)


def generate_workflow_template():
    return {
        "name": "CI/CD Workflow",
        "on": {"push": "main"},
        "jobs": {
            "build-and-test": {
                "runs-on": "ubuntu-latest",
                "steps": [
                    {"name": "Checkout code", "uses": "actions/checkout@v2"},
                    {"name": "Set up environment", "run": "<SETUP_COMMAND>"},
                    {"name": "Run tests", "run": "<TEST_COMMAND>"},
                ],
            },
            "deploy": {
                "needs": "build-and-test",
                "runs-on": "ubuntu-latest",
                "steps": [{"name": "Deploy", "run": "<DEPLOY_COMMAND>"}],
            },
        },
    }


def display_results(config):
    console.print(
        Panel.fit("Configuration files created successfully!", style="bold green")
    )
    console.print("Configuration file: [bold].cased/config.yaml[/bold]")
    console.print("Workflow file: [bold].cased/workflow.yaml[/bold]")

    console.print("\n[bold yellow]Next steps:[/bold yellow]")
    console.print("1. Review and edit the configuration files in the .cased directory.")
    console.print(
        "2. Replace all placeholder values (enclosed in < >) with your actual configuration."  # noqa: E501
    )
    console.print(
        "3. Once you've updated the config, run [bold]'cased build'[/bold] to generate your GitHub Actions workflow."  # noqa: E501
    )
