from functools import wraps

from cased.utils.config import load_config
from cased.utils.constants import CasedConstants
from rich.console import Console
from rich.panel import Panel

console = Console()


def validate_credentials(check_project_set=False):
    def decorator(func):
        def _validate_config(config):
            return config and all(
                [
                    config.get(CasedConstants.CASED_API_AUTH_KEY),
                    config.get(CasedConstants.CASED_ORG_ID),
                ]
            )

        def _validate_project_set(config):
            return config and all(
                [
                    config.get(CasedConstants.CASED_WORKING_PROJECT_NAME),
                    config.get(CasedConstants.CASED_WORKING_PROJECT_ID),
                ]
            )

        @wraps(func)
        def wrapper(*args, **kwargs):
            config = load_config(CasedConstants.ENV_FILE)
            if not _validate_config(config):
                console.print(
                    Panel(
                        "[bold red]You are not logged in.[/bold red]\nPlease run 'cased login' first.",  # noqa: E501
                        title="Authentication Error",
                        expand=False,
                    )
                )
                return
            elif check_project_set:
                if not _validate_project_set(config):
                    console.print(
                        Panel(
                            "[bold red]You have not selected a project yet.[/bold red]\nPlease run 'cased projects' first or provide a project name with the --project flag.",  # noqa: E501
                            title="Project Error",
                            expand=False,
                        )
                    )
                    return
                kwargs["project"] = config.get(
                    CasedConstants.CASED_WORKING_PROJECT_NAME
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator
