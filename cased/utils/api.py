import sys

import click
import requests
from rich.console import Console

from cased.utils.config import load_config
from cased.utils.constants import CasedConstants

console = Console()


# This is a special case, at this moment, users have not logged in yet.
# So leave it out of CasedAPI class.
def validate_tokens(api_token, org_name):
    return requests.post(
        f"{CasedConstants.API_BASE_URL}/validate-token/",
        json={"api_token": api_token, "org_name": org_name},
    )


class CasedAPI:
    def __init__(self):
        configs = load_config(CasedConstants.ENV_FILE)
        self.request_headers = {
            "X-CASED-API-KEY": str(configs.get(CasedConstants.CASED_API_AUTH_KEY)),
            "X-CASED-ORG-ID": str(configs.get(CasedConstants.CASED_ORG_ID)),
            "Accept": "application/json",
        }

    def get_branches(self, project_name, target_name):
        query_params = {"project_name": project_name, "target_name": target_name}
        response = requests.get(
            f"{CasedConstants.API_BASE_URL}/branches",
            headers=self.request_headers,
            params=query_params,
        )
        if response.status_code == 200:
            return response.json()
        else:
            click.echo("Failed to fetch branches. Please try again.")
            sys.exit(1)

    def get_projects(self):
        response = requests.get(
            f"{CasedConstants.BASE_URL}/deployments", headers=self.request_headers
        )
        if response.status_code == 200:
            return response.json()
        else:
            click.echo("Failed to fetch projects. Please try again.")
            sys.exit(1)

    def get_targets(self, project_name):
        params = {"project_name": project_name}
        response = requests.get(
            f"{CasedConstants.API_BASE_URL}/targets",
            headers=self.request_headers,
            params=params,
        )
        if response.status_code == 200:
            return response.json()
        else:
            click.echo("Failed to fetch targets. Please try again.")
            sys.exit(1)

    def get_deployments(self, project_name, target_name):
        response = requests.get(
            f"{CasedConstants.API_BASE_URL}/targets/{project_name}/{target_name}/deployments/",
            headers=self.request_headers,
        )
        if response.status_code == 200:
            return response.json()
        else:
            click.echo("Failed to fetch deployments. Please try again.")
            sys.exit(1)

    def deploy_branch(self, branch_name, target_name):
        # Implement branch deployment logic here
        response = requests.post(
            f"{CasedConstants.API_BASE_URL}/branch-deploys/",
            json={"branch_name": branch_name, "target_name": target_name},
            headers=self.request_headers,
        )
        if response.status_code == 200:
            click.echo(
                f"Successfully deployed branch '{branch_name}' to target '{target_name}'!"
            )
        else:
            sys.exit(1)

    def create_secrets(self, project_name: str, secrets: list):
        payload = {
            "storage_destination": "github_repository",
            "keys": [{"name": secret, "type": "credentials"} for secret in secrets],
        }
        response = requests.post(
            f"{CasedConstants.API_BASE_URL}/api/v1/secrets/{project_name}/setup",
            json=payload,
            headers=self.request_headers,
        )
        if response.status_code == 201:
            console.print("[green]Secrets setup successful![/green]")
            console.print(
                f"Please go to {CasedConstants.API_BASE_URL}/secrets/{project_name} to update these secrets."  # noqa: E501
            )
        else:
            console.print(
                f"[yellow]Secrets setup returned status code {response.status_code}.[/yellow]"  # noqa: E501
            )
            console.print(
                "Please go to your GitHub repository settings to manually set up the following secrets:"  # noqa: E501
            )
            for secret in secrets:
                console.print(f"- {secret}")
