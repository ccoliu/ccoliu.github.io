import os
import sys
import logging
from datetime import datetime


# Function to get the file path after packaging
def resource_path(relative_path):
    """
    Get absolute path to resource, works for development and PyInstaller executable.
    """
    # Check if running as a PyInstaller bundle
    if getattr(sys, 'frozen', False):  # Check if application is bundled with PyInstaller
        base_path = os.path.dirname(sys.executable)  # Path to the folder containing the .exe
    else:
        base_path = os.path.abspath(".")  # Path for development environment

    return os.path.join(base_path, relative_path)


class DynamicLogHandler:
    def __init__(self, log_folder, log_prefix="server"):
        """
        Initialize the DynamicLogHandler.
        :param log_folder: The folder where logs will be stored.
        :param log_prefix: The prefix for the log filenames.
        """
        self.log_folder = log_folder
        self.log_prefix = log_prefix
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.setup_general_logger()
        self.setup_web_logger()

    def setup_general_logger(self):
        """Set up the logger for general stdout logs."""
        self.general_log_file = os.path.join(
            self.log_folder, f"{self.current_date}_{self.log_prefix}_general.log"
        )
        self.general_logger = logging.getLogger(f"{self.log_prefix}_general")
        self.general_logger.setLevel(logging.INFO)
        self.general_logger.handlers = []  # Clear previous handlers

        # File handler for logging to a file
        general_file_handler = logging.FileHandler(self.general_log_file, mode="a")
        general_file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        self.general_logger.addHandler(general_file_handler)

        # Stream handler for logging to console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        self.general_logger.addHandler(console_handler)

    def setup_web_logger(self):
        """Set up the logger for web-related logs."""
        self.web_log_file = os.path.join(
            self.log_folder, f"{self.current_date}_{self.log_prefix}_web.log"
        )
        werkzeug_logger = logging.getLogger("werkzeug")
        werkzeug_logger.setLevel(logging.INFO)
        werkzeug_logger.handlers = []  # Clear previous handlers
        web_file_handler = logging.FileHandler(self.web_log_file, mode="a")
        web_file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        werkzeug_logger.addHandler(web_file_handler)

    def check_date_and_rotate_logs(self):
        """Check the date and rotate log files if the date has changed."""
        new_date = datetime.now().strftime("%Y-%m-%d")
        if new_date != self.current_date:
            self.current_date = new_date
            self.setup_general_logger()
            self.setup_web_logger()


class StreamToLogger:
    def __init__(self, logger, log_handler):
        """
        Redirects stdout to the logger.
        :param logger: The logger instance.
        :param log_handler: The DynamicLogHandler instance for rotating logs.
        """
        self.logger = logger
        self.log_handler = log_handler

    def write(self, message):
        if message.strip():
            self.log_handler.check_date_and_rotate_logs()  # Check and rotate logs if needed
            self.logger.info(message.strip())

    def flush(self):
        pass


def initialize_logging(log_prefix="server"):
    """
    Initialize the logging system.
    :param log_folder: Folder where logs will be stored.
    :param log_prefix: Prefix for the log filenames.
    :return: A DynamicLogHandler instance.
    """
    # Get the current path of the server
    current_path = resource_path("")

    # Create a Log folder if it does not exist
    log_folder_path = os.path.abspath(current_path + "/Log")
    if not os.path.exists(log_folder_path):
        os.makedirs(log_folder_path)  # Create the log folder
        print(f"Log folder created: {log_folder_path}")

    log_handler = DynamicLogHandler(log_folder_path, log_prefix)

    # Redirect stdout to the general logger
    sys.stdout = StreamToLogger(log_handler.general_logger, log_handler)

    return log_handler
