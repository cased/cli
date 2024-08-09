import click
from cased.commands.deploy import deploy
from cased.commands.login import login, logout
from cased.commands.resources import deployments, branches


@click.group()
def cli():
    """
    Cased CLI for authentication, target setup, and branch deployment.

    Use 'cased COMMAND --help' for more information on a specific command.
    """

    pass


cli.add_command(deploy)
cli.add_command(login)
cli.add_command(logout)
cli.add_command(deployments)
cli.add_command(branches)

# ... (keep the login and setup_target commands as they were) ...


if __name__ == "__main__":
    cli()
