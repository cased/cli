import click
from cased.commands.deploy import deploy
from cased.commands.login import login, logout
from cased.commands.resources import deployments, branches
from cased.commands.init import init
from cased.commands.spawn import spawn
from cased.commands.push import push
from cased.commands.transfer import transfer


@click.group()
def cli():
    """
    Cased CLI for authentication, target setup, and branch deployment.

    Use 'cased COMMAND --help' for more information on a specific command.
    """

    pass


cli.add_command(init)
cli.add_command(deploy)
cli.add_command(login)
cli.add_command(logout)
cli.add_command(deployments)
cli.add_command(branches)
cli.add_command(spawn)
cli.add_command(push)
cli.add_command(transfer)

# ... (keep the login and setup_target commands as they were) ...


if __name__ == "__main__":
    cli()
