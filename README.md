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

For development installation:

1. Clone the repository:
   ```
   git clone https://github.com/cased/csd.git
   cd csd
   ```

2. Install in editable mode:
   ```
   pip install -e .
   ```

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

## Contact

For any questions or support, please contact cli@cased.com