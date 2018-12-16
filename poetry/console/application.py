import sys

from cleo import Application as BaseApplication
from clikit.api.args.format import ArgsFormat
from clikit.api.command import CommandCollection
from clikit.api.io import IO
from clikit.api.io.flags import VERY_VERBOSE
from clikit.args import ArgvArgs
from clikit.io import ConsoleIO
from clikit.io import NullIO
from clikit.ui.components.exception_trace import ExceptionTrace

from poetry import __version__
from poetry.events.application_boot_event import ApplicationBootEvent
from poetry.events.events import Events
from poetry.plugins.plugin_manager import PluginManager

from .commands import AboutCommand
from .commands import AddCommand
from .commands import BuildCommand
from .commands import CheckCommand
from .commands import ConfigCommand
from .commands import ExportCommand
from .commands import InitCommand
from .commands import InstallCommand
from .commands import LockCommand
from .commands import NewCommand
from .commands import PublishCommand
from .commands import RemoveCommand
from .commands import RunCommand
from .commands import SearchCommand
from .commands import ShellCommand
from .commands import ShowCommand
from .commands import UpdateCommand
from .commands import VersionCommand

from .commands.debug import DebugCommand

from .commands.cache import CacheCommand

from .commands.self import SelfCommand

from .config import ApplicationConfig

from .commands.env import EnvCommand


class Application(BaseApplication):
    def __init__(self):
        self._config = ApplicationConfig("poetry", __version__)
        self._preliminary_io = ConsoleIO()
        self._dispatcher = None
        self._commands = CommandCollection()
        self._named_commands = CommandCollection()
        self._default_commands = CommandCollection()
        self._global_args_format = ArgsFormat()
        self._booted = False
        self._poetry = None
        self._io = NullIO()

        # Enable trace output for exceptions thrown during boot
        self._preliminary_io.set_verbosity(VERY_VERBOSE)

        self._disable_plugins = False

    @property
    def poetry(self):
        from poetry.factory import Factory

        if self._poetry is not None:
            return self._poetry

        self._poetry = Factory().create_poetry(
            self._io, disable_plugins=self._disable_plugins
        )
        self._poetry.set_event_dispatcher(self._config.dispatcher)

        return self._poetry

    def run(self, args=None, input_stream=None, output_stream=None, error_stream=None):
        self._io = self._preliminary_io

        try:
            if args is None:
                args = ArgvArgs()

            self._disable_plugins = (
                args.has_token("--no-plugins")
                or args.tokens
                and args.tokens[0] == "new"
            )

            if not self._disable_plugins:
                plugin_manager = PluginManager("application.plugin")
                plugin_manager.load_plugins()
                plugin_manager.activate(self)

            self.boot()

            io_factory = self._config.io_factory

            self._io = io_factory(
                self, args, input_stream, output_stream, error_stream
            )  # type: IO

            resolved_command = self.resolve_command(args)
            command = resolved_command.command
            parsed_args = resolved_command.args

            status_code = command.handle(parsed_args, self._io)
        except Exception as e:
            if not self._config.is_exception_caught():
                raise

            trace = ExceptionTrace(e)
            trace.render(self._io)

            status_code = self.exception_to_exit_code(e)

        if self._config.is_terminated_after_run():
            sys.exit(status_code)

        return status_code

    def boot(self):  # type: () -> None
        if self._booted:
            return

        dispatcher = self._config.dispatcher

        self._dispatcher = dispatcher
        self._global_args_format = ArgsFormat(
            list(self._config.arguments.values()) + list(self._config.options.values())
        )

        for command_config in self._config.command_configs:
            self.add_command(command_config)

        for command in self.get_default_commands():
            self.add(command)

        if dispatcher and dispatcher.has_listeners(Events.APPLICATION_BOOT):
            dispatcher.dispatch(
                Events.APPLICATION_BOOT, ApplicationBootEvent(self._config)
            )

        self._booted = True

    def reset_poetry(self):  # type: () -> None
        self._poetry = None

    def get_default_commands(self):  # type: () -> list
        commands = [
            AboutCommand(),
            AddCommand(),
            BuildCommand(),
            CheckCommand(),
            ConfigCommand(),
            ExportCommand(),
            InitCommand(),
            InstallCommand(),
            LockCommand(),
            NewCommand(),
            PublishCommand(),
            RemoveCommand(),
            RunCommand(),
            SearchCommand(),
            ShellCommand(),
            ShowCommand(),
            UpdateCommand(),
            VersionCommand(),
        ]

        # Cache commands
        commands += [CacheCommand()]

        # Debug command
        commands += [DebugCommand()]

        # Env command
        commands += [EnvCommand()]

        # Self commands
        commands += [SelfCommand()]

        return commands

    def get_plugin_commands(self):
        plugin_manager = self.poetry.plugin_manager
        providers = plugin_manager.command_providers

        for provider in providers:
            for command in provider.commands:
                yield command


if __name__ == "__main__":
    Application().run()
