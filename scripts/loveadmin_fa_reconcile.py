import pandas as pd
import logging
from logging import getLogger


def configure_logging(log_file=None, force_console=False):
    """
    Configures logging for the script. Logs to a file if specified, or to the console otherwise.

    :param log_file: Path to the log file (optional).
    :param force_console: Force logging to console even if log file is specified.
    """
    # Define colour codes for different log levels
    log_colors = {
        'DEBUG': '\033[1;34m',  # Blue
        'INFO': '\033[1;32m',   # Green
        'WARNING': '\033[1;33m',  # Yellow
        'ERROR': '\033[1;31m',  # Red
        'CRITICAL': '\033[1;41m'  # Red background
    }

    class CustomFormatter(logging.Formatter):
        """
        Custom formatter to add colours to log levels and format log messages.
        """
        def format(self, record):
            log_color = log_colors.get(record.levelname, '\033[0m')  # Default to no colour
            record.levelname = f"{log_color}{record.levelname}\033[0m"
            return super().format(record)

    # Format string for logs
    log_format = (
        "\033[1;37m%(asctime)s\033[0m - "
        "\033[1;34m%(filename)s\033[0m - "
        "\033[1;33m%(funcName)s\033[0m - "
        "\033[1;36m%(lineno)d\033[0m - "
        "%(levelname)s - %(message)s"
    )
    formatter = CustomFormatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    handlers = []
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    if not log_file or force_console:
        handlers.append(logging.StreamHandler())

    for handler in handlers:
        handler.setFormatter(formatter)

    logging.basicConfig(level=logging.DEBUG, handlers=handlers)
    return getLogger(__name__)


logger = configure_logging(force_console=True)


def merge_datasets(loveadmin_path, fa_club_portal_path, output_path):
    """
    Merges two datasets based on common keys and adds flags for presence in each dataset.

    :param loveadmin_path: Path to the LoveAdmin file.
    :param fa_club_portal_path: Path to the FA Club Portal file.
    :param output_path: Path to save the merged output file.
    """
    try:
        logger.info("Loading LoveAdmin data...")
        loveadmin_data = pd.read_excel(loveadmin_path)

        logger.info("Loading FA Club Portal data...")
        fa_club_portal_data = pd.read_excel(fa_club_portal_path, skiprows=6)

        logger.debug("Renaming columns for standardisation...")
        loveadmin_data = loveadmin_data.rename(columns={"Last name": "Surname", "First name": "First names"})

        logger.debug("Adding presence flags...")
        loveadmin_data["In_LoveAdmin"] = True
        fa_club_portal_data["In_FA_Club_Portal"] = True

        logger.info("Merging datasets...")
        merged_data = pd.merge(
            loveadmin_data,
            fa_club_portal_data,
            on=["First names", "Surname"],
            how="outer"
        )

        logger.debug("Filling NaN values for presence flags...")
        merged_data["In_LoveAdmin"] = merged_data["In_LoveAdmin"].fillna(False)
        merged_data["In_FA_Club_Portal"] = merged_data["In_FA_Club_Portal"].fillna(False)

        logger.info(f"Saving merged data to {output_path}...")
        merged_data.to_excel(output_path, index=False)

        logger.info("Merge process completed successfully.")

    except Exception as e:
        logger.error(f"An error occurred during the merge process: {e}")
        raise


if __name__ == "__main__":
    # Paths to the files
    loveadmin_file = "Data export 20250124-162359.xlsx"
    fa_club_portal_file = "Wilpshire Wanderers_RegistrationReport_24012025.xlsx"
    output_file = "Merged_LoveAdmin_FA_Club_Portal.xlsx"

    # Execute the merge function
    merge_datasets(loveadmin_file, fa_club_portal_file, output_file)
