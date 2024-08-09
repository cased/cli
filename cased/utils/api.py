import requests
import click
import os

API_BASE_URL = os.getenv("CASED_API_BASE_URL", "https://api.cased.com")


def get_branches():
    response = requests.get(f"{API_BASE_URL}/branches")
    if response.status_code == 200:
        return response.json()
    else:
        click.echo("Failed to fetch branches. Please try again.")
        return []


def get_targets():
    response = requests.get(f"{API_BASE_URL}/targets")
    if response.status_code == 200:
        return response.json()
    else:
        click.echo("Failed to fetch targets. Please try again.")
        return []


def deploy_branch(branch, target):
    # Implement branch deployment logic here
    response = requests.post(
        f"{API_BASE_URL}/deploy", json={"target": target, "branch": branch}
    )
    if response.status_code == 200:
        click.echo(f"Successfully deployed branch '{branch}' to target '{target}'!")
    else:
        click.echo("Deployment failed. Please check your input and try again.")
