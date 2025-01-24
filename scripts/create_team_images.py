# Script Description:
# This script generates images by overlaying text onto a base image.
# It allows for multi-line text placement, dynamic resizing of the image canvas,
# and output file naming based on input text.
#
# The script supports configurable input file names, output directories,
# and logging options. Logging can output to a file, console, or both, with
# colourised log levels.
#
# Usage:
# python3 script_name.py --help
# Options include setting input file name, output directory,
# enabling/disabling console logging, and specifying a log file.

import logging
import argparse
from logging import getLogger
from PIL import Image, ImageDraw, ImageFont
import os
import sys

# Constants for default configurations
DEFAULT_INPUT_FILE = "wwfc.png"
DEFAULT_OUTPUT_DIR = "output_images"
DEFAULT_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DEFAULT_FONT_SIZE = 300
DEFAULT_TEXT_COLOUR = "#000033"
DEFAULT_PADDING = 400
DEFAULT_LINE_SPACING = 20

# Configure logging
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

# Validate file existence
def validate_file(file_path, description="file"):
    """
    Validates if a file exists.

    :param file_path: Path to the file to validate.
    :param description: Description of the file (e.g., "Input file").
    """
    if not os.path.isfile(file_path):
        logger.error(f"The specified {description} does not exist: {file_path}")
        sys.exit(1)

# Function to generate images with text
def generate_images(
    base_image_path, output_dir, teams_list, font_path=DEFAULT_FONT_PATH,
    font_size=DEFAULT_FONT_SIZE, fill_color=DEFAULT_TEXT_COLOUR
):
    """
    Generates images by overlaying text onto a base image.

    :param base_image_path: Path to the base image.
    :param output_dir: Directory to save the generated images.
    :param teams_list: List of strings to overlay on the images.
    :param font_path: Path to the font file.
    :param font_size: Font size for the text.
    :param fill_color: Colour of the text.
    """
    logger.info("Starting image generation process")

    try:
        # Validate the input file
        validate_file(base_image_path, "input image")
        validate_file(font_path, "font file")

        # Load the base image
        base_image = Image.open(base_image_path)
        image_width, image_height = base_image.size
        logger.debug(f"Base image loaded with size: {image_width}x{image_height}")

        # Prepare the font
        try:
            font = ImageFont.truetype(font_path, font_size)
            logger.debug(f"Font loaded: {font_path} with size {font_size}")
        except IOError:
            logger.error("Failed to load font. Using default font.")
            font = ImageFont.load_default()

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        logger.debug(f"Output directory ensured: {output_dir}")

        for text in teams_list:
            logger.info(f"Processing text: {text}")
            # Clean up the string and split it into lines if necessary
            clean_text = text.strip()
            if "(" in clean_text:
                line1, line2 = clean_text.split("(", 1)
                line1 = line1.strip()
                line2 = f"({line2.strip()}"
            else:
                line1 = clean_text
                line2 = ""

            # Create a copy of the base image and prepare to draw
            output_image = base_image.copy()
            draw = ImageDraw.Draw(output_image)

            # Calculate text positions
            line1_width, line1_height = font.getbbox(line1)[2], font.getbbox(line1)[3]
            line2_width, line2_height = (
                font.getbbox(line2)[2], font.getbbox(line2)[3]
            ) if line2 else (0, 0)

            total_text_height = (
                line1_height + (line2_height if line2 else 0) + DEFAULT_LINE_SPACING
            )  # Add extra padding between lines
            padding = max(DEFAULT_PADDING, total_text_height + 50)  # Ensure enough space

            # Add space for the text
            new_image_height = image_height + padding
            final_image = Image.new("RGB", (image_width, new_image_height), "white")
            final_image.paste(output_image, (0, 0))

            # Adjust vertical positions for both lines
            text_start_y = image_height + (padding - total_text_height) // 2

            # Draw text centred at the bottom
            line1_x = (image_width - line1_width) // 2
            draw = ImageDraw.Draw(final_image)
            draw.text((line1_x, text_start_y), line1, font=font, fill=fill_color)

            if line2:
                line2_x = (image_width - line2_width) // 2
                line2_y = text_start_y + line1_height + DEFAULT_LINE_SPACING
                draw.text((line2_x, line2_y), line2, font=font, fill=fill_color)

            # Save the image with a filename based on the text
            output_filename = os.path.join(
                output_dir,
                clean_text.replace(" ", "_").replace("(", "").replace(")", "") + ".png"
            )
            final_image.save(output_filename)
            logger.info(f"Saved: {output_filename}")

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)

# Main function
def main():
    """
    Main function to parse arguments and initiate the image generation process.
    """
    parser = argparse.ArgumentParser(
        description="Generate images with text overlayed on a base image."
    )
    parser.add_argument(
        "--input", type=str, default=DEFAULT_INPUT_FILE,
        help=f"Path to the input base image (default: {DEFAULT_INPUT_FILE})"
    )
    parser.add_argument(
        "--output", type=str, default=DEFAULT_OUTPUT_DIR,
        help=f"Path to the output directory (default: {DEFAULT_OUTPUT_DIR})"
    )
    parser.add_argument(
        "--font", type=str, default=DEFAULT_FONT_PATH,
        help=f"Path to the font file (default: {DEFAULT_FONT_PATH})"
    )
    parser.add_argument(
        "--font_size", type=int, default=DEFAULT_FONT_SIZE,
        help=f"Font size for the text (default: {DEFAULT_FONT_SIZE})"
    )
    parser.add_argument(
        "--fill_color", type=str, default=DEFAULT_TEXT_COLOUR,
        help=f"Colour of the text (default: {DEFAULT_TEXT_COLOUR})"
    )
    parser.add_argument(
        "--log_file", type=str, help="Path to the log file (optional)"
    )
    parser.add_argument(
        "--force_console", action="store_true",
        help="Force logging to console even if a log file is specified"
    )
    parser.add_argument(
        "--teams_file", type=str,
        help="Path to a file containing team names, one per line (optional)."
    )

    args = parser.parse_args()

    global logger
    logger = configure_logging(log_file=args.log_file, force_console=args.force_console)

    # Load team names
    if args.teams_file:
        validate_file(args.teams_file, "teams file")
        with open(args.teams_file, "r") as f:
            teams_list = [line.strip() for line in f if line.strip()]
    else:
        teams_list = [
            "U7 Blue",
            "U16 Red",
            "U12 Blue (Mark Bacon)"
        ]

    generate_images(
        base_image_path=args.input,
        output_dir=args.output,
        teams_list=teams_list,
        font_path=args.font,
        font_size=args.font_size,
        fill_color=args.fill_color
    )

if __name__ == "__main__":
    main()
