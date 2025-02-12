import sys
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Any, Callable

from cased_cli.utils.exception import CasedAPIError
from rich.console import Console
from rich.progress import Progress


def run_process_with_status_bar(
    process_func: Callable[[], Any],
    description: str = "Processing...",
    timeout: int = 10,
    *args,
    **kwargs,
) -> Any:
    console = Console()
    result = None
    progress = Progress()
    task = progress.add_task(f"[green]{description}", total=100)

    progress.start()
    with ThreadPoolExecutor(max_workers=2) as executor:
        future = executor.submit(process_func, *args, **kwargs)
        start_time = time.time()
        while not future.done() and time.time() - start_time < timeout:
            elapsed = int(time.time() - start_time)
            steps = (elapsed / timeout) * 100
            progress.update(task, completed=min(steps, 100))
            time.sleep(0.1)

        try:
            result = future.result(timeout=0)  # Non-blocking check
            progress.update(task, completed=100, description="[bold green]Done!")
        except TimeoutError:
            console.print(
                f"\n[bold red]Process timed out after {timeout} seconds. Please try again later."
            )
            sys.exit(1)
        except CasedAPIError as e:
            console.print(f"\n[bold red]API Error: {e}")
            sys.exit(1)
        except Exception as _:
            console.print(
                "\n[bold red]An unexpected error occurred, please try again later."
            )
            sys.exit(1)

    progress.stop()
    return result
