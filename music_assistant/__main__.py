"""Start Music Assistant."""
import argparse
import asyncio
import logging
import os
import platform
import sys

from aiorun import run
from music_assistant.mass import MusicAssistant


def get_arguments():
    """Arguments handling."""
    parser = argparse.ArgumentParser(description="MusicAssistant")

    data_dir = os.getenv("APPDATA") if os.name == "nt" else os.path.expanduser("~")
    data_dir = os.path.join(data_dir, ".musicassistant")
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir)

    parser.add_argument(
        "-c",
        "--config",
        metavar="path_to_config_dir",
        default=data_dir,
        help="Directory that contains the MusicAssistant configuration",
    )
    parser.add_argument(
        "--debug", default=False, help="Start MusicAssistant with verbose debug logging"
    )
    arguments = parser.parse_args()
    return arguments


def main():
    """Start MusicAssistant."""
    # setup logger
    logger = logging.getLogger()
    logformat = logging.Formatter(
        "%(asctime)-15s %(levelname)-5s %(name)s.%(module)s -- %(message)s"
    )
    consolehandler = logging.StreamHandler()
    consolehandler.setFormatter(logformat)
    logger.addHandler(consolehandler)

    # parse arguments
    args = get_arguments()
    data_dir = args.config
    # create event_loop with uvloop
    event_loop = asyncio.get_event_loop()
    try:
        import uvloop

        uvloop.install()
    except ImportError:
        # uvloop is not available on Windows so safe to ignore this
        logger.warning("uvloop support is disabled")
    # config debug settings if needed
    if args.debug:
        event_loop.set_debug(True)
        logger.setLevel(logging.DEBUG)
        logging.getLogger("aiosqlite").setLevel(logging.INFO)
        logging.getLogger("asyncio").setLevel(logging.WARNING)
    else:
        logger.setLevel(logging.INFO)

    mass = MusicAssistant(data_dir, event_loop)

    # run UI in browser on windows and macos only
    if platform.system() in ["Windows", "Darwin"]:
        import webbrowser

        webbrowser.open(f"http://localhost:{mass.web.http_port}")

    run(mass.start(), loop=event_loop)


if __name__ == "__main__":
    main()
