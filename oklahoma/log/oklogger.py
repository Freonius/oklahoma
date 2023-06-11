from sys import stdout
from logging import (
    DEBUG,
    INFO,
    ERROR,
    WARNING,
    Logger,
    StreamHandler,
    Formatter,
    FileHandler,
)
from logging.handlers import RotatingFileHandler
from re import sub
from pathlib import Path
from os.path import abspath, isdir
from os import makedirs, sep
from contextlib import suppress
from typing import TYPE_CHECKING
from warnings import filterwarnings
from watchtower import CloudWatchLogHandler, DEFAULT_LOG_STREAM_NAME
from botocore.exceptions import ClientError
from ..aws import CloudWatchLogs
from ..utils import Singleton, Shell
from ..exceptions import ModuleLoadingError

if TYPE_CHECKING:
    from ..environment import Env

filterwarnings("ignore")


# pylint: disable=too-many-instance-attributes
class OKLogger(Logger, metaclass=Singleton):
    """Oklahoma Logger"""

    log_stream: str | None = None
    name_log_file: str
    frmt: str
    module_name: str
    _env: "Env | None"
    output: dict[int, str]
    formatter: Formatter

    @property
    def environ(self) -> "Env":
        """Environment"""
        if self._env is None:
            raise ModuleLoadingError("Module not yet loaded")
        return self._env

    @environ.setter
    def environ(self, val: "Env") -> None:
        self._env = val

    def _calc_level(self, _level: str) -> int:
        level: int = DEBUG
        try:
            _val: str = _level.upper().strip()
            if _val == "DEBUG":
                level = DEBUG
            elif _val == "INFO":
                level = INFO
            elif _val == "WARNING":  # pragma: no cover
                level = WARNING  # pragma: no cover
            elif _val == "ERROR":  # pragma: no cover
                level = ERROR  # pragma: no cover
            del _val
        except KeyError:  # pragma: no cover
            pass  # pragma: no cover
        if level is DEBUG and not __debug__:
            level = INFO  # I am going to be a nazi here
        return level

    def __init__(self, environ: "Env | None" = None) -> None:
        """The Oklahoma Logger (like any other loggers)

        Args:
            environ (Env | None, optional): Initialize it with\
                or without Env (it will be reloaded automatically).\
                      Defaults to None.
        """
        self._env = environ
        self.name_log_file = ""
        self.frmt = ""
        self.module_name = __name__
        self.output = {DEBUG: "", INFO: "", ERROR: "", WARNING: ""}
        self.formatter = Formatter(self.frmt)
        super().__init__(
            name="",
            level=INFO,
        )

    def __reload__(self) -> None:
        environ: "Env" = self.environ
        module: str = environ.profile.app.name
        log_stream: str | None = environ.profile.log.cloudwatch.stream
        log_level: str = environ.profile.log.level.value
        file: str = ""
        fld: str = self.environ.profile.log.folder
        if not fld.endswith(sep):
            fld += sep
        if environ.profile.log.file:
            file = fld + environ.profile.log.file
            if not file.endswith(".log"):
                file += ".log"
        else:
            _name: str = sub(r"(?<!^)(?=[A-Z])", "-", environ.profile.app.name).lower()
            file = fld + _name + ".log"
            del _name
        self.log_stream = log_stream
        level: int = self._calc_level(log_level)
        name_log_file: str = file

        module_name: str = module
        frmt: str | None = None

        if frmt is None:
            self.frmt = (
                f"[{module_name}@{Shell.get_docker_id()}"
                + ":%(asctime)s:%(module)s:%(lineno)s:%(levelname)s] %(message)s"
            )
        else:
            self.frmt = frmt  # pragma: no cover
        self.level = level
        self.name_log_file = name_log_file
        _log_fld: str = str(Path(abspath(self.name_log_file)).parent)
        if not isdir(_log_fld):
            makedirs(_log_fld)
        self.module_name = module_name

        self.formatter = Formatter(self.frmt)
        super().__init__(name=name_log_file, level=level)
        self._add_custom_handlers(log_level)
        self._add_rotation_handler()

    def _add_custom_handlers(self, level: str) -> None:
        self._add_custom_handler("stream", self._calc_level(level))
        if self.environ.profile.log.cloudwatch.use:
            with suppress(Exception):
                self._add_custom_handler("cloudwatch", self._calc_level(level))

    def _add_rotation_handler(
        self,
    ) -> None:
        _digits: int = self.environ.profile.log.rotation.size
        _size_part: str = self.environ.profile.log.rotation.unit.value
        if _size_part == "kb":
            _digits *= 1024
        elif _size_part == "mb":
            _digits *= 1024
            _digits *= 1024
        _bytes = _digits
        del _digits, _size_part
        _rh: RotatingFileHandler = RotatingFileHandler(
            self.name_log_file,
            backupCount=self.environ.profile.log.rotation.keep,
            maxBytes=_bytes,
        )
        _rh.formatter = self.formatter
        self.addHandler(_rh)
        del _bytes

    def _add_custom_handler(
        self,
        logtype: str,
        level: int | None = None,
    ) -> None:
        console_logger: StreamHandler | FileHandler | CloudWatchLogHandler
        if logtype == "stream":
            console_logger = StreamHandler(stdout)
        elif logtype == "file":
            console_logger = FileHandler(self.name_log_file)
        elif logtype == "cloudwatch":
            cloudwatch: CloudWatchLogs = CloudWatchLogs(
                self.module_name,
                self.environ.profile.aws.endpoint,
                self.environ.profile.aws.region,
            )
            try:
                cloudwatch.create(
                    stream_name=self.log_stream
                    if self.log_stream is not None
                    else DEFAULT_LOG_STREAM_NAME,
                    retention_days=self.environ.profile.log.cloudwatch.retention,
                    raise_on_error=True,
                )
                self.debug("Cloudwatch group created")
            except ClientError as ex:
                self.exception(ex)
            console_logger = CloudWatchLogHandler(
                log_group_name=self.module_name,
                log_stream_name=self.log_stream
                if self.log_stream is not None
                else DEFAULT_LOG_STREAM_NAME,
                boto3_client=cloudwatch.client,
            )
        else:
            return  # pragma: no cover
        if level is None:
            console_logger.setLevel(self.level)  # pragma: no cover
        else:
            console_logger.setLevel(level)
        console_logger.setFormatter(self.formatter)
        self.addHandler(console_logger)


# pylint: enable=too-many-instance-attributes
