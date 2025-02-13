import os
import click
import tempfile
from pathlib import Path
from rich import print
import re

class EnvChecker:
    PYTHON_PATHS = [
        "**/settings/*.py",
        "**/config/*.py",
        "manage.py",
        "**/wsgi.py",
        "**/asgi.py",
        "**/env.py",
    ]

    TYPESCRIPT_PATHS = [
        "**/config/*.ts",
        "**/env.ts",
        "**/environment.ts",
        "vite.config.ts",
        "next.config.js",
        ".env.ts"
    ]

    GO_PATHS = [
        "**/config/*.go",
        "**/cmd/*.go",
        "main.go",
        "**/env/*.go"
    ]

    EXCLUDE_PATTERNS = [
        "*/.*",
        "*/venv/*",
        "*/node_modules/*",
        "*/__pycache__/*",
        "*/dist/*",
        "*/.git/*"
    ]

    def __init__(self, verbose=False):
        self.temp_dir = tempfile.mkdtemp()
        self.env_vars_file = Path(self.temp_dir) / "env_example_vars.txt"
        self.verbose = verbose
        self.cwd = Path.cwd()

    def cleanup(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def write_env_example_vars(self):
        """Extract variables from .env.example file."""
        env_example = self.cwd / ".env.example"
        if not env_example.exists():
            if self.verbose:
                print("[yellow]Warning: No .env.example file found[/yellow]")
            open(self.env_vars_file, 'w').close()
            return

        with open(env_example) as f, open(self.env_vars_file, 'w') as out:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    var = line.split('=')[0].strip()
                    out.write(f"{var}\n")

    def write_system_vars(self):
        """Get current environment variables excluding system ones."""
        system_vars = {
            'SHELL=', 'USER=', 'PATH=', 'PWD=', 'HOME=', 'LANG=', 'LC_',
            'TERM=', 'COMMAND_MODE=', 'SHLVL=', '_=', 'XPC_', 'SSH_',
            'COLORTERM=', 'TERM_PROGRAM=', 'OLDPWD=', 'ZSH=', 'PAGER=',
            'LESS=', 'LOGNAME=', 'DISPLAY=', 'SECURITYSESSIONID=', 'TMPDIR='
        }
        
        with open(self.sys_vars_file, 'w') as f:
            for var in sorted(os.environ):
                if not any(var.startswith(s.rstrip('=')) for s in system_vars):
                    f.write(f"{var}\n")

    def scan_files(self, pattern: str, lang: str) -> set:
        """Scan files for environment variables and return found vars."""
        patterns = {
            "python": r"os\.environ\.get\(['\"]([A-Z_]*)['\"].*?\)|os\.environ\[['\"]([A-Z_]*)['\"]|os\.getenv\(['\"]([A-Z_]*)['\"]",
            "typescript": r"process\.env\.([A-Z_]*)|process\.env\[['\"]([A-Z_]*)['\"]|env\(['\"]([A-Z_]*)['\"]",
            "go": r"os\.Getenv\(['\"]([A-Z_]*)['\"]|os\.Setenv\(['\"]([A-Z_]*)['\"]|viper\.Get\w*\(['\"]([A-Z_]*)['\"]"
        }

        found_vars = set()
        for file in self.cwd.glob(pattern.lstrip('/')):
            if any(file.match(exclude) for exclude in self.EXCLUDE_PATTERNS):
                continue

            try:
                with open(file) as f:
                    content = f.read()
                    matches = re.finditer(patterns[lang], content)
                    for match in matches:
                        var_name = next((g for g in match.groups() if g), None)
                        if var_name:
                            found_vars.add(var_name)
                            if self.verbose:
                                print(f"Found {var_name} in {file.relative_to(self.cwd)}")
            except Exception as e:
                if self.verbose:
                    print(f"[red]Error reading {file}: {str(e)}[/red]")
        
        return found_vars

    def get_env_example_vars(self) -> set:
        """Get all variables from .env.example file."""
        env_vars = set()
        env_example = self.cwd / ".env.example"
        
        if not env_example.exists():
            if self.verbose:
                print("[yellow]Warning: No .env.example file found[/yellow]")
            return env_vars

        with open(env_example) as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    var = line.split('=')[0].strip()
                    env_vars.add(var)
        
        return env_vars

    def check_missing_vars(self) -> bool:
        """Check for missing required variables."""
        # Get all variables from .env.example
        env_example_vars = self.get_env_example_vars()
        if not env_example_vars:
            print("[yellow]⚠️  No variables found in .env.example[/yellow]")
            return False

        # Get all variables from settings files
        settings_vars = set()
        for pattern in self.PYTHON_PATHS:
            settings_vars.update(self.scan_files(pattern, "python"))
        for pattern in self.TYPESCRIPT_PATHS:
            settings_vars.update(self.scan_files(pattern, "typescript"))
        for pattern in self.GO_PATHS:
            settings_vars.update(self.scan_files(pattern, "go"))

        # Get current OS environment variables (excluding system ones)
        system_vars = {
            'SHELL', 'USER', 'PATH', 'PWD', 'HOME', 'LANG', 'LC_',
            'TERM', 'COMMAND_MODE', 'SHLVL', '_', 'XPC_', 'SSH_',
            'COLORTERM', 'TERM_PROGRAM', 'OLDPWD', 'ZSH', 'PAGER',
            'LESS', 'LOGNAME', 'DISPLAY', 'SECURITYSESSIONID', 'TMPDIR'
        }
        os_vars = {var for var in os.environ if not any(var.startswith(s) for s in system_vars)}

        print("\nRequired but not set:")
        print("--------------------")
        missing_found = False

        # Check each variable from .env.example
        for var in sorted(env_example_vars):
            # Variable is missing if it's not in OS environment and not in any settings file
            if var not in os_vars and var not in settings_vars:
                print(f"[red]❌ {var}[/red]")
                missing_found = True

        if not missing_found:
            print("[green]✓ All required environment variables are set[/green]")

        return missing_found

@click.command()
@click.option('-v', '--verbose', is_flag=True, help='Show detailed information about the scan')
def verify_env(verbose):
    """Check for missing required environment variables in the current directory."""
    checker = EnvChecker(verbose=verbose)
    try:
        missing_found = checker.check_missing_vars()
        if missing_found:
            raise click.ClickException("Missing required environment variables")
    finally:
        checker.cleanup()
