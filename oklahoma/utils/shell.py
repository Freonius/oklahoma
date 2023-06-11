# -*- coding: utf-8 -*-
# pylint: enable=missing-function-docstring,missing-module-docstring,missing-class-docstring
"""Module for shell utilities.

"""
from sys import executable
from dataclasses import dataclass
from socket import gethostname, gethostbyname
from subprocess import Popen, PIPE, STDOUT
from binascii import unhexlify, Error
from shlex import quote, join
from ..exceptions import ShellError


@dataclass
class ShellReturn:
    """Dataclass that holds all output
    from a shell command.
    """

    exit_code: int
    return_string: str
    stderr: str

    def __str__(self) -> str:
        return self.return_string

    def __repr__(self) -> str:
        return self.return_string

    def __bool__(self) -> bool:
        return self.exit_code == 0


class Shell:
    """Class that holds static methods for shell
    utilities.
    """

    def __init__(self) -> None:
        pass

    @staticmethod
    def execute_python_module(
        *params: object,
        raise_on_error: bool = False,
    ) -> ShellReturn:
        """Execute a python module from the command line.

        Example:

        >>> from oklahoma.utils import Shell
        >>> out = Shell.execute_python_module('alembic', 'upgrade', 'head')
        >>> if out:
        >>>     print("OK!")
        >>> else:
        >>>     print("KO")

        Args:
            *params (object): Additional arguments can\
                                    be added here.
            raise_on_error (bool, optional): \
                raise ShellError on return code != 0. \
                Defaults to False.

        Raises:
            ShellReturn: If raise_on_error is True \
                and return code is not 0

        Returns:
            ShellReturn: It will have the output in str \
                format, the error output, and the return code.
        """
        return Shell.execute(
            executable + "" if __debug__ else " -O",
            "-m",
            *params,
            raise_on_error=raise_on_error,
        )

    @staticmethod
    def execute(
        cmd: str,
        *params: object,
        raise_on_error: bool = False,
    ) -> ShellReturn:
        """Execute a shell command.

        Example:

        >>> from oklahoma.utils import Shell
        >>> out = Shell.execute('echo', 'hi')
        >>> # Can also be Shell.execute('echo hi')
        >>> print(out)    # hi
        >>> print(out.exit_code)        # 0 (hopefully)
        >>> # or you could use the bool value
        >>> if out:
        >>>     print("OK!")
        >>> else:
        >>>     print("KO")


        Args:
            cmd (str): Command to execute.
            *params (object): Additional arguments can\
                                be added here.
            raise_on_error (bool): raise ShellError on return code != 0

        Raises:
            ShellReturn: If raise_on_error is True and return code is not 0

        Returns:
            ShellReturn: It will have the output in str format, the error output, and the
                         return code.
        """
        if len(params) > 0:
            cmd = cmd.strip() + " " + join(list(map(quote, list(map(str, params)))))
        _proc: Popen[bytes]
        with Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True) as _proc:
            _stdout_b: bytes
            _stderr_b: bytes
            _stdout_b, _stderr_b = _proc.communicate()
            _ret_code: int = _proc.returncode
            _stdout: str = ""
            try:
                _stdout = _stdout_b.decode("utf-8").strip()
            except AttributeError:  # pragma: no cover
                pass  # pragma: no cover
            del _stdout_b
            _stderr: str = ""
            try:
                _stderr = _stderr_b.decode("utf-8").strip()
            except AttributeError:
                pass
            del _stderr_b
            if _ret_code != 0 and raise_on_error is True:
                raise ShellError(
                    cmd,
                    _stdout,
                    _stderr,
                    _ret_code,
                )
            return ShellReturn(_ret_code, _stdout, _stderr)

    @staticmethod
    def get_docker_id() -> str:
        """Get the first 12 characters of a docker id, or the ip address of the host.

        Returns:
            str: docker id or ip address.
        """
        try:
            _proc: Popen
            with Popen(
                "echo $(basename $(cat /proc/1/cpuset))",
                stdout=PIPE,
                stderr=STDOUT,
                shell=True,
            ) as _proc:
                _container_id: str = _proc.communicate()[0].decode("utf-8").strip()[:12]
                unhexlify(_container_id)
                return _container_id  # pragma: no cover
        except Error:
            return gethostbyname(gethostname())
