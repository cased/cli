# Cased CLI

A CLI tool for managing cloud infrastructure deployments and configurations with [Cased](https://cased_cli.com).

## Installation

### Prerequisites

- Python 3.12 or higher
- uv package manager
- [A Cased account](https://app.cased_cli.com)

### Installing uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installing the CLI

You can install the CLI from the PyPI repository:

```bash
uv pip install cased-cli
```

Or you can install the CLI from the source code:

1. Clone the repository:
```bash
git clone https://github.com/cased/cli
cd cli
```

2. Create and activate a virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows
```

3. Install dependencies:
```bash
uv pip install -r requirements.txt
```

4. Install the CLI in development mode:
```bash
uv pip install -e .
```

## Usage

After installation, explore the CLI with the `cased` command:

```bash
cased --help
```

### Key Commands

* `cased branches` - Display active branches
* `cased build` - Generate a GitHub Actions workflow based on the configuration
* `cased deploy` - Deploy a branch to a target environment
* `cased deployments` - Display recent deployments
* `cased init` - Initialize a new project configuration (alpha)
* `cased login` - Log in to the Cased system
* `cased logout` - Log out from your Cased account
* `cased projects` - Display and select Cased projects
* `cased targets` - Display target environments

For detailed help on any command:
```bash
cased COMMAND --help
```

## Configuration

The CLI stores configuration in `~/.cased/config/env`. You can configure:

- API authentication
- Organization settings
- Project configurations

## Environment Variables

- `CASED_API_AUTH_KEY` - Your API authentication key
- `CASED_ORG_ID` - Your organization ID
- `CASED_ORG_NAME` - Your organization name
- `CASED_BASE_URL` - API base URL (defaults to https://app.cased_cli.com)

## Support

For issues and feature requests, please open an issue on GitHub.

## License

MIT
