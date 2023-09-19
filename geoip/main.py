import argparse
import logging
import os
import sys
from typing import Optional

from geoip import csv_report, load_env
from geoip.ipinfo import BulkEnrich, Enrich

__author__ = "Chapin Bryce"
__date__ = "2023-09-19"
logger = logging.getLogger(__name__)


def setup_logging(logging_obj, log_file, verbose=False):
    """Function to setup logging configuration and test it.

    Args:
        logging_obj: A logging instance, returned from logging.getLogger().
        log_file: File path to write log messages to.
        verbose: Whether or not to enable the debug level in STDERR output.
    """
    logging_obj.setLevel(logging.DEBUG)

    # Logging formatter. Best to keep consistent for most use cases
    log_format = logging.Formatter(
        "%(asctime)s %(filename)s %(levelname)s %(module)s "
        "%(funcName)s %(lineno)d %(message)s"
    )

    # Setup STDERR logging, allowing you uninterrupted
    # STDOUT redirection
    stderr_handle = logging.StreamHandler(stream=sys.stderr)
    if verbose:
        stderr_handle.setLevel(logging.DEBUG)
    else:
        stderr_handle.setLevel(logging.INFO)
    stderr_handle.setFormatter(log_format)

    # Setup file logging
    file_handle = logging.FileHandler(log_file, "a")
    file_handle.setLevel(logging.DEBUG)
    file_handle.setFormatter(log_format)

    # Add handles
    logging_obj.addHandler(stderr_handle)
    logging_obj.addHandler(file_handle)


def setup_argparse(cli_args: list[str]) -> argparse.Namespace:
    # Setup a parser instance with common fields including a
    # description and epilog. The `formatter_class` instructs
    # argparse to show default values set for parameters.
    parser = argparse.ArgumentParser(
        description="GeoIP enrichment",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=f"Built by {__author__}, v.{__date__}",
    )

    # The simplest form of adding an argument, the name of the
    # parameter and a description of its form.
    parser.add_argument("IPS", help="Input file to parse", nargs="+")
    parser.add_argument("REPORT_NAME", help="Report file name")

    # An optional argument with multiple methods of specifying
    # the parameter. Includes a default value
    parser.add_argument(
        "-l",
        "--log",
        help="Path to log file",
        default="geoip.log",
    )

    # An optional argument which does not accept a value, instead
    # just modifies functionality.
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Include debug log messages"
    )

    # Once we've specified our arguments we can parse them for
    # reference
    args = parser.parse_args(cli_args)

    # Returning our parsed arguments for further use.
    return args


def entry(cli_args: Optional[list[str]] = None) -> None:
    """Entry point for the CLI."""
    if not cli_args:
        cli_args = sys.argv[1:]

    args = setup_argparse(cli_args)

    setup_logging(logger, args.log, args.verbose)

    logger.info("Starting enrichment.")

    if len(args.IPS) > 1:
        logger.info("Multiple IPs detected. Batching requests.")
        client = BulkEnrich(api_key=os.environ["API_KEY"])
    else:
        client = Enrich(api_key=os.environ["API_KEY"])
    enriched_data = client.lookup(args.IPS)
    logger.info("Enrichment complete. Generating report.")
    csv_report.create_report(args.REPORT_NAME, enriched_data)
    logger.info("Complete.")


if __name__ == "__main__":
    entry()
