from __future__ import annotations
import os
from pathlib import Path
import subprocess
from typing import Any, Callable

from .errors import PlinkError
from .inspect import InspectionView
from .utils import _get_valid_plink2_binary, _get_valid_plink1_9_binary


class Plink:
    def __init__(
        self, workdir: Path | str | None = None, binary: Path | str | None = None
    ):
        """Entrypoint to plink.

        Parameters
        ----------
        workdir : Pathlike or None
            The directory in which plink should run. If None, then will
            use the current working directory.

        binary : Pathlike or None, optional, default None
            One of The location of the plink binary to use, `None`, or a string
            specifying the version number. If `None` provided, will default to
            plink 2.

        """
        if workdir:
            workdir = Path(workdir)
            if not workdir.exists():
                raise ValueError(f"No such directory: {workdir}")
        self.workdir = workdir
        self._workdir = self.workdir if self.workdir else Path(os.getcwd())
        self.binary = binary
        self._binary = self._validate_binary(binary)

    def __repr__(self) -> str:
        workdir = self.workdir.as_posix() if self.workdir else None  # type: ignore
        return f"{self.__class__.__name__}(wordir={workdir})"

    def run(
        self,
        bfile: str | Path | None = None,
        out: str | Path | None = None,
        **kwargs: Any,
    ) -> InspectionView:
        """Runs a plink command with the parameters passed."""
        cmd = [self._binary]
        params = kwargs.copy()

        # Set bfile:
        if bfile:
            bfile = Path(bfile)
            cmd += ["--bfile", bfile.as_posix()]
            params["bfile"] = bfile
        # Set output
        if out and self.workdir:
            out = (self._workdir / out).as_posix()  # type: ignore
            cmd += ["--out", out]
            params["out"] = out

        for key, val in kwargs.items():
            key = key.replace("_", "-")
            # Set boolean flags
            if isinstance(val, bool) and val:
                cmd += [f"--{key}"]
            # Keywords with multiple parameters
            elif isinstance(val, (tuple, list)):
                cmd += [f"--{key}"] + [str(x) for x in val]
            # Keywords with single parameters
            else:
                cmd += [f"--{key}", str(val)]

        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if process.returncode != 0:
            raise PlinkError(process.stderr.decode("utf-8"))

        return InspectionView(process.stdout, params)

    def _validate_binary(self, binary: str | Path | None) -> str:
        valid_strings = {
            "1": _get_valid_plink1_9_binary,
            "1.9": _get_valid_plink1_9_binary,
            "2": _get_valid_plink2_binary,
        }
        if binary is None:
            return _get_valid_plink2_binary()
        if binary in valid_strings:
            return valid_strings[binary]()
        binary = Path(binary)
        if binary.exists():
            return binary.as_posix()
        raise ValueError(f"No plink binary found matching '{binary}'")
