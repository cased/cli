import subprocess

from rich.console import Console

console = Console()


def get_repo_name() -> str:
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            check=True,
        )
        repo_url = result.stdout.strip()
        return repo_url.split("/")[-1].replace(".git", "")
    except subprocess.CalledProcessError:
        console.print(
            "[bold yellow]Warning: Unable to get repository name from git. Using 'unknown' as project name.[/bold yellow]"  # noqa: E501
        )
        return "unknown"
