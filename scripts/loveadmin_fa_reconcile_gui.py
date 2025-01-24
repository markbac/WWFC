import pandas as pd
import logging
from logging import getLogger
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


def configure_logging(log_file=None, force_console=False):
    """
    Configures logging for the script. Logs to a file if specified, or to the console otherwise.

    :param log_file: Path to the log file (optional).
    :param force_console: Force logging to console even if log file is specified.
    """
    log_colors = {
        'DEBUG': '\033[1;34m',  # Blue
        'INFO': '\033[1;32m',   # Green
        'WARNING': '\033[1;33m',  # Yellow
        'ERROR': '\033[1;31m',  # Red
        'CRITICAL': '\033[1;41m'  # Red background
    }

    class CustomFormatter(logging.Formatter):
        def format(self, record):
            log_color = log_colors.get(record.levelname, '\033[0m')
            record.levelname = f"{log_color}{record.levelname}\033[0m"
            return super().format(record)

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


def merge_datasets_gui():
    """
    Launches a GUI application for merging datasets from two files based on common columns.
    """
    def select_loveadmin_file():
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        loveadmin_file_var.set(file_path)

    def select_fa_club_portal_file():
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        fa_club_portal_file_var.set(file_path)

    def save_output_file():
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        output_file_var.set(file_path)

    def show_help():
        messagebox.showinfo("Help", "For assistance, contact: mark@bacon.me.uk")

    def validate_and_merge():
        loveadmin_file = loveadmin_file_var.get()
        fa_club_portal_file = fa_club_portal_file_var.get()
        output_file = output_file_var.get()

        if not loveadmin_file or not fa_club_portal_file or not output_file:
            messagebox.showerror("Error", "Please select all required files.")
            return

        try:
            logger.info("Loading LoveAdmin data...")
            loveadmin_data = pd.read_excel(loveadmin_file)

            logger.info("Loading FA Club Portal data...")
            fa_club_portal_data = pd.read_excel(fa_club_portal_file, skiprows=6)

            if "Last name" not in loveadmin_data.columns or "First name" not in loveadmin_data.columns:
                raise ValueError("LoveAdmin file does not contain required columns: 'Last name', 'First name'.")

            if "First names" not in fa_club_portal_data.columns or "Surname" not in fa_club_portal_data.columns:
                raise ValueError("FA Club Portal file does not contain required columns: 'First names', 'Surname'.")

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

            logger.debug("Reordering columns...")
            columns_order = [
                "First names", "Surname",  # Common columns
                "In_LoveAdmin", "In_FA_Club_Portal", "Team", "Active mandates"  # Specific columns in desired order
            ] + [col for col in merged_data.columns if col not in columns_order]
            merged_data = merged_data[columns_order]

            logger.info(f"Saving merged data to {output_file}...")
            merged_data.to_excel(output_file, index=False)

            messagebox.showinfo("Success", "Merge completed successfully.")
            logger.info("Merge process completed successfully.")

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")

    # Create the GUI window
    root = tk.Tk()
    root.title("Wilpshire Wanderers Dataset Merger")
    root.configure(bg="#1E90FF")

    # Add logo
    logo_path = "/mnt/data/U5-6_Leaflet_2024-1-400x400.png"
    try:
        logo = Image.open(logo_path)
        logo = logo.resize((100, 100), Image.LANCZOS)
        logo = ImageTk.PhotoImage(logo)
        tk.Label(root, image=logo, bg="#1E90FF").grid(row=0, column=0, columnspan=3, pady=10)
    except Exception as e:
        logger.error(f"Unable to load logo: {e}")

    # Variables to hold file paths
    loveadmin_file_var = tk.StringVar()
    fa_club_portal_file_var = tk.StringVar()
    output_file_var = tk.StringVar()

    # Description
    tk.Label(
        root,
        text="This application merges LoveAdmin and FA Club Portal datasets based on common columns.",
        bg="#1E90FF", fg="white", wraplength=400, justify="center"
    ).grid(row=1, column=0, columnspan=3, padx=10, pady=10)

    # GUI Layout
    tk.Label(root, text="LoveAdmin File:", bg="#1E90FF", fg="white").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    tk.Entry(root, textvariable=loveadmin_file_var, width=50).grid(row=2, column=1, padx=10, pady=5)
    tk.Button(root, text="Browse", command=select_loveadmin_file).grid(row=2, column=2, padx=10, pady=5)

    tk.Label(root, text="FA Club Portal File:", bg="#1E90FF", fg="white").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    tk.Entry(root, textvariable=fa_club_portal_file_var, width=50).grid(row=3, column=1, padx=10, pady=5)
    tk.Button(root, text="Browse", command=select_fa_club_portal_file).grid(row=3, column=2, padx=10, pady=5)

    tk.Label(root, text="Save Merged File As:", bg="#1E90FF", fg="white").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    tk.Entry(root, textvariable=output_file_var, width=50).grid(row=4, column=1, padx=10, pady=5)
    tk.Button(root, text="Browse", command=save_output_file).grid(row=4, column=2, padx=10, pady=5)

    tk.Button(root, text="Merge Files", command=validate_and_merge).grid(row=5, column=1, pady=20)
    tk.Button(root, text="Help", command=show_help).grid(row=5, column=2, pady=20)

    # Run the GUI
    root.mainloop()


if __name__ == "__main__":
    merge_datasets_gui()
