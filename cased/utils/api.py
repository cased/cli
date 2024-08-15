import requests
import click
import os

API_BASE_URL = os.environ.get(
    "CASED_API_BASE_URL", default="https://app.cased.com/api/v1"
)
REQUEST_HEADERS = {
    "X-CASED-API-KEY": os.environ.get("CASED_API_AUTH_KEY"),
    "X-CASED-ORG-ID": str(os.environ.get("CASED_API_ORG_ID")),
    "Accept": "application/json",
}


def get_branches(target_name: str = None):
    query_params = {"target_name": target_name} if target_name else {}
    response = requests.get(
        f"{API_BASE_URL}/prs",
        headers=REQUEST_HEADERS,
        params=query_params,
    )
    if response.status_code == 200:
        return response.json()
    else:
        click.echo("Failed to fetch branches. Please try again.")
        return []


def get_targets():
    response = requests.get(f"{API_BASE_URL}/targets", headers=REQUEST_HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        click.echo("Failed to fetch targets. Please try again.")
        return []


def get_deployments():
    response = requests.get(f"{API_BASE_URL}/deployments/", headers=REQUEST_HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        click.echo("Failed to fetch deployments. Please try again.")
        return []


def deploy_branch(branch_name, target_name):
    # Implement branch deployment logic here
    response = requests.post(
        f"{API_BASE_URL}/branch-deploys/",
        json={"branch_name": branch_name, "target_name": target_name},
        headers=REQUEST_HEADERS,
    )
    if response.status_code == 200:
        click.echo(
            f"Successfully deployed branch '{branch_name}' to target '{target_name}'!"
        )
    else:
        click.echo("Deployment failed. Please check your input and try again.")
