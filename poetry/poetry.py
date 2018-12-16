from __future__ import absolute_import
from __future__ import unicode_literals

from clikit.api.event import EventDispatcher

from .__version__ import __version__
from .config import Config
from .packages import Locker
from .packages import Package
from .plugins import PluginManager
from .repositories import Pool
from .utils._compat import Path
from .utils.toml_file import TomlFile


class Poetry:

    VERSION = __version__

    def __init__(
        self,
        file,  # type: Path
        local_config,  # type: dict
        package,  # type: Package
        locker,  # type: Locker
        config,  # type: Config
        auth_config,  # type: Config
    ):
        self._file = TomlFile(file)
        self._package = package
        self._local_config = local_config
        self._locker = locker
        self._config = config
        self._auth_config = auth_config
        self._event_dispatcher = EventDispatcher()
        self._plugin_manager = None
        self._pool = Pool()

    @property
    def file(self):
        return self._file

    @property
    def package(self):  # type: () -> Package
        return self._package

    @property
    def local_config(self):  # type: () -> dict
        return self._local_config

    @property
    def locker(self):  # type: () -> Locker
        return self._locker

    @property
    def pool(self):  # type: () -> Pool
        return self._pool

    @property
    def config(self):  # type: () -> Config
        return self._config

    @property
    def auth_config(self):  # type: () -> Config
        return self._auth_config

    @property
    def event_dispatcher(self):  # type: () -> EventDispatcher
        return self._event_dispatcher

    @property
    def plugin_manager(self):  # type: () -> PluginManager
        return self._plugin_manager

    def set_config(self, config):  # type: (Config) -> None
        self._config = config

    def set_auth_config(self, auth_config):  # type: (Config) -> None
        self._auth_config = auth_config

    def set_locker(self, locker):  # type: (Locker) -> None
        self._locker = locker

    def set_pool(self, pool):  # type: (Pool) -> None
        self._pool = pool

    def set_event_dispatcher(self, event_dispatcher):  # type: (EventDispatcher) -> None
        self._event_dispatcher = event_dispatcher

    def set_plugin_manager(self, plugin_manager):  # type: (PluginManager) -> None
        self._plugin_manager = plugin_manager
