import logging
from termcolor import colored


class CustomFormatter(logging.Formatter):
    LEVEL_COLOR = {
        logging.DEBUG: "green",
        logging.INFO: "blue",
        logging.WARNING: "yellow",
        logging.ERROR: "red",
        logging.CRITICAL: "red",
    }

    LEVEL_ATTRS = {
        logging.CRITICAL: ["underline"],
    }

    def __init__(self, *, colored: bool = False) -> None:
        super().__init__()
        self.colored = colored

    def format(self, record: logging.LogRecord) -> str:
        fmt = "%(asctime)s %(levelname)-8s %(name)s %(message)s"
        if self.colored:
            fmt %= {
                "asctime": colored("%(asctime)s", "dark_grey"),
                "levelname": colored(
                    "%(levelname)-8s",
                    self.LEVEL_COLOR.get(record.levelno),
                    attrs=self.LEVEL_ATTRS.get(record.levelno),
                ),
                "name": colored("%(name)s", "magenta"),
                "message": "%(message)s",
            }
        return logging.Formatter(fmt).format(record)
