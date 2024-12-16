# Cased CLI

## Overview

Cased CLI is a powerful command-line interface tool designed to streamline deployment processes and manage branches efficiently. It provides an intuitive way to interact with the Cased system, offering functionalities such as user authentication, deployment management, and branch oversight.

## Features

- User authentication (login/logout)
- View recent deployments
- Display active branches
- Interactive deployment process with branch and target selection
- Comprehensive help system

## Installation

You can install the Cased CLI tool using pip:

```
pip install cased
```

This will install the latest version of the tool from PyPI.

## Usage

After installation, you can use the CLI tool by running `cased` followed by a command:

```
cased --help
```

### Available Commands:

- `cased login`: Log in to the Cased system
- `cased logout`: Log out from the Cased system
- `cased deployments`: View recent deployments
- `cased branches`: View active branches
- `cased deploy`: Deploy a branch to a target environment

For more details on each command, use:

```
cased COMMAND --help
```

## Development

To set up the Cased CLI for development:

1. Clone the repository:
   ```
   git clone https://github.com/cased/cli.git
   cd cli
   ```

2. Install Poetry (if not already installed):
   ```
   pip install poetry
   ```

3. Install dependencies:
   ```
   poetry install
   ```

4. Activate the virtual environment:
   ```
   poetry shell
   ```

5. Run the CLI in development mode:
   ```
   poetry run cased
   ```

### Making Changes

1. Make your changes to the codebase.
2. Update tests if necessary.
3. Run tests:
   ```
   poetry run pytest
   ```
4. Build the package:
   ```
   poetry build
   ```

### Submitting Changes

1. Create a new branch for your changes:
   ```
   git checkout -b feature/your-feature-name
   ```
2. Commit your changes:
   ```
   git commit -am "Add your commit message"
   ```
3. Push to your branch:
   ```
   git push origin feature/your-feature-name
   ```
4. Create a pull request on GitHub.

## Contact

For any questions or support, please contact cli@cased.com
