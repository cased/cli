# Cased CLI

A CLI tool for managing cloud infrastructure deployments and configurations.

## Installation

### Prerequisites

- Python 3.12 or higher
- uv package manager

### Installing uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installing the CLI

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

After installation, you can use the CLI with the `cased` command:

```bash
cased --help
```

### Available Commands

- `cased init` - Initialize a new project configuration
- `cased login` - Authenticate with Cased services
- `cased build` - Build your project according to configuration
- `cased deploy` - Deploy your project to the specified environment

For detailed help on any command:
```bash
cased COMMAND --help
```

## Development

### Setting up the Development Environment

1. Install development dependencies:
```bash
uv pip install pre-commit ruff isort
```

2. Install pre-commit hooks:
```bash
pre-commit install
```

### Code Style

This project uses:
- Ruff for linting and formatting
- isort for import sorting
- pre-commit for git hooks

Configuration for these tools can be found in:
- `pyproject.toml` - Ruff configuration
- `.ci-pre-commit-config.yaml` - Pre-commit hooks

To check code style:
```bash
pre-commit run --all-files
```

### Making Changes

1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and ensure all checks pass:
```bash
pre-commit run --all-files
```

3. Submit a pull request with your changes

## Configuration

The CLI stores configuration in `~/.cased/config/env`. You can configure:

- API authentication
- Organization settings
- Project configurations

## Environment Variables

- `CASED_API_AUTH_KEY` - Your API authentication key
- `CASED_ORG_ID` - Your organization ID
- `CASED_ORG_NAME` - Your organization name
- `CASED_BASE_URL` - API base URL (defaults to https://app.cased.com)

## Support

For issues and feature requests, please open an issue on GitHub.

## License

[License information here]
