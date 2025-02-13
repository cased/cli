import click
from cased_cli.commands.build import build
from cased_cli.commands.deploy import deploy
from cased_cli.commands.init import init
from cased_cli.commands.login import login, logout
from cased_cli.commands.resources import branches, deployments, projects, targets
from cased_cli.commands.check_env import check_env

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group()
def cli():
    """
    Cased CLI for authentication, target setup, and branch deployment.

    Use 'cased COMMAND --help' for more information on a specific command.
    """

    pass


cli.add_command(deploy)
cli.add_command(init)
cli.add_command(build)
cli.add_command(login)
cli.add_command(logout)
cli.add_command(deployments)
cli.add_command(branches)
cli.add_command(projects)
cli.add_command(targets)
cli.add_command(check_env)

main = cli

if __name__ == "__main__":
    try:
        cli()
    except Exception as _:
        click.echo("\nProcess interrupted. Exiting.")
