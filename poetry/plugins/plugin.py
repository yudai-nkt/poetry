from clikit.api.io import IO

from .base_plugin import BasePlugin


class Plugin(BasePlugin):
    """
    Generic plugin not related to the console application.

    The activate() method must be implemented and receives
    the Poetry instance.
    """

    type = "plugin"

    def activate(self, poetry, io):  # type: (Poetry, IO) -> None
        raise NotImplementedError()
