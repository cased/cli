import time
from rich.console import Console
from rich.progress import Progress
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Callable, Any


def run_process_with_status_bar(
    process_func: Callable[[], Any],
    description: str = "Processing...",
    timeout: int = 10,
    *args,
    **kwargs,
) -> Any:
    console = Console()
    result = None

    def update_progress(progress, task):
        start_time = time.time()
        while time.time() - start_time < timeout:
            elapsed = int(time.time() - start_time)
            progress.update(task, completed=min(elapsed, timeout))
            time.sleep(1)  # Update every second

    with Progress() as progress:
        task = progress.add_task(f"[green]{description}", total=timeout)

        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit the main process
            future = executor.submit(process_func, *args, **kwargs)
            start_time = time.time()
            while not future.done() and time.time() - start_time < timeout:
                elapsed = int(time.time() - start_time)
                progress.update(task, completed=min(elapsed, timeout))
                time.sleep(0.1)  # Update frequently for responsiveness

            try:
                result = future.result(timeout=timeout)
                progress.update(
                    task, completed=timeout, description="[bold green]Done!"
                )
            except TimeoutError:
                progress.update(task, description="[bold red]Timeout!")
                console.print(
                    f"\n[bold red]Process timed out after {timeout} seconds. Please try again later."
                )
            except Exception as e:
                progress.update(task, description="[bold red]Error!")
                console.print(f"\n[bold red]Error: {e}")

    return result
