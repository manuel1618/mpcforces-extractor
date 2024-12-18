import threading
import time
from rich.console import Console


class Logger:
    """
    This is a simple logging class
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Logger, cls).__new__(cls, *args, **kwargs)
                    cls._instance._initialize()
        return cls._instance

    def __init__(self):
        """
        Mainly to prevent: W0201
        """
        if not hasattr(self, "_logs"):  # Prevent reinitialization
            self._logs = []
            self._timings = {}
            self._console = Console()

    def _initialize(self):
        self._logs = []
        self._timings = {}
        self._console = Console()

    def _log(self, message):
        """
        Logs to the console and stores the message in the logs list.
        """
        self._logs.append(message)
        self._console.print(message)

    def log_header(self, header):
        """Log a header with separation lines."""
        separator = "-" * 50
        self._log(separator)
        self._log(f"[bold]{header}[/bold]")
        self._log(separator)

    def log_info(self, message, level=0):
        """Log an informational message."""
        indent = "\t" * level
        self._log(f"[cyan][ OUT ][/cyan]: {indent}{message}")

    def log_warn(self, message, level=0):
        """Log a warning message."""
        indent = "\t" * level
        self._log(f"[yellow][ WRN ][/yellow]: {indent}{message}")

    def log_err(self, message, level=0):
        """Log an error message."""
        indent = "\t" * level
        self._log(f"[red][ ERR ][/red]: {indent}{message}")

    def start_timing(self, label):
        """Start a timer for a specific label."""
        self._timings[label] = time.time()

    def stop_timing(self, label):
        """Stop the timer for a specific label and log the elapsed time."""
        if label in self._timings:
            elapsed_time = time.time() - self._timings[label]
            self.log_info(f"[TIMER] {label}: {elapsed_time:.6f} seconds")
            del self._timings[label]
        else:
            self.log_err(f"Timer with label '{label}' was not started.")

    def write_to_file(self, filepath):
        """
        Write the logs to a file.
        """
        with open(filepath, "w", encoding="utf8") as f:
            f.writelines(f"{line}\n" for line in self._logs)


# Usage Example:
logger = Logger()
logger.log_header("Application Start")
logger.log_info("This is an informational message.")
logger.log_warn("This is a warning message.")
logger.log_err("This is an error message.")
logger.start_timing("example_task")
time.sleep(2)  # Simulating a task
logger.stop_timing("example_task")
logger.write_to_file("logfile.txt")
