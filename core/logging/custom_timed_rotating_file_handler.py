from typing import Callable, Optional
from logging.handlers import TimedRotatingFileHandler


class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    """A timed rotating file handler that lets you pass the naming function directly."""

    def __init__(
        self,
        namer: Callable[[str], str],
        init_filename_arg: Optional[str] = None,
        *args,
        **kwargs
    ) -> None:
        super().__init__(namer(init_filename_arg), *args, **kwargs)
        self.namer = namer
