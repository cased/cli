import requests
from rich.console import Console

from cased.utils.config import load_config
from cased.utils.constants import CasedConstants
from cased.utils.exception import CasedAPIError

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
            "Authorization": f"Bearer {str(configs.get(CasedConstants.CASED_API_AUTH_KEY))}",
            "Accept": "application/json",
        }

    def _make_request(self, resource_name, method, url, **kwargs):
        response = requests.request(method, url, headers=self.request_headers, **kwargs)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise CasedAPIError(
                f"Failed to fetch {resource_name} from {url}",
                response.status_code,
                response.json(),
            )

    def get_branches(self, project_name):
        query_params = {"project_name": project_name}
        return self._make_request(
            resource_name="branches",
            method="GET",
            url=f"{CasedConstants.API_BASE_URL}/branches",
            params=query_params,
        )

    def get_projects(self):
        return self._make_request(
            resource_name="projects",
            method="GET",
            url=f"{CasedConstants.BASE_URL}/projects",
        )

    def get_targets(self, project_name):
        params = {"project_name": project_name}
        return self._make_request(
            resource_name="targets",
            method="GET",
            url=f"{CasedConstants.API_BASE_URL}/targets",
            params=params,
        )

    def get_deployments(self, project_name, target_name=None):
        params = {"project_name": project_name, "target_name": target_name}
        return self._make_request(
            resource_name="deployments",
            method="GET",
            url=f"{CasedConstants.API_BASE_URL}/deployments",
            params=params,
        )

    def deploy_branch(self, project_name, branch_name, target_name):
        json = {
            "project_name": project_name,
            "branch_name": branch_name,
            "target_name": target_name,
        }
        return self._make_request(
            resource_name="branch_deploy",
            method="POST",
            url=f"{CasedConstants.API_BASE_URL}/branch-deploys",
            json=json,
        )

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
